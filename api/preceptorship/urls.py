from django.urls import path, include

from api.preceptorship.views import PreceptorshipView, PreceptorshipStatusView, PreceptorshipFeedBackView, \
	ApprovePreceptorShipTraineeView, RevokeTraineePreceptorshipProfileView, TraineePreceptorshipProfileView, \
	TraineePreceptorshipProfileAddView, PreceptorshipLocalGlobalView, PDateUpdateView, PreceptorshipListingApiView, \
	InvoicePerceptorshipView, AttendanceFormPerceptorshipView, StatusPTestingView

app_name = "preceptorship"




# app_name will help us do a reverse look-up latter.
urlpatterns = [
	path('', PreceptorshipView.as_view(),  name='preceptorship'),
	path('<int:pk>', PreceptorshipView.as_view(),  name='preceptorship-get-id'),

	path('get-status', PreceptorshipStatusView.as_view(), name ='get-status' ),

	path('preceptorship-feedback', PreceptorshipFeedBackView.as_view(), name ='preceptorship-feedback' ),
	path('preceptorship-feedback/<int:pk>', PreceptorshipFeedBackView.as_view(), name ='preceptorship-feedback' ),

	path('preceptorship-approve-trainee/<int:pk>', ApprovePreceptorShipTraineeView.as_view(), name ='preceptorship-feedback' ),

	path('preceptorship-revoke-trainee/<int:pk>', RevokeTraineePreceptorshipProfileView.as_view(), name ='preceptorship-feedback' ),

	path('preceptorship-trainee-view', TraineePreceptorshipProfileView.as_view(), name ='preceptorship-feedback' ),

	path('preceptorship-add-trainee', TraineePreceptorshipProfileAddView.as_view(), name ='preceptorship-feedback' ),
	path('preceptorship-add-trainee/<int:pk>', TraineePreceptorshipProfileAddView.as_view(), name ='preceptorship-feedback' ),

	path('local-global-activity', PreceptorshipLocalGlobalView.as_view(), name='local-global-activity'),

	path('preceptor-updat-date/<int:pk>', PDateUpdateView.as_view(), name = 'updat-date'),

	path('preceptorship-listing', PreceptorshipListingApiView.as_view(),name = 'preceptorship-listing'),

	path('perceptorship-invoice-data', InvoicePerceptorshipView.as_view(),  name='invoice-data'),

	path('perceptorship-invoice-data/<int:pk>', InvoicePerceptorshipView.as_view(),  name='invoice-data'),

	path('perceptorship-attendance-form-data', AttendanceFormPerceptorshipView.as_view(),  name='attendance-form-data'),

	path('perceptorship-attendance-form-data/<int:pk>', AttendanceFormPerceptorshipView.as_view(),  name='attendance-form-data'),

	path('perceptorship-status-testing', StatusPTestingView.as_view(),
		 name='perceptorship-status-testing'),

]
