from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.pagination import CustomPagination
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin
from api.proctors.models import Proctors
from api.proctors.serializers import ProctorsNotAvailalbeViewSerializer
from api.speakingevent.models import (
    AttendanceFormSpeakingEvent,
    CognosId,
    Event,
    EventStatus,
    Speaker,
    SpeakingEvent,
    SpeakingEventFeedBack,
)
from api.speakingevent.serializers import (
    AgendaSerailizers,
    AttendanceEventSerailizers,
    AttendanceFormSpeakingEventUpdateSerailizers,
    AttendanceSpeakingEventSerailizers,
    CognosIdSerailizers,
    CognosIdUpdateSerailizers,
    CognosIdViewSerailizers,
    EventSerializer,
    EventViewListingSerializer,
    EventViewSerializer,
    MeetingDocsSerailizers,
    MeetingDocsStatusSerailizers,
    SignedLetterSerializer,
    SoeakingEventAttendanceSerailizers,
    SpeakerSerializer,
    SpeakerUpdateSerializer,
    SpeakingEventFeedBackSerializers,
    SpeakingEventSerializer,
    StatusAddSerializer,
)
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean
from cspro.utils import check, check_event, check_masterproctorship, check_perceptorship


# add and get dteails of speaking event
class SpeakingEventView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                event = Event.objects.get(pk=pk)
                serializer = EventViewSerializer(event)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )
            event = Event.objects.all()
            serializer = EventViewSerializer(event, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Details of serializer",
                log_description="",
                count=event.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Event matches the given query.",
            )
        except Event.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
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
            data._mutable = True
            data["user_id"] = request.user.id
            serializer = EventSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": data},
                    status_code=status.HTTP_201_CREATED,
                    description="Event is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
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
            saved_event = Event.objects.get(id=id)
            data = request.data
            serializer = EventSerializer(instance=saved_event, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Event is updated",
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
                description="No Event matches the given query.",
            )
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class SpeakerView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            event_id = request.query_params.get("event_id", "")
            if pk is not None:
                event = Speaker.objects.get(pk=pk)
                serializer = SpeakerSerializer(event)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )

            if event_id:
                event = Speaker.objects.filter(event__id=event_id)
                serializer = SpeakerSerializer(event, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )

            event = Speaker.objects.all()
            serializer = SpeakerSerializer(event, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Details of serializer",
                log_description="",
                count=event.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Speaker matches the given query.",
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaker doesn't exists",
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
            serializer = SpeakerSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                validate_data["user"] = request.user
                serializer.save(**validate_data)
                data = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": data},
                    status_code=status.HTTP_201_CREATED,
                    description="Speaker is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaker doesn't exists",
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
            data = request.data
            saved_data = Speaker.objects.get(id=pk)
            serializer = SpeakerUpdateSerializer(instance=saved_data, data=data)
            if serializer.is_valid():
                serializer.save()
                data = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": data},
                    status_code=status.HTTP_201_CREATED,
                    description="Speaker is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaker doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class SpeakingEventUpdateView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def post(self, request):
        try:
            data = request.data
            data["user_id"] = request.user.id
            serializer = SpeakingEventSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = serializer.instance.id
                return self.send_response(
                    success=True,
                    code=f"201",
                    payload={"id": data},
                    status_code=status.HTTP_201_CREATED,
                    description="Event is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# speaking event status add, get  view
class StatusSpeakingView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get("activity_id", "")
            if activity_id:
                activity_status = EventStatus.objects.filter(
                    event__id=activity_id
                ).order_by("timestamp")
                serializer = StatusAddSerializer(activity_status, many=True)
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
        except EventStatus.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event Status doesn't exists",
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
            data["user_id"] = request.user.id
            start_date = str(
                SpeakingEvent.objects.filter(event_status__event__id=data["event_id"])
                .latest("created_on")
                .start_date
            )
            end_date = str(
                SpeakingEvent.objects.filter(event_status__event__id=data["event_id"])
                .latest("created_on")
                .end_date
            )
            available_proctor = []
            not_available_proctor = []
            if data["status"] == "confirmed":
                proctors = Speaker.objects.filter(
                    event__id=data["event_id"], status=True, revoke=False
                )
                if proctors:
                    for each in proctors:
                        if each.proctor:
                            if not check(each.proctor.id, start_date, end_date):
                                if not check_perceptorship(
                                    each.proctor.id, start_date, end_date
                                ):
                                    if not check_masterproctorship(
                                        each.proctor.id, start_date, end_date
                                    ):
                                        if not check_event(
                                            each.proctor.id, start_date, end_date
                                        ):
                                            available_proctor.append(each.proctor.id)
                                        else:
                                            not_available_proctor.append(
                                                each.proctor.id
                                            )
                                    else:
                                        not_available_proctor.append(each.proctor.id)
                                else:
                                    not_available_proctor.append(each.proctor.id)
                            else:
                                not_available_proctor.append(each.proctor.id)
                        else:
                            serializer = StatusAddSerializer(data=data)
                            if serializer.is_valid():
                                saved_status = serializer.save()
                                return self.send_response(
                                    success=True,
                                    code=f"201",
                                    status_code=status.HTTP_201_CREATED,
                                    description="status is created",
                                )
                    if available_proctor and not not_available_proctor:
                        Speaker.objects.filter(
                            event__id=data["event_id"],
                            proctor__id__in=available_proctor,
                            revoke=False,
                        )
                        serializer = StatusAddSerializer(data=data)
                        if serializer.is_valid():
                            saved_status = serializer.save()
                            return self.send_response(
                                success=True,
                                code=f"201",
                                status_code=status.HTTP_201_CREATED,
                                description="status is created",
                            )
                    else:
                        proct = Proctors.objects.filter(id__in=not_available_proctor)
                        des = "These Proctors are not available"
                        for each in proct:
                            des = des + f" {each.user.name}"
                        return self.send_response(
                            code=f"422",
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            description=des,
                        )
                else:
                    return self.send_response(
                        code=f"422",
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        description="Confirm speech profile before confirmation of activity",
                    )
            serializer = StatusAddSerializer(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Event Status is created",
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
        except EventStatus.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event Status doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# add signed letter of speaker
class AddSiginedLetterView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def put(self, request, pk=None):
        try:
            data = request.data
            saved_data = Speaker.objects.get(id=pk)
            serializer = SignedLetterSerializer(instance=saved_data, data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Speaker is created",
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
        except Speaker.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaker doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# add agenda letter of event
class UploadAgenda(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def put(self, request, pk=None):
        try:
            data = request.data
            saved = Event.objects.get(id=pk)
            serializer = AgendaSerailizers(instance=saved, data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Event is created",
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
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# listing of speaking event
class SpeakingEventListing(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def sorting_data(self, column_name, order):
        try:

            dash = "" if order.lower() == "asc" else "-"
            if column_name == "id":
                return f"{dash}id"

            if column_name == "event_name":
                return f"{dash}event_status_event__event_status__event_name"

            if column_name == "event_location":
                return f"{dash}event_status_event__event_status__event_location"

            if column_name == "status":
                return f"{dash}event_status_event__status__id"

            return f"{dash}{column_name}"
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            search_value = request.query_params.get("search_value", None)
            column_name = request.query_params.get("column_name", "id")
            actvity_status = request.query_params.get("status", None)
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            order = request.query_params.get("order", "desc")
            area = request.query_params.get("area", None)
            is_dashboard = boolean(request.query_params.get("is_dashboard", ""))

            event = Event.objects.all()
            if search_value:
                event = event.filter(
                    Q(id__icontains=search_value)
                    | Q(activity_id__icontains=search_value)
                    | Q(event_country__name__icontains=search_value)
                    | Q(
                        event_status_event__event_status__event_name__icontains=search_value
                    )
                    | Q(event_status_event__user__name__icontains=search_value)
                    | Q(event_status_event__status__name__icontains=search_value)
                    | Q(event_status_event__reason__icontains=search_value)
                    | Q(event_speaker__proctor__user__name__icontains=search_value)
                    | Q(event_speaker__name_employee__icontains=search_value)
                    | Q(event_speaker__other_proctor__icontains=search_value)
                    | Q(
                        event_status_event__event_status__event_name__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__event_type__name__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__event_location__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__solution__solution__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__participants__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__audience_type__audience__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__audience_region__region__icontains=search_value
                    )
                    | Q(
                        event_status_event__event_status__start_date__icontains=search_value
                    )
                ).distinct()

            query_object = Q(event_status_event__is_active=True)

            if area:
                query_object &= Q(is_global=boolean(area))

            if actvity_status:
                query_object &= Q(event_status_event__status__code=actvity_status)

            event = (
                event.filter(query_object)
                .order_by(self.sorting_data(column_name, order))
                .distinct()
            )

            if is_dashboard:
                event = event.filter(is_global=True)
                event = event.exclude(event_status_event__status__code="closed")
            serializer = EventViewListingSerializer(
                event[offset : offset + limit], many=True
            )
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Speaking Event Details",
                log_description="",
                count=event.count(),
            )
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaking Event doesn't exists",
            )
        except FieldError as e:
            return self.send_response(
                code=f"500",
                description=f"{e} Cannot resolve keyword given in order_by into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# confirm speaker for event
class ConfirmSpeakerView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                speaker = Speaker.objects.get(id=pk)
                speaker.status = True
                speaker.save()
                return self.send_response(
                    description="speaker is activate successfuly",
                    success=True,
                    status_code=status.HTTP_200_OK,
                    code="200",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="speaker doesn't found",
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="speaker doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# revoke speaker
class RevokeSpeakerView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = Speaker.objects.get(id=pk)
                trainee.revoke = True
                trainee.save()
                return self.send_response(
                    description="speaker is is revoked successfuly",
                    success=True,
                    status_code=status.HTTP_200_OK,
                    code="200",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="speaker Profile doesn't found",
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="speaker Profile doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# add feedback of speaking event
class FeedBackSpeakingEvent(BaseAPIView):
    permission_classes = (AllowAny,)

    def sorting_feedback(self, column_name, order):
        try:

            dash = "" if order.lower() == "asc" else "-"
            if column_name == "id":
                return f"{dash}id"

            if column_name == "specialty":
                return f"{dash}specialty__name"

            if column_name == "country":
                return f"{dash}country__name"

            if column_name == "rate_event":
                return f"{dash}rate_event"

            if column_name == "rate_logistic_organization":
                return f"{dash}rate_logistic_organization"

            if column_name == "scientific_content":
                return f"{dash}scientific_content"

            return f"{dash}{column_name}"
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            event_id = request.query_params.get("event_id", "")
            search_value = request.query_params.get("search_value", None)
            column_name = request.query_params.get("column_name", "id")
            limit = int(request.query_params.get("limit", 10))
            offset = int(request.query_params.get("offset", 0))
            order = request.query_params.get("order", "desc")

            if event_id:
                event_feedback = SpeakingEventFeedBack.objects.filter(
                    event__id=event_id
                )
                if search_value:
                    event_feedback = event_feedback.filter(
                        Q(event__event_country__name__icontains=search_value)
                        | Q(speaker__proctor__user__name__icontains=search_value)
                        | Q(specialty__name__icontains=search_value)
                        | Q(country__name__icontains=search_value)
                    ).distinct()

                event_feedback = event_feedback.order_by(
                    self.sorting_feedback(column_name, order)
                )
                serializer = SpeakingEventFeedBackSerializers(
                    event_feedback[offset : offset + limit], many=True
                )
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            if pk:
                activity_status = SpeakingEventFeedBack.objects.get(id=pk)
                serializer = SpeakingEventFeedBackSerializers(activity_status)
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
                description="Enter Valid Speaking Id",
            )
        except IntegrityError as i:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(i),
            )
        except SpeakingEventFeedBack.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaking Event FeedBack doesn't exists",
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
            serializer = SpeakingEventFeedBackSerializers(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Speaking Event FeedBack is created",
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
        except SpeakingEventFeedBack.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaking Event FeedBack doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


# add attendance form of speaking event
class AttendanceFormSpeakingEventView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctorship_attendance = AttendanceFormSpeakingEvent.objects.filter(
                    event__id=pk
                )
                serializer = AttendanceSpeakingEventSerailizers(
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
            proctorship_attendance = AttendanceFormSpeakingEvent.objects.all()
            serializer = AttendanceSpeakingEventSerailizers(
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
                description="No SpeakingEvent matches the given query.",
            )
        except AttendanceFormSpeakingEvent.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="SpeakingEvent doesn't exists",
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
            data._mutable = True
            data["user_id"] = request.user.id
            type = SpeakingEvent.objects.filter(
                event_status__event__id=int(data["event_id"])
            ).latest("created_on")
            if (
                type.event_type.code
                == "speaking-at-corcym-webinar-hcp-peer-to-peer-event"
            ):
                if Event.objects.get(id=int(data["event_id"])).meeting_docs:
                    serializer = AttendanceEventSerailizers(data=data)
                    if serializer.is_valid():
                        saved = serializer.save()
                        return self.send_response(
                            success=True,
                            code=f"201",
                            status_code=status.HTTP_201_CREATED,
                            description="Attendance Speaking Event is created and Status is closed",
                        )
                else:
                    serializer = AttendanceSpeakingEventSerailizers(data=data)
                    if serializer.is_valid():
                        saved = serializer.save()
                        return self.send_response(
                            success=True,
                            code=f"201",
                            status_code=status.HTTP_201_CREATED,
                            description="Upload Meeting Docs for closing event status",
                        )

            else:
                serializer = AttendanceEventSerailizers(data=data)
                if serializer.is_valid():
                    saved = serializer.save()

                    return self.send_response(
                        success=True,
                        code=f"201",
                        status_code=status.HTTP_201_CREATED,
                        description="Attendance Speaking Event is created and status is closed",
                    )
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
        except AttendanceFormSpeakingEvent.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Attendance Speaking Event doesn't exists",
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
            proctorship_attendance = AttendanceFormSpeakingEvent.objects.get(
                event__id=pk
            )
            serializer = AttendanceFormSpeakingEventUpdateSerailizers(
                instance=proctorship_attendance, data=data
            )
            if serializer.is_valid():
                serializer.save()
                if not Event.objects.get(id=pk, meeting_docs__isnull=False):
                    pass
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
        except AttendanceFormSpeakingEvent.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Attendance Form doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# cognos id of event
class CongosIdViewForm(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctorship_attendance = CognosId.objects.filter(event__id=pk)
                serializer = CognosIdViewSerailizers(proctorship_attendance, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            proctorship_attendance = CognosId.objects.all()
            serializer = CognosIdViewSerailizers(proctorship_attendance, many=True)
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
                description="No CognosId Invoice matches the given query.",
            )
        except CognosId.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="CognosId doesn't exists",
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
            serializer = CognosIdSerailizers(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="CognosId is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except CognosId.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="CognosId doesn't exists",
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
            proctorship_attendance = CognosId.objects.get(event__id=pk)
            serializer = CognosIdUpdateSerailizers(
                instance=proctorship_attendance, data=data
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="CognosId is replaced",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except CognosId.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="CognosId doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class UploadMeetingDocs(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def put(self, request, pk=None):
        try:
            data = request.data
            saved = Event.objects.get(id=pk)
            try:
                if AttendanceFormSpeakingEvent.objects.get(event__id=pk):
                    data["user_id"] = request.user.id
                    serializer = MeetingDocsStatusSerailizers(instance=saved, data=data)
                    if serializer.is_valid():
                        saved_status = serializer.save()
                        return self.send_response(
                            success=True,
                            code=f"201",
                            status_code=status.HTTP_201_CREATED,
                            description="Meetinf docs is created and status is closed",
                        )
                    return self.send_response(
                        code=f"422",
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        description=serializer.errors,
                    )

            except:
                serializer = MeetingDocsSerailizers(instance=saved, data=data)
                if serializer.is_valid():
                    saved_status = serializer.save()
                    return self.send_response(
                        success=True,
                        code=f"201",
                        status_code=status.HTTP_201_CREATED,
                        description="Meeting Docs is created",
                    )
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
        except Event.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            print(e)
            return self.send_response(code=f"500", description=e)


class SpeakingEventWithOutAuthView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                event = Event.objects.get(pk=pk)
                serializer = EventViewSerializer(event)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )
            event = Event.objects.all()
            serializer = EventViewSerializer(event, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Details of serializer",
                log_description="",
                count=event.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Event matches the given query.",
            )
        except Event.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class SpeakerUnknownView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            event_id = request.query_params.get("event_id", "")
            if pk is not None:
                event = Speaker.objects.get(pk=pk)
                serializer = SpeakerSerializer(event)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )

            if event_id:
                event = Speaker.objects.filter(event__id=event_id)
                serializer = SpeakerSerializer(event, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="200",
                    description="Details of serializer",
                    log_description="",
                )

            event = Speaker.objects.all()
            serializer = SpeakerSerializer(event, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Details of serializer",
                log_description="",
                count=event.count(),
            )
        except ObjectDoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="No Speaker matches the given query.",
            )
        except Speaker.DoesNotExist:
            return self.send_response(
                code="422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Speaker doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)
