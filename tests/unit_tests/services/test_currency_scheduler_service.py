# test_lambda_function.py
import moto
import pytest
import boto3
import os
from src.services.currency_scheduler_service import CurrencySchedulerService
from src.db.models.currency_scheduler_metadata import CurrencySchedulerMetadata
from src.common import enum
from src.services.currency_api_service import CurrencyApiService
from tests.unit_tests.test_main import setup_table_case_2, aws_credentials, lambda_environment, mock_sqs, setup_table_case_3
from src.helpers import date_helper


def test_invoke_scheduler(mock_sqs, setup_table_case_2, aws_credentials, lambda_environment):
    print(os.environ)
    response = CurrencySchedulerService().invoke_scheduler()
    print(response)
    sqs_client = boto3.client('sqs')
    sqs_message = sqs_client.receive_message(
        QueueUrl=os.environ["CURRENCY_TRACKING_SQS_URL"])
    print(sqs_message)
    assert not (sqs_message) == False


def test_execute_scheduler(mock_sqs, setup_table_case_3, aws_credentials, lambda_environment):
    # verify after fetching current currency data
    date = date_helper.get_expected_cet_currency_date()
    previous_date = date_helper.get_expected_cet_currency_date(date)
    response = CurrencyApiService().fetch_currency_rates()
    assert response["date"] == previous_date
    currency_rates = response["currency_rates"]
    n = len(currency_rates.keys())
    c = 0
    print('response', response)
    currency_rates = response["currency_rates"]
    for currency in currency_rates:
        if 'value' in currency_rates[currency]:
            c += 1
    assert c == n
    status = CurrencySchedulerService().execute_scheduler()
    assert status == enum.SchedluerExecutionState.SUCCESS
    # verify after fetching recent currency data
    response = CurrencyApiService().fetch_currency_rates()
    assert response["date"] == date
    currency_rates = response["currency_rates"]
    c = 0
    print('response', response)
    currency_rates = response["currency_rates"]
    for currency in currency_rates:
        if 'value' in currency_rates[currency]:
            c += 1
    assert c == n
