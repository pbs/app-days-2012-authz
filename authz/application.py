# -*- coding: utf-8 -*-
"""
    authz.application
    ~~~~~~~~~~~~~~~~~

    Flask application factory

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
from flask import Flask, redirect, url_for
from flaskext.mongoalchemy import MongoAlchemy
from flaskext.openid import OpenID


mongo = MongoAlchemy()
"""The mongo alchemy connection object."""


openid = OpenID()
"""The openid store object."""


def create(extra_config=None, load_mongo=True, load_admin=True,
           load_rest_api=True, load_service_api=True):
    """Create a new Flask application object.

    The default configuration is loaded from authz.default_settings. You can
    override any of the settings by setting the AUTHZ_SETTINGS_OVERRIDE env var
    to point to the configuration file.

    You can also specify the extra_config argument to override the already
    loaded settings.

    Befire returning the app instance, all the necessary blueprints are
    registered.
    """
    app = Flask("authz")

    app.config.from_object('authz.default_settings')
    app.config.from_envvar('AUTHZ_SETTINGS_OVERRIDE', silent=True)

    if extra_config:
        app.config.from_object(extra_config)

    if load_mongo or load_admin or load_rest_api or load_service_api:
        mongo.init_app(app)

    if load_admin:
        openid.init_app(app)

        import admin
        admin.init(app)

    if load_rest_api:
        from api import rest_endpoints
        app.register_blueprint(rest_endpoints, url_prefix='/api/1.0')

    if load_service_api:
        from api import authorize_endpoints, authenticate_endpoints
        app.register_blueprint(authorize_endpoints, url_prefix='/authorize')
        app.register_blueprint(
            authenticate_endpoints,
            url_prefix='/authenticate')

    return app
