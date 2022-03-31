from djmoney.money import Money
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet


from .serializers import TransactionFileSerializer, TransactionSerializer
from ..models import Transaction
from ..utils import validate_date


class TransactionViewSet(ListModelMixin, GenericViewSet):
    parser_classes = [MultiPartParser]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset
        # Query params
        country = self.request.GET.get("country")
        date = self.request.GET.get("date")
        currency = self.request.GET.get("currency")
        # Raise an exception if required params aren't provided
        if not country and not date:
            raise exceptions.ParseError(
                "Country (ISO 3166) and date (YYYY/MM/DD) required"
            )
        # Filter by params as provided
        if country:
            queryset = queryset.filter(country=country)
        if date := validate_date(date):
            queryset = queryset.filter(date=date)
        # TODO: Query API for exchange per transaction
        # The functionality is there, but I'm nervous
        # if currency:
        # queryset = queryset.filter(amount_currency=currency)

        return queryset

    @action(detail=False, methods=("post",))
    def upload(self, request):
        print(request.data)
        serializer = TransactionFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# NOTE: Below not used in favour of class-based viewsets, for a cleaner and more
#  typical URL structure and less boilerplate or re-doing
# class ProcessFile(APIView):
#     """
#     An example of what a plain APIView may look like
#     """

#     def post(self, request, *args, **kwargs):
#         """
#         Upload a CSV of transactions for processing
#         :param request: Contains file to be processed
#         """

#         new_file = TransactionsFile.objects.create(file=request.FILES['file'])
#         new_file.process_file()

#         return Response(status=status.HTTP_201_CREATED)
