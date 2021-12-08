# from sendgrid import sendgrid
from django.db.models import Q
from sendgrid.helpers.mail import Mail
import sendgrid

from api.feedback.models import MemoProctorFeedBack, SoloSmartProctorFeedBack, ProctorshipProctorFeedback, \
    TraineeFeedback
from api.invoice.models import AttendanceForm, Invoice
from api.masterproctorship.models import MasterProctorshipProctors, MasterProctorshipProposal, MasterProctorship, \
    MasterProctorshipTraineeProfile, MasterProctorshipProctorReport, MasterProctorshipFeedback, \
    InvoiceMasterProctorShip, MasterProctorshipStatus, AttendanceFormMasterProctorShip
from api.newmics.models import MicsPreceptorship, MicsPreceptorshipProposal, MicsPreceptorshipProctors, MicsProctorship, \
    MicsProctorshipProposal, MicsProctorshipProctors
from api.preceptorship.models import Preceptorship, PreceptorshipProposal, PreceptorshipProctors, \
    AttendanceFormPerceptorship, PreceptorshipTraineeUploads, PreceptorshipStatus, InvoicePerceptorship, \
    TraineePreceptorshipProfile
from api.proctorship.models import Proctorship
from api.speakingevent.models import Speaker, SpeakingEvent, Event
from api.status.models import ProctorshipProctors, Proposal, StatusConstantData, Status
from api.trainee.models import TraineeProfile
from cspro.settings.settings import SENDGRID_API_KEY


def send_email_sendgrid_template(from_email="", to_email="", subject="", data="", template=""):
    try:
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

        message = sendgrid.helpers.mail.Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        message.dynamic_template_data = data
        message.template_id = template
        status = sg.send(message)
        return [status]
    except Exception as e:
        return e

def check_perceptorship(proctor_id, start_date, end_date):
    try:
        precep_query_object = Q(preceptorshipStatus_status__is_active=True)
        precep_query_object &= Q(preceptorshipStatus_status__status__code="confirmed") | Q(
            preceptorshipStatus_status__status__code="waiting-for-docs")

        percep_activities = Preceptorship.objects.filter(precep_query_object)
        percep_activities_id = [each.id for each in percep_activities]

        latest_percep_purposal_id = []
        for x in percep_activities_id:
            latest_percep_purposal_id.append(
                PreceptorshipProposal.objects.filter(status__preceptorship_activity__id=x).latest("created_on").id)

        precp_filtered = []
        for a in latest_percep_purposal_id:
            precp_proposal = PreceptorshipProposal.objects.get(id=a)
            if (str(precp_proposal.start_date) < start_date) and (str(precp_proposal.end_date) > start_date):
                precp_filtered.append(precp_proposal.id)
            elif (str(precp_proposal.start_date) < end_date) and (str(precp_proposal.end_date) > end_date):
                precp_filtered.append(precp_proposal.id)
            elif (str(precp_proposal.start_date) == start_date) or (str(precp_proposal.end_date) == end_date) or (str(precp_proposal.start_date) == end_date) or (str(precp_proposal.end_date) == start_date):
                precp_filtered.append(precp_proposal.id)

        percep_proctors = PreceptorshipProctors.objects.filter(
            preceptorship_proposal__id__in=precp_filtered, status=True)
        percep_proctors = [each.proctors.id for each in percep_proctors]
        if proctor_id in percep_proctors:
            return True
        return False
    except Exception as e:
        return e

def check_masterproctorship(proctor_id, start_date, end_date):
    try:
        master_query_object = Q(master_proctorship_status__is_active=True)
        master_query_object &= Q(master_proctorship_status__status__code="confirmed") | Q(
            master_proctorship_status__status__code="waiting-for-docs")

        master_activities = MasterProctorship.objects.filter(master_query_object)
        master_activities_id = [each.id for each in master_activities]

        latest_master_purposal_id = []
        for x in master_activities_id:
            latest_master_purposal_id.append(
                MasterProctorshipProposal.objects.filter(status__master_proctorship_activity__id=x).latest(
                    "created_on").id)

        master_filtered = []
        for a in latest_master_purposal_id:
            master_proposal = MasterProctorshipProposal.objects.get(id=a)
            if (str(master_proposal.start_date) < start_date) and (
                    str(master_proposal.end_date) > start_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) < end_date) and (str(master_proposal.end_date) > end_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) == start_date) or (str(master_proposal.end_date) == end_date) or (str(master_proposal.start_date) == end_date) or (str(master_proposal.end_date) == start_date):
                master_filtered.append(master_proposal.id)

        master_proctors = MasterProctorshipProctors.objects.filter(
            master_proctorship_proposal__id__in=master_filtered, status=True)
        percep_proctors = [each.proctors.id for each in master_proctors]
        if proctor_id in percep_proctors:
            return True
        return False
    except Exception as e:
        return e

