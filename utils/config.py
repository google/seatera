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

from yaml.loader import SafeLoader
from copy import deepcopy
from google.cloud import storage
from google.ads.googleads.client import GoogleAdsClient
import os
import yaml


BUCKET_NAME = os.getenv('bucket_name')
CONFIG_FILE_NAME = 'config.yaml'
CONFIG_FILE_PATH = BUCKET_NAME +  '/' + CONFIG_FILE_NAME
_ADS_API_VERSION = 'v11'

class Config:
    def __init__(self) -> None:
        self.file_path = CONFIG_FILE_PATH
        config = self.load_config_from_file()
        if config is None:
            config = {}

        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret')
        self.refresh_token = config.get('refresh_token', '')
        self.developer_token = config.get('developer_token', '')
        self.login_customer_id = config.get('login_customer_id', '')
        self.spreadsheet_url = config.get('spreadsheet_url', '')
        self.check_valid_config()

    def check_valid_config(self):
        if self.client_id and self.client_secret and self.refresh_token and self.developer_token and self.login_customer_id:
            self.valid_config = True
        else:
            self.valid_config = False

    def load_config_from_file(self):
        storage_clien = storage.Client()
        bucket = storage_clien.bucket(BUCKET_NAME)
        blob = bucket.blob(CONFIG_FILE_NAME)

        with blob.open() as f:
            config = yaml.load(f, Loader=SafeLoader)
        return config

    def save_to_file(self):
        try:
            config = deepcopy(self.__dict__)
            del config['file_path']
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(CONFIG_FILE_NAME)
            with blob.open('w') as f:
                yaml.dump(config, f)
            print(f"Configurations updated in {self.file_path}")
        except Exception as e:
            print(f"Could not write configurations to {self.file_path} file")
            print(e)

    def get_ads_client(self):
        return GoogleAdsClient.load_from_dict({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'login_customer_id': self.login_customer_id,
            'developer_token': self.developer_token,
            'refresh_token': self.refresh_token,
            'use_proto_plus': True,
        }, version=_ADS_API_VERSION)