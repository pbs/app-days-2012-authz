import time
import oauth2 as oauth

from flask import url_for, json

from authz.models import Consumer
from base import AuthzTestCase
from fixtures import TEST_CONSUMERS

__all__ = ('AuthenticateTestCase',)


def _build_request(consumer, method, url, body=''):
    """Build an OAuth signed request and return the request URL."""
    request = oauth.Request(
        method=method,
        url=url,
        body=body,
        parameters={
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_consumer_key': consumer.key,
        })

    request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    return request.to_url()


class AuthenticateTestCase(AuthzTestCase):
    def setUp(self):
        super(AuthenticateTestCase, self).setUp()

        # Create test data
        with self.app.test_request_context():
            for consumer in TEST_CONSUMERS:
                Consumer(**consumer).save()

    def test_not_authenticated(self):
        with self.app.test_request_context():
            url = url_for(
                'authenticate_endpoints.index',
                url="http://api.pbs.org/1.0/?format=json")

        rv = self.client.get(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.put(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.post(url)
        self.assertEquals(401, rv.status_code)

        rv = self.client.delete(url)
        self.assertEquals(401, rv.status_code)

    def test_not_authenticated_signed(self):
        consumer = oauth.Consumer(key="XYZ", secret="ABC")
        request_url = _build_request(
            consumer,
            "PUT",
            "http://api.pbs.org/1.0/stations/?format=json")

        with self.app.test_request_context():
            url = url_for('authenticate_endpoints.index', url=request_url)

        rv = self.client.put(url)
        self.assertEquals(401, rv.status_code)

    def test_authenticated_get(self):
        consumer = oauth.Consumer(key="XYZ", secret="ZYX")
        request_url = _build_request(
            consumer,
            "GET",
            "http://api.pbs.org/1.0/stations/?format=json")

        with self.app.test_request_context():
            url = url_for('authenticate_endpoints.index', url=request_url)

        rv = self.client.get(url)
        self.assertEquals(202, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("XYZ", response["key"])
        self.assertEquals("Consumer XYZ", response["name"])

        rv = self.client.post(url)
        self.assertEquals(401, rv.status_code)

    def test_authenticated_post(self):
        consumer = oauth.Consumer(key="XYZ", secret="ZYX")
        payload = json.dumps({"title": "Test Station", "tvcode": "TSTA"})
        request_url = _build_request(
            consumer,
            "POST",
            "http://api.pbs.org/1.0/stations/?format=json",
            body=payload)

        with self.app.test_request_context():
            url = url_for('authenticate_endpoints.index', url=request_url)

        rv = self.client.post(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(202, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("XYZ", response["key"])
        self.assertEquals("Consumer XYZ", response["name"])

        rv = self.client.put(url)
        self.assertEquals(401, rv.status_code)

    def test_authenticated_put(self):
        consumer = oauth.Consumer(key="DEF", secret="FED")
        payload = json.dumps({"title": "Test Station", "tvcode": "TSTA"})
        request_url = _build_request(
            consumer,
            "PUT",
            "http://api.pbs.org/1.0/stations/test-station/",
            body=payload)

        with self.app.test_request_context():
            url = url_for('authenticate_endpoints.index', url=request_url)

        rv = self.client.put(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(202, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("DEF", response["key"])
        self.assertEquals("Consumer DEF", response["name"])

        rv = self.client.delete(url)
        self.assertEquals(401, rv.status_code)

    def test_authenticated_delete(self):
        consumer = oauth.Consumer(key="ABC", secret="CBA")
        request_url = _build_request(
            consumer,
            "DELETE",
            "http://api.pbs.org/1.0/stations/test-station/")

        with self.app.test_request_context():
            url = url_for('authenticate_endpoints.index', url=request_url)

        rv = self.client.delete(url)
        self.assertEquals(202, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("ABC", response["key"])
        self.assertEquals("Consumer ABC", response["name"])

        rv = self.client.get(url)
        self.assertEquals(401, rv.status_code)
