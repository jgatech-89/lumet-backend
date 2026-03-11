from django.urls import path
from .views import ChoicesAPIView

urlpatterns = [
    path('choices/', ChoicesAPIView.as_view(), name='choices-list'),
]
