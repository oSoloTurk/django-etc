from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured

try:
    from django.apps import apps
    apps_get_model = apps.get_model
except ImportError:  # Django < 1.7
    from django.db.models import get_model
    apps_get_model = None


def choices_list(*choices):
    """Helps to define choices for models, that could be addressed
    later as dictionaries.

    To be used in conjunction with `get_choices()`.

    Example:

        class MyModel(models.Model):

            TYPE_ONE = 1
            TYPE_TWO = 2

            TYPES = choices_list(
                (TYPE_ONE, 'Type one title'),
                (TYPE_TWO, 'Type two title'),
            )

            type = models.PositiveIntegerField('My type', choices=get_choices(TYPES), default=TYPE_TWO)

            def get_display_type(self):
                return self.TYPES[self.type]

    :param set|list choices:
    :rtype: OrderedDict
    :return: Choices ordered dictionary
    """
    return OrderedDict(choices)


def get_choices(choices_list):
    """Returns model field choices from a given choices list.
    Choices list is defined with `choices_list()`.

    :param OrderedDict choices_list:
    :rtype: tuple
    :return: Choices tuple
    """
    return tuple((key, val) for key, val in choices_list.items())


def set_form_widgets_attrs(form, attrs):
    """Applies a given HTML attributes to each field widget of a given form.

    Example:

        set_form_widgets_attrs(my_form, {'class': 'clickable'})

    """
    for _, field in form.fields.items():
        attrs_ = dict(attrs)
        for name, val in attrs.items():
            if hasattr(val, '__call__'):
                attrs_[name] = val(field)
        field.widget.attrs = field.widget.build_attrs(attrs_)


def get_model_class_from_string(model_path):
    """Returns a certain model as defined in a string formatted `<app_name>.<model_name>`.

    Example:

        model = get_model_class_from_string('myapp.MyModel')

    """
    try:
        app_name, model_name = model_path.split('.')
    except ValueError:
        raise ImproperlyConfigured('`%s` must have the following format: `app_name.model_name`.' % model_path)

    if apps_get_model is None:
        model = get_model(app_name, model_name)
    else:
        try:
            model = apps_get_model(app_name, model_name)
        except (LookupError, ValueError):
            model = None

    if model is None:
        raise ImproperlyConfigured('`%s` refers to a model `%s` that has not been installed.' % (model_path, model_name))

    return model


def get_model_class_from_settings(settings_module, settings_entry_name):
    """Returns a certain model as defined in a given settings module.

    Example:

        myapp/settings.py

            from django.conf import settings

            MY_MODEL = getattr(settings, 'MYAPP_MY_MODEL', 'myapp.MyModel')


        myapp/some.py

            from myapp import settings

            model = get_model_class_from_settings(settings, 'MY_MODEL')

    """
    return get_model_class_from_string(getattr(settings_module, settings_entry_name))