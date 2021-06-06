import gspread


class GSpreadHandler:
    def __init__(self, service_account_json_file, spreadsheet_key):
        self.client = gspread.service_account(filename=service_account_json_file)
        self.sheet = self.client.open_by_key(spreadsheet_key)
