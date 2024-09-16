# test_lambda_function.py
import moto
from src.services.currency_api_service import CurrencyApiService
from tests.unit_tests.test_main import setup_table_case_1, aws_credentials
from src.helpers import date_helper


def test_fetch_currency_rates(setup_table_case_1):
    date = date_helper.get_expected_cet_currency_date()
    response = CurrencyApiService().fetch_currency_rates()
    assert response["date"] == date
    currency_rates = response["currency_rates"]
    print(currency_rates)
    # Assert the response values
    n = len(currency_rates.keys())
    c = 0
    for currency in currency_rates:
        assert currency_rates[currency]['change'] >= - \
            10 and currency_rates[currency]['change'] <= 50
        if 'change' in currency_rates[currency] and 'value' in currency_rates[currency]:
            c += 1
    assert c == n
