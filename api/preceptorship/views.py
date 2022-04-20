from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count, F, Q
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.pagination import CustomPagination
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin
from api.preceptorship.models import (
    AttendanceFormPerceptorship,
    InvoicePerceptorship,
    Preceptorship,
    PreceptorshipProposal,
    PreceptorshipStatus,
    PreceptorshipTraineeUploads,
    TraineePreceptorshipProfile,
)
from api.preceptorship.serializers import (
    AttendanceFormPerceptorshipUpdateSerailizers,
    AttendancePerceptorShipSerailizers,
    InvoicePerceptorshipSerializer,
    InvoicePerceptorshipUpdateSerializer,
    PProposalDateUpdateSerializer,
    PreceptorshipSerializer,
    PreceptorshipStatusSerializer,
    PreceptorshipStatusTestingSerializer,
    PreceptorshipStatusViewSerializer,
    PreceptorshipTraineeUpdateUploadsSerializers,
    PreceptorshipTraineeUploadsSerializers,
    PreceptorshipViewListingSerializer,
    PreceptorshipViewSerializer,
    TraineePreceptorshipSerializer,
    TraineeUpdatePreceptorshipSerializer,
)
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean
from cspro.utils import (
    check,
    check_event,
    check_masterproctorship,
    check_perceptorship,
    perceptership,
)

"""# get details and add perceptorship view
add perceptorship view
proctor_id:proctors data
product_id: product instance 
hospital_id: hospital instance 
"""


class PreceptorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    # get details of perceptorship by id
    def get(self, request, pk=None):
        try:
            if pk is not None:
                preceptorship = Preceptorship.objects.get(pk=pk)
                serializer = PreceptorshipViewSerializer(preceptorship)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            preceptorship = Preceptorship.objects.all()
            serializer = PreceptorshipViewSerializer(preceptorship, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=len(preceptorship),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Preceptorship matches the given query.",
            )
        except Preceptorship.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
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
            serializer = PreceptorshipSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                id = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": id},
                    status_code=status.HTTP_201_CREATED,
                    description="Preceptorship is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Preceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
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
            saved_preceptorship = Preceptorship.objects.get(id=id)
            data = request.data
            serializer = PreceptorshipSerializer(
                instance=saved_preceptorship, data=data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Preceptorship is updated",
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
                description="No Preceptorship matches the given query.",
            )
        except Preceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get and add perceptorship statuses
