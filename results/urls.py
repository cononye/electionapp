from django.urls import path
from .views import SubmitResultView, PublicDashboardView, PartyDashboardView

urlpatterns = [
    path('submit/', SubmitResultView.as_view(), name='submit-result'),
    path('dashboard/public/', PublicDashboardView.as_view(), name='public-dashboard'),
    path('dashboard/party/', PartyDashboardView.as_view(), name='party-dashboard'),
]
