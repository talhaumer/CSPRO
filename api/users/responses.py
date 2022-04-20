import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import is_server_error
from rest_framework.views import APIView


class BaseAPIView(APIView):
    """
    Base class for API views.
    """

    authentication_classes = ()
    permission_classes = (IsAuthenticated,)

    def send_response(
        self,
        success=False,
        code="",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        payload={},
        description="",
        exception=None,
        count=0,
        log_description="",
    ):
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
            if settings.DEBUG:
                description = f"error message: {description}"
            else:
                description = "Internal server error."
        return Response(
            data={
                "success": success,
                "code": code,
                "payload": payload,
                "description": description,
                "count": count,
            },
            status=status_code,
        )

    def send_data_response(
        self,
        success=False,
        code="",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        payload={},
        description="",
    ):
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
                description = f"error message: {description}"
            else:
                description = "Internal server error."
        return Response(
            data={
                "data": {
                    "success": success,
                    "code": code,
                    "payload": payload,
                    "description": description,
                }
            },
            status=status_code,
        )

    @staticmethod
    def get_oauth_token(email="", password="", grant_type="password"):
        try:
            url = settings.AUTHORIZATION_SERVER_URL
            # url ='http://192.168.100.10:8000/api/oauth/token/'
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"username": email, "password": password, "grant_type": grant_type}
            auth = HTTPBasicAuth(settings.OAUTH_CLIENT_ID, settings.OAUTH_CLIENT_SECRET)
            response = requests.post(url=url, headers=headers, data=data, auth=auth)
            if response.ok:
                json_response = response.json()
                return {
                    "access_token": json_response.get("access_token", ""),
                    "refresh_token": json_response.get("refresh_token", ""),
                }
            else:
                return {"error": response.json().get("error")}
        except Exception as e:
            # fixme: Add logger to log this exception
            return {"exception": str(e)}

    @staticmethod
    def revoke_oauth_token(token):
        try:
            url = settings.REVOKE_TOKEN_URL
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "token": token,
                "client_secret": settings.OAUTH_CLIENT_SECRET,
                "client_id": settings.OAUTH_CLIENT_ID,
            }
            response = requests.post(url=url, headers=headers, data=data)
            if response.ok:
                return True
            else:
                return False
        except Exception:
            # fixme: Add logger to log this exception
            return False

    def get_lookupid_by_code(self, code, lookup_category="", general=False):
        """
        Search the given code in main.Lookup table, and
        returns the row id or 0 (as zero means no data found)
        :param str lookup_category: Name of parent lookup category
        :param code: Lookup code (String)
        :return: pk of lookup object (int)
        """
        if general:
            if lookup_category:
                lookup_obj = Lookup.objects.filter(
                    lookup_category__code__exact=lookup_category, code=code
                ).first()
            else:
                # lookup_obj = Lookup.objects.filter(code=code, lookup_category_id__in=lookup_cat).first()
                lookup_obj = Lookup.objects.filter(code=code).first()
            if lookup_obj:
                return lookup_obj.id
            return 0
        else:
            lookup_cat = LookupCategory.objects.filter(parent_id=19).values_list("id")
            if lookup_category:
                lookup_obj = Lookup.objects.filter(
                    lookup_category__code__exact=lookup_category, code=code
                ).first()
            else:
                lookup_obj = Lookup.objects.filter(
                    code=code, lookup_category_id__in=lookup_cat
                ).first()
                # lookup_obj = Lookup.objects.filter(code=code).first()
            if lookup_obj:
                return lookup_obj.id
            if lookup_obj is None:
                return Lookup.objects.filter(
                    lookup_category__code__exact=lookup_category
                )
            return 0

    def get_lookupids(self, codes=[], lookup_category=""):
        """
        Search the given codes in main.Lookup table and
        returns the row ids.
        :param list codes: Lookup codes
        :param str lookup_category: Name of parent lookup category
        :rtype: list
        """
        if lookup_category:
            lookups = Lookup.objects.filter(
                lookup_category__code__exact=lookup_category, code__in=codes
            )
        else:
            lookups = Lookup.objects.filter(code__in=codes)
        if lookups.exists():
            return lookups.values_list("pk", flat=True)
        return []

    def get_lookups(self, code=""):
        lookups = Lookup.objects.filter(lookup_category__code__exact=code)
        print(lookups)
        if lookups.exists():
            return lookups.values_list("pk", flat=True)
        return []

    def is_dealer(self):
        """
        :return: True if dealer otherwise False
        """
        if self.request.user.roles.first().role.access_level == AccessLevel.DEALER:
            return True
        return False

    def approval_required(self):
        """
        :return: True if dealer or tenant otherwise False
        """
        try:
            return (
                self.request.user.roles.first().role.access_level
                < AccessLevel.SITE_MANAGER
            )
        except:
            return True

    def verify_fb_user(self, user):
        if user.provider == user.FACEBOOK and user.username.startswith(
            f"{user.id}{000}"
        ):
            # This means social user has not updated his number yet
            return True
        return False


class ImageUploadParser(FileUploadParser):
    media_type = "image/*"
