from typing import List, Dict

class RunSettings:
    def __init__(self, thresholds: Dict[str, str], start_date: str, end_date: str, accounts: List[str] = []):
        self.thresholds = thresholds
        self.start_date = start_date
        self.end_date = end_date
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

