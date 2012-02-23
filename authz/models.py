# -*- coding: utf-8 -*-
"""
    authz.models
    ~~~~~~~~~~~~~~~

    Define the MongoAlchemy models used in the application.

    :copyright: (c) 2012 by Ion Scerbatiuc
    :license: BSD
"""
import string
import random

from mongoalchemy.document import Index

from application import mongo


POLICY_ACTION_CHOICES = ("get", "post", "put", "delete")
"""The allowed values for the Policy.action field."""


def generate_key(length, extra_chars=None):
    """Generate a random key of the specified length.

    By default only letterts and digits are included in the key. If you want an
    extra set of characters to be considered, use the extra_chars arguments.
    """
    chars = string.letters + string.digits
    if extra_chars:
        chars += extra_chars

    return ''.join([random.choice(chars) for i in xrange(length)])


def generate_secret(length, extra_chars=None):
    """Generate a random secret of the specified length.

    By default letterts, digits and punctuation are included in the key. If you
    want an extra set of characters to be considered, use the extra_chars
    arguments.
    """
    chars = string.punctuation
    if extra_chars:
        chars += extra_chars

    return generate_key(length, extra_chars=chars)


class User(mongo.Document):
    """Model for OpenID users of the admin tool."""

    name = mongo.StringField(max_length=30)
    """:: user full name."""

    email = mongo.StringField(max_length=300)
    """:: email address."""

    openid = mongo.StringField(max_length=300)
    """:: openid identity."""

    iopenid = Index().ascending('openid').unique()
    """:: unique index for the openid key."""

    def __repr__(self):
        """Return the object representation used by the admin tool."""
        return self.name


class Consumer(mongo.Document):
    """Model for MediaCenter API consumers."""

    name = mongo.StringField(max_length=30)
    """:: the name of the consumer."""

    key = mongo.StringField(max_length=24)
    """:: the API consumer key."""

    secret = mongo.StringField(max_length=48)
    """:: the API consumer secret."""

    ikey = Index().ascending('key').unique()
    """:: unique index for the consumer key."""

    def __repr__(self):
        """Return the object representation used by the admin tool."""
        return getattr(self, 'name', '<Consumer>')

    def __init__(self, **kwargs):
        """Ensure that the key and secret are properly set when saving.

        If the keys were not set, they will be generated automatically.

        XXX [ion.scerbatiuc] - We should have this implemented in the commit
        override, but it seems to fail if we try to override it so we will keep
        this here until this can be solved.
        """
        if not kwargs.get('loading_from_db', False):
            if not kwargs.get('key'):
                kwargs['key'] = generate_key(24)

            if not kwargs.get('secret'):
                kwargs['secret'] = generate_secret(48)

        super(Consumer, self).__init__(**kwargs)


class Policy(mongo.Document):
    """Model for MediaCenter API policies."""

    consumer_key = mongo.StringField(max_length=24)
    """:: the key of the consumer for which this policy is set."""

    rid = mongo.StringField(max_length=200)
    """:: the resource identifier."""

    actions = mongo.SetField(
        mongo.EnumField(mongo.StringField(), *POLICY_ACTION_CHOICES))
    """:: the list of allowed actions."""

    def __repr__(self):
        """Return the object representation used by the admin tool."""
        return "%s:%s" % (self.consumer_key, self.rid)
