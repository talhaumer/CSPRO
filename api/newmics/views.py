from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.models import Products, Hospital
from api.newmics.models import NewMics, MicsTraineeProfile, MicsProctorshipStatus, MicsPreceptorshipStatus, \
    MicsPreceptorship, MicsPreceptorshipProposal, MicsProctorshipProposal, MicsPercevalFeedback, MicsProctorship, \
    MicsTraineeFeedback, MicsInvoice, MicsAttendanceForm, MicsProctorshipCertificateForm
from api.newmics.serializer import MicsProctorshipSerializer, MicsSerializer, MicsViewSerializer, \
    MicsTraineeProfileSerializer, TraineeMicsViewSerializer, MicsProctorshipStatusSerializer, \
    MicsPreceptorshipStatusSerializer, MicsViewListingSerializer, RecentPreceptorshipViewSerializer, \
    HospitalForMICSSerializer, CEOProctorsZoneViewSerializer, UpdateStatusPerceptershipSerializer, \
    UpdateStatusProctorshipSerializer, MicsPercevalSerializer, MicsTraineeFeedbackSerializer, MicsInvoiceSerializer, \
    MicsAttendanceFormSerailizers, MicsCertificateFormSerailizers
from api.pagination import CustomPagination
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin, IsOauthAuthenticated, \
    IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet
from api.proctors.models import Proctors
from api.serializers import HospitalSerializer
from api.users.models import User
from api.views import BaseAPIView
from cspro.utilities.convert_boolean import boolean
from cspro.utils import available_proctors, check, check_perceptorship, check_masterproctorship, check_event


