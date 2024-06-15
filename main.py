import os
from dotenv import load_dotenv
import pandas as pd
from colorama import Fore, Style, init
from modules.fetch_delegators import fetch_delegators
from modules.account_info import get_account_info, vests_to_hp
from modules.partners_info import get_partner_accounts, get_ignore_payment_accounts
from modules.utils import get_latest_file, get_previous_own_hp
from modules.save_to_xlsx import save_delegators_to_xlsx
from modules.payments import process_payments
from modules.calculations import calculate_additional_columns

# Initialize colorama
init(autoreset=True)

load_dotenv()

def get_own_hp(receiver_account):
    try:
        return get_account_info(receiver_account)
    except Exception as e:
        print(f"{Fore.RED}[Error]{Style.RESET_ALL} Error fetching own HP: {e}")
        return 0

def process_delegators(delegators_list, partner_accounts):
    partner_hp = 0
    delegators = []
    for item in delegators_list:
        try:
            delegator = item['delegator']
            vesting_shares = float(item['vesting_shares'].replace(' VESTS', ''))
            delegated_hp = round(vests_to_hp(vesting_shares, delegator), 3)
            if delegator in partner_accounts:
                partner_hp += delegated_hp
            else:
                delegators.append({
                    "Account": delegator,
                    "Delegated HP": delegated_hp
                })
        except Exception as e:
            print(f"{Fore.RED}[Error]{Style.RESET_ALL} Error processing delegator {Fore.BLUE}{item}{Style.RESET_ALL}: {e}")
    partner_hp = round(partner_hp, 3)
    return delegators, partner_hp

def insert_accounts_into_df(delegators, receiver_account, receiver_hp, partner_hp, ignore_payment_accounts):
    delegators.insert(0, {"Account": receiver_account, "Delegated HP": receiver_hp})
    delegators.insert(1, {"Account": "Partner Accounts", "Delegated HP": partner_hp})
    return delegators

def main():
    try:
        receiver_account = os.getenv("RECEIVER_ACCOUNT")
        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Fetching own HP for {Fore.BLUE}{receiver_account}{Style.RESET_ALL}...")
        own_hp = round(get_own_hp(receiver_account), 3)

        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Fetching latest file...")
        latest_file = get_latest_file('data', 'pd_')
        previous_own_hp = round(get_previous_own_hp(latest_file, receiver_account), 3)

        earnings = round(own_hp - previous_own_hp, 3)

        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Fetching delegators list...")
        delegators_list = fetch_delegators()
        partner_accounts = get_partner_accounts()
        ignore_payment_accounts = get_ignore_payment_accounts()

        delegators, partner_hp = process_delegators(delegators_list, partner_accounts)

        delegators = insert_accounts_into_df(delegators, receiver_account, own_hp, partner_hp, ignore_payment_accounts)

        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Calculating additional columns...")
        df = calculate_additional_columns(delegators, earnings)

        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Processing payments...")
        process_payments(df)

        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Saving delegators list to XLSX...")
        save_delegators_to_xlsx(df, earnings)

    except Exception as e:
        print(f"{Fore.RED}[Error]{Style.RESET_ALL} Error in main execution: {e}")

if __name__ == "__main__":
    main()
