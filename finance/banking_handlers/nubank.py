import google.auth
import pynubank
import os
from datetime import datetime
from gspread_handler.gspread_handler import create_transaction
from google.cloud import storage
import tempfile


def exists_in_worksheet(card_statement, transactions):
    exists = False

    for transaction in transactions:
        if transaction["id"] == card_statement["id"]:
            exists = True  # there is already a transaction with the same transaction ID

    return exists


class NubankHandler:
    DEFAULT_SCOPES = ['https://www.googleapis.com/auth/devstorage.read_only']

    def __init__(self, cpf, password, gc, cert_path=None):
        self.client = pynubank.Nubank()

        if cert_path is not None:
            self.client.authenticate_with_cert(cpf, password, cert_path)
        else:
            creds, _ = google.auth.default(scopes=self.DEFAULT_SCOPES)

            storage_client = storage.Client(os.environ["GCP_BUCKET_PROJECT"], credentials=creds)
            bucket = storage_client.get_bucket(os.environ["GCP_BUCKET_NAME"])
            blob = bucket.blob("finance/nubank-access-api-cert.p12")
            blob.download_to_filename(f"{tempfile.gettempdir()}/nubank-access-api-cert.p12")

            self.client.authenticate_with_cert(cpf, password, f"{tempfile.gettempdir()}/nubank-access-api-cert.p12")

        self.gc = gc

    def process(self, transactions):

        print('Processing Nubank Credit Card')
        self.process_credit_card(transactions)

        print('Processing Nu Conta')
        self.process_nuconta(transactions)

        print('Updating account balance overview')
        self.update_account_balance()
        self.update_credit_card_balance_overview()

        print('Finished syncing Nubank')

    def process_credit_card(self, transactions):
        card_statements = self.client.get_card_statements()

        credit_card_transactions_to_add = []
        for card_statement in card_statements:
            exists = exists_in_worksheet(card_statement, transactions)

            if not exists:
                transaction_time = datetime.strptime(card_statement['time'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                    '%Y-%m-%dT%H:%M')
                amount = str(card_statement["amount"])[:-2] + "." + str(card_statement["amount"])[-2:]

                # All credit card statements are positive numbers from the Nubank API.
                # But this is a going to be saved as negative to explicit define a spent transaction
                amount = str(float(amount) * -1)

                new_transaction = create_transaction(transaction_id=card_statement['id'],
                                                     time=transaction_time,
                                                     description=card_statement["description"],
                                                     amount=amount,
                                                     account="Nubank Crédito",
                                                     synced_at=datetime.today().strftime("%Y-%m-%dT%H:%M"))

                credit_card_transactions_to_add.append(new_transaction)

        if len(credit_card_transactions_to_add) > 0:
            self.gc.add_transactions_to_worksheet(credit_card_transactions_to_add)
        else:
            print('Nothing to sync (credit card)')

    def process_nuconta(self, transactions):
        nuconta_statements = self.client.get_account_statements()

        nuconta_statements_to_add = []
        for nuconta_statement in nuconta_statements:
            exists = exists_in_worksheet(nuconta_statement, transactions)

            if not exists:
                transaction_time = datetime.strptime(nuconta_statement["postDate"], "%Y-%m-%d").strftime(
                    "%Y-%m-%dT%H:%M")

                if nuconta_statement["__typename"] == 'PixTransferOutEvent':
                    amount = float(nuconta_statement["amount"]) * -1
                elif nuconta_statement["__typename"] == 'TransferInEvent':
                    amount = float(nuconta_statement["amount"])
                elif nuconta_statement["__typename"] == 'BillPaymentEvent':
                    amount = float(nuconta_statement["amount"]) * -1
                elif nuconta_statement["__typename"] == 'DebitPurchaseEvent':
                    amount = float(nuconta_statement["amount"]) * -1
                elif nuconta_statement["__typename"] == 'BarcodePaymentEvent':
                    amount = float(nuconta_statement["amount"]) * -1
                else:
                    amount = float(nuconta_statement["amount"]) * -1

                description = nuconta_statement["title"] + " - " + nuconta_statement["detail"].replace("\n", " ")

                new_transaction = create_transaction(transaction_id=nuconta_statement['id'],
                                                     time=transaction_time,
                                                     description=description,
                                                     amount=amount,
                                                     account="Nubank",
                                                     synced_at=datetime.today().strftime("%Y-%m-%dT%H:%M"))
                nuconta_statements_to_add.append(new_transaction)

        if len(nuconta_statements_to_add) > 0:
            self.gc.add_transactions_to_worksheet(nuconta_statements_to_add)
        else:
            print('Nothing to sync (Nubank)')

    def update_account_balance(self):
        current_balance = self.client.get_account_balance()
        self.gc.update_balance_overview(current_balance, 'Nubank')

    def update_credit_card_balance_overview(self):
        all_bills = self.client.get_bills()

        current_balance = -1
        for bill in all_bills:
            if bill["state"] == "open":
                current_balance = str(bill["summary"]["total_balance"])[:-2] + "." + str(bill["summary"]["total_balance"])[-2:]
                break

        current_balance = str(float(current_balance) * -1)
        self.gc.update_balance_overview(current_balance, 'Nubank Crédito')
