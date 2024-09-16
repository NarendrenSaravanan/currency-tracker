# import unzip_requirements
import traceback
import json
import sys
from src.services.currency_api_service import CurrencyApiService
from src.logger.logger import logger


def lambda_handler(event, context):
    """
    The input event is a API event
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
        print("BAD Request")
        body = {"message": "Bad Request"}
        response = {"statusCode": 400, "body": json.dumps(body)}

        return response
    lambda_response = None

    try:
        logger.info(event)
        lambda_response = CurrencyApiService().fetch_currency_rates()
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
