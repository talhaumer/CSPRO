from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.pagination import CustomPagination
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin, IsOauthAuthenticated
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from api.status.models import StatusConstantData
from api.views import BaseAPIView
from api.masterproctorship.models import MasterProctorship, MasterProctorShipConstantData, MasterProctorshipStatus, \
    MasterProctorshipTraineeProfile, MasterProctorshipProctorReport, MasterProctorshipFeedback, \
    MasterProctorshipProposal, AttendanceFormMasterProctorShip, InvoiceMasterProctorShip
from api.masterproctorship.serializers import MasterProctorshipSerializer, MasterProctorShipConstantDataSerializers, \
    MasterProctorshipViewSerializer, MasterProctorshipStatusSerializer, MasterProctorshipStatusViewSerializer, \
    TraineeMasterProctorshipSerializer, MasterProctorshipProctorReportSerializers, \
    TraineeMasterUpdateProctorshipSerializer, MasterProctorshipProctorUpdateReportSerializers, \
    MasterProctorshipFeedbackSerializers, MasterProctorshipUpdateFeedbackSerializers, MProposalDateUpdateSerializer, \
    MasterProctorshipListingSerializer, InvoiceMasterProctorshipSerializer, AttendanceFormMasterProctorShipSerailizers, \
    MasterProctorshipStatusTestingSerializer, AttendanceFormMasterProctorShipUpdateSerailizers, \
    InvoiceMasterProctorShipUpdateSerializer

# Create your views here.
from cspro.utils import check, check_perceptorship, check_masterproctorship, check_event, master_proctorship

