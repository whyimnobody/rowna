from datetime import datetime, timedelta
from dateutil.parser import parse, ParserError

# MOTE: Below is unused, as the functionality is implemented through panads
def validate_date(date):
    """
    Ensures date is a valid date to be converted

    :param date: date in a dateutil-compatible format
    :type date: str
    :return validated_date: parsed date object
    :type validated_date: datetime.date
    """

    try:
        validated_date = parse(date).date()
    except ParserError as _:
        validated_date = ""

    return validated_date


# NOTE: Below is supremely silly. Exchanges should be cognisant of the date of
# the transaction itself, and also, not slamming the API. Felt gross writing it,
#  but it works, like a first, rough draft, that should never be used. Ever.
def get_exchange_rate(currency_from, currency_to):
    """
    Get a single exchange rate from the specified API
    :param currency_from: the currency to exchange from
    :type currency_from: str
    :param currency_to: the currency to exchange to
    :type currency_to: str

    :return rate: the rate at which the currencies are exchanged
    :type rate: float
    """

    import requests

    url = f"https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.{currency_from}.{currency_to}.SP00.A"

    response = requests.get(
        url,
        params={
            "format": "jsondata",
            "updatedAfter": (datetime.today().date() - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            ),
        },
    )

    try:
        rate = (
            response.json()
            .get("dataSets")[0]
            .get("series")
            .get("0:0:0:0:0")
            .get("observations")
            .get("0")[0]
        )
        if rate:
            return rate
    except:  # Bad exception handling, because the API is not particularly well understood (or documented)
        # TODO: Do better than just returning a 0. Either exclude the result,
        # should the rate not be available or raise an exception if the response
        # is that critical
        return 0


def get_multiple_currency_exchange_rates(queryset, currency_to):
    """
    Retrieve all the currencies required and convert from the item currencies to
    the requested currency
    :param queryset: A model queryset containing the transactions to alter
    :param currency: The currency requested for the exchange
    :return exchanged
    """

    currencies = set([obj.amount_currency for obj in queryset])
    exchange_rates = dict()
    for currency in currencies:
        exchange_rates[currency] = get_exchange_rate(currency, currency_to)

    # exchanged_rates = {currency_code: rate for get_exchange_rate()}
