import string
import random
import datetime
import jdatetime

from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import datetime
from os.path import splitext
from django.contrib import messages


def random_num(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_time(frmt: str = '%Y-%m-%d %H:%M'):
    time = timezone.now()
    if frmt is not None:
        time = time.strftime(frmt)

    return time


def convert_gregorian_to_shamsi_date(gregorian_date, frmt=None):
    time = jdatetime.date.fromgregorian(date=gregorian_date)
    if frmt:
        time = time.strftime(frmt)
    return time


def upload_file_src(instance, path):
    now = get_time('%Y-%m-%d')
    return f'files/{now}/{path}'


def get_file_extension(file_name):
    if not file_name or not hasattr(file_name, 'file') or not file_name.file.name:
        return None
    name, extension = splitext(file_name.file.name)
    return extension


def get_timesince_persian(time):
    time_server = timezone.now()

    diff_time = datetime(
        time_server.year, time_server.month, time_server.day, time_server.hour, time_server.minute
    ) - datetime(
        time.year, time.month, time.day, time.hour, time.minute
    )

    diff_time_sec = diff_time.total_seconds()

    day = diff_time.days
    hour = int(diff_time_sec // 3600)
    minute = int(diff_time_sec // 60 % 60)

    if day > 0:
        output = _('%(days)s days ago.') % {'days': day}
    elif hour > 0:
        output = _('%(hours)s hours ago.') % {'hours': hour}
    elif minute > 0:
        output = _('%(minutes)s minutes ago.') % {'minutes': minute}
    else:
        output = _('Moments ago')

    return output


def validate_form(request, form):
    if form.is_valid():
        return True

    errors = form.errors.items()

    if not errors:
        messages.error(request, _('Entered data is not correct.'))
        return False

    for field, message in errors:
        for error in message:
            messages.error(request, error)

    return False


def toast_form_errors(request, form):
    errors = form.errors.items()
    if not errors:
        messages.error(request, _('Entered data is not correct.'))
        return False

    for field, message in errors:
        for error in message:
            messages.error(request, error)


def get_coded_phone_number(number):
    if not number or not isinstance(number, (str, int)):
        return None  #

    phone_number = str(number).lstrip('+')
    return f'+98{phone_number[1:]}' if phone_number.startswith('0') else f'+98{phone_number}'


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]

    return request.META.get('REMOTE_ADDR')


def convert_str_to_bool(str_vlue):
    if str_vlue == 'true':
        return True
    return False

