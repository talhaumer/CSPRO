from django.urls import path, include

from api.newmics.views import PreceptorshipStatusView, NewMicsView, AddMicsProctorshipView, MicsTraineeProfileView, \
	TraineeMicsView, RevokeMicsTraineeView, ApproveMicsTraineeView, MicsProctorshipStatusView, NewMicsCourseListing, \
	RecentScheduleActivitiesView, MicsHospitalZoneView, MicsProctorsOfCOEView, MICSHospitalView, \
	MicsPrecevalFeedbackView, MicsTraineeFeedbackView, MicsInvoiceView, MicsAttendanceFormView, MicsCertificateFormView

app_name = "new-mics"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
	path('add-new-mics', NewMicsView.as_view(),  name='new-mics'),

	path('add-new-mics/<int:pk>', NewMicsView.as_view(),  name='new-mics'),

	path('add-new-mics-proctorship/<int:pk>', AddMicsProctorshipView.as_view(),  name='new-mics-proctorship'),

	path('add-new-mics-trainee', MicsTraineeProfileView.as_view(),  name='new-mics-trainee'),

	path('add-new-mics-trainee/<int:pk>', MicsTraineeProfileView.as_view(),  name='new-mics-trainee'),

	path('active-mics-trainee/<int:pk>', ApproveMicsTraineeView.as_view(), name = 'active-trainee'),

	path('revoke-mics-trainee/<int:pk>', RevokeMicsTraineeView.as_view(), name = 'revoke-trainee'),

	path('get-mics-trainee', TraineeMicsView.as_view(), name='get-mics-trainee'),

	path('add-mics-perceptorship-status/<int:pk>', PreceptorshipStatusView.as_view(), name = 'add mics perceptorship status'),

	path('add-mics-proctorship-status/<int:pk>', MicsProctorshipStatusView.as_view(), name = 'add mics proctorship status'),

	path('mics-lsiting', NewMicsCourseListing.as_view(), name = 'add mics proctorship status'),

	path('hospital', MICSHospitalView.as_view(), name = 'add mics proctorship status'),

	path('recent-listing', RecentScheduleActivitiesView.as_view(), name = 'add mics proctorship status'),

	path('coe', MicsHospitalZoneView.as_view(), name = 'add mics proctorship status'),

	path('coe/proctors', MicsProctorsOfCOEView.as_view(), name = 'add mics proctorship status'),

	path('<name>-preceval-feedback', MicsPrecevalFeedbackView.as_view(), name='proctorship-feedback'),
	path('<name>-preceval-feedback/<int:pk>', MicsPrecevalFeedbackView.as_view(), name='proctorship-feedback'),

	path('<name>-trainee-feedback', MicsTraineeFeedbackView.as_view(), name='trainee-feedback'),
	path('<name>-trainee-feedback/<int:pk>', MicsTraineeFeedbackView.as_view(), name='trainee-feedback'),
	# path('revoke-perceptership', MicsProctorsOfCOEView.as_view(), name = 'add mics proctorship status'),

	path('<name>-invoice-data', MicsInvoiceView.as_view(), name='invoice-data'),

	path('<name>-invoice-data/<int:pk>', MicsInvoiceView.as_view(), name='invoice-data'),

	path('<name>-attendance-form-data', MicsAttendanceFormView.as_view(), name='attendance-form-data'),

	path('<name>-attendance-form-data/<int:pk>', MicsAttendanceFormView.as_view(), name='attendance-form-data'),

	path('<name>-certificate-form-data', MicsCertificateFormView.as_view(), name='attendance-form-data'),

	path('<name>-certificare-form-data/<int:pk>', MicsCertificateFormView.as_view(), name='attendance-form-data'),

	]