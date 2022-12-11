import re
from typing import List, Any, Dict
from pprint import pprint
from google.oauth2.credentials import Credentials
from utils.auth import CONFIG_FILE, SCOPES
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

_SHEETS_SERVICE_VERSION = 'v4'
_SHEETS_SERVICE_NAME = 'sheets'

class SheetsInteractor:
    def __init__(self, service, spreadsheet_url):
        self.service = service.spreadsheets()
        self.spreadsheet_url = spreadsheet_url
        self.spreadsheet_id = self._get_spreadsheet_id()

    
    def _get_spreadsheet_id(self) -> str:
        # Returns spreadsheet ID from spreadsheet URL
        if not self.spreadsheet_url:
            raise Exception("No spreadsheet URL found. Follow instructions in README and add spreadsheet URL in config.yaml")

        spreadsheet_regex = '/d/(.*?)/edit'
        spreadsheet_match = re.search(spreadsheet_regex, self.spreadsheet_url)

        if spreadsheet_match == None:
            raise Exception("Couldn't extract spreadsheet ID from URL.")

        spreadsheet_id = spreadsheet_match.group(1)
        return spreadsheet_id
    
    def write_to_spreadsheet(self, range, values):
        pass

    def read_from_spreadsheet(self, range) -> List[List[Any]]:
        results = self.service.values().get(
            spreadsheetId=self.spreadsheet_id, range=range).execute()
        values = results.get('values', [])
        return  values


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

    service = build(_SHEETS_SERVICE_NAME, _SHEETS_SERVICE_VERSION, credentials=creds)
    return service