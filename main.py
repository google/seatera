# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import logging
import utils.auth as auth
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

_LOGS_PATH = Path('./script.log')
_KEYWORDS_SHEET = 'Keywords'
_EXCLUSIONS_SHEET = 'Exclusions'

logging.basicConfig(filename=_LOGS_PATH,
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')



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
    google_ads_client = config.get_ads_client()

    main(google_ads_client, config.login_customer_id,
         sheets_handler, params, auto_upload_negatives=False)


def get_accounts_for_ui(config: Config):
    google_ads_client = config.get_ads_client()
    accounts = AccountsBuilder(google_ads_client).get_accounts(with_names=True)
    return accounts

def main(client: GoogleAdsClient,
         mcc_id: str,
         sheet_handler: SheetsInteractor,
         params: Dict[Any, Any] = None,
         auto_upload_negatives: bool = False):


    run_settings = RunSettings.from_dict(params)

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

    # pprint(keyword_recommendations)
    # pprint(exclusion_recommendations)

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


