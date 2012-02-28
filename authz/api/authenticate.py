# -*- coding: utf-8 -*-
"""
    authz.api.authenticate
    ~~~~~~~~~~~~~~~~~~~~~~

    Define the views for the authenticate endpoints.

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
import oauth2 as oauth
from cStringIO import StringIO
from urlparse import urlparse
from urllib import unquote_plus

from flask import Blueprint, Request, request, abort, jsonify

from authz.models import Consumer


authenticate_endpoints = Blueprint('authenticate_endpoints', __name__)


oauth_server = oauth.Server(
    signature_methods={'HMAC-SHA1': oauth.SignatureMethod_HMAC_SHA1()}
)


@authenticate_endpoints.route(
    '/<path:url>',
    methods=["GET", "POST", "PUT", "DELETE"])
def index(url):
    """Verify 2-legged oauth request using the specified URL.

    If the request is authenticated the consumer details are returned as a json
    document in the body.
    """
    original_request = _request_from_url(unquote_plus(url), request)
    oauth_request = oauth.Request.from_request(
        original_request.method,
        original_request.url,
        headers=request.headers,
        parameters=dict(
            [(k, v) for k, v in original_request.values.iteritems()]
        ))

    if not oauth_request:
        abort(401)

    try:
        consumer_key = oauth_request.get_parameter('oauth_consumer_key')
    except oauth.Error:
        abort(401)

    consumer = Consumer.query.filter(Consumer.key == consumer_key).first()
    if not consumer:
        abort(401)

    try:
        oauth_server.verify_request(oauth_request, consumer, None)
    except oauth.Error:
        abort(401)

    response = jsonify(name=consumer.name, key=consumer.key)
    response.status_code = 202
    return response


def _request_from_url(url, current_request):
    """Build a Request instance based on the URL and the current request.

    The current request is the originating request from were we extract
    information such as body, content type and method.
    """
    parts = urlparse(url)

    return Request.from_values(
        base_url="%s://%s" % (parts.scheme, parts.netloc),
        path=parts.path,
        query_string=parts.query,
        content_length=len(current_request.data),
        input_stream=StringIO(current_request.data),
        content_type=current_request.content_type,
        method=current_request.method)
