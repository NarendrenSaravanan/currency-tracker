# import unzip_requirements
import sys
import traceback
import json
from src.services.currency_scheduler_service import CurrencySchedulerService
from src.logger.logger import logger


def lambda_handler(event, context):
    """
    The input event is a SQS/Event Scheduler of Cloudwatch
    """
    def good_request(lambda_response):
        logger.info("GOOD Request")
        body = {
            "status": "success",
            "output": lambda_response
        }
        logger.info(body)
        response = {"statusCode": 200, "body": json.dumps(body)}

        return response

    def bad_request():
        # Throwing an error so that Destination is considered as failiure
        logger.error("Error Occurred - Scheduler")
        sys.exit("Error Occurred - Scheduler")

    lambda_response = None

    try:
        logger.info(event)
        if 'detail-type' in event and event['detail-type'] == 'Scheduled Event':
            lambda_response = CurrencySchedulerService().invoke_scheduler()
        else:
            lambda_response = CurrencySchedulerService().execute_scheduler()
        logger.info(lambda_response)

    except Exception as e:
        logger.error(e)
        logger.error("TRACED ERROR: ")
        logger.error(traceback.format_exc())
        raise

    finally:
        if lambda_response:
            return good_request(lambda_response)
        else:
            return bad_request()
