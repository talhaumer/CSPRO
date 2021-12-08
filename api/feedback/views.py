from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.feedback.models import ProctorshipProctorFeedback, TraineeFeedback, MemoProctorFeedBack, Rating, Reason, \
    PercevelDriver, SoloSmartProctorFeedBack, ProctorshipCertificateForm
from api.feedback.serializers import ProctorFeedbackSerializer, TraineeFeedbackSerializer, \
    MemoProctorFeedbackSerializer, TraineeMemoFeedbackSerializer, RatingDataSerializer, ReasonDataSerializer, \
    PercevelDriverDataSerializer, SoloSmartProctorFeedbackSerializer, MemoProctorUpdateFeedbackSerializer, \
    TraineeMemoUpdateFeedbackSerializer, SoloSmartUpdateFeedbackSerializer, TraineeUpdateFeedbackSerializer, \
    CertificateFormSerailizers, CertificateFormUpdateSerailizers
from api.invoice.models import Invoice, AttendanceForm
from api.invoice.views import AttendanceFormView
from api.permissions import IsOauthAuthenticated, IsOauthAuthenticatedSuperAdminLocalAdmin
from api.proctorship.models import Proctorship
from api.status.models import StatusConstantData, Status
from api.trainee.models import TraineeProfile
from api.views import BaseAPIView
from cspro.utils import check_product_feedback, proctorship

