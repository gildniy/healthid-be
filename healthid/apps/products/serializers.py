from rest_framework import serializers

from healthid.apps.products.models import Product


class ProductsSerializer(serializers.ModelSerializer):
    product_category = serializers.CharField(source='product_category.name')
    dispensing_size = serializers.CharField(source='dispensing_size.name')
    preferred_supplier = serializers.CharField(source='preferred_supplier.name')  # noqa
    backup_supplier = serializers.CharField(source='backup_supplier.name')
    quantity = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'product_category', 'dispensing_size',
            'sku_number', 'description', 'brand', 'manufacturer', 'vat_status',
            'sales_price', 'created_at', 'nearest_expiry_date',
            'preferred_supplier', 'backup_supplier', 'pre_tax_retail_price',
            'tags', 'reorder_point', 'reorder_max',
            'loyalty_weight', 'is_returnable', 'quantity',
        ]
