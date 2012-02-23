from flask import url_for

from authz.models import Consumer, Policy
from base import AuthzTestCase
from fixtures import TEST_CONSUMERS, TEST_POLICIES

__all__ = ('AuthorizeTestCase',)


class AuthorizeTestCase(AuthzTestCase):
    def setUp(self):
        super(AuthorizeTestCase, self).setUp()

        # Create test data
        with self.app.test_request_context():
            for consumer in TEST_CONSUMERS:
                Consumer(**consumer).save()

            for policy in TEST_POLICIES:
                Policy(**policy).save()

    def test_unauthorized(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="TUV",
                service="pbs:api",
                resource="program/test-program")

        rv = self.client.get(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(401, rv.status_code)

    def test_forbidden(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="ABC",
                service="pbs:api",
                resource="program/test-program")

        rv = self.client.get(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(403, rv.status_code)

    def test_invalid_resource(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="ABC",
                service="pbs:api",
                resource="program")

        rv = self.client.get(url)
        self.assertEquals(500, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(500, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(500, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(500, rv.status_code)

    def test_authorize_wildcard_resource(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="XYZ",
                service="pbs:api",
                resource="topic/science-technology")

        rv = self.client.get(url)
        self.assertEquals(202, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(403, rv.status_code)

    def test_authorize_wildcard_resourceid(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="XYZ",
                service="pbs:api",
                resource="station/utmedia")

        rv = self.client.get(url)
        self.assertEquals(202, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(202, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(202, rv.status_code)

    def test_authorize_resourceid(self):
        with self.app.test_request_context():
            url = url_for(
                'authorize_endpoints.index',
                consumer_key="XYZ",
                service="pbs:api",
                resource="program/test-program")

        rv = self.client.get(url)
        self.assertEquals(202, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(403, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(202, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(403, rv.status_code)
