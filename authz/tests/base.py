import unittest

from authz.application import mongo, create
from authz.models import Consumer, Policy


class AuthzTestCase(unittest.TestCase):
    TESTING = True
    MONGOALCHEMY_DATABASE = 'authz_test'

    def setUp(self):
        """Initialize the application with the test database."""
        self.app = create(extra_config=self)
        self.client = self.app.test_client()

    def tearDown(self):
        """Destroy the mongo db database."""
        with self.app.test_request_context():
            mongo.session.clear_collection(Consumer, Policy)

    def assertContains(self, response, text):
        """Validate if a specific text is found in the request."""
        self.assertTrue(text in response.data)
