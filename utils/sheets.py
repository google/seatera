import re
import logging
from typing import List, Any, Dict
from datetime import datetime
from google.oauth2.credentials import Credentials
from utils.auth import CONFIG_FILE, SCOPES
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

_SHEETS_SERVICE_VERSION = 'v4'
_SHEETS_SERVICE_NAME = 'sheets'

_HEADER = ['keyword', 'account name', 'account id', 'campaign name',
           'campaign id', 'adgroup name', 'adgroup id', 'clicks', 'impressions', 'conversions', 'cost', 'ctr']
_RUN_DATETIME = datetime.now()
_RUN_METADATA = f'Last run was completed on {_RUN_DATETIME}'
_KEYWORDS_SHEET = 'Keywords'
_EXCLUSIONS_SHEET = 'Exclusions'
_SS_NAME = 'SeaTerA'

class SheetsInteractor:
    def __init__(self, service, spreadsheet_url):
        self.service = service.spreadsheets()
        self.spreadsheet_url = spreadsheet_url
        self.spreadsheet_id = self._get_spreadsheet_id()

    def _get_spreadsheet_id(self) -> str:
        # Returns spreadsheet ID from spreadsheet URL
        if not self.spreadsheet_url:
            raise Exception(
                "No spreadsheet URL found. Follow instructions in README and add spreadsheet URL in config.yaml")

        spreadsheet_regex = '/d/(.*?)/edit'
        spreadsheet_match = re.search(spreadsheet_regex, self.spreadsheet_url)

        if spreadsheet_match == None:
            raise Exception("Couldn't extract spreadsheet ID from URL.")

        spreadsheet_id = spreadsheet_match.group(1)
        return spreadsheet_id

    def write_to_spreadsheet(self, ouput: Dict[str, Dict[Any, Any]]):
        data = []
        for sheet, values in ouput.items():
            self._clear_sheet(sheet)
            range = sheet + '!A1:' + \
                chr(len(values[0]) + 65) + str(len(values))
            data.append({'range': range, 'values': values})

        body = {'data': data, 'valueInputOption': "USER_ENTERED"}
        try:
            result = self.service.values().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=body).execute()
            logging.info(
                f"{(result.get('totalUpdatedRows') -4)} Rows updated.")
            return result
        except HttpError as e:
            logging.exception(e)
            return e

    def read_from_spreadsheet(self, range) -> List[List[Any]]:
        results = self.service.values().get(
            spreadsheetId=self.spreadsheet_id, range=range).execute()
        values = results.get('values', [])
        return values

    def _clear_sheet(self, sheet_name):
        """Helper function to clear output sheet before writing to it."""
        range_name = sheet_name + '!A:Z'
        self.service.values().clear(
            spreadsheetId=self.spreadsheet_id, range=range_name, body={}).execute()


def get_sheets_service(config: Dict[str, Any]):
    creds = None
    user_info = {
        "client_id": config['client_id'],
        "refresh_token": config['refresh_token'],
        "client_secret": config['client_secret']
    }
    creds = Credentials.from_authorized_user_info(user_info, SCOPES)

    # If credentials are expired, refresh.
    if creds.expired:
        creds.refresh(Request())

    service = build(_SHEETS_SERVICE_NAME,
                    _SHEETS_SERVICE_VERSION, credentials=creds)
    return service


def create_new_spreadsheet(sheet_service):
    spreadsheet_title = _SS_NAME
    worksheet_names = [_EXCLUSIONS_SHEET,
                        _KEYWORDS_SHEET]
    sheets = []
    for name in worksheet_names:
        worksheet = {
            'properties': {
                'title': name
            }
        }
        sheets.append(worksheet)

    spreadsheet = {
        'properties': {
            'title': spreadsheet_title
            },
        'sheets': sheets
    }
    ss = sheet_service.spreadsheets().create(body=spreadsheet,
                                            fields='spreadsheetUrl').execute()
    return ss.get('spreadsheetUrl')


def flatten_data(dict: Dict[str, Any]) -> List[List[Any]]:
    row_len = len(_HEADER)
    metadata_row = ['' for i in range(row_len)]
    metadata_row[0] = _RUN_METADATA
    keyowrds_recs_values = [metadata_row, _HEADER]

    for v in dict.values():
        for kw, data in v.items():
            for stats in data.values():
                row = [kw, stats['account'], stats['account_id'], stats['campaign'], stats['campaign_id'], stats['ad_group'], stats['ad_group_id'],
                       stats['clicks'], stats['impressions'], stats['conversions'], stats['cost'], stats['ctr']]
                keyowrds_recs_values.append(row)

    return keyowrds_recs_values


def flatten_exclusion_recommendation(ex_recs: Dict[str, Any]) -> List[List[Any]]:
    pass
