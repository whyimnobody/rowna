from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField, Money


class TransactionTypeOptions(models.TextChoices):
    """Transaction type choices for transaction type field"""

    PURCHASE = "purchase"
    SALE = "sale"


class TransactionsFile(models.Model):
    """Model for file of transactions"""

    # NOTE: Could also be stored as a TextField but prefer FileField for
    # possible other file types
    file = models.FileField()

    def process_file(self):
        """Process the given file, into a record stored in the model"""

        from fuzzywuzzy.process import extractOne
        import pandas as pd

        csv = pd.read_csv(self.file, parse_dates=["Date"])
        # Validate date column, dropping bad dates
        csv["Date"] = pd.to_datetime(csv["Date"], errors="coerce")
        # Drop dates we aren't interested in
        # TODO: Replace with settings value or DB value or range
        csv = csv[csv["Date"].dt.year == 2020]
        # Validate net amount column, replacing bad values with NaN
        csv["Net"] = pd.to_numeric(csv["Net"], errors="coerce")
        # Validate vat amount column, replacing bad values with NaN
        csv["VAT"] = pd.to_numeric(csv["VAT"], errors="coerce")
        # Drop rows with NaN values in either Net or VAT columns
        csv = csv.dropna(subset=["Net", "VAT"])

        # NOTE: Bulk create seems to be the best single query approach within
        # framework and without circumventing its "checks and balances"
        # Transaction.objects.bulk_create(
        #     [
        #         Transaction(
        #             date=row["Date"],
        #             country=Country.get_country_code(row["Country"]),
        #             type=extractOne(
        #                 row["Purchase/Sale"].strip().lower(),
        #                 TransactionTypeOptions.values,
        #                 score_cutoff=60,
        #             ),
        #             currency=Money(row["Net"], row["Currency"]),
        #             vat=Money(row["VAT"], row["Currency"]),
        #         )
        #         for row in csv.iterrows()
        #     ]
        # )
        # Below is a shotgun approach which could be optimised, but it works
        for _, row in csv.iterrows():
            Transaction.objects.create(
                date=row["Date"],
                country=Country.get_country_code(row["Country"]),
                type=extractOne(
                    row["Purchase/Sale"].strip().lower(),
                    TransactionTypeOptions.values,
                    score_cutoff=60,
                )[0],
                amount=Money(row["Net"], row["Currency"]),
                vat=Money(row["VAT"], row["Currency"]),
                src_id=self.id,
            )


class Transaction(models.Model):
    """Model for individual transactions"""

    date = models.DateField()
    country = CountryField()
    type = models.CharField(choices=TransactionTypeOptions.choices, max_length=16)
    # currency = models.CharField(max_length=3)  # NOTE: Replaced by field below
    # amount = models.IntegerField()  # NOTE: Replaced by field below
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency=None)
    vat = MoneyField(max_digits=19, decimal_places=2, default_currency=None)
    src = models.ForeignKey(TransactionsFile, on_delete=models.CASCADE)

    # def __str__(self):
    #     """Return a string representation of the transaction"""

    #     return f"{self.type.title()} on {self.date.strftime('%Y-%d-%m')} for {self.amount_currency}{self.amount}"


class Country(models.Model):
    """Model for additional or non-standard countries"""

    name = models.CharField(max_length=128)  # Expected name from sheet
    code = models.CharField(max_length=3)  # Country code in ISO-3166-1 format
    bad_code = models.CharField(max_length=8, null=True, blank=True)

    @classmethod
    def get_country_code(cls, query):
        """
        Retrieve 'official' code from DB for known bad code or non-standard
        country name"""

        from django_countries import countries

        if (len(query) == 2 or len(query) == 3) and (
            country := countries.alpha2(query)
        ):
            return country
        elif country := countries.by_name(query):
            return country
        else:
            qs = cls.objects.filter(
                models.Q(name__iexact=query)
                | models.Q(bad_code__iexact=query)
                | models.Q(code__iexact=query)
            )
            return qs[0].code if qs else query
