from typing import List, Dict, Any
from dateutil.parser import parse


class RunSettings:
    def __init__(self, thresholds: Dict[str, str], start_date: str, end_date: str, accounts: List[str] = []):
        if not start_date or not end_date:
            raise ValueError(
                "Start and end dates must be provided in settings sheet.")
        if parse(start_date) >= parse(end_date):
            raise ValueError("End Date must be later than Start Date")

        self.thresholds = thresholds
        self.start_date = parse(start_date).strftime("%Y-%m-%d")
        self.end_date = parse(end_date).strftime("%Y-%m-%d")
        self.accounts = accounts

        # Convert cost to cost micros
        self.thresholds['cost'] = str(int(self.thresholds['cost']) * 1000000)

    @staticmethod
    def from_sheet_read(input: List[List[str]]):
        thresholds = {}
        start_date = ''
        end_date = ''
        accounts = ''

        for list in input:
            key = list[0]
            try:
                value = list[1]
            except IndexError:
                value = 0

            if key == 'start_date':
                start_date = value
            elif key == 'end_date':
                end_date = value
            elif key == 'accounts':
                if not value:
                    accounts = []
                else:
                    accounts = str(value).split(',')

            else:
                thresholds[key] = value

        return RunSettings(thresholds, start_date, end_date, accounts)

    @staticmethod
    def from_dict(input:Dict[Any, Any]):
        thresholds = {
            'clicks': input.get('clicks', 0),
            'conversions': input.get('conversions', 0),
            'impressions': input.get('impressions', 0),
            'cost': input.get('cost', 0),
            'ctr': input.get('ctr', 0)
        }

        return RunSettings(thresholds=thresholds, start_date=input['start_date'], end_date=input['end_date'], accounts=input.get('accounts', []))

    def __repr__(self) -> str:
        return f'RunSettings("{self.thresholds}", "{self.start_date}", "{self.end_date}", "{self.accounts}")'
