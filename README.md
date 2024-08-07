# Automation of Reward Payments for Hive Power Delegators of Nexo Digital

This Python project automates the management of delegations and rewards on the Hive blockchain. It collects information from delegators, calculates rewards, processes payments, and generates detailed reports, in addition to sending notifications to Telegram and Discord.

## Description

The purpose of this project is to facilitate the management of Hive Power (HP) delegations for the [Nexo Digital](https://peakd.com/@nexo.digital "Nexo Digital Community") community, calculate HP rewards, automatically process payments, and generate reports. The script can be configured to run daily at a specific time and sends notifications with the payment status. It can also be adapted and used by any curation community on the Hive Blockchain.

## Installation

1. Clone the repository and navigate to the project folder:

   ```bash
   git clone https://github.com/sousafrc/payment-delegators-nexo-digital.git
   cd payment-delegators-nexo-digital
   ```
2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\Activate`
   ```
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit the `.env-example` file at the root of the project to configure the environment variables. After that, save and rename it to `.env`. Below is a configuration example:

```plaintext
RECEIVER_ACCOUNT=nexo.voter
PARTNER_ACCOUNTS=nexo.digital,nexo.witness,nexo.token

TOKEN_NAME=NEXO
TOKEN_FIXED_PRICE=0.1
HIVE_DEDUCTION_MULTIPLIER=2

ACTIVATE_PAYMENTS=True
PAYMENT_ACCOUNT=nexo.pool
HIVE_ENGINE_ACTIVE_PRIVATE_KEY=
HIVE_ENGINE_POSTING_PRIVATE_KEY=
IGNORE_PAYMENT_ACCOUNTS=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
```

## Usage

1. Ensure that the environment variables in the `.env` file are correctly configured.
2. Run the script:
   ```bash
   python main.py
   ```

The script will run daily at the specified time if automation is enabled (`AUTO_RUN=True`). It will process payments, generate reports, and send notifications to Telegram and Discord.

## Features

### Delegator Information Collection

- **fetch_delegators**: Fetches information about delegations made to the specified account.
- **get_account_info**: Retrieves the Hive Power (HP) of the receiver account.
- **get_partner_accounts**: Retrieves partner accounts.
- **get_ignore_payment_accounts**: Retrieves accounts to be ignored in payments.

### Reward Calculation

- **calculate_earnings**: Calculates the HP earnings of the receiver account compared to the previous period.
- **calculate_additional_columns**: Calculates percentages and HIVE deductions based on specific rules.

### Payment Processing

- **process_payments**: Processes reward payments for each eligible delegator.
- **process_payment_for_delegator**: Processes payment for a specific delegator.

### Report Generation

- **save_delegators_to_xlsx**: Generates an XLSX file with detailed information about delegators and rewards.
- **generate_status_message**: Generates a detailed message about the payment status.

### Notifications and Logs

- **send_telegram_file**: Sends notifications with the log file to Telegram.
- **send_discord_file**: Sends notifications with the generated XLSX file to Discord.

### Configuration Management

- **check_env_variables**: Checks if all necessary environment variables are configured.

## Project Structure

```plaintext
payment-delegators-nexo-digital/
├── data/
│   ├── log/
│   └── ...
├── modules/
│   ├── account_info.py
│   ├── calculations.py
│   ├── config.py
│   ├── discord_utils.py
│   ├── fetch_delegators.py
│   ├── logger.py
│   ├── memo_utils.py
│   ├── partners_info.py
│   ├── payments.py
│   ├── process_payment.py
│   ├── save_to_xlsx.py
│   ├── telegram_utils.py
│   ├── transaction.py
│   ├── utils.py
│   └── wallet_utils.py
├── .env
├── LICENSE.md
├── main.py
├── README.md
└── requirements.txt
```

## Contribution

1. Fork the repository.
2. Create a branch for your feature (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Support the Developer

If you find this project useful, consider supporting the developer by donating any amount to the [@sousafrc](https://peakd.com/@sousafrc "Fernando Sousa") account on the Hive Blockchain!
