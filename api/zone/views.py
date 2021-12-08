# from django.shortcuts import render
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.response import Response
from api.zone.models import Countries, Zone, query_zone_by_args, ZoneCountries
from api.zone.serializers import ZoneCountrySerializer, CountriesSerializer, ZoneSerializer, ZoneUpdateSerializer, UserZoneCountrySerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.views import BaseAPIView
from django.core.exceptions import FieldError
from rest_framework import status
from api.views import BaseAPIView
from api.pagination import CustomPagination
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import operator
from rest_framework import generics
from rest_framework import filters
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin, IsOauthAuthenticated
from cspro.utilities.convert_boolean import boolean

'''
Get Countries for dropdowns
'''
class CountriesView(BaseAPIView):
	permission_classes = (IsOauthAuthenticated, )
	def get(self, request, pk=None):
		try:
			user_zone = boolean(request.query_params.get("user_zone", ""))
			if pk is not None:
				country = Countries.objects.get(id=pk)
				serializer = CountriesSerializer(country)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')

			if user_zone == True:
				countries = Zone.objects.get(user_zone__user__id=request.user.id)
				serializer = UserZoneCountrySerializer(countries)
				res = serializer.data['countries']
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=res, code='200',
										  description="User's zone Countries", log_description='')

			countries = Countries.objects.all()
			serializer = CountriesSerializer(countries, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='All countries',log_description='', count = len(countries))
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Country matches the given query.")
		except Countries.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Countries doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)
	

	def post(self, request):
		try:
			data = request.data
			serializer = CountriesSerializer(data=data)
			if serializer.is_valid():
				country_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Country is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Countries.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Countries doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_countries = Countries.objects.get(id=id)
			data = request.data
			serializer = CountriesSerializer(instance=saved_countries, data=data, partial=True)
			if serializer.is_valid():
				country_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Country is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Country matches the given query.")
		except Countries.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Country doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

'''
Add zone by adding multiple countries 
'''
class AddZoneView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				zone = Zone.objects.get( pk=pk)
				serializer = ZoneSerializer(zone)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
			zones = Zone.objects.all()
			serializer = ZoneSerializer(zones, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = len(serializer.data))
		except Zone.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Zone doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

	def post(self, request):
		try:
			# {'zone': 'Asia', 'countries': ['Pakistan', 'India', 'Iran']}
			data = request.data
			serializer = ZoneSerializer(data = data)

			if serializer.is_valid():
				zone_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Zone is Created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Zone.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Zone doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except IntegrityError:
			return self.send_response(code=f'422', description="Zone already exists.",
									  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def put(self, request, pk=None):
		try:
			id = pk
			saved_zone = Zone.objects.get(id= id)
			data = request.data
			serializer = ZoneUpdateSerializer(instance=saved_zone, data=data)
			if serializer.is_valid():
				zone_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Zone is updated')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Zone.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Zone doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

'''
Zone Data table
'''
class ZoneViewSet(viewsets.ModelViewSet, BaseAPIView):
	permission_classes = (AllowAny, )
	queryset = Zone.objects.all()
	serializer_class = ZoneSerializer

	def list(self, request, **kwargs):
		try:
			country =  request.query_params.get('country_id', '')
			query_object = Q()

			if country != '':
				query_object &= Q(countries__id = country)
			
			zone = query_zone_by_args(query_object, **request.query_params)
			
			serializer = ZoneSerializer(zone['items'], many=True)
			print(serializer.data)
			
			result = dict()
			result['data'] = serializer.data
			result['draw'] = zone['draw']
			result['recordsTotal'] = zone['total']
			result['recordsFiltered'] = zone['count']
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=result,code= '',description='Zone Data Table ',log_description='')
		except Zone.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Zone doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print("----------------------------------------\n", e)
			return self.send_response(code=f'500',description=e)