def check(proctor_id, start_date, end_date):
    try:
        quer_object = Q(proctorship_status__is_active=True)
        quer_object &= Q(proctorship_status__status__code="confirmed") | Q(
            proctorship_status__status__code="waiting-for-docs")
        activities = Proctorship.objects.filter(quer_object)
        proctorship_id = [each.id for each in activities]
        latest_purposal_id = []
        for x in proctorship_id:
            latest_purposal_id.append(
                Proposal.objects.filter(status__proctorship_activity__id=x).latest("created_on").id)

        filtered = []
        for a in latest_purposal_id:
            proposal = Proposal.objects.get(id=a)
            if (str(proposal.start_date) < start_date) and (str(proposal.end_date) > start_date):
                filtered.append(proposal.id)
            elif (str(proposal.start_date) < end_date) and (str(proposal.end_date) > end_date):
                filtered.append(proposal.id)
            elif (str(proposal.start_date) == start_date) or (str(proposal.end_date) == end_date) or (str(proposal.start_date) == end_date) or (str(proposal.end_date) == start_date):
                filtered.append(proposal.id)

        proctorship_proctors = ProctorshipProctors.objects.filter(porposal__id__in=filtered, status=True)
        proctorship_proctors_id = [each.proctors.id for each in proctorship_proctors]
        proctorship_proctors_id = list(set(proctorship_proctors_id))

        if proctor_id in proctorship_proctors_id:
            return True
        return False
    except Exception as e:
        return e

def check_event(proctor_id, start_date, end_date):
    try:
        event_query_object = Q(event_status_event__is_active=True)
        event_query_object &= Q(event_status_event__status__code="confirmed") | Q(
            event_status_event__status__code="waiting-for-docs")
        event = Event.objects.filter(event_query_object)
        event_id = [each.id for each in event]
        filtered_event = []
        for each in event_id:
            speaking_event = SpeakingEvent.objects.filter(event_status__event__id=each).latest("created_on")
            if (str(speaking_event.start_date) < start_date) and (
                    str(speaking_event.end_date) > start_date):
                filtered_event.append(each)
            elif (str(speaking_event.start_date) < end_date) and (str(speaking_event.end_date) > end_date):
                filtered_event.append(each)
            elif (str(speaking_event.start_date) == start_date) or (str(speaking_event.end_date) == end_date) or (str(speaking_event.start_date) == end_date) or (str(speaking_event.end_date) == start_date):
                filtered_event.append(each)

        speakers = Speaker.objects.filter(event__id__in=filtered_event,proctor__isnull=False, status=True, revoke=False)
        speakes_id = [each.proctor.id for each in speakers]
        speakes_id = list(set(speakes_id))
        if proctor_id in speakes_id:
            return True
        return False
    except Exception as e:
        return e

def check_mics_perceptorship(proctor_id, start_date, end_date):
    try:
        master_query_object = Q(mics_preceptorshipStatus_status__is_active=True)
        master_query_object &= Q(mics_preceptorshipStatus_status__status__code="confirmed") | Q(
            mics_preceptorshipStatus_status__status__code="waiting-for-docs")

        master_activities = MicsPreceptorship.objects.filter(master_query_object)
        master_activities_id = [each.id for each in master_activities]

        latest_master_purposal_id = []
        for x in master_activities_id:
            latest_master_purposal_id.append(
                MicsPreceptorshipProposal.objects.filter(status__mics_preceptorship_activity__id=x).latest(
                    "created_on").id)

        master_filtered = []
        for a in latest_master_purposal_id:
            master_proposal = MicsPreceptorshipProposal.objects.get(id=a)
            if (str(master_proposal.start_date) < start_date) and (
                    str(master_proposal.end_date) > start_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) < end_date) and (str(master_proposal.end_date) > end_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) == start_date) or (str(master_proposal.end_date) == end_date) or (str(master_proposal.start_date) == end_date) or (str(master_proposal.end_date) == start_date):
                master_filtered.append(master_proposal.id)

        master_proctors = MicsPreceptorshipProctors.objects.filter(
            mics_preceptorship_proposal__id__in=master_filtered, status=True)
        percep_proctors = [each.proctors.id for each in master_proctors]
        if proctor_id in percep_proctors:
            return True
        return False
    except Exception as e:
        return e

