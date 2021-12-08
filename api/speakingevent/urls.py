from django.urls import path, include

from api.speakingevent.views import SpeakingEventView, SpeakerView, SpeakingEventUpdateView, StatusSpeakingView, \
	UploadAgenda, AddSiginedLetterView, SpeakingEventListing, RevokeSpeakerView, ConfirmSpeakerView, \
	FeedBackSpeakingEvent, AttendanceFormSpeakingEventView, CongosIdViewForm, UploadMeetingDocs, \
	SpeakingEventWithOutAuthView, SpeakerUnknownView

app_name = "speakingevent"

# app_name will help us do a reverse look-up latter.
urlpatterns = [

	path('add-speaking-event', SpeakingEventView.as_view(),  name='proctors'),
	path('add-speaking-event/<int:pk>', SpeakingEventView.as_view(),  name='proctors'),

	path('add-speaker', SpeakerView.as_view(), name = 'add-speaker'),
	path('add-speaker/<int:pk>', SpeakerView.as_view(), name = 'add-speaker'),

	path('update-speaking-event', SpeakingEventUpdateView.as_view(), name = 'update event'),

	path('add-status', StatusSpeakingView.as_view(), name='status'),

	# path('add-signed-letter', AddSiginedLetterView.as_view(), name='add-signed-letter'),
	path('add-signed-letter/<int:pk>', AddSiginedLetterView.as_view(), name='add-signed-letter'),


	path('add-update-agenda/<int:pk>', UploadAgenda.as_view(), name='update-add-agenda'),

	path('speaking-event-listing', SpeakingEventListing.as_view(), name = 'speaking-event-listing'),

	path('confirm-speaker/<int:pk>', ConfirmSpeakerView.as_view(), name = 'confirm-speakers'),

	path('revoke-speaker/<int:pk>', RevokeSpeakerView.as_view(), name = 'confirm-speakers'),

	path('add-speaking-event-feedback', FeedBackSpeakingEvent.as_view(), name = 'add-speaking-event-feedback'),

	path('add-speaking-event-feedback/<int:pk>', FeedBackSpeakingEvent.as_view(), name = 'add-speaking-event-feedback'),

	path('speakingevent-attendance-form-data', AttendanceFormSpeakingEventView.as_view(),
		 name='attendance-form-data'),

	path('speakingevent-attendance-form-data/<int:pk>', AttendanceFormSpeakingEventView.as_view(),
		 name='attendance-form-data'),

	path('add-speaking-event-cognos-id', CongosIdViewForm.as_view(), name ='cognos_id'),
	path('add-speaking-event-cognos-id/<int:pk>', CongosIdViewForm.as_view(), name ='cognos_id'),


	path("add-meeting-docs/<int:pk>", UploadMeetingDocs.as_view(), name = "upload meeting docs"),

	path("publicaly-get-speaking-event", SpeakingEventWithOutAuthView.as_view(), name = "publicaly-get-speaking-event"),
	path("publicaly-get-speaking-event/<int:pk>", SpeakingEventWithOutAuthView.as_view(), name = "publicaly-get-speaking-event"),

	path("publicaly-get-speaker", SpeakerUnknownView.as_view(), name = "publicaly-get-speaker"),
	path("publicaly-get-speaker/<int:pk>", SpeakerUnknownView.as_view(), name = "publicaly-get-speaker")

]