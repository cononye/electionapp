from django.urls import path
from .views import SubmitResultView

urlpatterns = [
    path('submit/', SubmitResultView.as_view(), name='submit-result'),
]
