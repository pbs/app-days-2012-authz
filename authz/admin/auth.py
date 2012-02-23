# -*- coding: utf-8 -*-
"""
    authz.auth
    ~~~~~~~~~~~~~~~~~~

    Define utilities and views for the authentication mechanism using OpenID
    and the MongoDB storage.

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
from functools import wraps

from flask import (
    request, session, g, redirect, url_for, render_template, flash)

from authz.application import openid
from authz.models import User


def login_required(func):
    """Decorator for enforcing login to be required for the decorated view."""
    @wraps(func)
    def _decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('.login', next=request.url))
        return func(*args, **kwargs)

    return _decorated_function


def login_before_request():
    """Handler for the flask before_request signal.

    To be registered an app creation in order to use the auth machinery.
    """
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter(User.openid == session["openid"]).first()


@openid.loginhandler
def login_view():
    """Login view for authenticating using OpenID."""
    if g.user is not None:
        return redirect(openid.get_next_url())

    error = openid.fetch_error()
    if request.method == 'POST':
        oid = request.form.get('openid')
        if oid:
            return openid.try_login(
                oid,
                ask_for=['email', 'fullname', 'nickname'])
        else:
            error = 'You need to specify a valid OpenID to continue'

    return render_template(
        'login.html',
        next=openid.get_next_url(),
        error=error)


def logout_view():
    session.pop('openid', None)
    flash('You were successfully signed out from MediaCenter Authz')
    return redirect(openid.get_next_url())


@openid.after_login
def login_openid(response):
    """Login the user after a successful OpenID authentication.

    If the user is not found in the database the login will be rejected. If the
    user is found, the user will be updated with the fullkname and email
    returned by the Provider and the session will be authenticated.
    """
    user = User.query.filter(User.openid == response.identity_url).first()
    if user:
        user.name = response.fullname
        user.email = response.email
        user.save()

        g.user = user
        session["openid"] = user.openid
    else:
        flash(
            "Your account doesn't have access to this system.",
            category="error")

    return redirect(openid.get_next_url())


def create_admin():
    """Helper function for creating an admin user."""
    from authz.application import create
    app = create(load_admin=False, load_rest_api=False, load_service_api=False)

    openid_identity = raw_input("Please provide an OpenID: ")
    if not openid_identity:
        print "ERROR: Please specify a valid OpenID identity"
        return 1

    full_name = raw_input("Full name (optional): ")
    email = raw_input("Email address (optional): ")

    user = User(
        openid=openid_identity,
        name=full_name,
        email=email)
    user.save()

    print "User with identity '%s' was successfully created" % openid_identity
