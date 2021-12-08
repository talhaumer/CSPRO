from django.urls import path, include
from api.status.views import StatusView, AlternativePorposalView, ConstantStatusDataView, DateUpdateView, StatusTestingView

app_name = "status"

urlpatterns = [
    path('add-status', StatusView.as_view(), name='status'),
    path('add-alternatives', AlternativePorposalView.as_view(), name = 'add-alternatives'),
    path('status-constant-data', ConstantStatusDataView.as_view(), name = 'status-constant-data'),
    path('updat-date/<int:pk>', DateUpdateView.as_view(), name = 'updat-date'),
    path('proctorship-status-testing', StatusTestingView.as_view(), name = 'proctorship-status-testing')
]

