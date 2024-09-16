from src.db.models.currency_rates import CurrencyRates
from src.db.models.currency_scheduler_metadata import CurrencySchedulerMetadata
from src.db.client import DbClient
from src.common import constants
from datetime import datetime, timedelta
from src.logger.logger import logger


class CurrencyApiService:
    def __init__(self) -> None:
        self.__db_client = DbClient()

    def __fetch_latest_currency_dates(self):
        recent_date = CurrencySchedulerMetadata.get(
            hash_key=constants.LATEST_SCHEDULER_EXECUTION).config_value["parsed_date"]
        previous_date_dt = datetime.strptime(
            recent_date, constants.DATE_TIME_FORMAT)-timedelta(days=1)
        previous_date = datetime.strftime(
            previous_date_dt, constants.DATE_TIME_FORMAT)
        return previous_date, recent_date

    def __fetch_db_currency_records(self, previous_date, recent_date):
        previous_records = self.__db_client.query_with_pk(
            CurrencyRates, previous_date)
        print(previous_records)
        previous_records_map = {}
        for record in previous_records:
            previous_records_map[record.currency_name] = record.currency_value
        recent_records = self.__db_client.query_with_pk(
            CurrencyRates, recent_date)
        final_res = {}
        for record in recent_records:
            res = {"value": record.currency_value}
            if record.currency_name in previous_records_map:
                res["change"] = record.currency_value - \
                    previous_records_map[record.currency_name]
            final_res[record.currency_name] = res
        return final_res

    def fetch_currency_rates(self):
        previous_date, recent_date = self.__fetch_latest_currency_dates()
        final_res = self.__fetch_db_currency_records(
            previous_date, recent_date)
        return {"date": recent_date, "currency_rates": final_res}
