import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from colorama import Fore, Style, init
from tabulate import tabulate
from modules.fetch_delegators import fetch_delegators
from modules.account_info import get_account_info, vests_to_hp
from modules.partners_info import get_partner_accounts, get_ignore_payment_accounts
from modules.utils import get_latest_file, get_previous_own_hp
from modules.save_to_xlsx import save_delegators_to_xlsx
from modules.payments import process_payments
from modules.calculations import calculate_additional_columns
from modules.logger import setup_logging
from modules.telegram_utils import send_telegram_file
from modules.discord_utils import send_discord_file

init(autoreset=True)


def check_env_variables():
    required_vars = [
        "RECEIVER_ACCOUNT",
        "PAYMENT_ACCOUNT",
        "HIVE_ENGINE_ACTIVE_PRIVATE_KEY",
        "HIVE_ENGINE_POSTING_PRIVATE_KEY",
        "TOKEN_NAME",
        "TOKEN_FIXED_PRICE",
        "HIVE_DEDUCTION_MULTIPLIER",
        "ACTIVATE_PAYMENTS",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "DISCORD_BOT_TOKEN",
        "DISCORD_CHANNEL_ID",
    ]
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logging.error(f"Environment variable {var} is not set")
            print(
                f"{Fore.RED}[Error]{Style.RESET_ALL} Environment variable {Fore.BLUE}{var}{Style.RESET_ALL} is not set"
            )

    if missing_vars:
        raise EnvironmentError(
            f"Environment variables not set: {', '.join(missing_vars)}"
        )

    logging.info(f"All required environment variables are set.")
    print(
        f"{Fore.GREEN}[Success]{Style.RESET_ALL} All required environment variables are set."
    )


def get_own_hp(receiver_account):
    try:
        logging.debug(f"Starting to fetch own HP for {receiver_account}.")
        own_hp = get_account_info(receiver_account)
        logging.info(f"Own HP for {receiver_account} is {own_hp}")
        return own_hp
    except Exception as e:
        logging.error(f"Error fetching own HP for {receiver_account}: {e}")
        raise


def fetch_delegators_info(receiver_account):
    try:
        logging.info(f"Fetching delegators info for {receiver_account}...")

        delegators_list = fetch_delegators()
        logging.debug(f"Delegators list: {delegators_list}")

        partner_accounts = get_partner_accounts()
        logging.debug(f"Partner accounts: {partner_accounts}")

        ignore_payment_accounts = get_ignore_payment_accounts()
        logging.debug(f"Ignore payment accounts: {ignore_payment_accounts}")

        logging.info(f"Delegators info fetched successfully for {receiver_account}.")
        return delegators_list, partner_accounts, ignore_payment_accounts
    except Exception as e:
        logging.error(f"Error fetching delegators info for {receiver_account}: {e}")
        raise


def calculate_earnings(own_hp, receiver_account):
    try:
        logging.info(f"Calculating earnings for {receiver_account}...")

        latest_file = get_latest_file("data", "pd_")
        logging.debug(f"Latest file found: {latest_file}")

        previous_own_hp = round(get_previous_own_hp(latest_file, receiver_account), 3)
        logging.debug(f"Previous own HP: {previous_own_hp}")

        earnings = round(own_hp - previous_own_hp, 3)
        logging.info(f"Earnings calculated: {earnings}")

        return earnings
    except Exception as e:
        logging.error(f"Error calculating earnings for {receiver_account}: {e}")
        raise


def process_delegators(delegators_list, partner_accounts):
    try:
        logging.info("Processing delegators list...")
        partner_hp = 0
        delegators = []
        for item in delegators_list:
            try:
                delegator = item["delegator"]
                vesting_shares = float(item["vesting_shares"])
                delegated_hp = round(vests_to_hp(vesting_shares, delegator), 3)
                if delegator in partner_accounts:
                    partner_hp += delegated_hp
                else:
                    delegators.append(
                        {"Account": delegator, "Delegated HP": delegated_hp}
                    )
                logging.debug(f"Processed delegator {delegator}: {delegated_hp} HP")
            except Exception as e:
                logging.error(f"Error processing delegator {item}: {e}")
        partner_hp = round(partner_hp, 3)
        logging.info(f"Delegators processed successfully. Partner HP: {partner_hp}")
        return delegators, partner_hp
    except Exception as e:
        logging.error(f"Error processing delegators: {e}")
        raise


def insert_accounts_into_df(delegators, receiver_account, receiver_hp, partner_hp):
    try:
        logging.info("Inserting accounts into DataFrame...")
        delegators.insert(0, {"Account": receiver_account, "Delegated HP": receiver_hp})
        delegators.insert(
            1, {"Account": "Partner Accounts", "Delegated HP": partner_hp}
        )
        logging.debug(
            f"Receiver account and partner accounts inserted: {delegators[:2]}"
        )
        logging.info("Accounts inserted into DataFrame successfully.")
        return delegators
    except Exception as e:
        logging.error(f"Error inserting accounts into DataFrame: {e}")
        raise


def main():
    try:
        now = datetime.now()
        timestamp = now.strftime("pd_%m-%d-%Y_%H-%M-%S")

        setup_logging(timestamp)

        load_dotenv()

        check_env_variables()

        receiver_account = os.getenv("RECEIVER_ACCOUNT")
        own_hp = round(get_own_hp(receiver_account), 3)

        earnings = calculate_earnings(own_hp, receiver_account)

        delegators_list, partner_accounts, ignore_payment_accounts = (
            fetch_delegators_info(receiver_account)
        )

        delegators, partner_hp = process_delegators(delegators_list, partner_accounts)

        delegators = insert_accounts_into_df(
            delegators, receiver_account, own_hp, partner_hp
        )

        logging.info("Calculating additional columns...")
        df = calculate_additional_columns(delegators, earnings)
        df["Unique Hash"] = ""
        logging.info("Additional columns calculated successfully.")

        logging.info("DataFrame before rewards:")
        print(tabulate(df, headers="keys", tablefmt="psql"))
        logging.debug(f"\n{tabulate(df, headers='keys', tablefmt='psql')}")

        logging.info("Processing rewards...")
        payments_enabled = os.getenv("ACTIVATE_PAYMENTS", "False") == "True"
        if payments_enabled:
            process_payments(df)
        else:
            print(tabulate(df, headers="keys", tablefmt="psql"))
            logging.info(
                "Payments are deactivated. Only spreadsheets will be generated."
            )

        logging.info("Saving delegators list to XLSX...")
        save_delegators_to_xlsx(df, earnings)

        logging.info("All tasks completed successfully.")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
    finally:
        log_file_path = f"data/log/log_{timestamp}.txt"
        telegram_success = send_telegram_file(
            log_file_path, "Log file for the latest execution"
        )
        if telegram_success:
            logging.info("Log file sent successfully to Telegram.")
        else:
            logging.error("Failed to send log file to Telegram.")

        latest_xlsx_file = get_latest_file("data", "pd_")
        discord_success = send_discord_file(
            latest_xlsx_file, "Spreadsheet for the latest execution"
        )
        if discord_success:
            logging.info("Spreadsheet file sent successfully to Discord.")
        else:
            logging.error("Failed to send spreadsheet file to Discord.")


if __name__ == "__main__":
    main()
