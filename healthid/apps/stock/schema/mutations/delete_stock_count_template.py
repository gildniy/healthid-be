from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.app_utils.database import (
    get_model_object
)

from healthid.apps.stock.schema.types import (
    StockCountTemplateType
)
from datetime import datetime
import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.stock.models import StockCountTemplate


class DeleteStockCountTemplate(graphene.Mutation):
    """
    Delete a stock count template.

    args:
    template_id(int): id of the template to be deleted

    returns:
    success(str): success message confirming template delete
    """

    stock_template = graphene.Field(StockCountTemplateType)
    success = graphene.String()
    errors = graphene.String()

    class Arguments:
        template_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        stock_tempalate = get_model_object(
            StockCountTemplate, 'id', kwargs.get('template_id'))
        to_email = stock_tempalate.assigned_users.values_list(
            'email', flat=True)
        email_stock_template = 'email_alerts/stocks/stock_email.html'
        subject = 'Stock counts template canceled'
        context = {
            'schedule_time': datetime.strftime(
                stock_tempalate.schedule_time.start_date, "%d-%b-%Y"),
            'by': str(info.context.user.email),
            'template_type': 'Stock counts',
            'small_text_detail': 'Hello, stock counts has been canceled'
        }
        send_mail = SendMail(email_stock_template, context, subject, to_email)
        stock_tempalate.hard_delete()
        send_mail.send()
        message = SUCCESS_RESPONSES[
            "deletion_success"].format("Stock template")
        return DeleteStockCountTemplate(success=message)
