
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.outlets import (
    query_countries_string,
    query_country_string_with_id,
    query_country_string_with_name,
    create_country_string,
    delete_country_string,
    update_country_string,
    create_city_string
)
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CountryTestCase(BaseConfiguration):

    def create_country(self, country_name='Uganda'):
        query_string = create_country_string.format(country_name=country_name)
        res = self.query_with_token(
            self.access_token_master, query_string
        )
        response = res['data']['createCountry']
        return response

    def create_city(self, country_name='Uganda', city_name='kampala'):
        country = self.create_country(country_name)
        country_id = country['country']['id']
        query_string = create_city_string.format(
            country_id=country_id,
            city_name=city_name
        )
        res = self.query_with_token(
            self.access_token_master, query_string
        )
        response = res['data']['createCity']['city']
        return response

    def test_create_country(self):
        query_string = create_country_string.format(country_name='Uganda')
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn('Uganda', response['data']
                      ['createCountry']['country']['name'])

    def test_create_country_already_exists(self):
        query_string = create_country_string.format(country_name='Uganda')
        self.create_country()
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(
            OUTLET_ERROR_RESPONSES["country_double_creation"].format("Uganda"),
            response['errors'][0]['message']
        )

    def test_create_country_wrong_name_format(self):
        query_string = create_country_string.format(country_name='%$#^&&**')
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertEqual(
            OUTLET_ERROR_RESPONSES[
                 "invalid_city_or_country_name"].format("Country"),
            response['errors'][0]['message'])

    def test_create_country_empty_country_name(self):
        query_string = create_country_string.format(country_name='')
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertEqual(OUTLET_ERROR_RESPONSES[
                         "invalid_city_or_country_name"].format("Country"),
                         response['errors'][0]['message'])

    def test_update_country_name(self):
        response = self.create_country('uganda')
        country_id = response['country']['id']
        query_string = update_country_string.format(
            id=country_id, name='Uganda2'
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(SUCCESS_RESPONSES["update_success"].format("Country"),
                      response['data']['editCountry']['success'])

    def test_update_country_name_that_exists(self):
        response = self.create_country('Kenya')
        response = self.create_country('uganda')
        country_id = response['country']['id']
        query_string = update_country_string.format(
            id=country_id, name='Kenya'
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(OUTLET_ERROR_RESPONSES[
                      "country_double_creation"].format("Kenya"),
                      response['errors'][0]['message'])

    def test_update_country_no_country_name(self):
        response = self.create_country('uganda')
        country_id = response['country']['id']
        query_string = update_country_string.format(
            id=country_id, name=''
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(OUTLET_ERROR_RESPONSES[
                      "invalid_city_or_country_name"].format("country"),
                      response['errors'][0]['message'])

    def test_update_country_doesnot_exist(self):
        country_name = 'fake-name'
        country_id = 300
        query_string = update_country_string.format(
            id=country_id, name=country_name
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(OUTLET_ERROR_RESPONSES[
                      "invalid_country_id"].format(country_id),
                      response['errors'][0]['message'])

    def test_delete_country(self):
        response = self.create_country('Uganda')
        country_id = response['country']['id']
        query_string = delete_country_string.format(
            id=country_id
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(SUCCESS_RESPONSES["deletion_success"].format("Country"),
                      response['data']['deleteCountry']['success'])

    def test_delete_country_doesnot_exist(self):
        country_id = 18888
        query_string = delete_country_string.format(
            id=country_id
        )
        response = self.query_with_token(
            self.access_token_master, query_string)
        self.assertIn(OUTLET_ERROR_RESPONSES[
                      "invalid_country_id"].format(country_id),
                      response['errors'][0]['message'])

    def test_fetch_all_countries(self):
        self.create_country(country_name='uganda')
        self.create_country(country_name='rwanda')
        self.create_country(country_name='kenya')
        self.create_country(country_name='Nigria')

        response = self.query_with_token(
            self.access_token_master, query_countries_string)
        # there are countries created in base setup class i.e (4+1)
        self.assertEqual(5, len(response['data']['countries']))

    def test_fetch_single_country_with_name(self):
        response = self.create_country(country_name='uganda')
        response = self.query_with_token(
            self.access_token_master,
            query_country_string_with_name.format(name='uganda')
        )
        self.assertEqual('Uganda', response['data']['country']['name'])

    def test_fetch_single_country_with_name_doesnot_exist(self):
        response = self.query_with_token(
            self.access_token_master,
            query_country_string_with_name.format(name='uganda')
        )
        self.assertEqual(OUTLET_ERROR_RESPONSES["inexistent_country_error"],
                         response['errors'][0]['message'])

    def test_fetch_single_country_id(self):
        response = self.create_country(country_name='uganda')
        country_id = response['country']['id']
        response = self.query_with_token(
            self.access_token_master,
            query_country_string_with_id.format(id=country_id)
        )
        self.assertEqual('Uganda', response['data']['country']['name'])
        self.assertEqual(str(country_id), response['data']['country']['id'])
