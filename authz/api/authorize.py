# -*- coding: utf-8 -*-
"""
    authz.api.authorize
    ~~~~~~~~~~~~~~~~~~~~

    Define the views for the authorize endpoints.

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
from flask import Blueprint, request, abort

from authz.application import mongo
from authz.models import Consumer, Policy


authorize_endpoints = Blueprint('authorize_endpoints', __name__)


@authorize_endpoints.route(
    '/<consumer_key>/<service>/<path:resource>/',
    methods=["GET", "POST", "PUT", "DELETE"])
def index(consumer_key, service, resource):
    """Authorize the specified consumer to use a particular service.

    We also check for wildcard patterns when searching through the existing
    policies so 'resource/*' would give access to 'resource/resource-id'.
    """
    consumer = Consumer.query.filter(Consumer.key == consumer_key).first()
    if not consumer:
        abort(401)

    try:
        rid_query = _build_rid_query(service, resource, request.method.lower())
    except ValueError:
        abort(500)

    query = {"consumer_key": consumer.key}
    query.update(rid_query)
    policies = mongo.session.query(Policy).filter(query)

    if not policies.first():
        abort(403)

    return "", 202


def _build_rid_query(service, resource, action):
    """Create the rid query filters for policies.

    Currently only resources in the following format are supported:
      * resource/resourceid

    You can also specify wildcards for resource parts but the / is mandatory
    in the expression.
    """
    resource_parts = resource.split("/")
    if len(resource_parts) < 2:
        raise ValueError()

    filters = tuple(set([
        "rid:%s:*/*" % service,
        "rid:%s:%s/*" % (service, resource_parts[0]),
        "rid:%s:%s/%s" % (service, resource_parts[0], resource_parts[1])
    ]))

    query_expression = []
    for filter in filters:
        query_expression.append({"rid": filter, "actions": action})

    return {"$or": query_expression}
