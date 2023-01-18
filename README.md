# SeaTerA
***
##### Get exclusion and keyword recommendations by analyzing your search terms

SeaTera helps advertisers manage keywords and exclusions across their accounts by analyzing their search terms.
SeaTera collects all search terms above configurable thresholds and checks if these search terms exist as keywords in other ad groups or if they do not exist as keywords at all. 
Advertisers can use this data in two ways:
1. Exclude keywords that drive traffic to the wrong ad group (Exist as keyword in a different ad group than the one that triggered the search term)
2. Add new keywords (Search terms that drive traffic but don't exist as keywords in any ad group)

This version is an MVP, that uses a python script running locally and a Google Spreadsheet to output the results.

The script will populate two seperate sheets:
1. Keywords - a list of search terms that drove traffic but do not currently exist as a keyword in any other ad group
2. Exclusions - a list of search terms that appear in an ad group even though they exist as keywords in different ad groups (one line per ad group)



## Prerequisites

1. [A Google Ads Developer token](https://developers.google.com/google-ads/api/docs/first-call/dev-token#:~:text=A%20developer%20token%20from%20Google,SETTINGS%20%3E%20SETUP%20%3E%20API%20Center.)

1. A GCP project 

1. Create [OAuth Credentials](https://console.cloud.google.com/apis/credentials/oauthclient) of type **Desktop**

1. [Enable Google ads API](https://developers.google.com/google-ads/api/docs/first-call/oauth-cloud-project#enable_the_in_your_project)
1. Enable Sheets API

1. Ask to join [this Google Group](https://groups.google.com/a/google.com/g/seatera-external/about)

1. Make a copy of [this spraedsheet](https://docs.google.com/spreadsheets/d/1d6nSLFPgv28D-Ry18r-YSH1Zv9iBTz1ZbViJT2D0WEM/edit?resourcekey=0-hdKLYkBP7YLXEaiP-K6UqQ#gid=0)

## Installation

0. Optional - Create a virtual environment
    ```shell
    python3 -m venv .venv
    . .venv/bin/activate
    ```

1. git clone the repository
    ```shell
    git clone https://professional-services.googlesource.com/solutions/seatera
    ```

1. CD into the folder and install dependencies - you might want to use venv 
    ```shell
    pip3 install -r requirements.txt
    ```
1. Fill in config.yaml with the following parameters:
    * client id - your oauth2 client ID
    * client secret - your oauth2 client secret
    * developer token
    * login_customer_id - your MCC account ID
    * refresh_token - **Leave empty!**
    * spreadsheet_url - the URL of your copy of the SeaTera spreadsheet

## Usage

1. In your copy of the spreadsheet, under the "Thresholds" Sheet, set your desired thresholds, date range and the accounts you want to run on.

1. Run the python script locally
    ```shell
    python3 main.py
    ```
1. You can add the -e flag to auto exclude all "Exclusion" results (not recommended for first run)
    ```shell
    python3 main.py -e
    ```
1. You can also upload all exclusion recommendations from spreadsheet without re-running the analysis by using the -u flag
    ```shell
    python3 main.py -u
    ```
