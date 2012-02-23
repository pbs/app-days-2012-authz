from wtforms import Form, validators, fields
from flask_admin.datastore.mongoalchemy import DisabledTextInput

from authz.models import generate_key, generate_secret, POLICY_ACTION_CHOICES
from widgets import ReadonlyTextInput


class ConsumerForm(Form):
    """Form for creating or editting Consumer instances via admin."""

    name = fields.TextField(
        u'Name',
        [validators.required(), validators.length(max=30)])

    key = fields.TextField(
        u'Consumer Key',
        [validators.length(max=24)],
        default=lambda: generate_key(24),
        widget=ReadonlyTextInput())

    secret = fields.TextField(
        u'Consumer Secret',
        [validators.length(max=48)],
        default=lambda: generate_secret(48),
        widget=ReadonlyTextInput())


class SelectActions(fields.SelectMultipleField):
    """Custom SelectMultipleField that returns a set instead of a list."""

    def process_formdata(self, valuelist):
        """Override the default process to return a set."""
        super(SelectActions, self).process_formdata(valuelist)
        self.data = set(self.data)


class PolicyForm(Form):
    """Form for creating or editting Policy instances via admin."""

    consumer_key = fields.TextField(
        u'Consumer',
        [validators.required(), validators.length(max=24)])

    rid = fields.TextField(
        u'Resource Identificator',
        [validators.length(max=200)])

    actions = SelectActions(
        u'Actions',
        [validators.required()],
        choices=[(key, key.upper()) for key in POLICY_ACTION_CHOICES])
