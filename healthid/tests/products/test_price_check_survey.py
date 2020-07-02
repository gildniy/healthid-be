from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.price_check_survey import (
    create_price_survey, delete_price_survey, get_all_price_surveys,
    get_price_survey, update_price_survey,
    update_price_survey_without_products,
    update_price_survey_without_suppliers)
from healthid.apps.products.models import Survey
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class TestPriceCheckSurvey(BaseConfiguration):
    """
    Test class for price check survey CRUD.
    """

    def setUp(self):
        super().setUp()
        self.survey_data = {
            'name': "Painkillers survey",
            'outlet_id': self.outlet.id,
            'suppliers': self.supplier.supplier_id,
            'products': self.product.id,
        }

        self.response = self.query_with_token(
            self.access_token_master,
            create_price_survey.format(**self.survey_data)
        )

        self.survey = self.response['data']['createPriceCheckSurvey']
        self.survey_name = self.survey['survey']['name']
        self.survey_id = self.survey['survey']['id']

    def test_create_price_check_survey(self):
        """
        Method to test if a price check survey
        can be created.
        """
        self.assertIn(
            'success', self.response['data']['createPriceCheckSurvey'])

        self.assertEqual(self.survey_data['name'], self.survey_name)

    def test_update_price_check_survey(self):
        """
        Method to test if a price check survey
        can be updated.
        """

        self.survey_data['survey_id'] = self.survey_id

        response = self.query_with_token(
            self.access_token_master,
            update_price_survey.format(**self.survey_data)
        )

        self.assertIn('updated successfully!',
                      response['data']['updatePriceCheckSurvey']['success'])

    def test_get_all_surveys(self):
        """
        Method to test if all created surveys
        can be returned.
        """
        response = self.query_with_token(
            self.access_token_master,
            get_all_price_surveys
        )

        self.assertGreater(len(response['data']['priceCheckSurveys']), 0)
        prices = response['data']['priceCheckSurveys'][0]['surveyPriceChecks']
        self.assertGreater(len(prices), 0)

    def test_get_one_survey(self):
        """
        Method to test if a specific survey
        can be returned.
        """
        response = self.query_with_token(
            self.access_token_master,
            get_price_survey.format(survey_id=self.survey_id)
        )

        name = response['data']['priceCheckSurvey']['name']
        self.assertEqual(self.survey_name, name)

    def test_delete_survey(self):
        """
        Method to test if a created survey
        can be deleted.
        """
        response = self.query_with_token(
            self.access_token_master,
            delete_price_survey.format(survey_id=self.survey_id)
        )

        self.assertIn("success", response['data']['deletePriceCheckSurvey'])

    ##############################
    # Testing edge cases
    ##############################

    def test_update_closed_survey(self):
        """
        Method to test if a closed survey
        can be updated.
        """
        # We first close the survey
        survey = get_model_object(Survey, 'id', self.survey_id)
        survey.survey_closed = True
        survey.save()

        self.survey_data['survey_id'] = self.survey_id

        response = self.query_with_token(
            self.access_token_master,
            update_price_survey.format(**self.survey_data)
        )

        message = PRODUCTS_ERROR_RESPONSES["closed_survey_error"]
        self.assertIn(message, response['errors'][0]['message'])

    def test_empty_name_when_creating(self):
        """
        Method to test for correct error message
        should the survey name field be left blank when
        creating a survey.
        """
        self.survey_data['name'] = " "

        response = self.query_with_token(
            self.access_token_master,
            create_price_survey.format(**self.survey_data)
        )

        message = "name field cannot be blank!"
        self.assertIn(message, response['errors'][0]['message'])

    def test_update_to_existing_survey_name(self):
        """
        Method to test if a survey name can be updated
        to an already existing name.
        """
        # create a new survey first
        self.survey_data['name'] = 'New Survey'
        self.query_with_token(
            self.access_token_master,
            create_price_survey.format(**self.survey_data)
        )

        # try to update existing survey name
        self.survey_data['survey_id'] = self.survey_id
        self.survey_data['name'] = 'New Survey'
        response = self.query_with_token(
            self.access_token_master,
            update_price_survey.format(**self.survey_data)
        )

        message = ERROR_RESPONSES["duplication_error"].format("New Survey")
        self.assertIn(message, response['errors'][0]['message'])

    def test_create_with_existing_name(self):
        """
        Method to test if a survey can be created
        with an already existing name.
        """
        # create a new article survey with the same data
        response = self.query_with_token(
            self.access_token_master,
            create_price_survey.format(**self.survey_data)
        )

        message = ERROR_RESPONSES[
                  "duplication_error"].format("Painkillers survey")
        self.assertIn(message, response['errors'][0]['message'])

    def test_delete_non_existent_survey(self):
        """
        Method to test error message when a non-existent survey id
        is provided when deleting.
        """
        survey_id = "thanosSnapped994"

        response = self.query_with_token(
            self.access_token_master,
            delete_price_survey.format(survey_id=survey_id)
        )
        message = 'does not exist.'
        self.assertIn(message, response['errors'][0]['message'])

    def test_update_without_products(self):
        """
        Method to test if survey details can be updated
        using only suppliers.
        """
        self.survey_data['survey_id'] = self.survey_id

        # remove the products entry
        del self.survey_data['products']

        response = self.query_with_token(
            self.access_token_master,
            update_price_survey_without_products.format(**self.survey_data)
        )

        message = PRODUCTS_ERROR_RESPONSES["product_prompt"]
        self.assertIn(message, response['errors'][0]['message'])

    def test_update_with_empty_suppliers(self):
        """
        Method to test response when products are but
        without suppliers.
        """
        self.survey_data['survey_id'] = self.survey_id

        response = self.query_with_token(
            self.access_token_master,
            update_price_survey_without_suppliers.format(**self.survey_data)
        )

        message = PRODUCTS_ERROR_RESPONSES["supplier_prompt"]
        self.assertIn(message, response['errors'][0]['message'])
