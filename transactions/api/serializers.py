from rest_framework import serializers

from ..models import Transaction, TransactionsFile


class TransactionFileSerializer(serializers.ModelSerializer):
    """Serializer for transaction file uploaded in CSV format"""

    class Meta:
        model = TransactionsFile
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions as stored"""

    class Meta:
        model = Transaction
        exclude = ("id",)
