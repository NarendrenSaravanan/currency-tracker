import pytz
from datetime import datetime, timedelta
from src.common import constants


def get_expected_cet_currency_date(given_date=""):
    if not given_date:
        cet = pytz.timezone('CET')
        given_date = datetime.now().astimezone(cet)
    else:
        given_date = datetime.strptime(
            given_date, constants.DATE_TIME_FORMAT)
    # shifting expected date to previous working day (MON-FRI)
    shift = timedelta(days=max(1, (given_date.weekday() + 6) % 7 - 3))
    expected_date_dt = given_date - shift
    expected_date = datetime.strftime(
        expected_date_dt, constants.DATE_TIME_FORMAT)
    return expected_date
