import os
import traceback
from src.helpers.currency_rate_scraper import CurrencyRateScraper
from src.db.models.currency_rates import CurrencyRates
from src.db.models.currency_scheduler_metadata import CurrencySchedulerMetadata
from src.db.client import DbClient
from src.aws.sqs.client import SqsClient
from src.common import constants
from src.common.enum import SchedluerExecutionState
from datetime import datetime
from src.logger.logger import logger
from src.helpers import date_helper


class CurrencySchedulerService:
    def __init__(self) -> None:
        self.__currency_rate_scraper = CurrencyRateScraper()
        self.__db_client = DbClient()
        self.__sqs_client = SqsClient()
        self.__ignore_expected_date_check = os.environ["IGNORE_EXPECTED_DATE_CHECK"]
        self.__currency_tracking_sqs_url = os.environ["CURRENCY_TRACKING_SQS_URL"]

    def __fetch_recent_scheduler_executions(self):
        try:
            recent_date = CurrencySchedulerMetadata.get(
                hash_key=constants.LATEST_SCHEDULER_EXECUTION).config_value["parsed_date"]
            recent_date_dt = datetime.strptime(
                recent_date, constants.DATE_TIME_FORMAT)
        except CurrencySchedulerMetadata.DoesNotExist:
            recent_date_dt = datetime.min
        return recent_date_dt

    def __update_scheduler_metadata(self, expected_date, status, exception):
        hash_key = constants.SCHEDULER_EXECUTION_META_PREFIX+expected_date
        try:
            model = CurrencySchedulerMetadata.get(
                hash_key=hash_key)
        except CurrencySchedulerMetadata.DoesNotExist:
            model = CurrencySchedulerMetadata(
                config_key=hash_key, config_value={})
        result = model.config_value
        logger.info('scheduler_metadata: {}'.format(result))
        if "status" in result and result["status"] == SchedluerExecutionState.SUCCESS:
            return
        result["status"] = status
        timestamp = datetime.now().timestamp()
        if "created_at" not in result:
            result["created_at"] = timestamp
        else:
            result["updated_at"] = timestamp
        if "no_of_executions" not in result:
            result["no_of_executions"] = 0
        result["no_of_executions"] = result["no_of_executions"] + 1
        if exception:
            result["exception"] = exception
        model.config_value = result
        model.save()
        logger.info('model: {}'.format(model))
        logger.info('scheduler_metadata: {}'.format(result))

    def execute_scheduler(self):
        expected_date = date_helper.get_expected_cet_currency_date()
        status, exception = SchedluerExecutionState.IN_PROGRESS, ""
        try:
            parsed_date_dt, currency_map = self.__currency_rate_scraper.execute()
            last_executed_dt = self.__fetch_recent_scheduler_executions()
            logger.info("last_executed_dt: {}".format(last_executed_dt))
            logger.info("parsed_date_dt: {}".format(parsed_date_dt))
            if parsed_date_dt <= last_executed_dt:
                if parsed_date_dt == last_executed_dt:
                    logger.info(constants.SKIP_PROCESSING_MSG)
                    return constants.SKIP_PROCESSING_MSG
                raise Exception("Currency Date not available yet: parsed_date_dt # {} last_executed_dt # {}".format(
                    parsed_date_dt, last_executed_dt))
            parsed_date = parsed_date_dt.strftime(constants.DATE_TIME_FORMAT)
            if not (self.__ignore_expected_date_check == "true") and parsed_date != expected_date:
                raise Exception("Expected Currency Date not available yet: expected_date # {} parsed_date # {}".format(
                    expected_date, parsed_date))
            model_items = [CurrencyRates(
                currency_name=name, currency_value=float(currency_map[name]), date=parsed_date) for name in currency_map]
            logger.info(model_items)
            self.__db_client.batch_write_db(CurrencyRates, model_items)
            status = SchedluerExecutionState.SUCCESS
            CurrencySchedulerMetadata(
                config_key=constants.LATEST_SCHEDULER_EXECUTION, config_value={"expected_date": expected_date, "parsed_date": parsed_date}).save()
        except Exception as err:
            status = SchedluerExecutionState.FAILED
            exception = str(err)
            logger.error("Exception occured: {}".format(exception))
            logger.error(traceback.format_exc())
            raise
        finally:
            self.__update_scheduler_metadata(expected_date, status, exception)
            return status

    def invoke_scheduler(self):
        parsed_date_dt = self.__currency_rate_scraper.parse_date_from_site()
        last_executed_dt = self.__fetch_recent_scheduler_executions()
        if parsed_date_dt == last_executed_dt:
            logger.info(constants.SKIP_PROCESSING_MSG)
            return constants.SKIP_PROCESSING_MSG
        self.__sqs_client.add_event(
            self.__currency_tracking_sqs_url, "invoke scheduler")
        return constants.INVOKED_SCHEDULER_MSG
