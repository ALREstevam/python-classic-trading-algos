import json
from pathlib import Path


class ReadSecrets:

    def __init__(self, json_secrets_file_path=None):
        self.secrets = None
        self.accessors = {}
        self.secrets_path = json_secrets_file_path

    def read(self, json_secrets_file_path=None):
        if not self.secrets_path and json_secrets_file_path:
            self.secrets_path = json_secrets_file_path

        path = Path(self.secrets_path)

        if path.is_file():
            with open(path) as f:
                self.secrets = json.load(f)
            return self
        else:
            raise FileNotFoundError
        
    def read_if_necessary(self, json_secrets_file_path=None):
        if not self.secrets_path and json_secrets_file_path:
            self.secrets_path = json_secrets_file_path

        if not self.secrets:
            self.read(self.secrets_path)

        return self

    def set_secrets_path(self, json_secrets_file_path):
        self.secrets_path = json_secrets_file_path
        return self

    def add_accessor(self, name, accessor):
        self.accessors[name] = lambda secret: accessor(secret)
        return self

    def access(self, name):
        self.read_if_necessary()

        if name in self.accessors:
            return self.accessors[name](self.secrets)
        else:
            raise Exception(f'invalid accessor {name}')

    def set_default_accessors(self):
        def plotly_accessor(secrets):
            from random import choice

            accounts = secrets['plotlyAccounts'] if 'plotlyAccounts' in secrets else [secrets['plotly']]

            return {
                'accounts': accounts,
                'get_random_account': lambda: choice(accounts),
                'main_account': secrets['plotly']
            }

        self.add_accessor('plotly', plotly_accessor)

        return self


def exercite():
    s = ReadSecrets()\
        .set_secrets_path('../secrets.json')\
        .set_default_accessors()

    print(s.access('plotly')['get_random_account']())