# add and get details of MAster Proctorship view
class MasterProctorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get details of MAsterProctorship by id in url
    def get(self, request, pk=None):
        try:
            if pk is not None:
                masterproctorship = MasterProctorship.objects.get(pk=pk)
                serializer = MasterProctorshipViewSerializer(masterproctorship)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            masterproctorship = MasterProctorship.objects.all()
            serializer = MasterProctorshipSerializer(masterproctorship, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='',
                                      count=len(masterproctorship))
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No MasterProctorship matches the given query.")
        except MasterProctorship.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
    """
        add masterproctorship
        country_id: countries instance 
        hospital_id:hospital instance 
        proctors_id:product
    """
    def post(self, request):
        try:
            data = request.data
            data['user_id'] = request.user.id
            serializer = MasterProctorshipSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                data = serializer.instance.id
                return self.send_response(success=True, code=f'201', payload={"id": data},
                                          status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MasterProctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, pk=None):
        try:
            id = pk
            saved_masterproctorship = MasterProctorship.objects.get(id=id)
            data = request.data
            serializer = MasterProctorshipSerializer(instance=saved_masterproctorship, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No MasterProctorship matches the given query.")
        except MasterProctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get constant data used for master proctorship
class MasterProctorshipConstantDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                masterproctorship = MasterProctorShipConstantData.objects.get(pk=pk)
                serializer = MasterProctorShipConstantDataSerializers(masterproctorship)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            masterproctorship = MasterProctorShipConstantData.objects.all()
            serializer = MasterProctorShipConstantDataSerializers(masterproctorship, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='',
                                      count=masterproctorship.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No MasterProctorShip Constant Data matches the given query.")
        except MasterProctorShipConstantData.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorShip Constant Data doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get,and add masterproctorship status
class MasterProctorshipStatusView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    # get masterproctorship status by masterproctorship id
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if activity_id:
                activity_status = MasterProctorshipStatus.objects.filter(
                    master_proctorship_activity__id=activity_id).order_by("timestamp")
                serializer = MasterProctorshipStatusViewSerializer(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter Valid MasterProctorshipId')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # add masterproctorship status a
    def post(self, request):
        try:
            data = request.data
            data['user_id'] = request.user.id
            start_date = str(
                MasterProctorshipProposal.objects.filter(
                    status__master_proctorship_activity__id=data["master_proctorship_activity_id"]).latest(
                    "created_on").start_date)
            end_date = str(MasterProctorshipProposal.objects.filter(
                status__master_proctorship_activity__id=data["master_proctorship_activity_id"]).latest(
                "created_on").end_date)

            if data["status"] == "confirmed":
                proctors = MasterProctorshipStatus.objects.filter(
                    master_proctorship_activity__id=data["master_proctorship_activity_id"]).filter(
                    alter_master_proctorship_porposal__isnull=False).latest(
                    'created_on').alter_master_proctorship_porposal.filter(
                    master_proctorship_porposal__isnull=False).latest('created_on').master_proctorship_porposal.all()
                for each in proctors:
                    if not check(each.proctors.id, start_date, end_date):
                        if not check_perceptorship(each.proctors.id, start_date, end_date):
                            if not check_masterproctorship(each.proctors.id, start_date, end_date):
                                if not check_event(each.proctors.id, start_date, end_date):
                                    proctors.update(status=False)
                                    each.status = True
                                    each.save()
                                    serializer = MasterProctorshipStatusSerializer(data=data)
                                    if serializer.is_valid():
                                        saved_status = serializer.save()
                                        return self.send_response(success=True, code=f'201',
                                                                  status_code=status.HTTP_201_CREATED,
                                                                  description='status is created')
                                    break
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="None of selected proctors is available")
            serializer = MasterProctorshipStatusSerializer(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Status is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# approce masterproctorship traineee
class ApproveMasterProctorshipTraineeView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MasterProctorshipTraineeProfile.objects.get(id=pk)
                trainee.status = True
                trainee.save()
                return self.send_response(description="trainee is activate successfuly", success=True,
                                          status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't found")
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

# revoke masterproctorship traineee
class RevokeMasterProctorshipTraineeProfileView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MasterProctorshipTraineeProfile.objects.get(id=pk)
                trainee.revoke = True
                trainee.save()
                return self.send_response(description="MasterProctorship Trainee Profile is is revoked successfuly",
                                          success=True, status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile Profile doesn't found")
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

# get master proctorship traineee
class MasterProctorshipTraineeProfileView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            master_proctorship_id = request.query_params.get('activity_id', '')
            if master_proctorship_id:
                trainees = MasterProctorshipTraineeProfile.objects.filter(master_proctorship__id=master_proctorship_id)
                serializer = TraineeMasterProctorshipSerializer(trainees, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='',
                                          count=len(trainees))
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter valid MasterProctorship Id', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No MasterProctorship Trainee Profile matches the given query.")
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# add masterporctorship traineee
class MasterProctorshipTraineeProfileAddView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MasterProctorshipTraineeProfile.objects.get(pk=pk)
                serializer = TraineeMasterProctorshipSerializer(trainee)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            trainees = MasterProctorshipTraineeProfile.objects.filter(revoke=False)
            serializer = TraineeMasterProctorshipSerializer(trainees, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='', count=trainees.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No MasterProctorship Trainee Profile matches the given query.")
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
    # Add masterproctorship trainee
    def post(self, request):
        try:
            data = request.data
            serializer = TraineeMasterProctorshipSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Trainee Profile is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
    # Update masterproctorship trainee by trainee id
    def put(self, request, pk=None):
        try:
            data = request.data
            saved_trainee = MasterProctorshipTraineeProfile.objects.get(pk=pk)
            serializer = TraineeMasterUpdateProctorshipSerializer(instance=saved_trainee, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Trainee Profile is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MasterProctorshipTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# add masterproctorship report view
class MasterProctorshipAddReportView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get masterproctorship report view by MP id
    def get(self, request, pk=None):
        try:
            if pk:
                activity_status = MasterProctorshipProctorReport.objects.filter(
                    master_proctorship_trainee__master_proctorship__id=pk)
                serializer = MasterProctorshipProctorReportSerializers(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter Valid MasterProctorshipId')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipProctorReport.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Proctor Report doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
    # post masterproctorship report
    def post(self, request):
        try:
            data = request.data
            data['user_id'] = request.user.id
            serializer = MasterProctorshipProctorReportSerializers(data=data)
            master_proctorship_id = MasterProctorship.objects.get(trainee_master_proctorship__id = data["master_proctorship_trainee_id"])
            if serializer.is_valid():
                saved_status = serializer.save()
                master_proctorship(master_proctorship_id)
                # count = MasterProctorshipTraineeProfile.objects.filter(
                #     master_proctorship__id=master_proctorship_id.id, revoke=False).count()
                # if InvoiceMasterProctorShip.objects.filter(master_proctorship__id=master_proctorship_id.id) and  MasterProctorshipFeedback.objects.filter(
                #             master_proctorship_activity__id=master_proctorship_id.id) and AttendanceFormMasterProctorShip.objects.filter(
                #                 master_proctorship__id=master_proctorship_id.id) and  count == MasterProctorshipProctorReport.objects.filter(
                #                         master_proctorship_trainee__master_proctorship__id=master_proctorship_id.id).count():
                #     MasterProctorshipStatus.objects.filter(
                #         master_proctorship_activity__id=master_proctorship_id.id).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'master_proctorship_activity':MasterProctorship.objects.get(id = master_proctorship_id),
                #                    'user': request.user}
                #     status_data = MasterProctorshipStatus.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201',
                #                                               status_code=status.HTTP_201_CREATED,
                #                                               description='MasterProctorship Proctor Report is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Proctor Report is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipProctorReport.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Proctor Report doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

    # update masterproctorship report view by MP id
    def put(self, request, pk=None):
        try:
            data = request.data
            saved_report = MasterProctorshipProctorReport.objects.get(master_proctorship_trainee__id=pk)
            serializer = MasterProctorshipProctorUpdateReportSerializers(instance=saved_report, data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Master MasterProctorship Proctor Report Updated')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipProctorReport.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Proctor Report doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

# add master proctorship feedback view
class MasterProctorshipFeedbackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get masterproctorship feedback view by MP id
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get("activity_id", "")
            if pk:
                activity_status = MasterProctorshipFeedback.objects.filter(master_proctorship_activity__id=pk)
                serializer = MasterProctorshipFeedbackSerializers(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            if activity_id:
                activity_status = MasterProctorshipFeedback.objects.filter(master_proctorship_activity__id=activity_id)
                serializer = MasterProctorshipFeedbackSerializers(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter Valid MasterProctorship Feedback')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
    # post masterproctorship feedback report

    def post(self, request):
        try:
            data = request.data
            serializer = MasterProctorshipFeedbackSerializers(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                master_proctorship(MasterProctorship.objects.get(id= data["master_proctorship_activity_id"]))
                # count = MasterProctorshipTraineeProfile.objects.filter(
                #     master_proctorship__id=data["master_proctorship_activity_id"]).count()
                # if count == MasterProctorshipProctorReport.objects.filter(
                #         master_proctorship_trainee__master_proctorship__id=data["master_proctorship_activity_id"]).count() and InvoiceMasterProctorShip.objects.filter(master_proctorship__id=data["master_proctorship_activity_id"]) and  AttendanceFormMasterProctorShip.objects.filter(
                #                 master_proctorship__id=data["master_proctorship_activity_id"]):
                #     MasterProctorshipStatus.objects.filter(
                #         master_proctorship_activity__id=data["master_proctorship_activity_id"]).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'master_proctorship_activity':MasterProctorship.objects.get(id= data["master_proctorship_activity_id"]),
                #                    'user': request.user}
                #     status_data = MasterProctorshipStatus.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='MasterProctorship Feedback is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Feedback is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)
    # update masterproctorship feedback report view by MP id
    def put(self, request, pk=None):
        try:
            data = request.data
            saved_report = MasterProctorshipFeedback.objects.get(master_proctorship_activity__id=pk)
            serializer = MasterProctorshipUpdateFeedbackSerializers(instance=saved_report, data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Feedback Updated')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# update date of masterproctorship view
class MDateUpdateView(BaseAPIView):
    permission_classes = (AllowAny,)

    def put(self, request, pk=None):
        try:
            saved_proposal = MasterProctorshipProposal.objects.get(id=pk)
            serializer = MProposalDateUpdateSerializer(instance=saved_proposal, data=request.data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Proposal Date  is updated')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipProposal.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Proposal doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)

""" masterproctorship listing view
# masterproctorship listing view
limit:10
offset:0
column_name:status
order:
status:code
type_training:code"""
class MasterProctorshipListingApiView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticated,)
    pagination_class = CustomPagination

    def sorting_data(self, column_name, order):
        try:
            dash = '' if order.lower() == 'asc' else '-'
            if column_name == 'id':
                return f'{dash}id'

            if column_name == 'cognos_id':
                return f'{dash}hospital__cognos_id'

            if column_name == 'hospital':
                return f'{dash}hospital__hospital_name'

            if column_name == 'training_type':
                return f'{dash}master_proctorship_type__name'

            if column_name == 'status':
                return f'{dash}master_proctorship_status__status'

            if column_name == 'proctor':
                return f'{dash}master_proctorship_status__alter_master_proctorship_porposal__master_proctorship_porposal__proctors__user__name'

            return f'{dash}{column_name}'
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            order = request.query_params.get('order', 'desc')
            search_value = request.query_params.get('search_value', None)
            column_name = request.query_params.get('column_name', None)
            # rev = request.query_params.get('order', '')
            actvity_status = request.query_params.get('status', None)
            type_training = request.query_params.get('type_training', None)

            master_proctorship = MasterProctorship.objects.all()
            if search_value:
                master_proctorship = master_proctorship.filter(Q(id__icontains=search_value) |
                                                               Q(activity_id__icontains=search_value) |
                                                               Q(user__name__icontains=search_value) |
                                                               Q(hospital__hospital_name__icontains=search_value) |
                                                               Q(country__name__icontains=search_value) |
                                                               Q(hotel__icontains=search_value) |
                                                               Q(master_proctorship_type__name__icontains=search_value) |
                                                               Q(number_of_cases__icontains=search_value) |
                                                               Q(transplant_time__icontains=search_value) |
                                                               Q(master_proctorship_status__alter_master_proctorship_porposal__master_proctorship_porposal__proctors__user__name__icontains=search_value)).distinct()

            query_object = Q(master_proctorship_status__is_active=True)

            if actvity_status:
                query_object &= Q(master_proctorship_status__status__code=actvity_status)

            if type_training:
                query_object &= Q(master_proctorship_type__code=type_training)

            master_proctorship = master_proctorship.filter(query_object).order_by(
                self.sorting_data(column_name, order)).distinct()
            # master_proctorship = self.sorting_data(master_proctorship, column_name)
            # if rev == 'true':
            #   master_proctorship =  master_proctorship.reverse()
            # results = self.paginate_queryset(master_proctorship, request, view=self)
            serializer = MasterProctorshipListingSerializer(master_proctorship[offset: offset + limit], many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='200',
                                      description='MasterProctorship Details', log_description='',
                                      count=master_proctorship.count())
        except MasterProctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get masterproctorship invoice
class InvoiceMasterProctorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    # get masterproctorship invoice by masterproctorship id
    def get(self, request, pk=None):
        try:
            activityid = request.query_params.get("activity_id", "")
            if pk is not None:
                proctorship_invoice = InvoiceMasterProctorShip.objects.filter(master_proctorship__id=pk)
                serializer = InvoiceMasterProctorshipSerializer(proctorship_invoice, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            if activityid:
                proctorship_invoice = InvoiceMasterProctorShip.objects.filter(master_proctorship__id=activityid)
                serializer = InvoiceMasterProctorshipSerializer(proctorship_invoice, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            proctorship_invoices = InvoiceMasterProctorShip.objects.all()
            serializer = InvoiceMasterProctorshipSerializer(proctorship_invoices, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='',
                                      count=proctorship_invoices.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No InvoiceMaster ProctorShip matches the given query.")
        except InvoiceMasterProctorShip.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="InvoiceMaster ProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request):
        try:
            data = request.data
            serializer = InvoiceMasterProctorshipSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                master_proctorship(MasterProctorship.objects.get(id=data["master_proctorship_id"]))
                # count = MasterProctorshipTraineeProfile.objects.filter(
                #     master_proctorship__id=data["master_proctorship_id"]).count()
                # if count == MasterProctorshipProctorReport.objects.filter(
                #         master_proctorship_trainee__master_proctorship__id=data[
                #             "master_proctorship_id"]).count() and MasterProctorshipFeedback.objects.filter(
                #     master_proctorship_activity__id=data[
                #         "master_proctorship_id"]) and AttendanceFormMasterProctorShip.objects.filter(
                #     master_proctorship__id=data["master_proctorship_id"]):
                #     MasterProctorshipStatus.objects.filter(
                #         master_proctorship_activity__id=data["master_proctorship_id"]).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'master_proctorship_activity': MasterProctorship.objects.get(
                #                        id=data["master_proctorship_id"]),
                #                    'user': request.user}
                #     status_data = MasterProctorshipStatus.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='MasterProctorship Feedback is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Feedback is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except InvoiceMasterProctorShip.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="InvoiceMaster ProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = InvoiceMasterProctorShip.objects.get(master_proctorship__id=pk)
            serializer = InvoiceMasterProctorShipUpdateSerializer(instance=proctorship_attendance, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='File is replaced')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except InvoiceMasterProctorShip.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Invoice MasterProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500',
                                      description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get add put post Attendance form
class AttendanceFormMasterProctorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            activityid = request.query_params.get("activity_id", "")
            if pk is not None:
                proctorship_attendance = AttendanceFormMasterProctorShip.objects.filter(master_proctorship__id=pk)
                serializer = AttendanceFormMasterProctorShipSerailizers(proctorship_attendance, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            if activityid:
                proctorship_attendance = AttendanceFormMasterProctorShip.objects.filter(
                    master_proctorship__id=activityid)
                serializer = AttendanceFormMasterProctorShipSerailizers(proctorship_attendance, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            proctorship_attendance = AttendanceFormMasterProctorShip.objects.all()
            serializer = AttendanceFormMasterProctorShipSerailizers(proctorship_attendance, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='',
                                      count=proctorship_attendance.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Attendance FormMasterProctorShip Invoice matches the given query.")
        except AttendanceFormMasterProctorShip.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance FormMasterProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request):
        try:
            data = request.data
            serializer = AttendanceFormMasterProctorShipSerailizers(data=data)
            if serializer.is_valid():
                serializer.save()
                master_proctorship(MasterProctorship.objects.get(id=data["master_proctorship_id"]))
                # count = MasterProctorshipTraineeProfile.objects.filter(
                #     master_proctorship__id=data["master_proctorship_id"]).count()
                # if count == MasterProctorshipProctorReport.objects.filter(
                #         master_proctorship_trainee__master_proctorship__id=data[
                #             "master_proctorship_id"]).count() and MasterProctorshipFeedback.objects.filter(
                #     master_proctorship_activity__id=data[
                #         "master_proctorship_id"]) and InvoiceMasterProctorShip.objects.filter(
                #     master_proctorship__id=data["master_proctorship_id"]):
                #     MasterProctorshipStatus.objects.filter(
                #         master_proctorship_activity__id=data["master_proctorship_id"]).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'master_proctorship_activity': MasterProctorship.objects.get(
                #                        id=data["master_proctorship_id"]),
                #                    'user': request.user}
                #     status_data = MasterProctorshipStatus.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='MasterProctorship Feedback is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Feedback is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)

        except AttendanceFormMasterProctorShip.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form MasterProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = AttendanceFormMasterProctorShip.objects.get(master_proctorship__id=pk)
            serializer = AttendanceFormMasterProctorShipUpdateSerailizers(instance=proctorship_attendance, data=data)
            if serializer.is_valid():
                saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Attendance Form MasterProctorShip is replaced')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except AttendanceFormMasterProctorShip.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form MasterProctorShip doesn't exists")
        except FieldError:
            return self.send_response(code=f'500',
                                      description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class StatusMTestingView(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data
            serializer = MasterProctorshipStatusTestingSerializer(data=data)
            if serializer.is_valid():
                saved_status = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='MasterProctorship Status is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MasterProctorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="MasterProctorship Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)