import os
from banking_handlers.nubank import NubankHandler
from gspread_handler.gspread_handler import GSpreadHandler

# Clients required to run
gc = GSpreadHandler(spreadsheet=os.environ["GOOGLE_SPREADSHEET_KEY"])
nu_client = NubankHandler(os.environ["NUBANK_CPF"], os.environ["NUBANK_PASSWORD"], gc)


def process_transactions_from_accounts():
    # Before we process the transactions, it will get the transactions that have already
    # been added in the Google worksheet, so we can check it to avoid duplicates
    transactions_in_worksheet = gc.get_transactions_from_worksheet()

    nu_client.process(transactions_in_worksheet)


def handle_pubsub(event, context):
    process_transactions_from_accounts()
    print('Finished the syncing process')


process_transactions_from_accounts()
