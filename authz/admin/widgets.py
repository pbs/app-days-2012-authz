from wtforms import widgets


class ReadonlyTextInput(widgets.TextInput):
    """Custom read-only text input widget."""

    def __call__(self, field, **kwargs):
        kwargs["readonly"] = "readonly"
        kwargs["class_"] = "readonly"
        return super(ReadonlyTextInput, self).__call__(field, **kwargs)
