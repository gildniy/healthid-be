import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role
from healthid.apps.outlets.models import \
    City, Country, Outlet, OutletUser
from healthid.apps.outlets.schema.outlet_schema import (CityType, CountryType,
                                                        OutletType,
                                                        OutletMetaType,
                                                        OutletContactsType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.outlet_utils.validators import validate_fields
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES, OUTLET_SUCCESS_RESPONSES
from healthid.apps.authentication.schema.queries.auth_queries import UserType
from healthid.utils.app_utils.check_user_in_outlet import \
    get_user_active_outlet
from healthid.utils.outlet_utils.metadata_handler import \
    add_outlet_metadata, update_outlet_metadata
from healthid.utils.app_utils.get_city import get_city
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.business.models import Business
from healthid.apps.orders.schema.mutations.suppliers.add_supplier_contacts \
    import AddSupplierContacts
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.orders.models.suppliers import SupplierOutletContacts
from healthid.utils.app_utils.get_city import get_city


class CreateOutlet(graphene.Mutation):
    """
    Creates an outlet
    """
    outlet = graphene.Field(OutletType)
    outlet_meta = graphene.Field(OutletMetaType)
    outlet_contacts = graphene.Field(OutletContactsType)
    success = graphene.String()

    class Arguments:
        name = graphene.String()
        kind_id = graphene.Int()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        lga = graphene.String()
        phone_number = graphene.String()
        date_launched = graphene.types.datetime.Date()
        prefix_id = graphene.String()
        business_id = graphene.String()
        country = graphene.String()
        city_name = graphene.String()
        tax_number = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        country_name = kwargs.get('country')
        city_name = kwargs.get('city_name')
        outlet_name = kwargs.get('name')
        business_id = kwargs.get('business_id')
        tax_number = kwargs.get('tax_number')
        find_outlets = \
            Outlet.objects.filter(name=outlet_name)

        if outlet_name and outlet_name.strip() != "":
            for outlet in find_outlets:
                if business_id == outlet.business_id:
                    raise GraphQLError(OUTLET_ERROR_RESPONSES['outlet_exists'])

            if tax_number:
                outlets_with_same_tax_number = Outlet.objects.filter(
                    tax_number=tax_number
                )
                if outlets_with_same_tax_number.count() > 0:
                    raise GraphQLError(
                        OUTLET_ERROR_RESPONSES['tax_number_exists']
                    )

            outlet = Outlet()
            for(key, value) in kwargs.items():
                setattr(outlet, key, value)
            role_instance = get_model_object(Role, 'id', user.role_id)
            if country_name and city_name:
                outlet.city = get_city(country_name, city_name)
            with SaveContextManager(outlet, model=Outlet) as outlet:
                add_outlet_metadata(outlet, kwargs.items())
                OutletUser.objects.create(
                    user=user, outlet=outlet, is_active_outlet=True,
                    role=role_instance)
                business = get_model_object(Business, 'id', outlet.business_id)

                master_admin = business.user
                city = get_city(business.country, business.city)
                contacts = {
                    "mobile_number": master_admin.mobile_number,
                    "email": master_admin.email,
                    "address_line_1": "N/A",
                    "address_line_2": "N/A",
                    "lga": "N/A",
                    "city_id": city.id,
                    "country_id": city.country_id
                }

                suppliers = Suppliers.objects.filter(business=business)
                
                for supplier in suppliers:
                    outlet = get_model_object(Outlet, 'id', outlet.id)
                    supplier = get_model_object(Suppliers, 'id', supplier.id)

                    supplier_outlet_contacts = []
                    for (key, value) in contacts.items():
                        supplier_outlet_contact = SupplierOutletContacts.objects.create(
                            dataKey=key, dataValue=value, outlet=outlet, supplier=supplier
                        )

                receipt_template = ReceiptTemplate(
                    outlet_id=outlet.id,
                    logo=business.logo
                )

                receipt_template.save()
                return CreateOutlet(
                    outlet=outlet,
                    success=SUCCESS_RESPONSES["creation_success"].format(
                        "Outlet")
                )

        raise GraphQLError(OUTLET_ERROR_RESPONSES['invalid_outlet_name'])


class UpdateOutlet(graphene.Mutation):
    """
    Updates an outlet
    """
    outlet = graphene.Field(OutletType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        address_line1 = graphene.String()
        address_line2 = graphene.String()
        phone_number = graphene.String()
        lga = graphene.String()
        date_launched = graphene.types.datetime.Date()
        prefix_id = graphene.String()
        preference_id = graphene.String()
        kind_id = graphene.Int()
        country = graphene.String()
        city_name = graphene.String()
        tax_number = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet_id = kwargs.get('id')
        country_name = kwargs.get('country')
        city_name = kwargs.get('city_name')
        outlet_name = kwargs.get('name')
        tax_number = kwargs.get('tax_number')
        outlet = get_user_active_outlet(user, outlet_id=outlet_id)

        all_outlets = Outlet.objects

        if outlet_name and outlet_name.strip() != "":
            outlets_with_same_name = all_outlets.filter(
                name=outlet_name, business_id=outlet.business_id).exclude(pk=outlet.id)
            if outlets_with_same_name.count() > 0:
                raise GraphQLError(OUTLET_ERROR_RESPONSES['outlet_exists'])

            if tax_number:
                outlets_with_same_tax_number = all_outlets.filter(
                    tax_number=tax_number
                ).exclude(pk=outlet.id)
                if outlets_with_same_tax_number.count() > 0:
                    raise GraphQLError(
                        OUTLET_ERROR_RESPONSES['tax_number_exists'])

            for(key, value) in kwargs.items():
                setattr(outlet, key, value)

            if country_name and city_name:
                outlet.city = get_city(country_name, city_name)

            outlet.save()
            update_outlet_metadata(outlet, kwargs.items())

            success = SUCCESS_RESPONSES["update_success"].format(outlet.name)
            return UpdateOutlet(outlet=outlet, success=success)

        raise GraphQLError(OUTLET_ERROR_RESPONSES['invalid_outlet_name'])


class DeleteOutlet(graphene.Mutation):
    """
    Deletes an outlet
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        outlet = get_model_object(Outlet, 'id', id)
        outlet.delete(user)
        return DeleteOutlet(
            success=SUCCESS_RESPONSES["deletion_success"].format("Outlet"))


class CreateCountry(graphene.Mutation):
    """
    Creates country
    """
    country = graphene.Field(CountryType)

    class Arguments:
        name = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        name = kwargs.get('name').strip().title()
        name = validate_fields.validate_name(name, 'Country')
        country = Country(name=name)
        with SaveContextManager(country, model=Country) as country:
            return CreateCountry(country=country)


class CreateCity(graphene.Mutation):

    """
    Creates a city
    """
    city = graphene.Field(CityType)

    class Arguments:
        city_name = graphene.String()
        country_id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        country_id = kwargs.get('country_id', '')
        city_name = kwargs.get('city_name', '')
        city_name = validate_fields.validate_name(city_name, 'city')
        city_name = city_name.title()
        country = get_model_object(Country, 'id', country_id)
        cities = [city['name'] for city in list(country.city_set.values())]
        if city_name in cities:
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES[
                    "city_double_creation_error"].format(
                    "City " + city_name))
        city = City(name=city_name, country=country)
        with SaveContextManager(city, model=City):
            return CreateCity(city=city)


class EditCountry(graphene.Mutation):
    """Edit a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()
        name = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'country')
        country = get_model_object(Country, 'id', id)
        country.name = name
        with SaveContextManager(country, model=Country):
            success = SUCCESS_RESPONSES["update_success"].format("Country")
            return EditCountry(country=country, success=success)


class EditCity(graphene.Mutation):
    """Edit country
    """
    city = graphene.Field(CityType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name', '').strip().title()
        name = validate_fields.validate_name(name, 'city')
        city = get_model_object(City, 'id', id)
        country_cities = City.objects.filter(country=city.country).all()
        if name in [str(city) in country_cities]:
            raise GraphQLError(OUTLET_ERROR_RESPONSES[
                "city_double_creation_error"].format(
                "The city " + name))
        city.name = name
        city.save()
        return EditCity(city=city,
                        success=SUCCESS_RESPONSES[
                            "update_success"].format("City"))


class DeleteCountry(graphene.Mutation):
    """Delete a country
    """
    country = graphene.Field(CountryType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        country = get_model_object(Country, 'id', id)
        country.delete(user)
        return DeleteCountry(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Country"))


class ActivateDeactivateOutletUser(graphene.Mutation):
    """
    Mutataion to activate or deactivate user from an outlet

    Attributes:
        outlet_id(int): id for outlet whose user you want to activate or
                        deactivate
        user_id(string): id for user  to activate or deactivate in
                         outlet
        is_active(boolean): True if you want to activate a user
                            otherwise False to deactivate

    Returns:
        message(string): indicating user has been activated or
                         deactivated
        user(obj): user who has been activated or deactivated
    """
    user = graphene.Field(UserType)
    message = graphene.String()

    class Arguments:
        outlet_id = graphene.Int(required=True)
        user_id = graphene.String(required=True)
        is_active = graphene.Boolean(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        outlet_user, message = outlet.activate_deactivate_user(
            info.context.user, **kwargs)
        return ActivateDeactivateOutletUser(message=message, user=outlet_user)


class ChangeUserDefaultOutlet(graphene.Mutation):
    """
    Mutation to change current user outlet

    Attributes:
        outlet_id(int): id for outlet whose user you want to change to

    Returns:
        message(string): indicating user has successfully changed to that outlet
        default_outlet(obj): the new current user default outlet
    """
    default_outlet = graphene.Field(OutletType)
    message = graphene.String()

    class Arguments:
        outlet_id = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        user_outlets = user.outletuser_set.filter(is_active_outlet=True)
        if not user_outlets:
            raise GraphQLError(OUTLET_ERROR_RESPONSES["no_active_outlets"])
        eligible_outlets = []
        for user_outlet in user_outlets:
            eligible_outlets.append(user_outlet.outlet_id)
        default_outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))
        if not default_outlet:
            raise GraphQLError(OUTLET_ERROR_RESPONSES["inexistent_outlet"].format(id=kwargs.get('outlet_id')))  #
        if default_outlet.id not in eligible_outlets:
            raise GraphQLError(OUTLET_ERROR_RESPONSES["user_not_in_outlet"])
        for user_outlet in user_outlets:
            setattr(user_outlet, 'is_default_outlet', default_outlet.id == user_outlet.outlet_id)
            user_outlet.save()
        return ChangeUserDefaultOutlet(message=OUTLET_SUCCESS_RESPONSES["outlet_now_default"],
                                       default_outlet=default_outlet)


class Mutation(graphene.ObjectType):
    create_outlet = CreateOutlet.Field()
    delete_outlet = DeleteOutlet.Field()
    update_outlet = UpdateOutlet.Field()
    create_city = CreateCity.Field()
    create_country = CreateCountry.Field()
    edit_country = EditCountry.Field()
    delete_country = DeleteCountry.Field()
    edit_city = EditCity.Field()
    activate_deactivate_outlet_user = ActivateDeactivateOutletUser.Field()
    change_user_default_outlet = ChangeUserDefaultOutlet.Field()