# add proctor feedback of perceval
class ProctorFeedbackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    # get the percevel feedback according to activity
    def get(self, request, pk=None):
        try:
            # get activity id to fetch the feedback
            activity_id = request.query_params.get("activity_id", "")
            if pk:
                product = ProctorshipProctorFeedback.objects.filter(proctorship__id=pk)
                serializer = ProctorFeedbackSerializer(product, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')

            if activity_id:
                product = ProctorshipProctorFeedback.objects.filter(proctorship__id=activity_id)
                serializer = ProctorFeedbackSerializer(product, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            # if id:
            #     product = ProctorshipProctorFeedback.objects.filter(proctorship__id=id)
            #     serializer = ProctorFeedbackSerializer(product)
            #     return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
            #                               code='', description='Details of serializer', log_description='')

            products = ProctorshipProctorFeedback.objects.all()
            serializer = ProctorFeedbackSerializer(products, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Feedback matches the given query.")
        except ProctorshipProctorFeedback.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Proctor Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

        # post the percevel feedback according to activity
    def post(self, request):
        try:
            data = request.data
            serializer = ProctorFeedbackSerializer(data=data)
            if serializer.is_valid():
                product_saved = serializer.save()
                proctorship(Proctorship.objects.get(id=data["proctorship_id"]))
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"], prod="Perceval") and count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() and AttendanceForm.objects.filter(proctorship__id=data["proctorship_id"]) and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     Status.objects.filter(proctorship_activity__id=data["proctorship_id"]).update(is_active=False)
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

        except ProctorshipProctorFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # put the percevel feedback according to activity
    def put(self, request, pk=None):
        try:
            id = pk
            saved_product = ProctorshipProctorFeedback.objects.get(proctorship__id=id)
            data = request.data
            serializer = ProctorFeedbackSerializer(instance=saved_product, data=data, partial=True)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Feedback matches the given query.")
        except ProctorshipProctorFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


# get, update, post trainee feeback
class TraineeFeedbackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    # get the trainee feedback according to activity
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if pk:
                trainee = TraineeFeedback.objects.get(trainee__id=pk)
                serializer = TraineeFeedbackSerializer(trainee)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')

            products = TraineeFeedback.objects.filter(trainee__proctorship__id=activity_id)
            serializer = TraineeFeedbackSerializer(products, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Trainee Feedback matches the given query.")
        except TraineeFeedback.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # post the trainee feedback according to activity
    def post(self, request):
        try:
            data = request.data
            serializer = TraineeFeedbackSerializer(data=data)
            if serializer.is_valid():
                product_saved = serializer.save()
                proctorship(Proctorship.objects.get(trainee_proctorship__id=data["trainee_id"]))
                # proctorship_id = Proctorship.objects.get(trainee_proctorship__id=data["trainee_id"]).id
                # count = TraineeProfile.objects.filter(proctorship__id=proctorship_id).count()
                # if check_product_feedback(proctorship_id) and AttendanceForm.objects.filter(proctorship__id=proctorship_id) and Invoice.objects.filter(proctorship__id=proctorship_id) and count == TraineeFeedback.objects.filter(
                #                         trainee__proctorship__id=proctorship_id).count():
                #     Status.objects.filter(proctorship_activity__id=proctorship_id).update(is_active=False)
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
        except TraineeFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # update the trainee feedback according to activity
    def put(self, request, pk=None):
        try:
            id = pk
            saved_product = TraineeFeedback.objects.get(trainee__id=id)
            data = request.data
            serializer = TraineeUpdateFeedbackSerializer(instance=saved_product, data=data, partial=True)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Trainee Feedback matches the given query.")
        except TraineeFeedback.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


# class TraineeMemoFeedbackView(BaseAPIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request, pk=None):
#         try:
#             if pk is not None:
#                 trainee = TraineeFeedback.objects.get(trainee__id=pk)
#                 serializer = TraineeMemoFeedbackSerializer(trainee)
#                 return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
#             products = TraineeFeedback.objects.filter(is_memo_family = True)
#             serializer = TraineeMemoFeedbackSerializer(products, many=True)
#             return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
#         except ObjectDoesNotExist:
#             return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Trainee Feedback matches the given query.")
#         except TraineeFeedback.DoesNotExist:
#             return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Feedback doesn't exists")
#         except FieldError:
#             return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
#         except Exception as e:
#             return self.send_response(code=f'500', description=e)
#
#     def post(self, request):
#         try:
#             feedback = request.data
#             serializer = TraineeMemoFeedbackSerializer(data=feedback)
#             if serializer.is_valid():
#                 product_saved = serializer.save()
#                 return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Feedback is created')
#             return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
#         except TraineeFeedback.DoesNotExist:
#             return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Trainee Feedback doesn't exists")
#         except FieldError:
#             return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
#         except Exception as e:
#             return self.send_response(code=f'500', description=e)
#
#     def put(self, request, pk=None):
#         try:
#             id = pk
#             saved_product = TraineeFeedback.objects.get(trainee__id=id)
#             data = request.data
#             serializer = TraineeMemoUpdateFeedbackSerializer(instance=saved_product, data=data, partial=True)
#             if serializer.is_valid():
#                 product_saved = serializer.save()
#                 return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Feedback is updated')
#             return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
#         except ObjectDoesNotExist:
#             return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Trainee Feedback matches the given query.")
#         except TraineeFeedback.DoesNotExist:
#             return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Trainee Feedback doesn't exists")
#         except FieldError:
#             return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
#         except Exception as e:
#             return self.send_response(code=f'500', description=e)


# add, get, update  memo proctor feedback
class MemoProctorFeedBackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    # get the Memo Proctor FeedBack feedback according to activity
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if pk is not None:
                trainee = MemoProctorFeedBack.objects.filter(proctorship__id=pk)
                serializer = MemoProctorFeedbackSerializer(trainee, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')

            if activity_id:
                trainee = MemoProctorFeedBack.objects.filter(proctorship__id=activity_id)
                serializer = MemoProctorFeedbackSerializer(trainee, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            products = MemoProctorFeedBack.objects.all()
            serializer = MemoProctorFeedbackSerializer(products, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Memo Feedback matches the given query.")
        except MemoProctorFeedBack.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # post the Memo Proctor FeedBack feedback according to activity
    def post(self, request):
        try:
            data = request.data
            serializer = MemoProctorFeedbackSerializer(data=data)
            if serializer.is_valid():
                product_saved = serializer.save()
                proctorship(Proctorship.objects.get(id=data["proctorship_id"]))
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"], prod="Memo Family") and count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() and AttendanceForm.objects.filter(proctorship__id=data["proctorship_id"]) and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     Status.objects.filter(proctorship_activity__id=data["proctorship_id"]).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(
                #                        id=data["proctorship_id"]), 'user': request.user}
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
        except MemoProctorFeedBack.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


    # upload the Memo Proctor FeedBack feedback according to activity
    def put(self, request, pk=None):
        try:
            id = pk
            saved_product = MemoProctorFeedBack.objects.get(proctorship__id=id)
            data = request.data
            serializer = MemoProctorUpdateFeedbackSerializer(instance=saved_product, data=data)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Memo Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Memo Feedback matches the given query.")
        except MemoProctorFeedBack.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get percevel driver data
class PercevelDriverDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    # get the  Percevel Driver Data COnstant data

    def get(self, request, pk=None):
        try:
            constant_data = PercevelDriver.objects.all()
            serializer =  PercevelDriverDataSerializer(constant_data, many = True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',description='Details of serializer', log_description='')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except PercevelDriver.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Percevel Driver doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get the  Reason Data COnstant data
class ReasonDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    def get(self, request, pk=None):
        try:
            constant_data = Reason.objects.all()
            serializer =  ReasonDataSerializer(constant_data, many = True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',description='Details of serializer', log_description='')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Reason.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Reason doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)


# get rating data
class RatingDataView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)

    # get the  Rating Data Constant data

    def get(self, request, pk=None):
        try:
            constant_data = Rating.objects.all()
            serializer =  RatingDataSerializer(constant_data, many = True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',description='Details of serializer', log_description='')
        except IntegrityError as i:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=str(i))
        except Rating.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Rating doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get, post, add solo smart feedback
class SoloSmartProctorFeedBackView(BaseAPIView):
    permission_classes = (IsOauthAuthenticated,)
    #get the solo smart proctor feedback data
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get("activity_id", "")

            if pk is not None:
                trainee = SoloSmartProctorFeedBack.objects.filter(proctorship__id=pk)
                serializer = SoloSmartProctorFeedbackSerializer(trainee, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')

            if activity_id:
                trainee = SoloSmartProctorFeedBack.objects.filter(proctorship__id=activity_id)
                serializer = SoloSmartProctorFeedbackSerializer(trainee, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            products = SoloSmartProctorFeedBack.objects.all()
            serializer = SoloSmartProctorFeedbackSerializer(products, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='', description='Details of serializer', log_description='')
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Memo Feedback matches the given query.")
        except SoloSmartProctorFeedBack.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # add the solo smart proctor feedback data
    def post(self, request):
        try:
            data = request.data
            serializer = SoloSmartProctorFeedbackSerializer(data=data)
            if serializer.is_valid():
                product_saved = serializer.save()
                proctorship(Proctorship.objects.get(id=data["proctorship_id"]))
                # count = TraineeProfile.objects.filter(proctorship__id=data["proctorship_id"]).count()
                # if check_product_feedback(data["proctorship_id"], prod="Solo Smart") and count == TraineeFeedback.objects.filter(trainee__proctorship__id=data["proctorship_id"]).count() and AttendanceForm.objects.filter(proctorship__id=data["proctorship_id"]) and Invoice.objects.filter(proctorship__id=data["proctorship_id"]):
                #     Status.objects.filter(proctorship_activity__id=data["proctorship_id"]).update(is_active=False)
                #     status_data = {'status': StatusConstantData.objects.get(code='closed'),
                #                    'proctorship_activity': Proctorship.objects.get(
                #                        id=data["proctorship_id"]), 'user': request.user}
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
        except SoloSmartProctorFeedBack.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # update the solo smart proctor feedback data
    def put(self, request, pk=None):
        try:
            id = pk
            saved_product = SoloSmartProctorFeedBack.objects.get(proctorship__id=id)
            data = request.data
            serializer = SoloSmartUpdateFeedbackSerializer(instance=saved_product, data=data, partial=True)
            if serializer.is_valid():
                product_saved = serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,description='Memo Feedback is updated')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description=serializer.errors)
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="No Memo Feedback matches the given query.")
        except SoloSmartProctorFeedBack.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="Memo Feedback doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

# get add, and put certificate of proctors percevel certificate
class CertificateFormView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get the perevel proctor certoificate
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get('activity_id', '')
            if pk is not None:
                proctorship_attendance = ProctorshipCertificateForm.objects.filter(proctorship__id=pk)
                serializer = CertificateFormSerailizers(proctorship_attendance, many=True)
                return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data,
                                          code='', description='Details of serializer', log_description='')

            proctorship_attendance = ProctorshipCertificateForm.objects.all()
            serializer = CertificateFormSerailizers(proctorship_attendance, many=True)
            return self.send_response(success=True, status_code=status.HTTP_200_OK, payload=serializer.data, code='',
                                      description='Details of serializer', log_description='',
                                      count=proctorship_attendance.count())
        except ObjectDoesNotExist:
            return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="No Certificate Form  matches the given query.")
        except ProctorshipCertificateForm.DoesNotExist:
            return self.send_response(code='', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Certificate Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # add the perevel proctor certoificate
    def post(self, request,name=None,pk=None):
        try:
            data = request.data
            obj = Proctorship.objects.get(id=pk)
            serializer = CertificateFormSerailizers(data=data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['proctorship'] = obj
                product_saved = serializer.save(**validated_data)
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Certificate Form is created')
            else:
                return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=serializer.errors)
        except ProctorshipCertificateForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Certificate Form doesn't exists")
        except Proctorship.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Certificate Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)

    # update the perevel proctor certoificate
    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = ProctorshipCertificateForm.objects.get(proctorship__id=pk)
            serializer = CertificateFormUpdateSerailizers(instance=proctorship_attendance, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED,
                                          description='Certificate Form is replaced')
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=serializer.errors)
        except ProctorshipCertificateForm.DoesNotExist:
            return self.send_response(code=f'422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description="Certificate Form doesn't exists")
        except FieldError:
            return self.send_response(code=f'500', description="Cannot resolve keyword given in 'order_by' into field")
        except Exception as e:
            return self.send_response(code=f'500', description=e)
