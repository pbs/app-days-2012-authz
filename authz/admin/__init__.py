# -*- coding: utf-8 -*-
"""
    authz.admin
    ~~~~~~~~~~~~

    Define the Flask admin endpoints

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
from flask import request, session, g, redirect, url_for
from flask.ext import admin
from flask.ext.admin.datastore.mongoalchemy import MongoAlchemyDatastore

from authz.application import mongo, openid
from authz.models import User, Consumer, Policy
from auth import (
    login_before_request, login_view, logout_view, login_required)
from forms import ConsumerForm, PolicyForm


def init(app):
    """Initialize the admin integration with the Flask app."""

    datastore = MongoAlchemyDatastore(
        (User, Consumer, Policy),
        mongo.session,
        model_forms={
            'Consumer': ConsumerForm,
            'Policy': PolicyForm,
        }
    )

    admin_blueprint = admin.create_admin_blueprint(
        datastore,
        view_decorator=login_required)

    admin_blueprint.before_request(login_before_request)

    admin_blueprint.add_url_rule(
        '/login/',
        endpoint='login',
        view_func=login_view,
        methods=['GET', 'POST'])

    admin_blueprint.add_url_rule(
        '/logout/',
        endpoint='logout',
        view_func=logout_view,
        methods=['GET',])

    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))