'''
Get zone view with pagination and search value
'''
class GetZoneView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			search_value = request.query_params.get('search_value', None)
			column_name = request.query_params.get('column_name', 'zone')
			name = request.query_params.get('name', '')
			countries = request.query_params.get('countries', '')
			rev = request.query_params.get('order', '')

			zone = Zone.objects.all()
			if search_value:
				zone = zone.filter(Q(id__icontains=search_value) |
								   Q(name__icontains=search_value) |
								   Q(zone_zone_countires__countries__name=search_value)).distinct()

			query_object = Q()

			if name:
				query_object &= Q(name=name)

			if countries:
				query_object &= Q(zone_zone_countires__countries__name=countries)

			zone = zone.filter(query_object)

			if column_name == 'name':
				zone = zone.order_by(column_name)

			if column_name == 'id':
				zone = zone.order_by('id')

			if column_name == 'countries':
				zone = zone.order_by('zone_zone_countires__countries__name')

			if rev == 'true':
				zone = zone.reverse()

			results = self.paginate_queryset(zone, request, view=self)
			serializer = ZoneSerializer(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='Zone Details',log_description='', count = zone.count())
		except Zone.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Zone doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

'''
countries pagination view 
'''
class CountriesPaginationView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination

	def get(self, request, pk=None):
		try:
			column_name =request.query_params.get('column_name','name')
			rev = request.query_params.get('order','')
			search_value = request.query_params.get('search_value', None)
						
			countries = Countries.objects.all()
			if search_value:
				countries = countries.filter(Q(id__icontains=search_value) |
											Q(name__icontains=search_value)).distinct()

			if column_name == 'name':
				countries = countries.order_by('name')

			if column_name == 'id':
				countries = countries.order_by('id')

			
			if rev == 'true':
				countries = countries.reverse()

			results = self.paginate_queryset(countries, request, view=self)
			serializer = CountriesSerializer(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='', count = len(countries))
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Country matches the given query.")
		except Countries.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Countries doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)







'''
Get countries of user Zone 
'''

class CountriesOfZoneView(BaseAPIView):
	permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin, )
	def get(self, request, pk=None):
		try:
			countries = Zone.objects.get(user_zone__user__id= request.user.id)
			serializer = UserZoneCountrySerializer(countries)
			res = serializer.data['countries']
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=res,code= '200',description='Details of serializer',log_description='')
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No Country matches the given query.")
		except Zone.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Countries doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

'''
Update zone view 
'''
class UpdateZoneView(BaseAPIView):
	permission_classes = (AllowAny, )

	def put(self, request, pk=None):
		try:
			data = request.data
			saved_zone = Zone.objects.get(id = pk)
			serializer = ZoneUpdateSerializer(instance=saved_zone,data=data)
			if serializer.is_valid():
				zone_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
										  description='Zone is updated')
			return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
									  description=serializer.errors)
		except Zone.DoesNotExist:
			return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
									  description="Zone doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500', description=e)

'''
Enabled Disabled zone 
'''
class ZoneEnableDisableView(BaseAPIView):
	permission_classes = (AllowAny, )
	def get(self, request, pk=None):
		try:
			if pk is not None:
				zone = Zone.objects.get( pk=pk)
				zone.status = not zone.status
				zone.save()
				if zone.status:
					return self.send_response(success=True,status_code=status.HTTP_200_OK,code= '',description='Zone is Enabled Successfuly',log_description='')
			return self.send_response(success=True,status_code=status.HTTP_200_OK, code= '',description='Zone is Disabled Successfuly',log_description='')
		except Zone.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Zone doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response( code=f'500',description=e)

'''
Countries with annomyus permissions  
'''
class CountriesAnnoysView(BaseAPIView):
	permission_classes = (AllowAny,)

	def get(self, request, pk=None):
		try:
			user_zone = boolean(request.query_params.get("user_zone", ""))
			if pk is not None:
				country = Countries.objects.get(id=pk)
				serializer = CountriesSerializer(country)
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
										  code='', description='Details of serializer', log_description='')

			if user_zone == True:
				countries = Zone.objects.get(user_zone__user__id=request.user.id)
				serializer = UserZoneCountrySerializer(countries)
				res = serializer.data['countries']
				return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=res, code='200',
										  description="User's zone Countries", log_description='')

			countries = Countries.objects.all()
			serializer = CountriesSerializer(countries, many=True)
			return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
									  description='All countries', log_description='', count=len(countries))
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
									  description="No Country matches the given query.")
		except Countries.DoesNotExist:
			return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
									  description="Countries doesn't exists")
		except FieldError:
			return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500', description=e)
