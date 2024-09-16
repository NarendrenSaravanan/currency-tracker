import pytest
import os
import moto
import json
import time
import boto3
import random
from src.db.models.currency_rates import CurrencyRates
from src.db.models.currency_scheduler_metadata import CurrencySchedulerMetadata
from src.db.client import DbClient
from src.helpers import date_helper
from src.common import constants


@pytest.fixture(autouse=True)
def lambda_environment():
    env_mapping = {
        "LOGGING_LEVEL": "INFO",
        "EURO_BANK_CURRENCY_URL": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html",
        "IGNORE_EXPECTED_DATE_CHECK": "true",
        "CURRENCY_TRACKING_SQS_URL": "dummy"
    }
    for env in env_mapping:
        os.environ[env] = env_mapping[env]


@pytest.fixture(autouse=True)
def mock_sqs():
    with moto.mock_aws():
        sqs_client = boto3.client('sqs')
        response = sqs_client.create_queue(QueueName='test')
        queue_url = response["QueueUrl"]
        os.environ["CURRENCY_TRACKING_SQS_URL"] = queue_url
        yield sqs_client


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = 'us-east-1'


@pytest.fixture
def setup_table_case_1(aws_credentials):
    # Store current and previous currency records based on current date
    with moto.mock_aws():
        if not CurrencyRates.exists():
            CurrencyRates.create_table(wait=True)
        if not CurrencySchedulerMetadata.exists():
            CurrencySchedulerMetadata.create_table(wait=True)
        data = {}
        with open('tests/samples/currency_rates_sample_1.json') as f:
            data = json.load(f)
        currency_data = []
        date = date_helper.get_expected_cet_currency_date()
        previous_date = date_helper.get_expected_cet_currency_date(date)
        for currency in data:
            change = random.randint(-9, 49)
            currency_data.append(CurrencyRates(
                currency_name=currency, currency_value=data[currency]+change, date=date))
            currency_data.append(CurrencyRates(
                currency_name=currency, currency_value=data[currency], date=previous_date))
        DbClient().batch_write_db(CurrencyRates, currency_data)
        meta = {
            "expected_date": date,
            "parsed_date": date
        }
        CurrencySchedulerMetadata(
            config_key=constants.LATEST_SCHEDULER_EXECUTION, config_value=meta).save()
        meta = {
            "created_at": time.time(),
            "no_of_executions": 1,
            "status": "SUCCESS"
        }
        CurrencySchedulerMetadata(
            config_key=constants.SCHEDULER_EXECUTION_META_PREFIX+date, config_value=meta).save()
        yield CurrencySchedulerMetadata.Meta.table_name


@pytest.fixture
def setup_table_case_2(aws_credentials):
    # Empty table data
    with moto.mock_aws():
        if not CurrencyRates.exists():
            CurrencyRates.create_table(wait=True)
        if not CurrencySchedulerMetadata.exists():
            CurrencySchedulerMetadata.create_table(wait=True)
        yield CurrencySchedulerMetadata.Meta.table_name


@pytest.fixture
def setup_table_case_3(aws_credentials):
    # Store current and previous currency records based on previous date
    with moto.mock_aws():
        if not CurrencyRates.exists():
            CurrencyRates.create_table(wait=True)
        if not CurrencySchedulerMetadata.exists():
            CurrencySchedulerMetadata.create_table(wait=True)
        data = {}
        with open('tests/samples/currency_rates_sample_1.json') as f:
            data = json.load(f)
        currency_data = []
        date = date_helper.get_expected_cet_currency_date()
        date = date_helper.get_expected_cet_currency_date(date)
        previous_date = date_helper.get_expected_cet_currency_date(date)
        for currency in data:
            change = random.randint(-10, 50)
            currency_data.append(CurrencyRates(
                currency_name=currency, currency_value=data[currency]+change, date=date))
            currency_data.append(CurrencyRates(
                currency_name=currency, currency_value=data[currency], date=previous_date))
        DbClient().batch_write_db(CurrencyRates, currency_data)
        meta = {
            "expected_date": date,
            "parsed_date": date
        }
        CurrencySchedulerMetadata(
            config_key=constants.LATEST_SCHEDULER_EXECUTION, config_value=meta).save()
        meta = {
            "created_at": time.time(),
            "no_of_executions": 1,
            "status": "SUCCESS"
        }
        CurrencySchedulerMetadata(
            config_key=constants.SCHEDULER_EXECUTION_META_PREFIX+date, config_value=meta).save()
        yield CurrencySchedulerMetadata.Meta.table_name
