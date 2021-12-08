from django.db import models

from api.masterproctorship.models import MasterProctorship
from api.preceptorship.models import Preceptorship
from api.proctorship.models import Proctorship
from main.models import Base
# Create your models here.

class Invoice(Base):
    proctorship = models.ForeignKey(Proctorship, on_delete=models.CASCADE, related_name='proctorship_invoice', db_column='ProctorShipID', default=None, null = True)
    invoice_number = models.CharField(db_column='InvoiceNumber', default=None, max_length=255, null=True, blank=True)
    fee_covered = models.CharField(db_column='FEECoveredbyMedicalAffair', default='', max_length=255)
    other_cost =models.CharField(db_column='OtherCostsCoveredByMedicalAffair', default='', max_length=255)
    invoice_date = models.DateField(db_column='DateOfInvoice', default=None)
    note = models.TextField(db_column='Note', default='')
    invoice_sent = models.BooleanField(db_column='InvoicesSentToTheAdministration', default=False)
    class Meta:
        db_table = 'Invoice'

class AttendanceForm(Base):
    attendance_form = models.FileField(db_column='AttendanceForm', upload_to='uploads/', null=True,
                                                blank=True, default=None)
    proctorship = models.ForeignKey(Proctorship, on_delete=models.CASCADE, related_name='proctorship_attendance_form',
                                    db_column='ProctorShipID', default=None, null=True)
    class Meta:
        db_table = "AttendanceForm"