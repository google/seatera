import sys
import logging
import utils.auth as auth
from pathlib import Path
from pprint import pprint
from utils.auth import CONFIG_FILE, SCOPES
from utils.sheets import SheetsInteractor, get_sheets_service
from utils.ads_searcher import AccountsBuilder
from utils.entities import RunSettings
from typing import Dict, Any, Optional, Union
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException



_THRESHOLDS_RANGE = 'Thresholds!A2:B12'
_LOGS_PATH = Path('./script.log')

logging.basicConfig(filename=_LOGS_PATH,
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')



def main(client: GoogleAdsClient, mcc_id: str, config: Dict[str, Any]):
    sheets_service = get_sheets_service(config)
    sheet_handler = SheetsInteractor(sheets_service, config['spreadsheet_url'])
    run_settings = RunSettings.from_sheet_read(sheet_handler.read_from_spreadsheet(_THRESHOLDS_RANGE))
    pprint(run_settings.thresholds)
    if not run_settings.accounts:
        run_settings.accounts = AccountsBuilder(client).get_accounts()


if __name__ == "__main__":
    config = auth.get_config(CONFIG_FILE) 
    # Check if client needs to set refresh_token in YAML.
    # If so, run auth_utils.py.
    if config['refresh_token'] == None:
        auth.main()
    
    try:
        google_ads_client = GoogleAdsClient.load_from_storage(CONFIG_FILE)
    except:
        print('Refer to README.md and fill out values in google-ads.yaml')
        sys.exit(1)

    mcc_id = str(config['login_customer_id'])
    
    main(google_ads_client, mcc_id, config)