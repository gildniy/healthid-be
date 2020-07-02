from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import create_measuremt_unit
from healthid.utils.messages.common_responses import\
    SUCCESS_RESPONSES, ERROR_RESPONSES


class TestDispensingSize(BaseConfiguration):
    """
    class handles all tests for meaurement units
    """

    def test_create_dispensing_size(self):
        """
        test meaurement creation
        """
        reponse = self.query_with_token(self.access_token_master,
                                        create_measuremt_unit)
        self.assertIn(SUCCESS_RESPONSES[
                      "creation_success"].format("Dispensing Size"),
                      reponse['data']['createDispensingSize']['message'])
        self.assertIn('data', reponse)
        self.assertNotIn('errors', reponse)

    def test_duplicate_unit(self):
        """
        test duplicate  meauremnt unit
        """
        self.query_with_token(self.access_token_master, create_measuremt_unit)
        duplicate_dispensing = self.query_with_token(
            self.access_token_master, create_measuremt_unit)
        self.assertIn(ERROR_RESPONSES[
                      "duplication_error"].format(
            "DispensingSize with name tablets"),
            duplicate_dispensing['errors'][0]['message'])
        self.assertIn('errors', duplicate_dispensing)
