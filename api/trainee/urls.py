from django.urls import path, include

from api.trainee.views import TraineeProfileView, UpdateTraineeView, ApproveTraineeView, RevokeTraineeView, TraineeProctorshipView


app_name = "trainee"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
	path('add-trainee', TraineeProfileView.as_view(),  name='train-profile'),
	path('add-trainee/<int:pk>', TraineeProfileView.as_view(),  name='trainee-profile'),

	path('update/', UpdateTraineeView.as_view(), name = 'trainee-profile-update'),
	path('update/<int:pk>', UpdateTraineeView.as_view(), name = 'trainee-profile-update'),
	
	path('active-trainee/<int:pk>', ApproveTraineeView.as_view(), name = 'active-trainee'),

	path('revoke-trainee/<int:pk>', RevokeTraineeView.as_view(), name = 'revoke-trainee'),

	path('proctorship-trainee', TraineeProctorshipView.as_view(), name='proctorship-trainee')
	]