from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute


class CurrencyRates(Model):
    class Meta:
        table_name = "currency-rates"
    currency_name = UnicodeAttribute(range_key=True)
    date = UnicodeAttribute(hash_key=True)
    currency_value = NumberAttribute()


'''
Sample Data:

{
 "date": "2024-09-12",
 "currency_name": "AUD",
 "currency_value": 2
}

{
 "date": "2024-09-13",
 "currency_name": "AUD",
 "currency_value": 1.6542
}

{
 "date": "2024-09-12",
 "currency_name": "BGN",
 "currency_value": 2.5
}

{
 "date": "2024-09-13",
 "currency_name": "BGN",
 "currency_value": 1.9558
}
'''