class NewMicsView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                preceptorship = NewMics.objects.get(pk=pk)
                serializer = MicsViewSerializer(preceptorship)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            new_mics = NewMics.objects.all()
            serializer = MicsViewSerializer(new_mics, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='', count=new_mics.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No New Mics matches the given query.")
        except NewMics.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="New Mics doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request):
        try:
            data = request.data
            # data['zone_id'] = request.user.admin_user.get().zone.id
            # data['user_id'] =
            serializer = MicsSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['user'] = User.objects.get(id=request.user.id)
                validated_data['product'] = Products.objects.get(id=2)
                validated_data['mics_perceptorship']['hospital'] = Hospital.objects.get(
                    id=request.data['mics_perceptorship'].pop('hospital_id'))
                serializer.save(**validated_data)
                id = serializer.instance.id
                return self.send_response(success=True, code=f'201', payload={'id': id},
                                          status_code=status.HTTP_201_CREATED, description='New Mics is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except NewMics.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="New Mics doesn't exists")
        except Products.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="New Mics doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class AddMicsProctorshipView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def post(self, request, pk=None):
        try:
            mics = NewMics.objects.get(id=pk)
            data = request.data
            # data['user_id'] = request.user.id
            serializer = MicsProctorshipSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['user'] = request.user
                validated_data['mics'] = mics
                serializer.save(**validated_data)
                id = serializer.instance.id
                return self.send_response(success=True, code=f'201', payload={'id': id},
                                          status_code=status.HTTP_201_CREATED,
                                          description='Mics Proctorship is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except NewMics.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Proctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsTraineeProfileView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MicsTraineeProfile.objects.get(pk=pk, revoke=False)
                serializer = MicsTraineeProfileSerializer(trainee)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            trainees = MicsTraineeProfile.objects.filter(revoke=False)
            serializer = MicsTraineeProfileSerializer(trainees, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='', count=len(trainees))
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Mics Proctorship matches the given query.")
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Proctorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request, pk=None):
        try:
            # query_object = Q(mics_perceptotship__product__id=2)
            mics = NewMics.objects.get(id=pk)
            data = request.data
            serializer = MicsTraineeProfileSerializer(data=data, many=True, context={
                "mics": mics})
            if serializer.is_valid():
                # validated_data = serializer.validated_data
                # for obj in validated_data:
                #     obj['mics'] = mics
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Trainee Addedd successfully')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Proctorship doesn't exists")
        except NewMics.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, pk=None):
        try:
            # query_object = Q(mics_perceptotship__product__id=2)
            # mics = NewMics.objects.get(id=pk)
            trainee = MicsTraineeProfile.objects.get(id=pk)
            data = request.data
            serializer = MicsTraineeProfileSerializer(trainee,data=data,partial=True)
            if serializer.is_valid():
                # validated_data = serializer.validated_data
                # for obj in validated_data:
                #     obj['mics'] = mics
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Trainee Updated successfully')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Proctorship doesn't exists")
        except NewMics.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

class ApproveMicsTraineeView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MicsTraineeProfile.objects.get(id=pk)
                trainee.status = True
                trainee.save()
                return self.send_response(description="trainee is activate successfuly", success=True,
                                          status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Trainee doesn't found")
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Trainee doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class RevokeMicsTraineeView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            if pk is not None:
                trainee = MicsTraineeProfile.objects.get(id=pk)
                trainee.revoke = True
                trainee.save()
                return self.send_response(description="trainee is is revoked successfuly", success=True,
                                          status_code=status.HTTP_200_OK, code='200')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Trainee Profile doesn't found")
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Trainee Profile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class TraineeMicsView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk=None):
        try:
            mics_id = request.query_params.get('activity_id', '')
            if mics_id:
                trainees = MicsTraineeProfile.objects.filter(mics__id=mics_id, )
                serializer = TraineeMicsViewSerializer(trainees, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='',
                                          count=len(trainees))
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter valid Mics Id', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Trainee matches the given query.")
        except MicsTraineeProfile.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="TraineeProfile doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsProctorshipStatusView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if activity_id:
                activity_status = MicsProctorshipStatus.objects.filter(proctorship_activity__id=activity_id).order_by(
                    "timestamp")
                serializer = MicsProctorshipStatusSerializer(activity_status, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter Valid Mics ProctorshipId')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MicsProctorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Proctor doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request, pk=None):
        try:
            try:
                data = request.data
                mics = NewMics.objects.get(id=pk)
                # data['user_id'] = request.user.id
                mics_per = MicsProctorshipProposal.objects.filter(
                    status__proctorship_activity__mics__id=pk).latest(
                    "created_on")

                start_date = str(mics_per.start_date)
                end_date = str(mics_per.end_date)

                if data["status"] == "confirmed":
                    proctors = MicsProctorshipStatus.objects.filter(
                        proctorship_activity__mics__id=pk).filter(
                        mics_proctorship_porposal__isnull=False).latest(
                        'created_on').mics_proctorship_porposal.filter(
                        mics_proctor_porposal__isnull=False).latest(
                        'created_on').mics_proctor_porposal.all()
                    for each in proctors:
                        if not check(each.proctors.id, start_date, end_date):
                            if not check_perceptorship(each.proctors.id, start_date, end_date):
                                if not check_masterproctorship(each.proctors.id, start_date, end_date):
                                    if not check_event(each.proctors.id, start_date, end_date):
                                        proctors.update(status=False)
                                        each.status = True
                                        each.save()
                                        serializer = UpdateStatusProctorshipSerializer(data=data,
                                                                                       context={"mics": mics})
                                        if serializer.is_valid():
                                            validated_data = serializer.validated_data
                                            validated_data['user'] = request.user
                                            saved_status = serializer.save(**validated_data)
                                            return self.send_response(success=True, code=f'201',
                                                                      status_code=status.HTTP_201_CREATED,
                                                                      description='status is created')
                                        break
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="None of selected proctors is available")

                serializer = UpdateStatusProctorshipSerializer(data=data, context={"mics": mics})
                if serializer.is_valid():
                    validated_data = serializer.validated_data
                    validated_data['user'] = request.user
                    saved_status = serializer.save(**validated_data)
                    return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                              description='status is created')
                else:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description=serializer.errors)
            except IntegrityError as i:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=str(i))
        except MicsProctorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class PreceptorshipStatusView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if activity_id:
                activity_status = MicsPreceptorshipStatus.objects.filter(
                    mics_preceptorship_activity__id=activity_id).order_by(
                    "timestamp")
                serializer = MicsPreceptorshipStatusSerializer(activity_status, many=True)

                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')
            return self.send_response(success=False, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, payload=[],
                                      code='422', description='Enter Valid Mics Perceptorship id')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MicsPreceptorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=" Mics Perceptorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def post(self, request, pk=None):
        try:
            data = request.data
            mics = NewMics.objects.get(id=pk)
            # data['user_id'] = request.user.id
            mics_per = MicsPreceptorshipProposal.objects.filter(
                status__mics_preceptorship_activity__mics__id=pk).latest(
                "created_on")

            start_date = str(mics_per.start_date)
            end_date = str(mics_per.end_date)

            if data["status"] == "confirmed":
                proctors = MicsPreceptorshipStatus.objects.filter(
                    mics_preceptorship_activity__mics__id=pk).filter(
                    alter_mics_preceptorship_porposal__isnull=False).latest(
                    'created_on').alter_mics_preceptorship_porposal.filter(
                    mics_preceptorship_porposal__isnull=False).latest('created_on').mics_preceptorship_porposal.all()
                for each in proctors:
                    if not check(each.proctors.id, start_date, end_date):
                        if not check_perceptorship(each.proctors.id, start_date, end_date):
                            if not check_masterproctorship(each.proctors.id, start_date, end_date):
                                if not check_event(each.proctors.id, start_date, end_date):
                                    proctors.update(status=False)
                                    each.status = True
                                    each.save()
                                    serializer = UpdateStatusPerceptershipSerializer(data=data, context={"mics": mics})
                                    if serializer.is_valid():
                                        validated_data = serializer.validated_data
                                        validated_data['user'] = request.user
                                        saved_status = serializer.save(**validated_data)
                                        return self.send_response(success=True, code=f'201',
                                                                  status_code=status.HTTP_201_CREATED,
                                                                  description='status is created')
                                    break
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="None of selected proctors is available")

            serializer = UpdateStatusPerceptershipSerializer(data=data, context={"mics": mics})
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['user'] = request.user
                saved_status = serializer.save(**validated_data)
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='status is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except MicsPreceptorshipStatus.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics Perceptorship Status doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            print(e)
            return self.send_response(code=f'500', description=e)