def check_mics_perceptorship(proctor_id, start_date, end_date):
    try:
        master_query_object = Q(mics_proctorship_status__is_active=True)
        master_query_object &= Q(mics_proctorship_status__status__code="confirmed") | Q(
            mics_proctorship_status__status__code="waiting-for-docs")

        master_activities = MicsProctorship.objects.filter(master_query_object)
        master_activities_id = [each.id for each in master_activities]

        latest_master_purposal_id = []
        for x in master_activities_id:
            latest_master_purposal_id.append(
                MicsProctorshipProposal.objects.filter(status__proctorship_activity__id=x).latest(
                    "created_on").id)

        master_filtered = []
        for a in latest_master_purposal_id:
            master_proposal = MicsProctorshipProposal.objects.get(id=a)
            if (str(master_proposal.start_date) < start_date) and (
                    str(master_proposal.end_date) > start_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) < end_date) and (str(master_proposal.end_date) > end_date):
                master_filtered.append(master_proposal.id)
            elif (str(master_proposal.start_date) == start_date) or (str(master_proposal.end_date) == end_date) or (str(master_proposal.start_date) == end_date) or (str(master_proposal.end_date) == start_date):
                master_filtered.append(master_proposal.id)

        master_proctors = MicsProctorshipProctors.objects.filter(
            porposal__id__in=master_filtered, status=True)
        percep_proctors = [each.proctors.id for each in master_proctors]
        if proctor_id in percep_proctors:
            return True
        return False
    except Exception as e:
        return e




