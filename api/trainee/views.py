from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from api.views import BaseAPIView
from api.trainee.models import TraineeProfile
from api.trainee.serializers import TrainSerializer, TraineeUpdateSerializer, TrainProctorshipSerializer


# Create your views here.
'''
add and get tainees for proctorship
'''
class TraineeProfileView(BaseAPIView):
	permission_classes = (AllowAny,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				trainee = TraineeProfile.objects.get(pk=pk, revoke = False)
				serializer = TrainSerializer(trainee)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			trainees = TraineeProfile.objects.filter(revoke = False)
			serializer = TrainSerializer(trainees, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = trainees.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Trainee Profile matches the given query.")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="TraineeProfile doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		try:
			data = request.data
			serializer = TrainSerializer(data = data)
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='trainee is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except TraineeProfile.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="trainee doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


'''
update traineee profile for proctorship
'''
class UpdateTraineeView(BaseAPIView):
	permission_classes = (AllowAny,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				trainee = TraineeProfile.objects.get(pk=pk)
				serializer = TraineeUpdateSerializer(trainee)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			trainees = TraineeProfile.objects.filter(revoke = False)
			serializer = TrainSerializer(trainees, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = trainees.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No trainee matches the given query.")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Profile doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

	def put(self, request, pk=None):
		try:
			id = pk
			saved_trainee= TraineeProfile.objects.get(id= id)
			data = request.data
			serializer = TraineeUpdateSerializer(instance=saved_trainee, data=data, partial=True)
			if serializer.is_valid():
				trainee_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Trainee Profile is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Trainee Profile matches the given query.")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Profile doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


'''
Approve traineee for proctorship
'''
class ApproveTraineeView(BaseAPIView):
	permission_classes = (AllowAny,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				trainee = TraineeProfile.objects.get(id=pk)
				trainee.status = True
				trainee.save()
				return self.send_response(description= "trainee is activate successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="User doesn't found")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="User doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)

'''
Revoke traineee for proctorship
'''
class RevokeTraineeView(BaseAPIView):
	permission_classes = (AllowAny,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				trainee = TraineeProfile.objects.get(id=pk)
				trainee.revoke = True
				trainee.save()
				return self.send_response(description= "trainee is is revoked successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Profile doesn't found")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Profile doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)


'''
traineee of proctorship by activity id
'''
class TraineeProctorshipView(BaseAPIView):
	permission_classes = (AllowAny,)
	def get(self, request, pk=None):
		try:
			proctorship_id = request.query_params.get('activity_id', '')
			if proctorship_id:
				trainees = TraineeProfile.objects.filter(proctorship__id = proctorship_id,)
				serializer = TrainProctorshipSerializer(trainees, many=True)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = len(trainees))
			return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[], code='422',description='Enter valid Proctorship Id', log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Trainee matches the given query.")
		except TraineeProfile.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="TraineeProfile doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)