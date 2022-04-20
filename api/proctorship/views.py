from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db.models import Max, OuterRef, Q, Subquery
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.pagination import CustomPagination
from api.permissions import (
    IsOauthAuthenticated,
    IsOauthAuthenticatedSuperAdminLocalAdmin,
)
from api.proctorship.models import ConstantData, Proctorship
from api.proctorship.serializers import (
    ConstantDataSerializer,
    ProctorshipListingViewSerializer,
    ProctorshipSerializer,
    ProctorshipViewSerializer,
)
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean

"""# add proctorship
product_id: products table
secondary_product_id:products table
proctor_id : proctors table
zone_countries_id: ZOneCountries 
"""


class ProctorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get proctorship details by id
    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctorship = Proctorship.objects.get(pk=pk)
                serializer = ProctorshipViewSerializer(proctorship)
                data = serializer.data

                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )
            proctorship = Proctorship.objects.all()
            serializer = ProctorshipViewSerializer(proctorship, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Details of serializer",
                log_description="",
                count=proctorship.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctorship matches the given query.",
            )
        except Proctorship.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="proctorship doesn't exists",
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
            data["zone_id"] = request.user.admin_user.get().zone.id
            data["user_id"] = request.user.id
            serializer = ProctorshipSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": data},
                    status_code=status.HTTP_201_CREATED,
                    description="Proctor is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Proctorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctorship doesn't exists",
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
            saved_proctorship = Proctorship.objects.get(id=id)
            data = request.data
            serializer = ProctorshipSerializer(
                instance=saved_proctorship, data=data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="proctorship is updated",
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
                description="No proctorship matches the given query.",
            )
        except Proctorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="proctorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get constant data that used in proctorship perceptorship and in masterproctorship
class ConstantDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def get(self, request, pk=None):
        try:
            res = {}

            data = [
                "mvr/avr-approach",
                "title",
                "other-advanced-training",
                "other-advanced-training",
                "types-of-advanced-training",
                "types-of-first-training",
                "types-of-training",
            ]
            for each in data:
                proctorship = ConstantData.objects.filter(type=each)
                serializer = ConstantDataSerializer(proctorship, many=True)
                res[each] = serializer.data

            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=res,
                code="200",
                description="Details of serializer",
                log_description="",
                count=proctorship.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Proctorship matches the given query.",
            )
        except ConstantData.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="proctorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProctorshipListingApiView(BaseAPIView, CustomPagination):
    """
    procotorship listing data api view
    limit:10
    offset:0
    search_value:str
    status:bool
    product:id
    area:bool
    type_training:code
    column_name:str
    order:True
    is_dashboard:bool
    """

    permission_classes = (IsOauthAuthenticated,)
    pagination_class = CustomPagination

    def sorting_data(self, column_name, order):
        try:
            dash = "" if order.lower() == "asc" else "-"

            if column_name == "id":
                return f"{dash}id"

            if column_name == "status":
                return f"{dash}proctorship_status__status__id"

            if column_name == "cognos_id":
                return f"{dash}hospital__cognos_id"

            if column_name == "date":
                return (
                    f"{dash}proctorship_status__alter_proctorship_porposal__start_date"
                )
                #
            if column_name == "proctor":
                return f"{dash}proctorship_status__alter_proctorship_porposal__proctor_porposal__proctors__user__name"

            if column_name == "hospital":
                return f"{dash}hospital__hospital_name"

            if column_name == "product":
                return f"{dash}product__product_name"

            if column_name == "training_type":
                return f"{dash}training_type__name"

            if column_name == "is_global":
                return f"{dash}is_global"

            return f"{dash}{column_name}"
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            search_value = request.query_params.get("search_value", None)
            column_name = request.query_params.get("column_name", "id")
            order = request.query_params.get("order", "desc")
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            actvity_status = request.query_params.get("status", None)
            type_training = request.query_params.get("type_training", None)
            area = request.query_params.get("area", None)
            product = request.query_params.get("product", None)
            is_dashboard = boolean(request.query_params.get("is_dashboard", ""))

            proctorship = Proctorship.objects.all()

            if search_value:
                proctorship = proctorship.filter(
                    Q(id__icontains=search_value)
                    | Q(user__name__icontains=search_value)
                    | Q(activity_id__icontains=search_value)
                    | Q(hospital__hospital_name__icontains=search_value)
                    | Q(product__product_name__icontains=search_value)
                    | Q(secondary_product__product_name__icontains=search_value)
                    | Q(training_type__name__icontains=search_value)
                    | Q(new_center__name__icontains=search_value)
                    | Q(types_of_first_training__name__icontains=search_value)
                    | Q(type_advance_training__name__icontains=search_value)
                    | Q(other_advanced_training__name__icontains=search_value)
                    | Q(specific_training__name__icontains=search_value)
                    | Q(not_implant_regularly__name__icontains=search_value)
                    | Q(
                        proctorship_status__alter_proctorship_porposal__proctor_porposal__proctors__user__name__icontains=search_value
                    )
                ).distinct()

            query_object = Q(proctorship_status__is_active=True)

            if product:
                query_object &= Q(product__id=int(product)) | Q(
                    secondary_product__id=int(product)
                )

            if area:
                query_object &= Q(is_global=boolean(area))

            if type_training:
                query_object &= Q(training_type__code=type_training)

            proctorship.filter(query_object).order_by(
                str(self.sorting_data(column_name, order))
            )

            if actvity_status:
                query_object &= Q(proctorship_status__status__code=actvity_status)

            proctorship = (
                proctorship.filter(query_object)
                .order_by(str(self.sorting_data(column_name, order)))
                .distinct()
            )
            if is_dashboard:
                proctorship = proctorship.filter(is_global=True)
                proctorship = proctorship.exclude(
                    proctorship_status__status__code="closed"
                )

            serializer = ProctorshipListingViewSerializer(
                proctorship[offset : offset + limit], many=True
            )
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Proctorship Details",
                log_description="",
                count=proctorship.count(),
            )
        except Proctorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get past proctorship for second implant
class ProctorshipForSecondImplant(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def get(self, request, pk=None):
        try:

            query_object = Q(proctorship_status__is_active=True)
            query_object &= Q(proctorship_status__status__code="closed")
            query_object &= Q(new_center__code="first-proctorship")
            proctorship = Proctorship.objects.filter(query_object)

            serializer = ProctorshipListingViewSerializer(proctorship, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Proctorship Details",
                log_description="",
                count=proctorship.count(),
            )
        except Proctorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Proctorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)
