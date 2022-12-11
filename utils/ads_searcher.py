from dateutil.parser import parse
from google.ads.googleads.client import GoogleAdsClient


class Builder(object):
    def __init__(self, client, customer_id):
        self._service = client.get_service('GoogleAdsService')
        self._client = client
        self._customer_id = customer_id
        self._enums = {
            'match_type': client.get_type('KeywordMatchTypeEnum').KeywordMatchType
        }

    def _get_rows(self, query):
        search_request = self._client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = self._customer_id
        search_request.query = query
        response = self._service.search_stream(request=search_request)
        return response



class SearchTermBuilder(Builder):
    """Gets Keywords recommednations from a single account."""

    def build(self, params):
        query = f"""
            SELECT 
                search_term_view.search_term,
                customer.descriptive_name,
                customer.currency_code,
                campaign.name,
                ad_group.name,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.cost_micros,
                metrics.conversions
            FROM 
                search_term_view 
            WHERE 
                campaign.advertising_channel_type = 'SHOPPING' 
                AND metrics.clicks >= {params['clicks']} 
                AND metrics.impressions >= {params['impressions']} 
                AND metrics.ctr > {params['ctr']} 
                AND metrics.average_cpc > {params['average_cpc']}
                AND metrics.cost_micros > {params['cost_micros']} 
                AND metrics.conversions > {params['conversions']}
        """

        if params.get('start_date') and params.get('end_date'):
            if parse(params['start_date']) <= parse(params['end_date']):
                query += f" AND segments.date BETWEEN '{params['start_date']}' AND '{params['end_date']}'" 
            else:
                logging.info('Given end date is sooner than start date. Running for default dates.')
        else: 
            logging.info('Did not get date range. Running for default dates.')

        rows = self._get_rows(query)   
        search_terms = {}
        for batch in rows:
            for row in batch.results:
                print(row)
                search_terms[row.search_term_view.search_term] = {
                    'account' : row.customer.descriptive_name,
                    'campaign' : row.campaign.name,
                    'ad group': row.ad_group.name,
                    'clicks': row.metrics.clicks,
                    'impressions': row.metrics.impressions,
                    'conversions': row.metrics.conversions,
                    'ctr': row.metrics.ctr * 100,
                    'currency' : row.customer.currency_code,
                    'cost': row.metrics.cost_micros / 1000000,
                    'average_cpc': row.metrics.average_cpc
                }
                
        return search_terms


class KeywordRemoverBuilder(Builder):
    """Gets Keywords from a single account."""

    def build(self, search_terms):
        rows = self._get_rows('''
        SELECT
            ad_group_criterion.keyword.text
        FROM 
            ad_group_criterion
        WHERE 
            ad_group_criterion.type = KEYWORD
        ''')

        for batch in rows:
            for row in batch.results:
                try:
                    search_terms.pop(row.ad_group_criterion.keyword.text)
                except:
                    pass


class AccountsBuilder(Builder):
    """Gets all client accounts' IDs under the MCC."""

    def __init__(self, client):
        super().__init__(client, client.login_customer_id)
        self._client = client

    def get_accounts(self):
        """Used to get all client accounts using API"""
        accounts = []
        query = '''
        SELECT
          customer_client.descriptive_name,
          customer_client.id
        FROM
          customer_client
        WHERE
          customer_client.manager = False
    	'''

        rows = self._get_rows(query)
        for batch in rows:
            for row in batch.results:
                accounts.append(str(row.customer_client.id))

        return accounts