from graphql import GraphQLError


class ValidateStockTransfer():
    """Class to validate the stock transfer fields
    """
    def validate_fields(self, **fields):
        """Method to ensure that the stock transfer gets the
        appropriate validated fields to feed into the database
        """
        if len(fields['batch_ids']) != len(fields['quantities']):
            raise GraphQLError(
                'An equal number of products and quantities must be provided!')

    def validate_transfer(self, transfer_number):
        """Method to check that the supplied field is not empty
        """
        if not transfer_number or transfer_number.isspace():
            raise GraphQLError('Please enter a valid transfer number!')


validate = ValidateStockTransfer()
