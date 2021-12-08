import operator
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

from api.pagination import CustomPagination
from api.permissions import IsOauthAuthenticatedSuperAdmin, IsOauthAuthenticated
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean
from cspro.utils import send_email_sendgrid_template
from .models import User, query_user_by_args, UserInfo, EmailToken
from .serializers import (
    UserSerializer,
    UpdateProfileSerializer,
    UserFormUpdateSerializer,
    PasswordSerializers,
    UserViewSerializer, UpdateProfileDataSerializer, ChangePasswordSerializer,
)
from django.contrib.auth import logout
from oauth2_provider.models import AccessToken



""" Login for auth user that should provide name and email to login into application its used for admin,
superadmin and sales manager
"""

class LoginView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        password = request.data.get('password', '')
        email = request.data.get('email', '')
        try:
            user = authenticate(request, email=email, password=password)
            if user:
                if user.is_active:
                    oauth_token = self.get_oauth_token(email, password)
                    if 'access_token' in oauth_token:
                        serializer = UserSerializer(user)
                        user_data = serializer.data
                        user_data['access_token'] = oauth_token.get('access_token')
                        user_data['refresh_token'] = oauth_token.get('refresh_token')
                        return self.send_response(success=True, code=f'200', status_code=status.HTTP_200_OK,
                                                  payload=user_data, description='You are logged in!',
                                                  log_description=f'User {user_data["email"]}. with id .{user_data["id"]}. has just logged in.')
                    else:
                        return self.send_response(description='Something went wrong with Oauth token generation.',
                                                  code=f'500')
                else:
                    description = 'Your account is blocked or deleted.'
                    return self.send_response(success=False, code=f'422',
                                              status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload={},
                                              description=description)
            return self.send_response(success=False, code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      payload={}, description='Email or password is incorrect.')
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Add User according to roles, this action is only performed  by super admin of application
get add 
Add zone id of zone table 
country_id from countries table 
role_code is from roles table
"""
class AddUserView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def post(self, request):
        try:
            user = request.data
            serializer = UserSerializer(data=user)
            if serializer.is_valid():
                user_saved = serializer.save()
                password_token = uuid4()
                EmailToken.objects.create(user=serializer.instance, token=password_token)

                link = f'{settings.WEB_URL}activate-account/{str(password_token)}'

                # link =
                data = {
                    "first_name": serializer.data['name'],
                    "Link": link
                }
                send_email_sendgrid_template(
                    from_email=settings.SUPPORTEMAIL,
                    to_email=serializer.data['email'],
                    subject="",
                    data=data,
                    template=settings.VERIFYACCOUNT
                )
                data = {
                    "id": serializer.data['id'],
                    "name": serializer.data['name'],
                    "email": serializer.data['email'],
                    "token": password_token
                }
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, payload=data,
                                          description='User is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except IntegrityError:
            return self.send_response(code=f'422', description="Email already exists.",
                                      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Set user password by authenticating token that we send in a mail
"""
class PasswordView(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, pk=None):
        try:
            data = request.data
            obj = EmailToken.objects.get(token__exact=data['token'])
            if obj:
                serializer = PasswordSerializers(data=request.data)
                if serializer.is_valid():
                    user = User.objects.get(id=obj.user_id)
                    user.set_password(request.data['password'])
                    user.is_active = True
                    user.save()
                    deleted = EmailToken.objects.filter(user__id=obj.user_id, token__exact=data['token']).delete()
                    return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                              description="Your password is set successfuly")
            else:
                return self.send_response(code=f'422',
                                          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="token and user data doesn't match")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User Doesn't exist")
        except Exception as e:
            return self.send_response(code=f'500', description=e)



"""
Update user profile block not whole user form by this  
"""
class UpdateProfile(BaseAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOauthAuthenticated,)

    def get(self, request):
        try:
            id = request.user.id
            saved_user = User.objects.get(id=request.user.id)
            serializer = UpdateProfileDataSerializer(saved_user)
            return self.send_response(
                success=True, code=f'200.', payload=serializer.data, status_code=status.HTTP_200_OK,
                description="User ")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except IntegrityError:
            return self.send_response(code=f'422', description="Email already exists.",
                                      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)




    def put(self, request, pk=None):
        try:
            id = pk
            saved_user = User.objects.get(id=request.user.id)
            data = request.data
            serializer = UpdateProfileSerializer(instance=saved_user, data=data, partial=True)
            if serializer.is_valid():
                data_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='User is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No User matches the given query.")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