class PreceptorshipStatusView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    # # get perceptorship statuses by perceptorship id
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get("activity_id", "")
            if activity_id:
                activity_status = PreceptorshipStatus.objects.filter(
                    preceptorship_activity__id=activity_id
                ).order_by("timestamp")
                serializer = PreceptorshipStatusViewSerializer(
                    activity_status, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            return self.send_response(
                success=False,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                payload=[],
                code="422",
                description="Enter Valid ProctorshipId",
            )
        except IntegrityError as i:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(i),
            )
        except PreceptorshipStatus.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship Status doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # add perceptorship activity status
    def post(self, request):
        try:
            data = request.data
            data["user_id"] = request.user.id
            start_date = str(
                PreceptorshipProposal.objects.filter(
                    status__preceptorship_activity__id=data["perceptorship_activity_id"]
                )
                .latest("created_on")
                .start_date
            )
            end_date = str(
                PreceptorshipProposal.objects.filter(
                    status__preceptorship_activity__id=data["perceptorship_activity_id"]
                )
                .latest("created_on")
                .end_date
            )

            if data["status"] == "confirmed":
                proctors = (
                    PreceptorshipStatus.objects.filter(
                        preceptorship_activity__id=data["perceptorship_activity_id"]
                    )
                    .filter(alter_preceptorship_porposal__isnull=False)
                    .latest("created_on")
                    .alter_preceptorship_porposal.filter(
                        preceptorship_porposal__isnull=False
                    )
                    .latest("created_on")
                    .preceptorship_porposal.all()
                )
                for each in proctors:
                    if not check(each.proctors.id, start_date, end_date):
                        if not check_perceptorship(
                            each.proctors.id, start_date, end_date
                        ):
                            if not check_masterproctorship(
                                each.proctors.id, start_date, end_date
                            ):
                                if not check_event(
                                    each.proctors.id, start_date, end_date
                                ):
                                    proctors.update(status=False)
                                    each.status = True
                                    each.save()
                                    serializer = PreceptorshipStatusSerializer(
                                        data=data
                                    )
                                    if serializer.is_valid():
                                        saved_status = serializer.save()
                                        return self.send_response(
                                            success=True,
                                            code=f"201",
                                            status_code=status.HTTP_201_CREATED,
                                            description="status is created",
                                        )
                                    break
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="None of selected proctors is available",
                )

            serializer = PreceptorshipStatusSerializer(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="status is created",
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
        except PreceptorshipStatus.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship Status doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# get and add perceptorship feedback
class PreceptorshipFeedBackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    # get perceptorship feedback form by perceptorship id
    def get(self, request, pk=None):
        try:
            activityid = request.query_params.get("activity_id", "")

            if pk:
                activity_status = PreceptorshipTraineeUploads.objects.filter(
                    preceptorship_trainee__preceptorship__id=pk
                )
                serializer = PreceptorshipTraineeUploadsSerializers(
                    activity_status, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            if activityid:
                activity_status = PreceptorshipTraineeUploads.objects.filter(
                    preceptorship_trainee__preceptorship__id=activityid
                )
                serializer = PreceptorshipTraineeUploadsSerializers(
                    activity_status, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            return self.send_response(
                success=False,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                payload=[],
                code="422",
                description="Enter Valid ProctorshipId",
            )
        except IntegrityError as i:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(i),
            )
        except PreceptorshipTraineeUploads.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorshipm Trainee Uploads doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # add perceptorship feedback form
    def post(self, request):
        try:

            data = request.data
            serializer = PreceptorshipTraineeUploadsSerializers(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                perceptership(
                    Preceptorship.objects.get(
                        trainee_preceptorship__id=data["preceptorship_trainee_id"]
                    )
                )
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Preceptorship Trainee Uploads is created",
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
        except PreceptorshipTraineeUploads.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship Trainee Uploads doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)

    # update perceptorship feedback form by perceptorship id
    def put(self, request, pk=None):
        try:
            data = request.data
            saved_report = PreceptorshipTraineeUploads.objects.get(
                preceptorship_trainee__id=pk
            )
            serializer = PreceptorshipTraineeUpdateUploadsSerializers(
                instance=saved_report, data=data
            )
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Master Proctorship Updated",
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
        except PreceptorshipTraineeUploads.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship Trainee Uploads doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# approve perceptorship training view
class ApprovePreceptorShipTraineeView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = TraineePreceptorshipProfile.objects.get(id=pk)
                trainee.status = True
                trainee.save()
                return self.send_response(
                    description="trainee is activate successfuly",
                    success=True,
                    status_code=status.HTTP_200_OK,
                    code="200",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Preceptorship Profile doesn't found",
            )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Preceptorship Profile doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# revoke perceptorship traineees
class RevokeTraineePreceptorshipProfileView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = TraineePreceptorshipProfile.objects.get(id=pk)
                trainee.revoke = True
                trainee.save()
                return self.send_response(
                    description="trainee is is revoked successfuly",
                    success=True,
                    status_code=status.HTTP_200_OK,
                    code="200",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Profile doesn't found",
            )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Profile doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# get trainee of perceptorship view by perceptorship id
class TraineePreceptorshipProfileView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            preceptorship_id = request.query_params.get("activity_id", "")
            if preceptorship_id:
                trainees = TraineePreceptorshipProfile.objects.filter(
                    preceptorship__id=preceptorship_id
                )
                serializer = TraineePreceptorshipSerializer(trainees, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=len(trainees),
                )
            return self.send_response(
                success=False,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                payload=[],
                code="422",
                description="Enter valid preceptorship Id",
                log_description="",
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Trainee Preceptorship Profile matches the given query.",
            )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Profile doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# add trainee for perceptorship
class TraineePreceptorshipProfileAddView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = TraineePreceptorshipProfile.objects.get(pk=pk)
                serializer = TraineePreceptorshipSerializer(trainee)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            trainees = TraineePreceptorshipProfile.objects.filter(revoke=False)
            serializer = TraineePreceptorshipSerializer(trainees, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=len(trainees),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Trainee Preceptorship Profile matches the given query.",
            )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Trainee Profile doesn't exists",
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
            if type(data) == list:
                serializer = TraineePreceptorshipSerializer(data=data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return self.send_response(
                        success=True,
                        code=f"201",
                        status_code=status.HTTP_201_CREATED,
                        description="trainee is created",
                    )
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
            else:
                serializer = TraineePreceptorshipSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return self.send_response(
                        success=True,
                        code=f"201",
                        status_code=status.HTTP_201_CREATED,
                        description="trainee is created",
                    )
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="trainee doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    """Update Perceptorship traine by trainee id"""

    def put(self, request, pk=None):
        try:
            data = request.data
            saved_trainee = TraineePreceptorshipProfile.objects.get(pk=pk)
            serializer = TraineeUpdatePreceptorshipSerializer(
                instance=saved_trainee, data=data
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="trainee is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except TraineePreceptorshipProfile.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="trainee doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get perceptorship local global activities
"""
# get perceptorship local global activities 
params are area_type:bool and procduct_id= id
"""


class PreceptorshipLocalGlobalView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            area_type = request.query_params.get("area_type", "")
            zone_id = request.user.admin_user.get().zone.id
            product = request.query_params.get("product_id", "")
            query_object = Q(preceptorshipStatus_status__is_active=True)
            query_object &= Q(
                Q(preceptorshipStatus_status__status__code="confirmed")
                | Q(preceptorshipStatus_status__status__code="processing")
                | Q(preceptorshipStatus_status__status__code="pending")
                | Q(preceptorshipStatus_status__status__code="alternative-proposal")
            )

            if area_type == "local":
                preceptorship = Preceptorship.objects.filter(
                    is_global=False, zone__id=zone_id, product__id=product
                )
                preceptorship = preceptorship.filter(query_object).distinct()
                serializer = PreceptorshipViewSerializer(preceptorship, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=preceptorship.count(),
                )
            else:
                preceptorship = Preceptorship.objects.filter(
                    is_global=True, product__id=product
                )
                preceptorship = preceptorship.filter(query_object).distinct()
                serializer = PreceptorshipViewSerializer(preceptorship, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                    count=preceptorship.count(),
                )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Preceptorship matches the given query.",
            )
        except Preceptorship.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# update perceptorship date
class PDateUpdateView(BaseAPIView):
    permission_classes = (AllowAny,)

    def put(self, request, pk=None):
        try:
            saved_proposal = PreceptorshipProposal.objects.get(id=pk)
            serializer = PProposalDateUpdateSerializer(
                instance=saved_proposal, data=request.data
            )
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="porposal Date  is updated",
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
        except PreceptorshipProposal.DoesNotExist:
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


""""perceptorship listing
# perceptorship listing
limit:4
offset:0
column_name:proctor
order:desc
status:code
type_training:code
area:bool
product:id
is_dashboard:bool
"""


class PreceptorshipListingApiView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def sorting_data(self, column_name, order):
        try:
            dash = "" if order.lower() == "asc" else "-"
            if column_name == "id":
                return f"{dash}id"

            if column_name == "date":
                return f"{dash}preceptorshipStatus_status__alter_preceptorship_porposal__start_date"

            if column_name == "cognos_id":
                return f"{dash}hospital__cognos_id"

            if column_name == "product":
                return f"{dash}product__product_name"

            if column_name == "training_type":
                return f"{dash}training_type__name"

            if column_name == "proctor":
                return f"{dash}preceptorshipStatus_status__alter_preceptorship_porposal__preceptorship_porposal__proctors__user__name"

            if column_name == "status":
                return f"{dash}preceptorshipStatus_status__status__id"

            if column_name == "is_global":
                return f"{dash}is_global"

            return f"{dash}{column_name}"
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            order = request.query_params.get("order", "desc")
            search_value = request.query_params.get("search_value", None)
            column_name = request.query_params.get("column_name", None)
            actvity_status = request.query_params.get("status", None)
            type_training = request.query_params.get("type_training", None)
            area = request.query_params.get("area", None)
            product = request.query_params.get("product", None)
            is_dashboard = boolean(request.query_params.get("is_dashboard", ""))

            perceptorship = Preceptorship.objects.all()
            if search_value:
                perceptorship = perceptorship.filter(
                    Q(id__icontains=search_value)
                    | Q(activity_id__icontains=search_value)
                    | Q(user__name__icontains=search_value)
                    | Q(hospital__hospital_name__icontains=search_value)
                    | Q(product__product_name__icontains=search_value)
                    | Q(secondary_product__product_name__icontains=search_value)
                    | Q(training_type__name__icontains=search_value)
                    | Q(types_of_first_training__name__icontains=search_value)
                    | Q(type_advance_training__name__icontains=search_value)
                    | Q(specific_training__name__icontains=search_value)
                    | Q(not_implant_regularly__name__icontains=search_value)
                    | Q(is_global__icontains=search_value)
                    | Q(
                        preceptorshipStatus_status__alter_preceptorship_porposal__preceptorship_porposal__proctors__user__name__icontains=search_value
                    )
                ).distinct()

            query_object = Q(preceptorshipStatus_status__is_active=True)

            if product:
                query_object &= Q(product__id=product)

            if area:
                query_object &= Q(is_global=boolean(area))

            if actvity_status:
                query_object &= Q(
                    preceptorshipStatus_status__status__code=actvity_status
                )

            if type_training:
                query_object &= Q(training_type__code=type_training)

            perceptorship = (
                perceptorship.filter(query_object)
                .order_by(self.sorting_data(column_name, order))
                .distinct()
            )

            if is_dashboard:
                perceptorship = perceptorship.filter(is_global=True)
                perceptorship = perceptorship.exclude(
                    preceptorshipStatus_status__status__code="closed"
                )

            serializer = PreceptorshipViewListingSerializer(
                perceptorship[offset : offset + limit], many=True
            )
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Perceptorship Details",
                log_description="",
                count=perceptorship.count(),
            )
        except Preceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Perceptorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# Get add, update invoice for perceptorship
class InvoicePerceptorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # Get  invoice for perceptorship by  perceptorship
    def get(self, request, pk=None):
        try:
            activityid = request.query_params.get("activity_id", "")
            if pk is not None:
                proctorship_invoice = InvoicePerceptorship.objects.filter(
                    preceptorship__id=pk
                )
                serializer = InvoicePerceptorshipSerializer(
                    proctorship_invoice, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            if activityid:
                proctorship_invoice = InvoicePerceptorship.objects.filter(
                    preceptorship__id=activityid
                )
                serializer = InvoicePerceptorshipSerializer(
                    proctorship_invoice, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            proctorship_invoices = InvoicePerceptorship.objects.all()
            serializer = InvoicePerceptorshipSerializer(proctorship_invoices, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctorship_invoices.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No ProctorShip Invoice matches the given query.",
            )
        except InvoicePerceptorship.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="ProctorShip doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # Post perceptorship invoice
    def post(self, request):
        try:
            data = request.data
            serializer = InvoicePerceptorshipSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                perceptership(Preceptorship.objects.get(id=data["preceptorship_id"]))

                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Preceptorship is created",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )

        except InvoicePerceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # Update  invoice for perceptorship by  perceptorship
    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = InvoicePerceptorship.objects.get(
                preceptorship__id=pk
            )
            serializer = InvoicePerceptorshipUpdateSerializer(
                instance=proctorship_attendance, data=data
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="File is replaced",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except InvoicePerceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="AttendanceForm doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get add, update for perceptorship
class AttendanceFormPerceptorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            activityid = request.query_params.get("activity_id", "")

            if pk is not None:
                proctorship_attendance = AttendanceFormPerceptorship.objects.filter(
                    preceptorship__id=pk
                )
                serializer = AttendancePerceptorShipSerailizers(
                    proctorship_attendance, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            if activityid:
                proctorship_attendance = AttendanceFormPerceptorship.objects.filter(
                    preceptorship__id=activityid
                )
                serializer = AttendancePerceptorShipSerailizers(
                    proctorship_attendance, many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )

            proctorship_attendance = AttendanceFormPerceptorship.objects.all()
            serializer = AttendancePerceptorShipSerailizers(
                proctorship_attendance, many=True
            )
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="",
                description="Details of serializer",
                log_description="",
                count=proctorship_attendance.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No ProctorShip Invoice matches the given query.",
            )
        except AttendanceFormPerceptorship.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="ProctorShip doesn't exists",
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
            serializer = AttendancePerceptorShipSerailizers(data=data)
            if serializer.is_valid():
                serializer.save()
                perceptership(Preceptorship.objects.get(id=data["preceptorship_id"]))

                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Preceptorship is created",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
        except AttendanceFormPerceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Preceptorship doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = AttendanceFormPerceptorship.objects.get(
                preceptorship__id=pk
            )
            serializer = AttendanceFormPerceptorshipUpdateSerailizers(
                instance=proctorship_attendance, data=data
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="File is replaced",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except AttendanceFormPerceptorship.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="AttendanceForm doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class StatusPTestingView(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data
            serializer = PreceptorshipStatusTestingSerializer(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="status is created",
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
        except PreceptorshipStatus.DoesNotExist:
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
