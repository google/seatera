
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

    def build(self, thresholds, start_date, end_date):
        query = f"""
            SELECT 
                search_term_view.search_term,
                customer.descriptive_name,
                customer.id,
                customer.currency_code,
                campaign.name,
                campaign.id,
                ad_group.name,
                ad_group.id,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.cost_micros,
                metrics.conversions
            FROM 
                search_term_view 
            WHERE 
                campaign.advertising_channel_type = 'SEARCH'
                AND search_term_view.status = 'NONE'
                AND metrics.clicks >= {thresholds['clicks']} 
                AND metrics.impressions >= {thresholds['impressions']} 
                AND metrics.ctr > {thresholds['ctr']} 
                AND metrics.cost_micros > {thresholds['cost']} 
                AND metrics.conversions > {thresholds['conversions']}
                AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        """

        rows = self._get_rows(query)
        search_terms = {}
        for batch in rows:
            for row in batch.results:
                row = row._pb
                try:
                    search_terms[row.search_term_view.search_term][row.ad_group.id] = {
                        'account_id': row.customer.id,
                        'account': row.customer.descriptive_name,
                        'campaign': row.campaign.name,
                        'campaign_id': row.campaign.id,
                        'ad_group': row.ad_group.name,
                        'ad_group_id': row.ad_group.id,
                        'clicks': row.metrics.clicks,
                        'impressions': row.metrics.impressions,
                        'conversions': row.metrics.conversions,
                        'ctr': row.metrics.ctr * 100,
                        'cost': row.metrics.cost_micros / 1000000
                    }

                except KeyError:
                    search_terms[row.search_term_view.search_term] = {
                        row.ad_group.id: {
                            'account_id': row.customer.id,
                            'account': row.customer.descriptive_name,
                            'campaign': row.campaign.name,
                            'campaign_id': row.campaign.id,
                            'ad_group': row.ad_group.name,
                            'ad_group_id': row.ad_group.id,
                            'clicks': row.metrics.clicks,
                            'impressions': row.metrics.impressions,
                            'conversions': row.metrics.conversions,
                            'ctr': row.metrics.ctr * 100,
                            'cost': row.metrics.cost_micros / 1000000
                        }
                    }

        return search_terms


class KeywordDedupingBuilder(Builder):
    """Gets Keywords from a single account, removes if from search term dict if
    KW exist in the same ad group. If exist in a different ad group, adds to exclusion list with
    to be add as negative kw in the st's original ad group."""

    def build(self, search_terms):
        rows = self._get_rows('''
        SELECT
            ad_group_criterion.keyword.text,
            ad_group.id,
            ad_group_criterion.negative 
        FROM 
            ad_group_criterion
        WHERE 
            ad_group_criterion.type = KEYWORD
        AND
            ad_group_criterion.status IN ('ENABLED', 'PAUSED')
        AND
            campaign.advertising_channel_type = 'SEARCH'
        ''')

        # Create a dict of keywords that appear in the search term list
        # and all the ad groups they exist in
        keywords = {}
        for batch in rows:
            for row in batch.results:
                row = row._pb
                # if keyword is not in search term dict, move on to the next one
                if not search_terms.get(row.ad_group_criterion.keyword.text):
                    continue
                try:
                    keywords[row.ad_group_criterion.keyword.text].append(
                        row.ad_group.id)
                except KeyError:
                    keywords[row.ad_group_criterion.keyword.text] = [
                        row.ad_group.id]

        # Create exclusion dict of negative keywords. Will have search terms
        # that appear in other ad groups as keywords.
        exclusion_list = {}
        for kw, kw_ags in keywords.items():
            st_stats = search_terms[kw]
            for ag in kw_ags:
                if st_stats.get(ag):
                    st_stats.pop(ag)
            # If st ad groups remain, add their stats and kw to exclusion list.
            if st_stats:
                exclusion_list[kw] = st_stats

            search_terms.pop(kw)

        return exclusion_list


class AccountsBuilder(Builder):
    """Gets all client accounts' IDs under the MCC."""

    def __init__(self, client):
        super().__init__(client, client.login_customer_id)
        self._client = client

    def get_accounts(self, with_names=False):
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
        AND customer_client.status = 'ENABLED'
    	'''

        rows = self._get_rows(query)
        for batch in rows:
            for row in batch.results:
                row = row._pb
                account = str(row.customer_client.id)
                if with_names:
                    account += ' - ' + str(row.customer_client.descriptive_name)
                accounts.append(account)

        return accounts
