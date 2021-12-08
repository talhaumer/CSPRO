from django.urls import path, include

from api.proctorship.views import ProctorshipView, ConstantDataView, ProctorshipListingApiView, \
	ProctorshipForSecondImplant

app_name = "proctorship"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
	path('add-proctorship', ProctorshipView.as_view(),  name='proctorship'),

	path('add-proctorship/<int:pk>', ProctorshipView.as_view(),  name='proctorship-get-id'),

	path('get-constant-data', ConstantDataView.as_view(), name='get-constant-data'),

	path('proctorship-listing', ProctorshipListingApiView.as_view(), name = 'proctorship-listing'),

	path('proctorship-second-implant', ProctorshipForSecondImplant.as_view(), name = "Drop down activites for second implant")
	]