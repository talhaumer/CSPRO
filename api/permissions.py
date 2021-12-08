from django.contrib.auth import authenticate
from oauth2_provider.models import AccessToken
from oauth2_provider.views import ProtectedResourceView
from rest_framework import permissions

from api.users.models import AccessLevel


class BaseAuthPermission(permissions.BasePermission):

    def verify_header(self, request):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
                    # request.data['created_by'] = request.user.id
                    return True
        return False

    def verify_cookie(self, request):
        try:
            access_token = request.COOKIES.get('u-at', None)
            if access_token:
                request.user = AccessToken.objects.get(token=access_token).user
                request.user.access_token = access_token
                # request.data['created_by'] = request.user.id
                return True
            else:
                return False
        except AccessToken.DoesNotExist:
            return False


class IsOauthAuthenticated(BaseAuthPermission):

    def has_permission(self, request, view):
        return self.verify_header(request)


class IsPostOrIsAuthenticated(BaseAuthPermission):

    def has_permission(self, request, view):
        # allow all POST requests
        if request.method == 'POST':
            self.verify_header(request)
            return True

        # Otherwise, only allow authenticated requests
        return request.user and request.user.is_authenticated


class IsGetOrIsAuthenticated(permissions.BasePermission, ProtectedResourceView):

    def has_permission(self, request, view):
        # allow all POST requests
        if request.method == 'GET':
            if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
                if not hasattr(request, "user") or request.user.is_anonymous:
                    user = authenticate(request=request)
                    if user:
                        request.user = request._cached_user = user
            return True

        # Otherwise, only allow authenticated requests
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
                    return True

class IsOauthAuthenticatedSuperAdminLocalAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.SUPER_ADMIN_CODE or user.role.code == AccessLevel.LOCAL_ADMIN_CODE:
                        print("super_admin")
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False

class IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
			if not hasattr(request, "user") or request.user.is_anonymous:
				user = authenticate(request=request)
				if user:
					if (request.method == 'POST' or request.method == 'GET') and (user.role.code == AccessLevel.SUPER_ADMIN_CODE or user.role.code == AccessLevel.LOCAL_ADMIN_CODE):
						print("super_admin")
						request.user = request._cached_user = user
						# request.data['created_by'] = request.user.id
						return True
					else:
						return False
		else:
			try:
				access_token = request.COOKIES.get('u-at', None)
				if access_token:
					request.user = AccessToken.objects.get(token=access_token).user
					request.user.access_token = access_token
					request.data['created_by'] = request.user.id
					return True
				else:
					return False
			except AccessToken.DoesNotExist:
				return False


class IsOauthAuthenticatedSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.SUPER_ADMIN_CODE:
                        print("super_admin")
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsGETOAuthenticatedSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if request.method == 'GET' and user.role.code == AccessLevel.LOCAL_ADMIN_CODE:
                        request.user = request._cached_user = user
                        return True
                    elif user.role.code == AccessLevel.SUPER_ADMIN_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsPostOAuthenticatedSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if request.method == 'GET' and user.role.code == AccessLevel.SUPER_ADMIN_CODE:
                        request.user = request._cached_user = user
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False

# Proctors Persmissions
class IsGetOAuthenticatedSuperAdminLocalAdminSalesManager(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.method == "POST":
			return True
		if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
			if not hasattr(request, "user") or request.user.is_anonymous:
				user = authenticate(request=request)
				if user:
					if request.method == 'GET' and (user.role.code == AccessLevel.SUPER_ADMIN_CODE or user.role.code == AccessLevel.LOCAL_ADMIN_CODE or user.role.code == AccessLevel.SALES_MANAGER_CODE):
						request.user = request._cached_user = user
						return True
					else:
						return False
		else:
			try:
				access_token = request.COOKIES.get('u-at', None)
				if access_token:
					request.user = AccessToken.objects.get(token=access_token).user
					request.user.access_token = access_token
					request.data['created_by'] = request.user.id
					return True
				else:
					return False
			except AccessToken.DoesNotExist:
				return False


class IsPostOAuthenticatedSuperAdminUpdate(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.method == "POST":
			return True
		if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
			if not hasattr(request, "user") or request.user.is_anonymous:
				user = authenticate(request=request)
				if user:
					if request.method == 'PUT' and (user.role.code == AccessLevel.SUPER_ADMIN_CODE):
						request.user = request._cached_user = user
						return True
					else:
						return False
		else:
			try:
				access_token = request.COOKIES.get('u-at', None)
				if access_token:
					request.user = AccessToken.objects.get(token=access_token).user
					request.user.access_token = access_token
					request.data['created_by'] = request.user.id
					return True
				else:
					return False
			except AccessToken.DoesNotExist:
				return False

class IsGETOAuthenticatedSalesManager(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if request.method == 'GET' and user.role.code == AccessLevel.SALES_MANAGER_CODE:
                        request.user = request._cached_user = user
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsOauthAuthenticatedLocalAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.LOCAL_ADMIN_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsOauthAuthenticatedSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.SUPER_ADMIN_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsOauthAuthenticatedSalesManager(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.SALES_MANAGER_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsOauthAuthenticatedLocalAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.LOCAL_ADMIN_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsOauthAuthenticatedProctor(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    if user.role.code == AccessLevel.LOCAL_ADMIN_CODE:
                        request.user = request._cached_user = user
                        # request.data['created_by'] = request.user.id
                        return True
                    else:
                        return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False
