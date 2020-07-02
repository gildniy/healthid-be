from healthid.tests.base_config import BaseConfiguration
from healthid.apps.sales.models import Promotion, PromotionType


class TestPromotion(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.promotion_type = PromotionType.objects.create(name='Special')
        self.promotion_data = {
            'title': 'my promo',
            'promotion_type_id': self.promotion_type.id,
            'description': 'nice promo',
            'discount': 10,
            'outlet_id': self.outlet.id
        }
        self.promotion = Promotion.objects.create(**self.promotion_data)
        self.promotion_data['title'] = 'another promo'
        self.second_promotion = Promotion.objects.create(**self.promotion_data)
