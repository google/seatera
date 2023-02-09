import yaml
from yaml.loader import SafeLoader
from copy import deepcopy

CONFIG_FILE = './config.yaml'


class Config:
    def __init__(self) -> None:
        self.file_path = CONFIG_FILE
        config = self.load_config_from_file()
        if config is None:
            config = {}

        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret')
        self.refresh_token = config.get('refresh_token', '')
        self.developer_token = config.get('developer_token', '')
        self.login_customer_id = config.get('login_customer_id', '')
        self.spreadsheet_url = config.get('spreadsheet_url', '')
        self.use_proto_plus = True
        self.check_valid_config()

    def check_valid_config(self):
        if self.client_id and self.client_secret and self.refresh_token and self.developer_token and self.login_customer_id:
            self.valid_config = True
        else:
            self.valid_config = False

    def load_config_from_file(self):
        with open(self.file_path, 'r') as f:
            config = yaml.load(f, Loader=SafeLoader)
        return config

    def save_to_file(self):
        try:
            config = deepcopy(self.__dict__)
            del config['file_path']
            with open(self.file_path, 'w') as f:
                yaml.dump(config, f)
            print(f"Configurations updated in {self.file_path}")
        except Exception as e:
            print(f"Could not write configurations to {self.file_path} file")
            print(e)
