from healthid.utils.stock_utils.stock_counts import stock_counts
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.database import (
    SaveContextManager,
    get_model_object
)
from healthid.apps.stock.schema.types import (
    StockCountTemplateType
)
from datetime import datetime
import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.stock.models import StockCountTemplate


class EditStockCountTemplate(graphene.Mutation):
    """
    Edit a stock count template.

    args:
        template_id(int): id of the template to be edited
        product_ids(list): list of product ids
        event_id(int): id of an event
        assigned_user_ids(list): list of assigned user ids
        designated_user_ids(list): list of designated user ids
        outlet_id(int): id of the outlet whose stock is being counted

    returns:
        success(str): success message confirming template edit
        stock_template(obj): 'StockCountTemplate' object containing the
                             template details
    """

    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()

    class Arguments:
        template_id = graphene.Int(required=True)
        product_ids = graphene.List(graphene.Int)
        event_type_id = graphene.String(required=True)
        assigned_user_ids = graphene.List(graphene.String)
        designated_user_ids = graphene.List(graphene.String)
        outlet_id = graphene.Int()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        template_instance = get_model_object(
            StockCountTemplate, 'id', kwargs.get('template_id'))
        template_fields = stock_counts.get_template_fields(**kwargs)
        stock_tempalate = stock_counts.add_fields_to_template(
            template_instance,
            **template_fields
        )
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts template updated'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, stock counts schedule has \
            been modified'
        }
        params = {'model': StockCountTemplate}
        with SaveContextManager(stock_tempalate, **params) as stock_tempalate:
            send_mail = SendMail(email_stock_template,
                                 context, subject, to_email)
            send_mail.send()
            message = SUCCESS_RESPONSES["edit_success"].format(
                "Stock count template")
            return EditStockCountTemplate(
                stock_template=stock_tempalate, success=message)
