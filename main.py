import sys
import logging
import utils.auth as auth
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint
from utils.auth import CONFIG_FILE, SCOPES
from utils.sheets import SheetsInteractor, get_sheets_service, create_new_spreadsheet, flatten_data
from utils.ads_searcher import AccountsBuilder, SearchTermBuilder, KeywordDedupingBuilder
from utils.ads_mutator import NegativeKeywordsUploader
from utils.entities import RunSettings
from utils.config import Config
from typing import Dict, Any, Optional, Union
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from time import time

_THRESHOLDS_RANGE = 'Thresholds!A2:B12'
_LOGS_PATH = Path('./script.log')
_KEYWORDS_SHEET = 'Keywords'
_EXCLUSIONS_SHEET = 'Exclusions'

logging.basicConfig(filename=_LOGS_PATH,
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

parser = ArgumentParser(
    description='Extract keywords and negative keywords from your search terms.')
parser.add_argument('-e', '--upload-negatives', default=False, action='store_true',
                    help='Use this flag if you want to automatically add the negative keywords to the ad groups.')
parser.add_argument('-u', '--upload-negatives-from-sheet', default=False, action='store_true',
                    help='Use this flag to read the "exclusions" sheet and upload them as negative keywords. This will do no other processing.')
arguments = parser.parse_args()


def _get_search_terms(client: GoogleAdsClient, run_settings: RunSettings, account: str) -> Dict[str, Dict[str, Any]]:
    """Uses the SearchTermBuilder class to get all Search Terms from A specific account"""
    builder = SearchTermBuilder(client, account)
    return builder.build(run_settings.thresholds, run_settings.start_date, run_settings.end_date)


def _dedup_and_get_exclusions(client: GoogleAdsClient, run_settings: RunSettings, account: str, search_terms: Dict[str, Any]):
    """Removes existing keywords froms search term dict and return an exclusion list"""
    kw_builder = KeywordDedupingBuilder(client, account)
    return kw_builder.build(search_terms)


def _add_negative_keywords(client, account, neg_kw):
    builder = NegativeKeywordsUploader(client, account)
    builder.upload_from_script(neg_kw)


def upload_from_sheets(client, sheet_handler):
    pass


def run_from_ui(params: Dict[str, str], config: Config):
    # Temp function to trigger the run from UI. For when we want to keep both running options
    sheets_service = get_sheets_service(config.__dict__)
    if not config.spreadsheet_url:
        config.spreadsheet_url = create_new_spreadsheet(sheets_service)
        config.save_to_file()
    sheets_handler = SheetsInteractor(sheets_service, config.spreadsheet_url)
    google_ads_client = GoogleAdsClient.load_from_storage(CONFIG_FILE)

    main(google_ads_client, config.login_customer_id,
         config, sheets_handler, params, False)


def get_accounts_for_ui():
    google_ads_client = GoogleAdsClient.load_from_storage(CONFIG_FILE)
    accounts = AccountsBuilder(google_ads_client).get_accounts(with_names=True)
    return accounts

def main(client: GoogleAdsClient,
         mcc_id: str,
         config: Dict[str, Any],
         sheet_handler: SheetsInteractor,
         params: Dict[Any, Any] = None,
         auto_upload_negatives: bool = False):

    if params:
        run_settings = RunSettings.from_dict(params)
    else:
        run_settings = RunSettings.from_sheet_read(
            sheet_handler.read_from_spreadsheet(_THRESHOLDS_RANGE))

    if not run_settings.accounts:
        run_settings.accounts = AccountsBuilder(client).get_accounts()

    logging.info(run_settings)

    keyword_recommendations = {}
    exclusion_recommendations = {}
    for account in run_settings.accounts:
        search_terms = _get_search_terms(client, run_settings, account)
        exclusions = _dedup_and_get_exclusions(
            client, run_settings, account, search_terms)
        if search_terms:
            keyword_recommendations[account] = search_terms
        if exclusions:
            exclusion_recommendations[account] = exclusions

    pprint(keyword_recommendations)
    pprint(exclusion_recommendations)

    # If auto upload, iterate over exclusion dict and for each account add negative kws
    if auto_upload_negatives:
        for account, neg_kw in exclusion_recommendations.items():
            _add_negative_keywords(client, account, neg_kw)

    flattened_kw_recommendations = flatten_data(keyword_recommendations)
    flattened_exclusion_recommendations = flatten_data(
        exclusion_recommendations)

    sheet_handler.write_to_spreadsheet(
        {_KEYWORDS_SHEET: flattened_kw_recommendations,
         _EXCLUSIONS_SHEET: flattened_exclusion_recommendations})


if __name__ == "__main__":
    start = time()
    try:
        auto_upload_negatives = arguments.upload_negatives
        upload_negatives_from_sheets = arguments.upload_negatives_from_sheet

        config = auth.get_config(CONFIG_FILE)
        # Check if client needs to set refresh_token in YAML.
        # If so, run auth_utils.py.
        if config['refresh_token'] == None:
            config['refresh_token'] = auth.main()

        try:
            google_ads_client = GoogleAdsClient.load_from_storage(CONFIG_FILE)
        except:
            print('Refer to README.md and fill out values in config.yaml')
            sys.exit(1)

        mcc_id = str(config['login_customer_id'])
        sheets_service = get_sheets_service(config)
        sheet_handler = SheetsInteractor(
            sheets_service, config['spreadsheet_url'])

        if upload_negatives_from_sheets:
            upload_from_sheets(google_ads_client, sheet_handler)

        main(google_ads_client, mcc_id, config,
             sheet_handler, auto_upload_negatives)

    except Exception as e:
        logging.exception(e)
        pprint('Run did not complete succesfully. Refer to logs.')
    finally:
        end = time()
        total_time = end - start
        print("\n" + "Total run time: " + str(total_time))
