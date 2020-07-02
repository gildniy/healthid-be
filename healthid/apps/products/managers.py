from healthid.manager import BaseManager


class ProductManager(BaseManager):
    """
    Custom manager product model
    Attributes:
        active_only(bool): Specify if deactived products should be included
        approved_only(bool): Specify if proposed products should be included
        original_only(bool): Specify if proposed products edits should be
                             included
    """

    def __init__(self, *args, **kwargs):
        self.active_only = kwargs.pop('active_only', True)
        self.approved_only = kwargs.pop('approved_only', True)
        self.original_only = kwargs.pop('original_only', True)
        super(ProductManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.active_only:
            queryset = queryset.filter(is_active=True)
        if self.original_only:
            queryset = queryset.filter(parent_id__isnull=True)
        if self.approved_only:
            queryset = queryset.filter(is_approved=True)
        return queryset

    def for_business(self, business_id):
        return self.filter(business_id=business_id)


class QuantityManager(BaseManager):
    """
    Custom manager product model
    Attributes:
        original_only(bool): Specify if proposed quantity edits should be
                              included.
    """

    def __init__(self, *args, **kwargs):
        self.original_only = kwargs.pop('original_only', True)
        super(QuantityManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.original_only:
            queryset = queryset.filter(parent_id__isnull=True)
        return queryset