def available_proctors(proctors, start_date, end_date):
    try:
        if proctors:
            quer_object = Q(proctorship_status__is_active=True)
            quer_object &= Q(proctorship_status__status__code="confirmed") | Q(
                proctorship_status__status__code="waiting-for-docs")
            activities = Proctorship.objects.filter(quer_object)
            proctorship_id = [each.id for each in activities]
            latest_purposal_id = []
            for x in proctorship_id:
                latest_purposal_id.append(
                    Proposal.objects.filter(status__proctorship_activity__id=x).latest("created_on").id)

            filtered = []
            for a in latest_purposal_id:
                proposal = Proposal.objects.get(id=a)
                if (str(proposal.start_date) < start_date) and (str(proposal.end_date) > start_date):
                    filtered.append(proposal.id)
                elif (str(proposal.start_date) < end_date) and (str(proposal.end_date) > end_date):
                    filtered.append(proposal.id)
                elif (str(proposal.start_date) == start_date) or (str(proposal.end_date) == end_date) or (
                        str(proposal.start_date) == end_date) or (str(proposal.end_date) == start_date):
                    filtered.append(proposal.id)

            proctorship_proctors = ProctorshipProctors.objects.filter(porposal__id__in=filtered, status=True)
            proctorship_proctors_id = [each.proctors.id for each in proctorship_proctors]
            proctorship_proctors_id = list(set(proctorship_proctors_id))
            proctors = proctors.exclude(id__in=proctorship_proctors_id)

        # check for perceptorship
        if proctors:
            precep_query_object = Q(preceptorshipStatus_status__is_active=True)
            precep_query_object &= Q(preceptorshipStatus_status__status__code="confirmed") | Q(
                preceptorshipStatus_status__status__code="waiting-for-docs")

            percep_activities = Preceptorship.objects.filter(precep_query_object)
            percep_activities_id = [each.id for each in percep_activities]

            latest_percep_purposal_id = []
            for x in percep_activities_id:
                latest_percep_purposal_id.append(
                    PreceptorshipProposal.objects.filter(status__preceptorship_activity__id=x).latest(
                        "created_on").id)

            precp_filtered = []
            for a in latest_percep_purposal_id:
                precp_proposal = PreceptorshipProposal.objects.get(id=a)
                if (str(precp_proposal.start_date) < start_date) and (str(precp_proposal.end_date) > start_date):
                    precp_filtered.append(precp_proposal.id)
                elif (str(precp_proposal.start_date) < end_date) and (str(precp_proposal.end_date) > end_date):
                    precp_filtered.append(precp_proposal.id)
                elif (str(precp_proposal.start_date) == start_date) or (
                        str(precp_proposal.end_date) == end_date) or (
                        str(precp_proposal.start_date) == end_date) or (str(precp_proposal.end_date) == start_date):
                    precp_filtered.append(precp_proposal.id)
                else:
                    pass

            percep_proctors = PreceptorshipProctors.objects.filter(
                preceptorship_proposal__id__in=precp_filtered, status=True)
            percep_proctors = [each.proctors.id for each in percep_proctors]
            percep_proctors = list(set(percep_proctors))
            proctors = proctors.exclude(id__in=percep_proctors)

        # MasterProctorship
        if proctors:
            master_query_object = Q(master_proctorship_status__is_active=True)
            master_query_object &= Q(master_proctorship_status__status__code="confirmed") | Q(
                master_proctorship_status__status__code="waiting-for-docs")

            master_activities = MasterProctorship.objects.filter(master_query_object)
            master_activities_id = [each.id for each in master_activities]

            latest_master_purposal_id = []
            for x in master_activities_id:
                latest_master_purposal_id.append(
                    MasterProctorshipProposal.objects.filter(status__master_proctorship_activity__id=x).latest(
                        "created_on").id)

            master_filtered = []
            for a in latest_master_purposal_id:
                master_proposal = MasterProctorshipProposal.objects.get(id=a)
                if (str(master_proposal.start_date) < start_date) and (
                        str(master_proposal.end_date) > start_date):
                    master_filtered.append(master_proposal.id)
                elif (str(master_proposal.start_date) < end_date) and (str(master_proposal.end_date) > end_date):
                    master_filtered.append(master_proposal.id)
                elif (str(master_proposal.start_date) == start_date) or (
                        str(master_proposal.end_date) == end_date) or (
                        str(master_proposal.start_date) == end_date) or (
                        str(master_proposal.end_date) == start_date):
                    master_filtered.append(master_proposal.id)
                else:
                    pass

            master_proctors = MasterProctorshipProctors.objects.filter(
                master_proctorship_proposal__id__in=master_filtered, status=True)
            maste_proctors = [each.proctors.id for each in master_proctors]
            maste_proctors = list(set(maste_proctors))
            proctors = proctors.exclude(id__in=maste_proctors)

        if proctors:
            event_query_object = Q(event_status_event__is_active=True)
            event_query_object &= Q(event_status_event__status__code="confirmed") | Q(
                event_status_event__status__code="waiting-for-docs")
            event = Event.objects.filter(event_query_object)
            event_id = [each.id for each in event]
            filtered_event = []
            for each in event_id:
                speaking_event = SpeakingEvent.objects.filter(event_status__event__id=each).latest("created_on")
                if (str(speaking_event.start_date) < start_date) and (
                        str(speaking_event.end_date) > start_date):
                    filtered_event.append(each)
                elif (str(speaking_event.start_date) < end_date) and (str(speaking_event.end_date) > end_date):
                    filtered_event.append(each)
                elif (str(speaking_event.start_date) == start_date) or (
                        str(speaking_event.end_date) == end_date) or (
                        str(speaking_event.start_date) == end_date) or (str(speaking_event.end_date) == start_date):
                    filtered_event.append(each)
                else:
                    pass

            speakers = Speaker.objects.filter(event__id__in=filtered_event,proctor__isnull=False, status=True, revoke=False)
            speakes_id = [each.proctor.id for each in speakers]
            speakes_id = list(set(speakes_id))
            proctors = proctors.exclude(id__in=speakes_id)
        return proctors
    except Exception as e:
        return e




def activity_id(char, num):
    import datetime
    time = str(datetime.datetime.now().strftime('%y%m%d'))
    time = str(num)+time
    count = len(list(time))
    zero = 10-count
    add = "0"*zero
    return f'{char}{add + time}'

def solo_memo(activity_id):
    if MemoProctorFeedBack.objects.filter(proctorship__id =activity_id) and SoloSmartProctorFeedBack.objects.filter(proctorship__id =activity_id):
        return True
    else:
        return False

def memo_perc(activity_id):
    if MemoProctorFeedBack.objects.filter(proctorship__id =activity_id) and ProctorshipProctorFeedback.objects.filter(proctorship__id =activity_id):
        return True
    else:
        return False


