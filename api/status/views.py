from django.core.exceptions import FieldError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status

from api.masterproctorship.models import MasterProctorship, MasterProctorshipProposal, MasterProctorshipProctors
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin, IsOauthAuthenticated
from api.preceptorship.models import PreceptorshipProctors, PreceptorshipProposal, Preceptorship
from api.proctors.models import Proctors
from api.proctorship.models import Proctorship
from api.speakingevent.models import Speaker, SpeakingEvent, Event
from api.status.models import Status, Proposal, StatusConstantData, ProctorshipProctors
from api.views import BaseAPIView
from rest_framework.permissions import AllowAny
from api.status.serializers import StatusSerializer, AlternativeSerializer, ConstantStatusDataSerializer, \
    StatusViewSerializer, ProposalDateUpdateSerializer, StatusTestingSerializer


# Create your views here.
from cspro.utils import check, check_perceptorship, check_masterproctorship, check_event

# add and get status of proctorship
class StatusView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin, )

    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if activity_id:
                activity_status = Status.objects.filter(proctorship_activity__id= activity_id).order_by("timestamp")
                serializer = StatusViewSerializer(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[], code='422',description='Enter Valid ProctorshipId')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Status.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request):
        try:
            data = request.data
            data['user_id'] =request.user.id
            start_date = str(Proposal.objects.filter(status__proctorship_activity__id = data["proctorship_activity_id"]).latest("created_on").start_date)
            end_date = str(Proposal.objects.filter(
                status__proctorship_activity__id=data["proctorship_activity_id"]).latest("created_on").end_date)
            if data["status"] == "confirmed":
                proctors = Status.objects.filter(proctorship_activity__id = data["proctorship_activity_id"]).filter(alter_proctorship_porposal__isnull=False).latest('created_on').alter_proctorship_porposal.filter(proctor_porposal__isnull=False).latest('created_on').proctor_porposal.all()
                for each in proctors:
                    if not check(each.proctors.id, start_date, end_date):
                        if not check_perceptorship(each.proctors.id, start_date, end_date):
                            if not check_masterproctorship(each.proctors.id, start_date, end_date):
                                if not check_event(each.proctors.id, start_date, end_date):
                                    proctors.update(status=False)
                                    each.status = True
                                    each.save()
                                    serializer = StatusSerializer(data=data)
                                    if serializer.is_valid():
                                        saved_status = serializer.save()
                                        return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                                                  description='status is created')
                                    break
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="None of selected proctors is available")

            serializer = StatusSerializer(data = data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='status is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Status.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class AlternativePorposalView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            activity_status = Proposal.objects.filter(proctorship_activity__id= activity_id)
            serializer = AlternativeSerializer(activity_status, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Proposal.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Proposal doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


    def post(self, request):
        try:
            data = request.data
            serializer = AlternativeSerializer(data = data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Proposal is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Proposal.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Proposal doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


# get status constants
class ConstantStatusDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    def get(self, request, pk=None):
        try:
            constant_data = StatusConstantData.objects.all()
            serializer =  ConstantStatusDataSerializer(constant_data, many = True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',description='Details of serializer', log_description='')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Proposal.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Status Constant Data doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# update date after waiting for docs
class DateUpdateView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    def put(self, request, pk=None):
        try:
            saved_proposal = Proposal.objects.get(id = pk)
            serializer = ProposalDateUpdateSerializer(instance= saved_proposal, data = request.data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='porposal Date  is updated')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Proposal.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Proposal doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class StatusTestingView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    def post(self, request):
        try:
            data = request.data
            serializer = StatusTestingSerializer(data = data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='status is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Status.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Proctor doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

