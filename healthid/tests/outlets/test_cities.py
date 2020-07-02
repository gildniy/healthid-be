from healthid.apps.outlets.models import Country
from healthid.tests.outlets.test_countries import CountryTestCase
from healthid.tests.test_fixtures.outlets import (
    create_city_string,
    query_cities_string,
    edit_city_string,
    query_city_string_by_name,
    query_city_string_by_id,
)
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class CityTestCase(CountryTestCase):

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

    def test_create_city(self):
        response = self.create_city(city_name='kampala')
        self.assertEqual('Kampala', response['name'])

    def test_create_city_empty_city_name(self):
        country = self.create_country()
        country_id = country['country']['id']
        query_string = create_city_string.format(
            country_id=country_id,
            city_name=''
        )
        response = self.query_with_token(
            self.access_token_master, query_string
        )
        self.assertEqual(
            OUTLET_ERROR_RESPONSES[
                "invalid_city_or_country_name"].format("city"),
            response['errors'][0]['message'])

    def test_create_city_country_does_not_exist(self):
        country_id = 300
        query_string = create_city_string.format(
            country_id=country_id,
            city_name='kampala'
        )
        response = self.query_with_token(
            self.access_token_master, query_string
        )
        self.assertEqual(
            OUTLET_ERROR_RESPONSES["invalid_country_id"].format(country_id),
            response['errors'][0]['message'])

    def test_create_city_already_exists(self):
        self.create_city()
        country_id = Country.objects.get(name='Uganda').id
        query_string = create_city_string.format(
            country_id=country_id,
            city_name='kampala'
        )
        response = self.query_with_token(
            self.access_token_master, query_string
        )
        self.assertEqual(OUTLET_ERROR_RESPONSES[
                         "city_double_creation_error"].format("City Kampala"),
                         response['errors'][0]['message'])

    def test_edit_city(self):
        city = self.create_city(city_name='kampala')
        city_id = city['id']
        query_string = edit_city_string.format(
            id=city_id,
            name='Nairobi'
        )
        response = self.query_with_token(
            self.access_token_master, query_string
        )
        self.assertEqual(
            'Nairobi', response['data']['editCity']['city']['name'])

    def test_edit_city_doesnot_exist(self):
        faked_id = 2
        query_string = edit_city_string.format(
            id=faked_id,
            name='Nairobi'
        )
        response = self.query_with_token(
            self.access_token_master, query_string
        )
        self.assertEqual(
            OUTLET_ERROR_RESPONSES["invalid_city_id"].format(faked_id),
            response['errors'][0]['message'])

    def test_fetch_all_cities(self):
        self.create_city(country_name='Uganda', city_name='kampala')
        self.create_city(country_name='Kenya', city_name='nairobi')
        self.create_city(country_name='Rwanda', city_name='Kigali')
        response = self.query_with_token(
            self.access_token_master, query_cities_string)
        # there are cities created in base setup class i.e (3+1)
        self.assertEqual(4, len(response['data']['cities']))

    def test_fetch_single_city_with_name(self):
        self.create_city(city_name='kampala')
        response = self.query_with_token(
            self.access_token_master,
            query_city_string_by_name.format(name='kampala')
        )
        self.assertEqual('Kampala', response['data']['city']['name'])

    def test_fetch_single_city_with_name_doesnot_exist(self):
        response = self.query_with_token(
            self.access_token_master,
            query_city_string_by_name.format(name='kampala')
        )
        self.assertEqual(OUTLET_ERROR_RESPONSES["inexistent_city_error"],
                         response['errors'][0]['message'])

    def test_fetch_single_city_with_id(self):
        response = self.create_city(city_name='kampala')
        city_id = response['id']
        response = self.query_with_token(
            self.access_token_master,
            query_city_string_by_id.format(id=city_id)
        )
        self.assertEqual('Kampala', response['data']['city']['name'])
        self.assertEqual(str(city_id), response['data']['city']['id'])
