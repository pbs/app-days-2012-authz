from flask import url_for, json

from authz.models import Consumer, Policy
from base import AuthzTestCase
from fixtures import TEST_CONSUMERS, TEST_POLICIES

__all__ = ('ConsumersApiTestCase', 'PoliciesApiTestCase')


class ConsumersApiTestCase(AuthzTestCase):
    def setUp(self):
        super(ConsumersApiTestCase, self).setUp()

        # Create test data
        with self.app.test_request_context():
            for consumer in TEST_CONSUMERS:
                Consumer(**consumer).save()

    def test_get_all_consumers(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers')

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals(3, len(response["objects"]))

    def test_get_single_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers', consumer_key='DEF')

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("DEF", response['key'])

    def test_create_consumer_without_name(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers')

        rv = self.client.post(url, data="{}", content_type="application/json")
        self.assertEquals(400, rv.status_code)
        self.assertTrue("Missing required field: name" in rv.data)

    def test_create_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers')

        payload = json.dumps({"name": "Test Consumer"})
        rv = self.client.post(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(201, rv.status_code)

        response = json.loads(rv.data)
        self.assertTrue("key" in response)
        self.assertTrue("name" in response)
        self.assertTrue("policies" in response)

    def test_update_invalid_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers', consumer_key='TUV')

        rv = self.client.put(url, data="{}", content_type="application/json")
        self.assertEquals(404, rv.status_code)

    def test_update_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers', consumer_key='XYZ')

        payload = json.dumps({
            "key": "IJH", # the key should not get updated
            "name": "Test Consumer Changed"
        })
        rv = self.client.put(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(200, rv.status_code)

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("XYZ", response["key"])
        self.assertEquals("Test Consumer Changed", response["name"])

    def test_delete_invalid_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers', consumer_key='TUV')

        rv = self.client.put(url, data="{}", content_type="application/json")
        self.assertEquals(404, rv.status_code)

    def test_delete_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.consumers', consumer_key='DEF')

        rv = self.client.delete(url)
        self.assertEquals(204, rv.status_code)
        self.assertEquals('', rv.data)

        rv = self.client.get(url)
        self.assertEquals(404, rv.status_code)


class PoliciesApiTestCase(AuthzTestCase):
    def setUp(self):
        super(PoliciesApiTestCase, self).setUp()

        # Create test data
        with self.app.test_request_context():
            for consumer in TEST_CONSUMERS:
                Consumer(**consumer).save()

            for policy in TEST_POLICIES:
                Policy(**policy).save()

    def test_get_policies(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ")

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals(3, len(response["objects"]))

    def test_get_single_policy(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:station/*")

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertTrue("consumer" in response)
        self.assertEquals("rid:pbs:api:station/*", response["rid"])
        self.assertEquals(
            set(["get", "put", "delete"]),
            set(response["actions"]))

    def test_get_policies_through_consumer(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.consumers',
                consumer_key="XYZ")

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        rv = self.client.get(response["policies"])
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals(3, len(response["objects"]))

    def test_get_consumer_through_policy(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:station/*")

        rv = self.client.get(url)
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        rv = self.client.get(response["consumer"])
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("XYZ", response["key"])

    def test_create_policy_invalid_consumer(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.policies', consumer_key="TUV")

        rv = self.client.post(url, data="{}", content_type="application/json")
        self.assertEquals(404, rv.status_code)

    def test_create_policy_missing_fields(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.policies', consumer_key="XYZ")

        rv = self.client.post(
            url,
            data='{"rid": "rid:pbs:api:station/bbmedia"}',
            content_type="application/json")
        self.assertEquals(400, rv.status_code)
        self.assertContains(rv, "Missing required fields: actions")

        rv = self.client.post(url, data='{}', content_type="application/json")
        self.assertEquals(400, rv.status_code)
        self.assertContains(rv, "Missing required fields: rid, actions")

    def test_create_policy(self):
        with self.app.test_request_context():
            url = url_for('rest_endpoints.policies', consumer_key="XYZ")

        payload = json.dumps({
            "rid": "rid:pbs:api:station/bbmedia",
            "actions": ["get", "put"]})
        rv = self.client.post(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(201, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("rid:pbs:api:station/bbmedia", response["rid"])
        self.assertEquals(set(["get", "put"]), set(response["actions"]))
        self.assertTrue("consumer" in response)

    def test_update_policy_invalid_consumer(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="TUV",
                rid="rid:pbs:api:station/*")

        rv = self.client.put(url, data="{}", content_type="application/json")
        self.assertEquals(404, rv.status_code)

    def test_update_policy_invalid_rid(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:program/*")

        rv = self.client.put(url, data="{}", content_type="application/json")
        self.assertEquals(404, rv.status_code)

    def test_update_policy(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:station/*")

        payload = json.dumps({"actions": ["get", "post", "put", "put"]})
        rv = self.client.put(
            url, data=payload,
            content_type="application/json")
        self.assertEquals(200, rv.status_code)

        response = json.loads(rv.data)
        self.assertEquals("rid:pbs:api:station/*", response["rid"])
        self.assertEquals(
            set(["get", "post", "put"]),
            set(response["actions"]))
        self.assertTrue("consumer" in response)

    def test_delete_policy_invalid_consumer(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="TUV",
                rid="rid:pbs:api:station/*")

        rv = self.client.delete(url)
        self.assertEquals(404, rv.status_code)

    def test_delete_policy_invalid_rid(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:program/*")

        rv = self.client.delete(url)
        self.assertEquals(404, rv.status_code)

    def test_delete_policy(self):
        with self.app.test_request_context():
            url = url_for(
                'rest_endpoints.policies',
                consumer_key="XYZ",
                rid="rid:pbs:api:station/*")

        rv = self.client.delete(url)
        self.assertEquals(204, rv.status_code)

        rv = self.client.get(url)
        self.assertEquals(404, rv.status_code)
