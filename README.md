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

1. A new GCP project with billing attached

1. Create [OAuth Credentials](https://console.cloud.google.com/apis/credentials/oauthclient) of type **Web**

1. [Enable Google ads API](https://developers.google.com/google-ads/api/docs/first-call/oauth-cloud-project#enable_the_in_your_project)
1. Enable Sheets API


## Installation

1. Click the big blue button to deploy:
   
   [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)


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
