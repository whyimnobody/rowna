from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from transactions.api.views import TransactionViewSet

# https://www.django-rest-framework.org/api-guide/routers/#api-guide
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("transactions", TransactionViewSet)

app_name = "api"
urlpatterns = router.urls
