import datetime

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.pagination import CustomPagination
from api.permissions import (
    IsGetOAuthenticatedSuperAdminLocalAdminSalesManager,
    IsOauthAuthenticated,
    IsOauthAuthenticatedSuperAdminLocalAdmin,
    IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet,
    IsPostOAuthenticatedSuperAdminUpdate,
)
from api.proctors.models import Proctors
from api.proctors.serializers import (
    ProctorsSerializer,
    ProctorsUpdateSerializer,
    ProctorsViewSerializer,
    ProctorsZoneDropViewSerializer,
    ProctorsZoneViewSerializer,
)
from api.speakingevent.models import Event, Speaker, SpeakingEvent
from api.users.models import User
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean
from cspro.utils import available_proctors


class ProctorsView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctor = Proctors.objects.get(pk=pk)
                serializer = ProctorsViewSerializer(proctor)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            proctors = Proctors.objects.all()
            serializer = ProctorsViewSerializer(proctors, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist as e:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctor matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    def post(self, request):
        try:
            data = request.data
            serializer = ProctorsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Proctor is created",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
        except IntegrityError as i:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(i),
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctor doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


class ProctorsOfZoneView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            is_zone = boolean(request.query_params.get("is_zone", ""))
            search_value = request.query_params.get("search_value", "")
            product = request.query_params.get("product_id", "")
            activity_date = request.query_params.get("activity_date", "")
            start_date = request.query_params.get("start_date", "")
            end_date = request.query_params.get("end_date", "")
            limit = request.query_params.get("limit", None)
            offset = int(request.query_params.get("offset", 0))
            is_global = boolean(request.query_params.get("is_global", ""))
            event = boolean(request.query_params.get("event", ""))
            speaker = boolean(request.query_params.get("speaker", ""))
            is_master_proctorshhip = boolean(
                request.query_params.get("is_master_proctorshhip", "")
            )
            area_of_experties = request.query_params.get("area_of_experties_id", "")
            activity_id = pk

            if is_zone and event:
                countries = request.user.admin_user.get().zone.zone_zone_countires.all()
                countries_id = [country.countries.id for country in countries]
                query_object = Q()
                if speaker:
                    query_object &= Q(only_speaker=True)
                    if area_of_experties:
                        query_object &= Q(area_of_experties__id=area_of_experties)
                else:
                    query_object &= Q(only_speaker=False)

                proctors = Proctors.objects.filter(
                    user__is_active=True,
                    contract_ending_details__gt=end_date,
                    user__country__id__in=countries_id,
                )

                proctors = proctors.filter(query_object)
                if activity_id:
                    speakers = Speaker.objects.filter(
                        event__id=activity_id, proctor__isnull=False, revoke=False
                    )
                    speakes_id = [each.proctor.id for each in speakers]
                    speakes_id = list(set(speakes_id))
                    proctors = proctors.exclude(id__in=speakes_id)

                proctors = available_proctors(proctors, start_date, end_date)

                if search_value:
                    proctors = proctors.filter(
                        Q(user__name__icontains=search_value)
                    ).distinct()

                if limit:
                    serializer = ProctorsZoneViewSerializer(
                        proctors[offset : offset + int(limit)], many=True
                    )
                else:
                    serializer = ProctorsZoneDropViewSerializer(proctors, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            if is_global and event:
                query_object = Q()
                if speaker:
                    query_object &= Q(only_speaker=True)
                    query_object &= Q(area_of_experties__id=area_of_experties)
                else:
                    query_object &= Q(only_speaker=False)

                proctors = Proctors.objects.filter(
                    user__is_active=True, contract_ending_details__gt=end_date
                )

                proctors = proctors.filter(query_object)

                proctors = proctors.exclude(
                    unavailability_start_date__lt=start_date,
                    unavailability_end_date__gt=start_date,
                )
                proctors = proctors.exclude(
                    unavailability_start_date__gte=end_date,
                    unavailability_end_date__lte=end_date,
                )
                if activity_id:
                    speakers = Speaker.objects.filter(
                        event__id=activity_id, proctor__isnull=False, revoke=False
                    )
                    speakes_id = [each.proctor.id for each in speakers]
                    speakes_id = list(set(speakes_id))
                    proctors = proctors.exclude(id__in=speakes_id)

                proctors = available_proctors(proctors, start_date, end_date)

                if search_value:
                    proctors = proctors.filter(
                        Q(user__name__icontains=search_value)
                    ).distinct()

                if limit:
                    serializer = ProctorsZoneViewSerializer(
                        proctors[offset : offset + int(limit)], many=True
                    )
                else:
                    serializer = ProctorsZoneDropViewSerializer(proctors, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            if is_zone:
                countries = request.user.admin_user.get().zone.zone_zone_countires.all()
                countries_id = [country.countries.id for country in countries]
                proctors = Proctors.objects.filter(
                    user__is_active=True,
                    only_speaker=False,
                    products__id=product,
                    user__country__id__in=countries_id,
                    contract_ending_details__gt=end_date,
                )

                proctors = proctors.exclude(
                    unavailability_start_date__lt=start_date,
                    unavailability_end_date__gt=start_date,
                )
                proctors = proctors.exclude(
                    unavailability_start_date__gte=end_date,
                    unavailability_end_date__lte=end_date,
                )
                proctors = available_proctors(proctors, start_date, end_date)

                if search_value:
                    proctors = proctors.filter(
                        Q(user__name__icontains=search_value)
                    ).distinct()

                if limit:
                    serializer = ProctorsZoneViewSerializer(
                        proctors[offset : offset + int(limit)], many=True
                    )
                else:
                    serializer = ProctorsZoneDropViewSerializer(proctors, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            if is_global:
                proctors = Proctors.objects.filter(
                    user__is_active=True,
                    only_speaker=False,
                    products__id=product,
                    contract_ending_details__gt=end_date,
                )

                proctors = proctors.exclude(
                    unavailability_start_date__lt=start_date,
                    unavailability_end_date__gt=start_date,
                )
                proctors = proctors.exclude(
                    unavailability_start_date__gte=end_date,
                    unavailability_end_date__lte=end_date,
                )
                proctors = available_proctors(proctors, start_date, end_date)

                if search_value:
                    proctors = proctors.filter(
                        Q(user__name__icontains=search_value)
                    ).distinct()

                if limit:
                    serializer = ProctorsZoneViewSerializer(
                        proctors[offset : offset + int(limit)], many=True
                    )
                else:
                    serializer = ProctorsZoneDropViewSerializer(proctors, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            if is_master_proctorshhip:
                proctors = Proctors.objects.filter(
                    user__is_active=True, only_speaker=False, is_masterproctorship=True
                )
                proctors = proctors.exclude(contract_ending_details__lt=end_date)
                proctors = proctors.exclude(
                    proctorShip_contract_ending_details__lt=end_date
                )
                proctors = proctors.exclude(
                    unavailability_start_date__lt=start_date,
                    unavailability_end_date__gt=start_date,
                )
                proctors = proctors.exclude(
                    unavailability_start_date__gte=end_date,
                    unavailability_end_date__lte=end_date,
                )
                proctors = available_proctors(proctors, start_date, end_date)

                if search_value:
                    proctors = proctors.filter(
                        Q(user__name__icontains=search_value)
                    ).distinct()

                if limit:
                    serializer = ProctorsZoneViewSerializer(
                        proctors[offset : offset + int(limit)], many=True
                    )
                else:
                    serializer = ProctorsZoneDropViewSerializer(proctors, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=[],
                code="",
                description="Details of serializer",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class GloabalProctorsView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:

            proctors = Proctors.objects.all()
            results = self.paginate_queryset(proctors, request, view=self)
            serializer = ProctorsZoneViewSerializer(results, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProctorsUpdateView(BaseAPIView):
    permission_classes = (IsPostOAuthenticatedSuperAdminUpdate,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctor = Proctors.objects.get(pk=pk)
                serializer = ProctorsUpdateSerializer(proctor)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            proctors = Proctors.objects.all()
            serializer = ProctorsSerializer(proctors, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    def put(self, request, pk=None):
        try:
            id = pk
            saved_proctor = Proctors.objects.get(id=id)
            data = request.data
            serializer = ProctorsUpdateSerializer(instance=saved_proctor, data=data)
            if serializer.is_valid():
                focus_saved = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Proctors is updated",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProctorsPaginationView(BaseAPIView, CustomPagination):
    permission_classes = (IsGetOAuthenticatedSuperAdminLocalAdminSalesManager,)
    pagination_class = CustomPagination

    def sorting_data(self, column_name, order):
        try:
            dash = "" if order.lower() == "asc" else "-"
            if column_name == "proctor_name":
                return f"{dash}user__name"

            if column_name == "country":
                return f"{dash}user__country__name"

            if column_name == "proctor_email":
                return f"{dash}user__email"

            if column_name == "is_active":
                return f"{dash}user__is_active"

            if column_name == "telephone":
                return f"{dash}telephone"

            if column_name == "only_speaker":
                return f"{dash}only_speaker"

            if column_name == "hospital":
                return f"{dash}proctors_pivot_id__hospital__hospital_name"

            if column_name == "products":
                return f"{dash}products__product_name"

            if column_name == "area_of_experties":
                return f"{dash}area_of_experties__name"

            if column_name == "approach":
                return f"{dash}approach__name"

            if column_name == "spoken_languages":
                return f"{dash}spoken_languages__language"

            return f"{dash}{column_name}"
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            order = request.query_params.get("order", "desc")
            column_name = request.query_params.get("column_name", "id")
            search_value = request.query_params.get("search_value", None)

            country = request.query_params.get("country", None)
            is_active = request.query_params.get("is_active", None)
            only_speaker = request.query_params.get("only_speaker", None)

            product = request.query_params.get("product", None)

            is_dashboard = boolean(request.query_params.get("is_dashboard", ""))
            is_masterproctorship = request.query_params.get("is_masterproctorship", "")
            query_object = Q()

            proctors = Proctors.objects.all()
            if search_value:
                proctors = proctors.filter(
                    Q(id__icontains=search_value)
                    | Q(user__name__icontains=search_value)
                    | Q(user__email__icontains=search_value)
                    | Q(user__is_active__icontains=search_value)
                    | Q(telephone__icontains=search_value)
                    | Q(user__country__name__icontains=search_value)
                    | Q(proctors_pivot_id__hospital__hospital_name=search_value)
                    | Q(note__icontains=search_value)
                    | Q(products__product_name__icontains=search_value)
                    | Q(only_speaker__icontains=search_value)
                    | Q(area_of_experties__name__icontains=search_value)
                    | Q(spoken_languages__language__icontains=search_value)
                    | Q(approach__name__icontains=search_value)
                ).distinct()

            if is_active:
                query_object &= Q(user__is_active=boolean(is_active))

            if country:
                query_object &= Q(user__country__id=country)

            if product:
                query_object &= Q(products__id=product)

            if only_speaker:
                query_object &= Q(only_speaker=boolean(only_speaker))

            if is_masterproctorship:
                query_object &= Q(is_masterproctorship=boolean(is_masterproctorship))

            order = self.sorting_data(column_name, order)
            proctors = proctors.filter(query_object).order_by(order)
            if is_dashboard:
                expired_soon = proctors.filter(
                    contract_ending_details__gt=datetime.datetime.now()
                ).order_by("contract_ending_details")[0:10]
                serializer = ProctorsViewSerializer(expired_soon, many=True)
                expired = proctors.filter(
                    contract_ending_details__lt=datetime.datetime.now()
                ).order_by("-contract_ending_details")[0:10]
                expired = ProctorsViewSerializer(expired, many=True)
                res = {"expired soon": serializer.data, "expired": expired.data}
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=res,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            serializer = ProctorsViewSerializer(
                proctors[offset : offset + limit], many=True
            )

            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctor matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProctorsOfCOEView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            hospital = request.query_params.get("hospital_id", "")
            start_date = request.query_params.get("start_date", "")
            end_date = request.query_params.get("end_date", "")
            product = request.query_params.get("product_id", "")

            proctors = Proctors.objects.filter(
                proctors_pivot_id__hospital=hospital,
                only_speaker=False,
                user__is_active=True,
            )
            proctors = proctors.exclude(
                proctorShip_contract_ending_details__lt=end_date
            )

            proctors = proctors.exclude(
                unavailability_start_date__lte=start_date,
                unavailability_end_date__gte=start_date,
            )
            proctors = proctors.exclude(
                unavailability_start_date__gte=end_date,
                unavailability_end_date__lte=end_date,
            )

            proctors = available_proctors(proctors, start_date, end_date)
            serializer = ProctorsZoneViewSerializer(proctors, many=True)

            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class SpeakersProctorsView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            zone = request.query_params.get("zone", "")
            if zone:
                countries = request.user.admin_user.get().zone.zone_zone_countires.all()
                countries_id = [country.countries.id for country in countries]
                proctors = Proctors.objects.filter(user__is_active=True)
                results = self.paginate_queryset(proctors, request, view=self)
                serializer = ProctorsZoneViewSerializer(results, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=proctors.count(),
                )

            proctors = Proctors.objects.all()
            results = self.paginate_queryset(proctors, request, view=self)
            serializer = ProctorsZoneViewSerializer(results, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class DeleteProctorsView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctor = User.objects.get(proctor_user__id=pk)
                proctor.is_active = False
                proctor.save()
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=[],
                    code="",
                    description="Deleted Successfully",
                    log_description="",
                )
        except ObjectDoesNotExist as e:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctor matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProctorsTestView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            is_zone = boolean(request.query_params.get("is_zone", ""))
            search_value = request.query_params.get("search_value", "")
            product = request.query_params.get("product_id", "")
            start_date = request.query_params.get("start_date", "")
            end_date = request.query_params.get("end_date", "")
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            is_global = boolean(request.query_params.get("is_global", ""))
            is_speaker = boolean(request.query_params.get("is_speaker", ""))
            is_master_proctorshhip = boolean(
                request.query_params.get("is_master_proctorshhip", "")
            )

            proctors = Proctors.objects.filter(
                products__id=product,
                only_speaker=False,
                user__is_active=True,
                contract_starting_details__lt=start_date,
                contract_ending_details__gt=end_date,
            )

            proctors = proctors.exclude(
                unavailability_start_date__lt=start_date,
                unavailability_end_date__gt=end_date,
            )

            proctors = proctors.exclude(
                porposal_proctor_id__porposal__status__status__code__in=[
                    "waiting-for-docs",
                    "confirmed",
                ],
                porposal_proctor_id__status=True,
                porposal_proctor_id__porposal__status__is_active=True,
                porposal_proctor_id__porposal__start_date__lt=start_date,
                porposal_proctor_id__porposal__end_date__gt=end_date,
            )

            serializer = ProctorsZoneViewSerializer(proctors, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctors.count(),
            )

        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctors matches the given query.",
            )
        except Proctors.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctors doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)
