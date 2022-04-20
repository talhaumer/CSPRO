from django.core.exceptions import FieldError, ObjectDoesNotExist
from rest_framework import status

from api.feedback.models import TraineeFeedback
from api.invoice.models import AttendanceForm, Invoice
from api.invoice.serializer import (
    AttendanceFormSerailizers,
    AttendanceFormUpdateSerailizers,
    InvoiceSerializer,
    InvoiceUpdateSerializer,
)
from api.permissions import IsOauthAuthenticatedSuperAdminLocalAdmin
from api.proctorship.models import Proctorship
from api.views import BaseAPIView
from cspro.utils import proctorship


# add, get , update proctorship invoice
class InvoiceView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)
    #  get  proctorship invoice by proctorship id
    def get(self, request, pk=None):
        try:
            if pk is not None:
                proctorship_invoice = Invoice.objects.filter(proctorship__id=pk)
                serializer = InvoiceSerializer(proctorship_invoice, many=True)
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=serializer.data,
                    code="",
                    description="Details of serializer",
                    log_description="",
                )
            proctorship_invoices = Invoice.objects.all()
            serializer = InvoiceSerializer(proctorship_invoices, many=True)
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
                description="No  Invoice matches the given query.",
            )
        except Invoice.DoesNotExist:
            return self.send_response(
                code="",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invoice doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # add proctorship invoice id
    def post(self, request):
        try:
            data = request.data
            serializer = InvoiceSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                proctorship(Proctorship.objects.get(id=data["proctorship_id"]))
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Invoice is created",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )

        except Invoice.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invoice doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)

    # update proctorship invoice by getting instance with proctorship id
    def put(self, request, pk: None):
        try:
            data = request.data
            invoice = Invoice.objects.get(proctorship__id=pk)
            serializer = InvoiceUpdateSerializer(instance=invoice, data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Invoice is replaced",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except Invoice.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invoice doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


# get, post, update attendance form
class AttendanceFormView(BaseAPIView):
    permission_classes = (IsOauthAuthenticatedSuperAdminLocalAdmin,)

    # get, attendance form by proctorship id
    def get(self, request, pk=None):
        try:
            activity_id = request.query_params.get("activity_id", "")
            if pk is not None:
                proctorship_attendance = AttendanceForm.objects.filter(
                    proctorship__id=pk
                )
                serializer = AttendanceFormSerailizers(
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

            proctorship_attendance = AttendanceForm.objects.all()
            serializer = AttendanceFormSerailizers(proctorship_attendance, many=True)
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
                description="No Attendance Form  matches the given query.",
            )
        except AttendanceForm.DoesNotExist:
            return self.send_response(
                code="",
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

    # post attendance form
    def post(self, request):
        try:
            data = request.data
            serializer = AttendanceFormSerailizers(data=data)
            if serializer.is_valid():
                serializer.save()
                proctorship(Proctorship.objects.get(id=data["proctorship_id"]))
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Attendance Form is created",
                )
            else:
                return self.send_response(
                    code=f"422",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors,
                )
        except AttendanceForm.DoesNotExist:
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

    # update attendance form getting instance by proctorship id

    def put(self, request, pk: None):
        try:
            data = request.data
            proctorship_attendance = AttendanceForm.objects.get(proctorship__id=pk)
            serializer = AttendanceFormUpdateSerailizers(
                instance=proctorship_attendance, data=data
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Attendance Form is replaced",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except AttendanceForm.DoesNotExist:
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
