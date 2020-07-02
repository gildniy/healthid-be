from healthid.utils.stock_utils.stock_counts import stock_counts
from healthid.utils.messages.stock_responses import STOCK_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.database import (
    SaveContextManager,
)
from healthid.apps.events.models import Event
from healthid.apps.stock.schema.types import (
    StockCountTemplateType
)
from datetime import datetime
from django.db import IntegrityError
import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.stock.models import StockCountTemplate


class CreateStockCountTemplate(graphene.Mutation):
    """
    Create a stock count template.

    args:
        product_ids(list): list of product ids
        event_id(int): id of an event
        assigned_user_ids(list): list of assigned user ids
        designated_user_ids(list): list of designated user ids
        outlet_id(int): id of the outlet whose stock is being counted

    returns:
        success(str): success message confirming template creation
        stock_template(obj): 'StockCountTemplate' object containing the
                             template details
    """

    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()

    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)
        event_type_id = graphene.String(required=True)
        assigned_user_ids = graphene.List(graphene.String, required=True)
        designated_user_ids = graphene.List(graphene.String, required=True)
        batch_ids = graphene.List(graphene.String)
        outlet_id = graphene.Int(required=True)
        end_date = graphene.String(required=True)
        start_date = graphene.String(required=True)
        interval = graphene.Int(required=True)
        end_on = graphene.String()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        template_instance = StockCountTemplate()
        template_fields = stock_counts.get_template_fields(**kwargs)
        with SaveContextManager(template_instance) as stock_tempalate:
            stock_tempalate = stock_counts.add_fields_to_template(
                template_instance,
                **template_fields
            )
            event = Event(
                start_date=template_fields['start_date'],
                end_date=template_fields['end_date'],
                event_title=f'Stock Count Reminder',
                description=f'Stock reminder count on auto scheduling',
                event_type=template_fields['event_type']
            )
            event.save()
            stock_tempalate.schedule_time = event
            stock_tempalate.created_by = info.context.user
            stock_tempalate.unique = True
            try:
                stock_tempalate.save()
            except IntegrityError:
                raise IntegrityError(STOCK_ERROR_RESPONSES[
                    'template_integrity_error'])
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts alert'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, you have been assigned to carry'
                                 ' out stock counts'
        }
        send_mail = SendMail(email_stock_template, context, subject, to_email)
        send_mail.send()
        if stock_tempalate.interval:
            message = SUCCESS_RESPONSES["with_interval"].format(
                "Template with interval {} days".format(
                    stock_tempalate.interval))
        else:
            message = SUCCESS_RESPONSES[
                "creation_success"].format("Stock count template")
        return CreateStockCountTemplate(
            stock_template=stock_tempalate, success=message)
