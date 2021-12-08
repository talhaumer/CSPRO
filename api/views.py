from api.serializers import HospitalViewSerializer, HospitalNameSerializer, HospitalUpdateSerializer, \
	AreaOfExpertiesSerializer, ApproachSerializer, ProductsSerializer, ProductsViewSerializer, HospitalSerializer, \
	HcpRoleSerializer, LanguagesSerializer, SolutionSerializer, AudienceSerializer, RegionSerializer, EventSerializer, \
	SpecialitySerializer
from api.models import query_hospital_by_args, Products, Approach, AreaOfExperties, Hospital, Hcp_role, Languages, \
	Solution, Audience, Region, EventType, Speciality
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import is_server_error
from cspro.settings import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from requests.auth import HTTPBasicAuth 
import requests 
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin, IsGetOrIsAuthenticated, \
	IsGetOAuthenticatedSuperAdminLocalAdminSalesManager, IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet, \
	IsPostOAuthenticatedSuperAdminUpdate, IsOauthAuthenticated
from django.db.models import Q
from api.pagination import CustomPagination
import operator

from cspro.utilities.convert_boolean import boolean


class BaseAPIView(APIView):
	"""
	Base class for API views.
	"""
	authentication_classes = ()
	permission_classes = (AllowAny,)


	def send_response(self,success=False, code='', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, payload={}, description='',	exception=None,count = 0,log_description = ""):
		"""
		Generates response.
		:param success: bool tells if call is successful or not.
		:param code: str status code.
		:param status_code: int HTTP status code.
		:param payload: list data generated for respective API call.
		:param description: str description.
		:param exception: str description.
		:rtype: dict.
		"""
		if not success and is_server_error(status_code):
			print(1)
			if settings.DEBUG:
				description = f'error message: {description}'
			else:
				description = 'Internal server error.'
		return Response(data={'success': success, 'code': code,'payload': payload,'description': description,'count': count},status=status_code)

	def send_data_response(self,success=False,code='',status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,payload={},description=''):
		"""
		Generates response for data tables.
		:param success: bool tells if call is successful or not.
		:param code: str status code.
		:param status_code: int HTTP status code.
		:param payload: list data generated for respective API call.
		:param description: str description.
		:rtype: dict.
		"""
		if not success and is_server_error(status_code):
			if settings.DEBUG:
				description = f'error message: {description}'
			else:
				description = 'Internal server error.'
		return Response(data={'data': {'success': success,'code': code,'payload': payload,'description': description}},status=status_code)

	@staticmethod
	def get_oauth_token(email='', password='', grant_type='password'):
		try:
			url = settings.AUTHORIZATION_SERVER_URL
			# url ='http://192.168.100.10:8000/api/oauth/token/'
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
			data = {
				'username': email,
				'password': password,
				'grant_type': grant_type
			}
			auth = HTTPBasicAuth(
				settings.OAUTH_CLIENT_ID,
				settings.OAUTH_CLIENT_SECRET
			)
			response = requests.post(
				url=url,
				headers=headers,
				data=data,
				auth=auth
			)
			if response.ok:
				json_response = response.json()
				return {
					'access_token': json_response.get('access_token', ''),
					'refresh_token': json_response.get('refresh_token', '')
				}
			else:
				return {'error': response.json().get('error')}
		except Exception as e:
			# fixme: Add logger to log this exception
			return {'exception': str(e)}

	@staticmethod
	def revoke_oauth_token(token):
		try:
			url = settings.REVOKE_TOKEN_URL
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
			data = {
				'token': token,
				'client_secret': settings.OAUTH_CLIENT_SECRET,
				'client_id': settings.OAUTH_CLIENT_ID
			}
			response = requests.post(
				url=url,
				headers=headers,
				data=data
			)
			if response.ok:
				return True
			else:
				return False
		except Exception:
			# fixme: Add logger to log this exception
			return False


