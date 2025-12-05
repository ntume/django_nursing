import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def validate_password(password):
    message = ''
    valid = True
    if not re.findall('\d', password):
        message = message + "Your password must contain at least 1 digit, 0-9. "
        valid = False

    if not re.findall('[A-Z]', password):
        message = message + "Your password must contain at least 1 uppercase letter, A-Z."
        valid = False

    if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
        message = message + "Your password must contain at least 1 special character: ()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        valid = False

    return valid, message