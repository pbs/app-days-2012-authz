# -*- coding: utf-8 -*-
"""
    authz.api.rest
    ~~~~~~~~~~~~~~~

    Define the views for the authz REST API endpoints.

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
from flask import Blueprint, request, url_for, abort, jsonify, json, g
from flask.views import MethodView

from authz.models import Consumer, Policy


rest_endpoints = Blueprint('rest_endpoints', __name__)


class BaseApi(MethodView):
    """Base class for the API views."""

    def jsonify(self, obj, status_code=200):
        """Return a JSON response using the specified mapping.

        The specified mapping must be a valid python mapping or an
        AssertionError will be raised.
        """
        assert isinstance(obj, dict)

        response = jsonify(obj)
        response.status_code = status_code
        return response


class ConsumersApi(BaseApi):
    """API handlers for the consumers collection endpoint."""

    def _serialize(self, consumer):
        """Serialize the consumer object to be ready for jsonify."""
        return {
            "name": consumer.name,
            "key": consumer.key,
            "secret": consumer.secret,
            "policies": url_for(
                "rest_endpoints.policies",
                consumer_key=consumer.key),
            "resource_uri": url_for(
                "rest_endpoints.consumers",
                consumer_key=consumer.key)
        }

    def get(self, consumer_key=None):
        """Return the list of consumers in the system.

        If consumer key is specified, return only the specified consumer.
        """
        if consumer_key:
            consumer = Consumer.query.filter(
                Consumer.key == consumer_key
            ).first_or_404()
            payload = self._serialize(consumer)
        else:
            payload = {
                "objects": []
            }
            consumers = Consumer.query.filter()
            for consumer in consumers:
                payload["objects"].append(self._serialize(consumer))

        return self.jsonify(payload)

    def post(self):
        """Create a new consumer in the system.

        This method requires a JSON payload containing the consumer attributes.
        Currently only name is required. The consumer key is automatically
        generated and is returned with the response payload.
        """
        payload = json.loads(request.data)
        if "name" not in payload:
            abort(400, "Missing required field: name")

        consumer = Consumer(name=payload["name"])
        consumer.save()
        return self.jsonify(self._serialize(consumer), status_code=201)

    def put(self, consumer_key):
        """Update and existing consumer.

        This method requires a JSON payload containing the new consumer
        attributes.
        """
        consumer = Consumer.query.filter(
            Consumer.key == consumer_key
        ).first_or_404()

        payload = json.loads(request.data)
        for attr, value in payload.iteritems():
            if attr not in ('_id', 'key'):
                setattr(consumer, attr, value)

        consumer.save()
        return self.jsonify(self._serialize(consumer))

    def delete(self, consumer_key):
        """Delete the specified consumer from the system."""
        consumer = Consumer.query.filter(
            Consumer.key == consumer_key
        ).first_or_404()

        consumer.remove()
        return '', 204


consumers_view = ConsumersApi.as_view('consumers')
rest_endpoints.add_url_rule(
    '/consumers/', defaults={'consumer_key': None},
    view_func=consumers_view, methods=['GET'])
rest_endpoints.add_url_rule(
    '/consumers/',
    view_func=consumers_view, methods=['POST'])
rest_endpoints.add_url_rule(
    '/consumers/<consumer_key>/',
    view_func=consumers_view, methods=['GET', 'PUT', 'DELETE'])


class PoliciesApi(BaseApi):
    """API handlers for the policies collection endpoint."""

    def _serialize(self, policy):
        """Serialize the policy object to be ready for jsonify."""
        return {
            "rid": policy.rid,
            "actions": list(policy.actions),
            "consumer": url_for(
                "rest_endpoints.consumers",
                consumer_key=policy.consumer_key)
        }

    def get(self, consumer_key, rid=None):
        """Return the list of policies for the specified consumer.

        If resource id is specified, return only that policy.
        """
        if rid:
            policy = Policy.query.filter(
                Policy.consumer_key == consumer_key,
                Policy.rid == rid
            ).first_or_404()
            payload = self._serialize(policy)
        else:
            policies = Policy.query.filter(Policy.consumer_key == consumer_key)
            payload = {"objects": []}
            for policy in policies:
                payload["objects"].append(self._serialize(policy))

        return self.jsonify(payload)

    def post(self, consumer_key):
        """Create a new policy definition for the specified consumer.

        This method requires a JSON payload containing the policy definition.
        :: For example:
            {
                "rid": "rid:mc:master:stations/bbmedia",
                "actions": ["get", "put"]
            }
        """
        consumer = Consumer.query.filter(
            Consumer.key == consumer_key
        ).first_or_404()

        missing_fields = []
        payload = json.loads(request.data)
        for required_field in ("rid", "actions"):
            if required_field not in payload:
                missing_fields.append(required_field)

        if missing_fields:
            abort(400, "Missing required fields: %s" % (
                ", ".join(missing_fields)))

        policy = Policy(
            consumer_key=consumer_key,
            rid=payload["rid"],
            actions=set(payload["actions"]))
        policy.save()
        return self.jsonify(self._serialize(policy), status_code=201)

    def put(self, consumer_key, rid):
        """Update the definition for the specified policy.

        This method requires a JSON payload containing the updated attributes
        of the policy. Currently only actions is considered.
        :: For example:
            {
                "actions": ["get", "put"]
            }
        """
        policy = Policy.query.filter(
            Policy.consumer_key == consumer_key,
            Policy.rid == rid
        ).first_or_404()

        payload = json.loads(request.data)
        if "actions" not in payload:
            abort(400, "Missing required field: actions")

        policy.actions = set(payload["actions"])
        policy.save()
        return self.jsonify(self._serialize(policy), status_code=200)

    def delete(self, consumer_key, rid):
        """Delete the policy definition from the specified consumer."""
        policy = Policy.query.filter(
            Policy.consumer_key == consumer_key,
            Policy.rid == rid
        ).first_or_404()

        policy.remove()
        return '', 204


policies_view = PoliciesApi.as_view('policies')
rest_endpoints.add_url_rule(
    '/consumers/<consumer_key>/policies/', defaults={'rid': None},
    view_func=policies_view, methods=['GET'])
rest_endpoints.add_url_rule(
    '/consumers/<consumer_key>/policies/',
    view_func=policies_view, methods=['POST'])
rest_endpoints.add_url_rule(
    '/consumers/<consumer_key>/policies/<path:rid>/',
    view_func=policies_view, methods=['GET', 'PUT', 'DELETE'])


@rest_endpoints.route('/')
def api_index():
    """The API index endpoint used to discover all the available endpoints."""
    return jsonify({
        "consumers": {
            "list_endpoint": url_for("rest_endpoints.consumers")
        }
    })
