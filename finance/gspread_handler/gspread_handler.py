import gspread
import os
import google.auth


def create_transaction(transaction_id=None, time=None, description="", amount=None, account="",
                       synced_at=None):
    return {"id": transaction_id,
            "time": time,
            "description": description,
            "amount": amount,
            "account": account,
            "synced_at": synced_at
            }


class GSpreadHandler:
    DEFAULT_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

    def __init__(self, spreadsheet=None, service_account_json_file=None):
        if service_account_json_file is not None:
            self.client = gspread.service_account(filename=service_account_json_file)
        else:
            creds, _ = google.auth.default(scopes=self.DEFAULT_SCOPES)
            self.client = gspread.authorize(creds)

        self.spreadsheet = self.client.open_by_key(spreadsheet)
        self.worksheet = self.spreadsheet.worksheet("Transactions")

    def get_transactions_from_worksheet(self):
        transactions_range = self.worksheet.get("A2:F")

        if len(transactions_range) != 0:
            transactions = [create_transaction(transaction_id=transaction[0],
                                               time=transaction[1],
                                               description=transaction[2],
                                               amount=transaction[3],
                                               account=transaction[4],
                                               synced_at=transaction[5]) for transaction in transactions_range]
        else:
            return []

        return transactions

    def add_transactions_to_worksheet(self, transactions):
        past_transactions = self.get_transactions_from_worksheet()

        next_index = len(past_transactions) + 2

        range_to_update = f'A{next_index}:F{len(transactions) + 2}'

        parsed_transactions = []
        for transaction in transactions:
            parsed_transactions.append([
                transaction["id"],
                transaction["time"],
                transaction["description"],
                transaction["amount"],
                transaction["account"],
                transaction["synced_at"]
            ])

        self.worksheet.update(range_to_update, parsed_transactions)

        print('Added set of transactions')