User listing data for user views query parameters are those
limit:10
offset:0
search_value:str
column_name:country
order:
country:id
zone:id
name:str
email:str
is_active:bool
role:code
mail_notification:bool
"""
class GetUserView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)
    pagination_class = CustomPagination

    # def boolean(self, status):
    #     if status == 'true' or status == "True":
    #         return True
    #     else:
    #         return False

    def sorting_data(self, column_name, rev):
        try:
            dash = '' if rev.lower() == 'asc' else '-'

            if column_name == 'id':
                return f'{dash}id'

            if column_name == 'zone':
                return f'{dash}zone__name'

            if column_name == 'country':
                return f'{dash}user__country__name'

            if column_name == 'email':
                return f'{dash}user__email'

            if column_name == 'role':
                return f'{dash}user__role'

            if column_name == 'name':
                return f'{dash}user__name'

            if column_name == 'is_active':
                return f'{dash}user__is_active'

        except Exception as e:
            return str(e)

    def filtration(self, zone, name, country, email, is_active, role, mail_notification):
        try:
            query_object = Q()

            if mail_notification:
                query_object &= Q(mail_notification=boolean(mail_notification))

            if zone:
                query_object &= Q(zone__id=zone)

            if name:
                query_object &= Q(user__name=name)

            if email:
                query_object &= Q(user__email=email)

            if is_active:
                query_object &= Q(user__is_active=boolean(is_active))

            if role:
                query_object &= Q(user__role__name=role)

            if country:
                query_object &= Q(user__country__id=country)

            return query_object
        except Exception as e:
            return e

    def get(self, request, pk=None):
        try:
            if pk:
                users = UserInfo.objects.get(id=pk)
                serializer = UserViewSerializer(users)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='200', description='Details of serializer', log_description='',
                                          count=len(serializer.data))

            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            column_name = request.query_params.get('column_name', 'id')
            order = request.query_params.get('order', "desc")
            search_value = request.query_params.get('search_value', None)
            zone = request.query_params.get('zone', None)
            name = request.query_params.get('name', None)
            country = request.query_params.get('country', None)
            email = request.query_params.get('email', None)
            is_active = request.query_params.get('is_active', None)
            role = request.query_params.get('role', None)
            mail_notification = request.query_params.get('mail_notification', None)

            users = UserInfo.objects.all()
            if search_value:
                users = users.filter(Q(user__name__icontains=search_value) |
                                     Q(user__email__icontains=search_value) |
                                     Q(user__role__name__icontains=search_value) |
                                     Q(id__icontains=search_value) |
                                     Q(user__country__name__icontains=search_value) |
                                     Q(user__is_active__icontains=search_value) |
                                     Q(zone__name__icontains=search_value)).distinct()

            query_object = self.filtration(zone, name, country, email, is_active, role, mail_notification)
            order = self.sorting_data(column_name, order)
            users = users.filter(query_object).order_by(order)
            serializer = UserViewSerializer(users[offset: offset + limit], many=True)
            data = serializer.data
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=data, code='200',
                                      description='Details of serializer', log_description='', count=users.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No User matches the given query.")
        except UserInfo.DoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Local admins listing 
"""
class LocalAdminListingView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def get(self, request, pk=None):
        """
        Super Admin Can send invitation to the local admin directly with all rights
        """
        try:

            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            user = User.objects.filter(role="local_admin").order_by('-id')
            data = user[offset: offset + limit]
            serializer = UserSerializer(data, many=True)

            return self.send_response(
                success=True, code=f'200.', payload=serializer.data, status_code=status.HTTP_200_OK,
                description="User local Admin", count=user.count())
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User Model Doesn't exist")
        except Exception as e:
            return self.send_response(code=f'500.', description=e)

"""
only sales manager listing 
"""
class SalesManagerListingView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def get(self, request, pk=None):
        """
        Super Admin Can send invitation to the local admin directly with all rights
        """
        try:

            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            # query_object = Q()
            user = User.objects.filter(role="sales_manager").order_by('-id')
            data = user[offset: offset + limit]
            serializer = UserSerializer(data, many=True)

            return self.send_response(
                success=True, code=f'200.', payload=serializer.data, status_code=status.HTTP_200_OK,
                description="User Sales Manager", count=user.count())
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User Model Doesn't exist")
        except Exception as e:
            return self.send_response(code=f'500.', description=e)

