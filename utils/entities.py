from typing import List, Dict
from dateutil.parser import parse

class RunSettings:
    def __init__(self, thresholds: Dict[str, str], start_date: str, end_date: str, accounts: List[str] = []):
        if not start_date or not end_date:
            raise ValueError("Start and end dates must be provided in settings sheet.")
        if parse(start_date) >= parse(end_date):
            raise ValueError("End Date must be later than Start Date") 

        self.thresholds = thresholds
        self.start_date = parse(start_date)
        self.end_date = parse(end_date)
        self.accounts = accounts
    
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
                accounts = value

            else:
                thresholds[key] = int(value)
            
        return RunSettings(thresholds, start_date, end_date, accounts.split(','))

