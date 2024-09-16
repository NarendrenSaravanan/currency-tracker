import boto3


class SqsClient:
    def __init__(self):
        self.__client = boto3.client('sqs')

    def add_event(self, queue_url, message):
        response = self.__client.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            DelaySeconds=123)
        return response