"""
only super admin listing 
"""
class SuperAdminListingView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def get(self, request, pk=None):
        """
        Super Admin Can send invitation to the local admin directly with all rights
        """
        try:

            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            # query_object = Q()
            user = User.objects.filter(role="super_admin").order_by('-id')
            data = user[offset: offset + limit]
            serializer = UserSerializer(data, many=True)

            return self.send_response(
                success=True, code=f'200.', payload=serializer.data, status_code=status.HTTP_200_OK,
                description="User Super Admin", count=user.count())
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User Model Doesn't exist")
        except Exception as e:
            return self.send_response(code=f'500.', description=e)

"""
Blocked un blocked user View
"""
class BlockedUnBlockedUsersView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    # pagination_class = CustomPagination
    def get(self, request, pk=None):
        try:
            if pk is not None:
                user = User.objects.get(id=pk, deleted=False)
                user.is_active = not user.is_active
                user.save()
                print(user)
                if user.is_active == True:
                    return self.send_response(description="users is activate successfuly", success=True,
                                              status_code=status.HTTP_200_OK, code='200')
                else:
                    return self.send_response(description="users is Blocked successfuly", success=True,
                                              status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't found")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

"""
Update User Whole form by super admin 
"""
class UpdateUserFormView(BaseAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                user = User.objects.get(admin_user__id=pk)
                serializer = UserFormUpdateSerializer(user)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No User matches the given query.")
        except User.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, pk=None):
        try:
            id = pk
            saved_user = User.objects.get(admin_user__id=id)
            data = request.data
            serializer = UserFormUpdateSerializer(instance=saved_user, data=data, partial=True)
            if serializer.is_valid():
                data_saved = serializer.save(image=request.data.get('image'))
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='User is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No User matches the given query.")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Soft delete user its only done by admin
\ 
"""
class DeleteUsersView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                user = User.objects.get(id=pk)
                user.deleted = True
                user.is_active = False
                print(user)
                return self.send_response(description="users is deleted successfuly", success=True,
                                          status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't found")
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

"""
Geting paginations of usrer
"""
class UserPaginationView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            column_name = request.query_params.get('column_name', 'name')
            rev = request.query_params.get('order', '')
            search_value = request.query_params.get('search_value', None)

            users = User.objects.all()
            if search_value:
                users = users.filter(Q(id__icontains=search_value) |
                                     Q(name__icontains=search_value) |
                                     Q(email__icontains=search_value) |
                                     Q(role__name__icontains=search_value) |
                                     Q(business_unit__icontains=search_value))

            if rev == 'true':
                ordered = sorted(users, reverse=True, key=operator.attrgetter(column_name))
            else:
                ordered = sorted(users, reverse=False, key=operator.attrgetter(column_name))
            results = self.paginate_queryset(ordered, request, view=self)
            serializer = UserSerializer(results, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='', count=len(users))
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Hospital matches the given query.")
        except User.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Hospital doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Forget user password added by Ashar 
"""
class ForgotPasswordView(BaseAPIView):
    parser_class = ()
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        try:
            if request.data['email'] == "" or None:
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Email is required"
                )
            else:
                user = User.objects.get(email__exact=request.data['email'])
                password_token = uuid4()
                EmailToken.objects.create(user=user, token=password_token)

                link = f'{settings.WEB_URL}recover-password/{str(password_token)}'

                data = {
                    "Link": link
                }
                send_email_sendgrid_template(
                    from_email=settings.SUPPORTEMAIL,
                    to_email=user.email,
                    subject="",
                    data=data,
                    template=settings.FORGOTPASSWORD
                )
            # send_html_email_with_sendgrid(user.email, "Forgot Password Link", str(email_link.token))

            return self.send_response(
                success=True,
                code=f'201',
                # payload=serializer.data,
                status_code=status.HTTP_201_CREATED,
                description="Forgot password link sent successfully",
            )
        except User.DoesNotExist:
            return self.send_response(
                code=f'422',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="User does not exists"
            )
        except Exception as e:
            return self.send_response(
                code=f'500',
                description=e
            )

"""
Update user password 
"""
class ChangePasswordView(BaseAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOauthAuthenticated,)
    def put(self, request):
        try:
            obj = request.user
            serializer = ChangePasswordSerializer(data = request.data)
            if serializer.is_valid():
                if not obj.check_password(serializer.data.get("old_password")):
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="old password in incorect")
                obj.set_password(serializer.data.get("new_password"))
                obj.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, payload=[],
                                          description='Password is Updated')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

"""
Logout user by revoking auth token
"""
class UserLogoutView(BaseAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOauthAuthenticated,)
    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
            if not self.revoke_oauth_token(token):
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="User doesn't logout")
            logout(request)
            return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, payload=[],
                                          description='User logout successfully')
        except User.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="User doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
