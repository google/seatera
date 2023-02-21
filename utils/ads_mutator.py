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

import logging

class Mutator(object):
    def __init__(self, client, customer_id):
        self._client = client
        self._customer_id = customer_id


class NegativeKeywordsUploader(Mutator):
    def __init__(self, client, customer_id):
        super().__init__(client, customer_id)
        self._ad_group_service = client.get_service("AdGroupService")
        self._ad_group_criterion_service = client.get_service(
            "AdGroupCriterionService")

    def upload_from_script(self, keywords):
        operations = []
        for kw, adgroups in keywords.items():
            for ag_id in adgroups:
                # Create keyword.
                ad_group_criterion_operation = self._client.get_type(
                    "AdGroupCriterionOperation")
                ad_group_criterion = ad_group_criterion_operation.create
                ad_group_criterion.ad_group = self._ad_group_service.ad_group_path(
                    self._customer_id, ag_id
                )
                ad_group_criterion.status = self._client.enums.AdGroupCriterionStatusEnum.ENABLED
                ad_group_criterion.keyword.text = kw
                ad_group_criterion.keyword.match_type = (
                    self._client.enums.KeywordMatchTypeEnum.EXACT
                )
                ad_group_criterion.negative = True
                operations.append(ad_group_criterion_operation)

        ad_group_criterion_response = (
            self._ad_group_criterion_service.mutate_ad_group_criteria(
                request={'response_content_type': 'MUTABLE_RESOURCE',
                         'customer_id': self._customer_id, 'operations': operations}
            )
        )
        for result in ad_group_criterion_response.results:
            logging.info(
                f"Added negative keyword {result.ad_group_criterion.keyword.text} in ad group {result.ad_group_criterion.ad_group} ."
            )