class NewMicsCourseListing(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    pagination_class = CustomPagination

    def boolean(self, status):
        if status == 'true' or status == "True":
            return True
        else:
            return False

    def sorting_data(self, column_name, order):
        try:
            dash = '' if order.lower() == 'asc' else '-'

            if column_name == 'id':
                return f'{dash}id'

            if column_name == 'status':
                return f'{dash}mics_perceptotship__mics_preceptorshipStatus_status__status__id'

            if column_name == 'proctorship_status':
                return f'{dash}mics_peroctorship__mics_proctorship_status__status__id'

            if column_name == 'cognos_id':
                return f'{dash}mics_peroctorship__hospital__cognos_id'

            if column_name == 'date':
                return f'{dash}mics_perceptotship__mics_preceptorshipStatus_status__alter_mics_preceptorship_porposal__start_date'
                #
            if column_name == 'proctor':
                return f'{dash}mics_perceptotship__mics_preceptorshipStatus_status__alter_mics_preceptorship_porposal__mics_preceptorship_porposal__proctors__user__name'

            if column_name == 'hospital':
                return f'{dash}mics_peroctorship__hospital__hospital_name'

            if column_name == 'proctorship_proctor':
                return f'{dash}mics_peroctorship__mics_proctorship_status__mics_proctorship_porposal__mics_proctor_porposal__proctors__user__name'

            # if column_name == 'product':
            #     return f'{dash}product__product_name'

            # if column_name == 'training_type':
            #     return f'{dash}training_type__name'

            if column_name == 'is_rat':
                return f'{dash}is_rat'

            return f'{dash}{column_name}'
        except Exception as e:
            return str(e)

    def get(self, request, pk=None):
        try:
            search_value = request.query_params.get('search_value', None)
            column_name = request.query_params.get('column_name', "id")
            order = request.query_params.get('order', 'desc')
            limit = int(request.query_params.get('limit', 10))
            offset = int(request.query_params.get('offset', 0))
            actvity_status = request.query_params.get('status', None)
            type_of_course = request.query_params.get('type_of_course', None)
            hospital = request.query_params.get('hospital', None)
            country = request.query_params.get('country', None)

            new_mics = NewMics.objects.all()
            if search_value:
                new_mics = new_mics.filter(Q(id__icontains=search_value) |
                                           Q(user__name__icontains=search_value) |
                                           Q(mics_perceptotship__hospital__hospital_name__icontains=search_value) |
                                           Q(mics_perceptotship__product__product_name__icontains=search_value) |
                                           Q(mics_perceptotship__mics_preceptorshipStatus_status__status__code__icontains=search_value) |
                                           Q(mics_perceptotship__mics_preceptorshipStatus_status__alter_mics_preceptorship_porposal__start_date__icontains=search_value) |
                                           Q(mics_perceptotship__mics_preceptorshipStatus_status__alter_mics_preceptorship_porposal__mics_preceptorship_porposal__proctors__user__name__icontains=search_value) |
                                           Q(mics_peroctorship__country__name__icontains=search_value) |
                                           Q(mics_peroctorship__hospital__hospital_name__icontains=search_value) |
                                           Q(mics_peroctorship__hotel__icontains=search_value) |
                                           Q(mics_peroctorship__number_of_cases__icontains=search_value) |
                                           Q(mics_peroctorship__mics_proctorship_status__status__code__icontains=search_value) |
                                           Q(mics_peroctorship__mics_proctorship_status__mics_proctorship_porposal__start_date__icontains=search_value) |
                                           Q(mics_peroctorship__transplant_time__icontains=search_value) |
                                           Q(mics_peroctorship__mics_proctorship_status__mics_proctorship_porposal__mics_proctor_porposal__proctors__user__name__icontains=search_value)).distinct()

            query_object = Q(mics_perceptotship__mics_preceptorshipStatus_status__is_active=True) | Q(
                mics_peroctorship__mics_proctorship_status__is_active=True)

            if country:
                query_object &= Q(mics_peroctorship__country__id=int(country))

            if type_of_course:
                query_object &= Q(is_global=self.boolean(type_of_course))

            if hospital:
                query_object &= Q(mics_peroctorship__hospital__id=hospital) | Q(
                    mics_perceptotship__hospital__id=hospital)

            new_mics.filter(query_object).order_by(str(self.sorting_data(column_name, order)))

            if actvity_status:
                query_object &= Q(mics_peroctorship__mics_proctorship_status__status__code=actvity_status) | Q(
                    mics_perceptotship__mics_preceptorshipStatus_status__status__code=actvity_status)

            new_mics = new_mics.filter(query_object).order_by(str(self.sorting_data(column_name, order))).distinct()

            serializer = MicsViewListingSerializer(new_mics[offset: offset + limit], many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='200',
                                      description='Mics Details', log_description='', count=new_mics.count())
        except NewMics.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Mics doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class RecentScheduleActivitiesView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            is_rat = boolean(request.query_params.get('is_rat', False))
            # zone_id = request.user.admin_user.get().zone.id
            # product = request.query_params.get("product_id", '2')
            query_object = Q(mics__is_rat=is_rat, product__id=2,
                             mics_preceptorshipStatus_status__status__code__in=["confirmed", "processing", "pending",
                                                                                "alternative-proposal"],mics_preceptorshipStatus_status__is_active=True)

            preceptorship = MicsPreceptorship.objects.filter(query_object).distinct()
            serializer = RecentPreceptorshipViewSerializer(preceptorship, many=True)
            # preceptorship = preceptorship.filter(query_object)
            # preceptorship = preceptorship.filter(
            #     preceptorshipStatus_status__status__code__in=["confirmed", "processing", "pending",
            #                                                   "alternative-proposal"])
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                      code='', description='Details of serializer', log_description='',
                                      count=preceptorship.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Preceptorship matches the given query.")
        except MicsPreceptorship.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Preceptorship doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsHospitalZoneView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def get(self, request, pk=None):
        try:
            # area_type = request.query_params.get('area_type', '')
            product = request.query_params.get('product_id', '2')
            country = request.query_params.get('country_id', '')
            query_object = Q(is_it_preceptorship=True, qualified_for_news_mics_program=True)
            if product:
                query_object &= Q(products__id=product)

            if country:
                query_object &= Q(hospital_id__country__id=country)

            # countries = request.user.admin_user.get().zone.zone_zone_countires.all()
            # countries_id = [country.countries.id for country in countries]
            hospitals = Hospital.objects.filter(query_object).distinct()
            serializer = HospitalForMICSSerializer(hospitals, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                      code='', description='Details of serializer', log_description='',
                                      count=hospitals.count())

        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Hospital matches the given query.")

        except Hospital.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Product doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsProctorsOfCOEView(BaseAPIView, CustomPagination):
    permission_classes = (IsOauthAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            hospital = request.query_params.get('hospital_id', '')
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            product = request.query_params.get('product_id', '2')
            query_object = Q()
            if hospital:
                query_object &= Q(proctors_pivot_id__hospital=hospital)
            proctors = Proctors.objects.filter(query_object, only_speaker=False, user__is_active=True)
            proctors = proctors.exclude(proctorShip_contract_ending_details__lt=end_date)

            proctors = proctors.exclude(unavailability_start_date__lte=start_date,
                                        unavailability_end_date__gte=start_date)
            proctors = proctors.exclude(unavailability_start_date__gte=end_date,
                                        unavailability_end_date__lte=end_date)

            proctors = available_proctors(proctors, start_date, end_date)
            serializer = CEOProctorsZoneViewSerializer(proctors, many=True)

            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='', count=proctors.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Proctors matches the given query.")
        except Proctors.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Proctors doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


# Create your views here.
class MICSHospitalView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdminPostOrGet,)

    def post(self, request):
        try:
            data = request.data
            print(data)
            d = Products.objects.get(product_name="Perceval").id
            data['products_id'] = [d]
            serializer = HospitalSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Hospital is created')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Hospital matches the given query.")
        except Hospital.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Hospital doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsPrecevalFeedbackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            # if name == 'perceptership':
            #     obj = MicsPreceptorship.objects.get(id=pk)
            # else:
            obj = MicsProctorship.objects.get(id=pk)
            if obj.mics_perceval_feedback_mics_proctorship.count() > 0:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="Data Already Exists")
            # return False
            serializer = MicsPercevalSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['mics_proctorship'] = obj
                product_saved = serializer.save(**validated_data)
                MicsProctorship.close_proctorship(obj)
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"], prod="Perceval") and count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() and AttendanceForm.objects.filter(proctorship__id=data["proctorship_id"]) and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(id=data["proctorship_id"]),
                #                    'user': request.user}
                #     status_data = Status.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201',
                #                           status_code=status.HTTP_201_CREATED,
                #                           description='Feedback is created')
                return self.send_response(success=True, code=f'201',
                                          status_code=status.HTTP_201_CREATED,
                                          description='Feedback is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)

        except MicsPercevalFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Feedback doesn't exists")
        except MicsPreceptorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Feedback doesn't exists")
        except MicsProctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, name=None,pk=None):
        try:
            id = pk
            saved_product = MicsPercevalFeedback.objects.get(id=pk)
            MicsPreceptorship.close_perceptership(saved_product)
            data = request.data
            serializer = MicsPercevalSerializer(instance=saved_product, data=data, partial=True)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Feedback matches the given query.")
        except MicsPercevalFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsTraineeFeedbackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            MicsTraineeProfile.objects.get(id=data["trainee_id"])
            if name == 'perceptership':
                obj = MicsPreceptorship.objects.get(id=pk)
                if obj.mics_trainee_feedback_mics_perceptership.filter(trainee_id=data['trainee_id']).count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")
            else:
                obj = MicsProctorship.objects.get(id=pk)
                if obj.mics_trainee_feedback_mics_proctorship.filter(trainee_id=data['trainee_id']).count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")


            # return False
            serializer = MicsTraineeFeedbackSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                if name == 'perceptership':
                    validated_data['mics_perceptership'] = obj
                else:
                    validated_data['mics_proctorship'] = obj
                product_saved = serializer.save(**validated_data)
                if name == 'perceptership':
                    MicsPreceptorship.close_perceptership(obj)
                else:
                    MicsProctorship.close_proctorship(obj)
                # proctorship_id = MicsTraineeFeedback.objects.get(id=data["trainee_id"]).id
                # count = TraineeProfile.objects.filter(proctorship__id=proctorship_id).count()
                # if check_product_feedback(proctorship_id) and AttendanceForm.objects.filter(proctorship__id=proctorship_id) and Invoice.objects.filter(proctorship__id=proctorship_id) and count == TraineeFeedback.objects.filter(
                #                         trainee__proctorship__id=proctorship_id).count():
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(id=proctorship_id),
                #                    'user': request.user}
                #     status_data = Status.objects.create(**status_data)
                #     status_data.save()
                #
                #     return self.send_response(success=True, code=f'201',
                #                           status_code=status.HTTP_201_CREATED,
                #                           description='Feedback is created')
                return self.send_response(success=True, code=f'201',
                                          status_code=status.HTTP_201_CREATED,
                                          description='Feedback is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except MicsTraineeFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Feedback doesn't exists")
        except MicsPreceptorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Feedback doesn't exists")
        except MicsProctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request,name=None, pk=None):
        try:
            id = pk
            saved_product = MicsTraineeFeedback.objects.get(id=id)
            data = request.data
            serializer = MicsTraineeFeedbackSerializer(instance=saved_product, data=data, partial=True)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Trainee Feedback matches the given query.")
        except MicsTraineeFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsInvoiceView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            if name == 'perceptership':
                obj = MicsPreceptorship.objects.get(id=pk)
                obj = MicsPreceptorship.objects.get(id=pk)
                if obj.mics_invoice_mics_perceptership.all().count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")
                MicsPreceptorship.close_perceptership(obj)
            else:
                obj = MicsProctorship.objects.get(id=pk)
                if obj.mics_invoice_mics_proctorship.all().count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")
                MicsProctorship.close_proctorship(obj)
            serializer = MicsInvoiceSerializer(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                if name == 'perceptership':
                    validated_data['mics_perceptership'] = obj
                else:
                    validated_data['mics_proctorship'] = obj
                product_saved = serializer.save(**validated_data)
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"]) and count == TraineeFeedback.objects.filter(
                #         trainee__proctorship__id=data["proctorship_id"]).count() and AttendanceForm.objects.filter(
                #         proctorship__id=data["proctorship_id"]):
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(id=data["proctorship_id"]),
                #                    'user': request.user}
                #     status_data = Status.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='Invoice is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Invoice is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)

        except MicsInvoice.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Invoice doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request, name=None, pk= None):
        try:
            data = request.data
            invoice = MicsInvoice.objects.get(id=pk)
            serializer = MicsInvoiceSerializer(instance=invoice, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Invoice is replaced')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MicsInvoice.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Invoice doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsAttendanceFormView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            if name == 'perceptership':
                obj = MicsPreceptorship.objects.get(id=pk)
                if obj.mics_perceval_feedback_mics_perceptership.all().count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")
            else:
                obj = MicsProctorship.objects.get(id=pk)
                if obj.mics_attendance_form_mics_proctorship.all().count() > 0:
                    return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                              description="Data Already Exists")

            # return False

            serializer = MicsAttendanceFormSerailizers(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                if name == 'perceptership':
                    validated_data['mics_perceptership'] = obj
                else:
                    validated_data['mics_proctorship'] = obj
                product_saved = serializer.save(**validated_data)
                if name == 'perceptership':
                    MicsPreceptorship.close_perceptership(obj)
                else:
                    MicsProctorship.close_proctorship(obj)
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"]) and \
                #         count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() \
                #         and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(id=data["proctorship_id"]),
                #                    'user': request.user}
                #     status_data = Status.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='Attendance Form is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Attendance Form is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except MicsAttendanceForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request,name=None, pk= None):
        try:
            data = request.data
            proctorship_attendance = MicsAttendanceForm.objects.get(id=pk)
            serializer = MicsAttendanceFormSerailizers(instance=proctorship_attendance, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Attendance Form is replaced')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MicsAttendanceForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


class MicsCertificateFormView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            # if name == 'perceptership':
            #     obj = MicsPreceptorship.objects.get(id=pk)
            #     if obj.mics_certificate_form_mics_perceptership.all().count() > 0:
            #         return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            #                                   description="Data Already Exists")
            #     MicsPreceptorship.close_perceptership(obj)
            # else:
            obj = MicsProctorship.objects.get(id=pk)
            if obj.mics_certificate_form_mics_proctorship.all().count() > 0:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description="Data Already Exists")
            MicsProctorship.close_proctorship(obj)
            serializer = MicsCertificateFormSerailizers(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                # if name == 'perceptership':
                #     validated_data['mics_perceptership'] = obj
                # else:
                validated_data['mics_proctorship'] = obj
                product_saved = serializer.save(**validated_data)

                MicsProctorship.close_proctorship(obj)
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"]) and \
                #         count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() \
                #         and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(id=data["proctorship_id"]),
                #                    'user': request.user}
                #     status_data = Status.objects.create(**status_data)
                #     status_data.save()
                #     return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                #                               description='Attendance Form is created')
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Attendance Form is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except MicsProctorshipCertificateForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    def put(self, request,name=None, pk= None):
        try:
            data = request.data
            proctorship_attendance = MicsProctorshipCertificateForm.objects.get(id=pk)
            serializer = MicsCertificateFormSerailizers(instance=proctorship_attendance, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Attendance Form is replaced')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except MicsProctorshipCertificateForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Attendance Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