# Create your views here.
class ProductView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				product = Products.objects.get(id=pk)
				serializer = ProductsViewSerializer(product)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			products = Products.objects.all()
			serializer = ProductsViewSerializer(products, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Products matches the given query.")
		except Products.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Product doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)
	

	def post(self, request):
		try:
			products = request.data
			print(products)
			serializer = ProductsSerializer(data=products)
			if serializer.is_valid():
				product_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Product is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Products.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Products doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_product = Products.objects.get(id=id)
			data = request.data
			serializer = ProductsSerializer(instance=saved_product, data=data, partial=True)
			if serializer.is_valid():
				product_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Products is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Products matches the given query.")
		except Products.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Products doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)




class HospitalGetView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				hospital = Hospital.objects.get(pk=pk)
				serializer = HospitalSerializer(hospital)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			hospitals = Hospital.objects.all()
			serializer = HospitalSerializer(hospitals, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

# Create your views here.
# add hospital view
class HospitalView(BaseAPIView):
	permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				hospital = Hospital.objects.get(pk=pk)
				serializer = HospitalSerializer(hospital)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			hospitals = Hospital.objects.all()
			serializer = HospitalSerializer(hospitals, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

	def post(self, request):
		try:
			data = request.data
			print(data)
			serializer = HospitalSerializer(data = data)
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Hospital is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hospital doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


# update hospotal
class HospitalUpdateView(BaseAPIView):
	permission_classes = (IsPostOAuthenticatedSuperAdminUpdate,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				hospital = Hospital.objects.get(pk=pk)
				# print(hospital.values_list('products__id'))
				serializer = HospitalUpdateSerializer(hospital)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			hospitals = Hospital.objects.all()
			serializer = HospitalUpdateSerializer(hospitals, many=True)
			print(serializer.data)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)
	
	def put(self, request, pk=None):
		try:
			id = pk
			saved_hospital = Hospital.objects.get(id= id)
			data = request.data
			serializer = HospitalUpdateSerializer(instance=saved_hospital, data=data, partial=True)
			if serializer.is_valid():
				hospital_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Hospital is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hospital doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

# hospital according to countries view
class HospitalCountryView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			country = request.query_params.get('country_id','')
			hospital = Hospital.objects.filter(hospital_id__country__id=country)
			serializer = HospitalNameSerializer(hospital, many = True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


# delete hospital view
class DeleteHospitalView(BaseAPIView):
	permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				hospital = Hospital.objects.get(id=pk)
				hospital.deleted = True
				print(hospital)
				return self.send_response(description= "Hospital is deleted successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't found")
		except Hospital.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hospital doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)



class HcpRoleView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				hcprole = Hcp_role.objects.get(pk=pk)
				serializer = HcpRoleSerializer(hcprole)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			hcproles = Hcp_role.objects.all()
			serializer = HcpRoleSerializer(hcproles, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hcp_role matches the given query.")
		except Hcp_role.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hcp_role doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		# pprint(request.data)
		try:
			serializer = HcpRoleSerializer( data = request.data)
			
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Hcp_role is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Hcp_role.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hcp_role doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_role= Hcp_role.objects.all(id= id)
			data = request.data
			serializer = HcpRoleSerializer(instance=saved_role, data=data, partial=True)
			if serializer.is_valid():
				role_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Hcp role is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No HCP ROLE matches the given query.")
		except Hcp_role.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hcp role doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)




#################################################################################
# get view of languages for dropdown
class LanguageView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				language = Languages.objects.get(pk=pk)
				serializer = LanguagesSerializer(language)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			languages = Languages.objects.all()
			serializer = LanguagesSerializer(languages, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Languages matches the given query.")
		except Languages.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Languages doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		# pprint(request.data)
		try:
			serializer = LanguagesSerializer( data = request.data)
			
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Languages is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Languages.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Languages doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_language= Languages.objects.get(id= id)
			data = request.data
			serializer = LanguagesSerializer(instance=saved_language, data=data, partial=True)
			if serializer.is_valid():
				language_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description=' Languages is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Languages matches the given query.")
		except Languages.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Languages doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

#################################################################################

class AudienceView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				audience = Audience.objects.get(id = pk)
				serializer = AudienceSerializer(audience)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			audience = Audience.objects.all()
			serializer = AudienceSerializer(audience, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Audience matches the given query.")
		except Audience.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Audience doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		# pprint(request.data)
		try:
			serializer = AudienceSerializer( data = request.data)
			
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Audience is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Audience.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Audience doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_audience= Audience.objects.get(id= id)
			data = request.data
			serializer = AudienceSerializer(instance=saved_audience, data=data, partial=True)
			if serializer.is_valid():
				audience_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Audience is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Audience matches the given query.")
		except Audience.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Audience doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


#################################################################################

class RegionView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				region = Region.objects.get(pk=pk)
				serializer = RegionSerializer(region)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			region = Region.objects.all()
			serializer = RegionSerializer(region, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Region matches the given query.")
		except Region.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Region doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		# pprint(request.data)
		try:
			serializer = RegionSerializer( data = request.data)
			
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Region is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Region.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Region doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_region= Region.objects.get( id= id)
			data = request.data
			serializer = RegionSerializer(instance=saved_region, data=data, partial=True)
			if serializer.is_valid():
				region_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Region is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Region matches the given query.")
		except Region.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Region doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

	def delete(self, request, pk=None):
		try:
			id = pk
			region = Region.objects.all( id = id)
			region.delete()
			return Response({"message": "Proctor with id `{}` has been deleted.".format(pk)},status=204)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Region matches the given query.")
		except Region.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hcp role doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

#################################################################################

class SolutionView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				solution = Solution.objects.get(pk=pk)
				serializer = SolutionSerializer(solution)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			solution = Solution.objects.all()
			serializer = SolutionSerializer(solution, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Solution matches the given query.")
		except Solution.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hcp_role doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


	def post(self, request):
		# pprint(request.data)
		try:
			serializer = SolutionSerializer( data = request.data)
			
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Proctor is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Solution.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Proctor doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_solution= Solution.objects.get(id= id)
			data = request.data
			serializer = SolutionSerializer(instance=saved_solution, data=data, partial=True)
			if serializer.is_valid():
				solution_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Hcp role is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Languages matches the given query.")
		except Solution.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hcp role doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

	def delete(self, request, pk=None):
		try:
			id = pk
			solution = Solution.objects.get(id = id)
			solution.delete()
			return Response({"message": "Proctor with id `{}` has been deleted.".format(pk)},status=204)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Languages matches the given query.")
		except Solution.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Hcp role doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

# get aread of experties
class AreaOfExpertiesView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				experties = AreaOfExperties.objects.get(pk=pk)
				serializer = AreaOfExpertiesSerializer(experties)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			experties = AreaOfExperties.objects.all()
			serializer = AreaOfExpertiesSerializer(experties, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No AreaOfExperties matches the given query.")
		except AreaOfExperties.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="AreaOfExperties doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


# Get appraoches for drop down
class ApproachView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			if pk is not None:
				approach = Approach.objects.get(pk=pk)
				serializer = ApproachSerializer(approach)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			approach = Approach.objects.all().distinct()
			serializer = ApproachSerializer(approach, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No AreaOfExperties matches the given query.")
		except Approach.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="AreaOfExperties doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)



class HospitalViewSet(viewsets.ModelViewSet, BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	queryset = Hospital.objects.all()
	serializer_class = HospitalSerializer

	def list(self, request, **kwargs):
		try:
			products = request.query_params.get('products_id', '')
			country =  request.query_params.get('country_id', '')
			is_it_preceptorship = request.query_params.get('is_it_preceptorship', '')
			qualified_for_news_mics_program = request.query_params.get('qualified_for_news_mics_program', '')
			
			IS_IT_PRECEPTORSHIP = {'Yes':True, 'No':False}

			query_object = Q()

			if country != '':
				query_object &= Q(hospital_id__country__id = country)

			if products != '':
				query_object = Q(products__id = products)

			if is_it_preceptorship != '':
				query_object &= Q(is_it_preceptorship = IS_IT_PRECEPTORSHIP[is_it_preceptorship])

			if qualified_for_news_mics_program != '':
				query_object &= Q(qualified_for_news_mics_program = IS_IT_PRECEPTORSHIP[qualified_for_news_mics_program])


			hospital = query_hospital_by_args(query_object, **request.query_params)
			
			serializer = HospitalSerializer(hospital['items'], many=True)
			print(serializer.data)
			
			result = dict()
			result['data'] = serializer.data
			result['draw'] = hospital['draw']
			result['recordsTotal'] = hospital['total']
			result['recordsFiltered'] = hospital['count']
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=result,code= '',description='Proctors Data Table ',log_description='')
		except Hospital.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Proctors doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("2nd", e)
			return self.send_response(code=f'500',description=e)




class HospiatlPaginationView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)

	def get(self, request, pk=None):
		try:
			column_name =request.query_params.get('column_name','hospital_name')
			rev = request.query_params.get('order','')
			search_value = request.query_params.get('search_value', None)
			# limit = int(request.query_params.get('limit', 10))
			# offset = int(request.query_params.get('offset', 0))
						
			hospitals = Hospital.objects.all()
			if search_value:
				hospitals = hospitals.filter(Q(hospital_name__icontains=search_value) )
											# Q(number_of_trainee__icontains=search_value) |
											# Q(cognos_id__icontains = search_value)|
											# Q(code__icontains = search_value) )



			serializer = HospitalViewSerializer(hospitals, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


class COEView(BaseAPIView, CustomPagination):
	permission_classes = (IsGetOAuthenticatedSuperAdminLocalAdminSalesManager, )
	pagination_class = CustomPagination
	def boolean(self, status):
		if status == 'true' or status == "True":
			return True
		else:
			return False

	def get(self, request, pk=None):
		try:
			column_name =request.query_params.get('column_name','hospital_name')
			rev = request.query_params.get('order','')
			search_value = request.query_params.get('search_value', None)
			hospital_name = request.query_params.get('hospital_name', '')
			country = request.query_params.get('country', '')
			products = request.query_params.get('products', '')
			number_of_trainee = request.query_params.get('number_of_trainee', '')
			location = request.query_params.get('location', '')
			qualified_for_news_mics_program = request.query_params.get('qualified_for_news_mics_program', '')
			cognos_id = request.query_params.get('cognos_id', '')
			code = request.query_params.get('code', '')
			deleted = request.query_params.get('deleted', '')
						
			hospitals = Hospital.objects.filter(is_it_preceptorship = True)

			if search_value:
				hospitals = hospitals.filter(Q(id__icontains=search_value) |
											Q(hospital_name__icontains=search_value) |
											Q(number_of_trainee__icontains=search_value) |
											Q(cognos_id__icontains = search_value)|
											Q(products__product_name__icontains = search_value) |
											Q(hospital_id__country__name__icontains=search_value) |
											Q(location__icontains=search_value) |
											Q(is_it_preceptorship__icontains=search_value) |
											Q(qualified_for_news_mics_program__icontains=search_value) |
											Q(code__icontains = search_value) )

			query_object = Q()

			if hospital_name:
				query_object &= Q(hospital_name=hospital_name)

			if country:
				query_object &= Q(hospital_id__country__id=country)

			if products:
				query_object &= Q(products__id=products)

			if number_of_trainee:
				query_object &= Q(number_of_trainee=number_of_trainee)

			if location:
				query_object &= Q(location=location)

			if qualified_for_news_mics_program:
				query_object &= Q(qualified_for_news_mics_program = self.boolean(qualified_for_news_mics_program))

			if cognos_id:
				query_object &= Q(cognos_id = cognos_id)

			if code:
				query_object &= Q(code = code)

			if deleted:
				query_object &= Q(deleted=deleted)


			hospitals = hospitals.filter(query_object)
			main_coulmns = ['hospital_name','products', 'number_of_trainee', 'location', 'is_it_preceptorship', 'qualified_for_news_mics_program','cognos_id', 'code', 'deleted']

			if column_name in main_coulmns:
				hospitals = hospitals.order_by(column_name)

			elif column_name == "country":
				hospitals = hospitals.order_by('hospital_id__country__name')

			
			if rev == 'true':
				hospitals = hospitals.reverse()
			results = self.paginate_queryset(hospitals, request, view=self)
			serializer = HospitalViewSerializer(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


# hospital and coe listing
'''# hospital and coe listing
for hospital is_it_preceptorship:false
while for COE is_it_preceptorship:true

limit:50
offset:0
column_name:id
order:
search_value:str
hospital_name:str
country:id
products:id
number_of_trainee:num
location:str
qualified_for_news_mics_program:bool
cognos_id:str
deleted:bool
is_it_preceptorship:true'''
class JustHospitalView(BaseAPIView, CustomPagination):
	permission_classes = (IsGetOAuthenticatedSuperAdminLocalAdminSalesManager,)

	def sorting_data(self, colum_name, order):
		try:
			dash = '' if order.lower() == 'asc' else '-'

			if colum_name == "id":
				return f'{dash}id'

			if colum_name == "hospital_name":
				return f'{dash}hospital_name'

			if colum_name == "number_of_trainee":
				return f'{dash}number_of_trainee'

			if colum_name == "products":
				return f'{dash}products__product_name'

			if colum_name == "country":
				return f'{dash}hospital_id__country__name'

			if colum_name == "location":
				return f'{dash}location'

			if colum_name == "qualified_for_news_mics_program":
				return f'{dash}qualified_for_news_mics_program'

			if colum_name == "cognos_id":
				return f'{dash}cognos_id'

			return f'{dash}{colum_name}'
		except Exception as e:
			return e

	def get(self, request, pk=None):
		try:
			column_name =request.query_params.get('column_name','id')
			order = request.query_params.get('order', 'desc')
			limit = int(request.query_params.get('limit', 10))
			offset = int(request.query_params.get('offset', 0))
			search_value = request.query_params.get('search_value', None)
			hospital_name = request.query_params.get('hospital_name', '')
			country = request.query_params.get('country', '')
			products = request.query_params.get('products', '')
			number_of_trainee = request.query_params.get('number_of_trainee', '')
			location = request.query_params.get('location', '')
			qualified_for_news_mics_program = request.query_params.get('qualified_for_news_mics_program', '')
			cognos_id = request.query_params.get('cognos_id', '')
			code = request.query_params.get('code', '')
			deleted = request.query_params.get('deleted', '')
			is_it_preceptorship = boolean(request.query_params.get('is_it_preceptorship', ''))

			hospitals = Hospital.objects.filter(is_it_preceptorship=is_it_preceptorship)

			if search_value:
				hospitals = hospitals.filter(Q(id__icontains=search_value) |
											 Q(hospital_name__icontains=search_value) |
											 Q(number_of_trainee__icontains=search_value) |
											 Q(cognos_id__icontains=search_value) |
											 Q(products__product_name__icontains=search_value) |
											 Q(hospital_id__country__name__icontains=search_value) |
											 Q(location__icontains=search_value) |
											 Q(is_it_preceptorship__icontains=search_value) |
											 Q(qualified_for_news_mics_program__icontains=search_value) |
											 Q(code__icontains=search_value)).distinct()

			query_object = Q()

			if hospital_name:
				query_object &= Q(hospital_name=hospital_name)

			if country:
				query_object &= Q(hospital_id__country__id=country)

			if products:
				query_object &= Q(products__id=products)

			if number_of_trainee:
				query_object &= Q(number_of_trainee=number_of_trainee)

			if location:
				query_object &= Q(location=location)

			if qualified_for_news_mics_program:
				query_object &= Q(qualified_for_news_mics_program=boolean(qualified_for_news_mics_program))

			if cognos_id:
				query_object &= Q(cognos_id=cognos_id)

			if code:
				query_object &= Q(code=code)

			if deleted:
				query_object &= Q(deleted=boolean(deleted))

			hospitals = hospitals.filter(query_object)
			hospitals = hospitals.filter(query_object).order_by(str(self.sorting_data(column_name, order)))

			serializer = HospitalViewSerializer(hospitals[offset: offset + limit], many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count=hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

# check for congnos if
class CognosIdView(BaseAPIView, CustomPagination):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			search_value = request.query_params.get('search_value', None)
			
			if search_value:
				# hospitals = Hospital.objects.filter(Q(cognos_id__iexact = search_value))
				if Hospital.objects.filter(Q(cognos_id__iexact = search_value)):
					return self.send_response(success=True,status_code=status.HTTP_200_OK, payload={},code= '200',description=True ,log_description='')
				else:
					return self.send_response(success=True,status_code=status.HTTP_200_OK, payload={},code= '200',description=False ,log_description='')
			else:
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload={},code= '200',description="Add Value for search" ,log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Hospital doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

# get hospital view according to countires
class HospitalCountryView(BaseAPIView):
	permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin, )

	def get(self, request, pk=None):
		try:
			area_type = request.query_params.get('area_type', '')
			country = request.query_params.get('country', None)
			if area_type == 'local':
				countries = request.user.admin_user.get().zone.zone_zone_countires.all()
				countries_id = [country.countries.id for country in countries]
				hospitals = Hospital.objects.filter(hospital_id__country__id__in=countries_id, is_it_preceptorship=True).distinct()
				serializer = HospitalNameSerializer(hospitals, many=True)
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
										  code='', description='Details of serializer', log_description='', count = hospitals.count())
			if country:
				hospitals = Hospital.objects.filter(hospital_id__country__id=country).distinct()
				serializer = HospitalNameSerializer(hospitals, many=True)
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
										  code='', description='Details of serializer', log_description='', count = hospitals.count())

			hospitals = Hospital.objects.filter(is_it_preceptorship=True).distinct()
			serializer = HospitalNameSerializer(hospitals, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count=hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Product doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


# get hospital of zone
class HospitalZoneView(BaseAPIView):
	permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
	def get(self, request, pk=None):
		try:
			area_type = request.query_params.get('area_type', '')
			product = request.query_params.get('product_id', '')

			if area_type == 'local':
				countries = request.user.admin_user.get().zone.zone_zone_countires.all()
				countries_id = [country.countries.id for country in countries]
				hospitals = Hospital.objects.filter(hospital_id__country__id__in=countries_id, is_it_preceptorship=True, products__id=product).distinct()
				serializer = HospitalNameSerializer(hospitals, many=True)
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
										  code='', description='Details of serializer', log_description='', count=hospitals.count())

			hospitals = Hospital.objects.filter(is_it_preceptorship = True, products__id=product).distinct()
			serializer = HospitalNameSerializer(hospitals, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count=hospitals.count())
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Hospital.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Product doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

#
class EventTypeView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			event = EventType.objects.all()
			serializer = EventSerializer(event, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except EventType.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Product doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)


class SpecialityView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated,)
	def get(self, request, pk=None):
		try:
			event = Speciality.objects.all()
			serializer = SpecialitySerializer(event, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Hospital matches the given query.")
		except Speciality.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Product doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)
