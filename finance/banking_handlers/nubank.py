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

    def process_credit_card(self, transactions):
        card_statements = self.client.get_card_statements()

        credit_card_transactions_to_add = []
        for card_statement in card_statements:
            exists = exists_in_worksheet(card_statement, transactions)

            if not exists:
                transaction_time = datetime.strptime(card_statement['time'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                    '%Y-%m-%dT%H:%M')
                amount = str(card_statement["amount"])[:-2] + "." + str(card_statement["amount"])[-2:]

                new_transaction = create_transaction(transaction_id=card_statement['id'],
                                                     time=transaction_time,
                                                     description=card_statement["description"],
                                                     amount=amount,
                                                     account="Nubank",
                                                     synced_at=datetime.today().strftime("%Y-%m-%dT%H:%M"))

                credit_card_transactions_to_add.append(new_transaction)

        if len(credit_card_transactions_to_add) > 0:
            self.gc.add_transactions_to_worksheet(credit_card_transactions_to_add)
        else:
            print('Nothing to sync')
