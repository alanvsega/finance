import os
import sys

from banking_handlers.nubank import NubankHandler
from gspread_handler.gspread_handler import GSpreadHandler


def process_transactions_from_accounts():
    # Clients required to run
    gc = GSpreadHandler(spreadsheet=os.environ["GOOGLE_SPREADSHEET_KEY"])
    nu_client = NubankHandler(os.environ["NUBANK_CPF"], os.environ["NUBANK_PASSWORD"], gc)

    # Before we process the transactions, it will get the transactions that have already
    # been added in the Google worksheet, so we can check it to avoid duplicates
    transactions_in_worksheet = gc.get_transactions_from_worksheet()

    nu_client.process(transactions_in_worksheet)


def handle_pubsub(event, context):
    process_transactions_from_accounts()
    print('Finished the syncing process')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        process_transactions_from_accounts()
    else:
        print('You need to explicit pass \'run\' as argument to start the processing.')
