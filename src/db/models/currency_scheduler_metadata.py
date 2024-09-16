from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute


class CurrencySchedulerMetadata(Model):
    class Meta:
        table_name = "currency-scheduler-metadata"
    config_key = UnicodeAttribute(hash_key=True)
    config_value = MapAttribute()


'''
Sample Data:

{
 "config_key": "latest_scheduler_execution",
 "config_value": {
  "expected_date": "2024-09-14",
  "parsed_date": "2024-09-13"
 }
}

{
 "config_key": "scheduler_meta_2024-09-14",
 "config_value": {
  "created_at": 1726421253.241872,
  "no_of_executions": 1,
  "status": "SUCCESS"
 }
}
'''
