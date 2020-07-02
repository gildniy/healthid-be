import json
from graphql import GraphQLError
from healthid.apps.outlets.models import \
    City, Country
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


def get_city(country_name, city_name):
    """
    Get city object

    Args:
        country_name: string
        city_name: string

    Returns:
        city(obj): city object
        graphql error: if country or city is not found
    """
    with open("healthid/utils/app_utils/countries.json") as countries:
        data = json.load(countries)
        country_data = [
            country_info for country_info
            in data if country_info['country'].casefold()
            == country_name.casefold()
        ]
        city_data = [
            city_info for city_info
            in data if city_info['name'].casefold() == city_name.casefold()
        ]
        if len(city_data) > 0:
            city = City.objects.filter(name__icontains=city_name).first()
            if city:
                return city
            else:
                if len(country_data) > 0:
                    country = Country.objects.filter(
                        name__icontains=country_data[0]["country"]).first()
                    if country:
                        city = City.objects.create(
                            name=city_data[0]["name"],
                            country=country
                        )
                        return city
                    else:
                        country = Country.objects.create(
                            name=country_data[0]["country"])
                        city = City.objects.create(
                            name=city_data[0]["name"], country=country)
                        return city
                else:
                    raise GraphQLError(
                        OUTLET_ERROR_RESPONSES["country_not_exist"])
        else:
            raise GraphQLError(OUTLET_ERROR_RESPONSES["city_not_exist"])
