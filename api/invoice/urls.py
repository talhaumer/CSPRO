from django.urls import path, include

from api.invoice.views import InvoiceView, AttendanceFormView


app_name = "invoice"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
	path('invoice-data', InvoiceView.as_view(),  name='invoice-data'),

	path('invoice-data/<int:pk>', InvoiceView.as_view(),  name='invoice-data'),

	path('attendance-form-data', AttendanceFormView.as_view(),  name='attendance-form-data'),

	path('attendance-form-data/<int:pk>', AttendanceFormView.as_view(),  name='attendance-form-data'),
]