def perc_solo(activity_id):
    if ProctorshipProctorFeedback.objects.filter(proctorship__id =activity_id) and  SoloSmartProctorFeedBack.objects.filter(proctorship__id =activity_id):
        return True
    else:
        return False




def check_product_feedback(activity_id, prod = None):

    product = []
    if Proctorship.objects.get(id=activity_id).product:
        product.append(Proctorship.objects.get(id=activity_id).product.product_name)
    if Proctorship.objects.get(id=activity_id).secondary_product:
        product.append(Proctorship.objects.get(id=activity_id).secondary_product.product_name)


    if ("Memo Family" in product) and ("Solo Smart" in product):
        return solo_memo(activity_id)
    elif  ("Memo Family" in product) and ("Perceval" in product):
        return memo_perc(activity_id)
    elif ("Perceval" in product) and ("Solo Smart" in product):
        return perc_solo(activity_id)

    elif "Perceval" == product[0]:
        if ProctorshipProctorFeedback.objects.filter(proctorship__id=activity_id):
            return True
        else:
            return False


    elif "Solo Smart" == product[0]:
        if SoloSmartProctorFeedBack.objects.filter(proctorship__id=activity_id):
            return True
        else:
            return False

    elif "Memo Family" == product[0]:
        if MemoProctorFeedBack.objects.filter(proctorship__id=activity_id):
            return True
        else:
            return False





# if prod == "Memo Family":
#     if not MemoProctorFeedBack.objects.filter(proctorship__id=activity_id):
#         return True
# elif not prod:
#     if MemoProctorFeedBack.objects.filter(proctorship__id=activity_id):
#         return True
#     else:
#         return False


def perceptership(obj):
    if AttendanceFormPerceptorship.objects.filter(preceptorship__id=obj.id) and InvoicePerceptorship.objects.filter(
            preceptorship__id=obj.id) and PreceptorshipTraineeUploads.objects.filter(
            preceptorship_trainee__preceptorship__id=obj.id,
            preceptorship_trainee__revoke=False).count() == TraineePreceptorshipProfile.objects.filter(
        preceptorship__id=obj.id).count() and PreceptorshipStatus.objects.filter(preceptorship_activity__id=obj.id).order_by("-id")[0].status.code != 'closed':
        PreceptorshipStatus.objects.filter(preceptorship_activity__id=obj.id).update(is_active=False)
        status_obj = {}
        status_obj['preceptorship_activity'] = obj
        status_obj['status'] = StatusConstantData.objects.get(code='closed')
        status = PreceptorshipStatus.objects.create(**status_obj)



def proctorship(obj):
    if check_product_feedback(obj.id, prod="Solo Smart") and TraineeProfile.objects.filter(proctorship__id=obj.id, revoke=False).count() == TraineeFeedback.objects.filter(
            trainee__proctorship__id=obj.id, trainee__revoke = False).count() and AttendanceForm.objects.filter(
            proctorship__id=obj.id) and Invoice.objects.filter(proctorship__id=obj.id)  and Status.objects.filter(
            proctorship_activity__id=obj.id).order_by("-id")[
                0].status.code != 'closed':
        Status.objects.filter(proctorship_activity__id=obj.id).update(is_active=False)
        status_data = {'status': StatusConstantData.objects.get(code='closed'),
                       'proctorship_activity': Proctorship.objects.get(
                           id=obj.id)}
        status_data = Status.objects.create(**status_data)
        status_data.save()


def master_proctorship(obj):
    if MasterProctorshipTraineeProfile.objects.filter(
                    master_proctorship__id=obj.id, revoke=False).count() == MasterProctorshipProctorReport.objects.filter(
            master_proctorship_trainee__master_proctorship__id=obj.id, master_proctorship_trainee__revoke=False).count() and MasterProctorshipFeedback.objects.filter(
        master_proctorship_activity__id=obj.id) and InvoiceMasterProctorShip.objects.filter(
        master_proctorship__id=obj.id) and AttendanceFormMasterProctorShip.objects.filter(
                    master_proctorship__id=obj.id) and MasterProctorshipStatus.objects.filter(
            master_proctorship_activity__id=obj.id).order_by("-id")[
                0].status.code != 'closed':
        MasterProctorshipStatus.objects.filter(
            master_proctorship_activity__id=obj.id).update(is_active=False)
        status_data = {'status': StatusConstantData.objects.get(code='closed'),
                       'master_proctorship_activity': obj}
        status_data = MasterProctorshipStatus.objects.create(**status_data)
        status_data.save()
