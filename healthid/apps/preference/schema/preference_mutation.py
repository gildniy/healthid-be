import graphene
from graphene_django import DjangoObjectType
from healthid.apps.preference.models import OutletPreference
from graphql_jwt.decorators import login_required
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class OutletTypePreference(DjangoObjectType):
    class Meta:
        model = OutletPreference


class UpdateOutletPreference(graphene.Mutation):
    """
    Updates an outlet preference
    """
    preference = graphene.Field(OutletTypePreference)
    success = graphene.String()

    class Arguments:
        outlet_timezone = graphene.String()
        preference_id = graphene.String(required=True)
        outlet_currency = graphene.String()
        outlet_vat = graphene.Float()
        barcode_preference = graphene.Boolean()
        email_preference = graphene.Boolean()
        reorder_point = graphene.Int()
        reorder_max = graphene.Int()
        retain_user = graphene.Boolean()
        sales_hold = graphene.Int()
        alert_low_inventory = graphene.Boolean()
        alert_near_expiry = graphene.Boolean()
        weeks_to_start_supply_alert = graphene.Int()
        payment_method = graphene.String()
        minimum_weeks_for_sales_velocity = graphene.Int()
        sales_velocity = graphene.Int()

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        info = info
        preference = OutletPreference().update_preference(info,
                                                          OutletPreference,
                                                          **kwargs)
        return cls(
            preference=preference,
            success=SUCCESS_RESPONSES[
                "update_success"].format("Preference"))


class Mutation(graphene.ObjectType):
    update_preference = UpdateOutletPreference.Field()
