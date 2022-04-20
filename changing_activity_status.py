import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q

from api.masterproctorship.models import MasterProctorship, MasterProctorshipStatus
from api.newmics.models import (
    MicsPreceptorship,
    MicsPreceptorshipStatus,
    MicsProctorship,
    MicsProctorshipStatus,
)
from api.preceptorship.models import Preceptorship, PreceptorshipStatus
from api.proctorship.models import Proctorship
from api.speakingevent.models import Event, EventStatus, SpeakingEvent
from api.status.models import Status, StatusConstantData

# date = datetime.today().strftime('%Y-%m-%d') -
date = datetime.today() + timedelta(1)
date = datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
print(date)


def add_activities_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=all_asctivities())
    t1.start()


def all_asctivities():
    change_proctorship_status_confirmed()
    change_perceptership_status_confirmed()
    change_masterproctorship_status_confirmed()
    change_speakingevent_status_confirmed()
    change_mics_perceptership_status_confirmed()
    change_first_mics_proctorship_status_confirmed()


# Change Proctoship Status
def change_proctorship_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = Proctorship.objects.filter(
            proctorship_status__status__code__in=stat,
            proctorship_status__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total Confirmed Proctorships : {proctorships.count()}")
        for each in proctorships:
            # If status is only pending
            if each.proctorship_status.all().count() <= 2:
                if (
                    each.proctorship_status.all()
                    .order_by("id")[0]
                    .alter_proctorship_porposal.get()
                    .end_date
                    <= date
                ):
                    procotrshipStatus(each, "past-due")
                    print(f"Proctorship of id {each.id} status changed to past Due ")
            # If status is confirmed directly from pending
            elif (
                each.proctorship_status.all().count() == 3
                and each.proctorship_status.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if (
                    each.proctorship_status.all()[0]
                    .alter_proctorship_porposal.get()
                    .end_date
                    <= date
                ):
                    procotrshipStatus(each, "waiting-for-docs")
                    print(
                        f"Proctorship of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif each.proctorship_status.all().count() > 2:
                # If alternate
                if (
                    each.proctorship_status.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        each.proctorship_status.all()
                        .filter(is_active=True)[0]
                        .alter_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        procotrshipStatus(each, "past-due")
                        print(
                            f"Proctorship of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        each.proctorship_status.all()
                        .order_by("-id")[1]
                        .alter_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        procotrshipStatus(each, "waiting-for-docs")
                        print(
                            f"Proctorship of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def procotrshipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["proctorship_activity"] = each
            obj["is_active"] = True
            Status.objects.filter(proctorship_activity__id=each.id).update(
                is_active=False
            )
            obj["status"] = StatusConstantData.objects.get(code=code)
            Status.objects.create(**obj)
    except:
        pass


# Change Perceptership Status
def change_perceptership_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = Preceptorship.objects.filter(
            preceptorshipStatus_status__status__code__in=stat,
            preceptorshipStatus_status__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total Confirmed Preceptorship : {proctorships.count()}")
        for each in proctorships:
            # If status is only pending
            pre_obj = each.preceptorshipStatus_status
            if pre_obj.all().count() <= 2:
                if (
                    pre_obj.all()
                    .order_by("id")[0]
                    .alter_preceptorship_porposal.get()
                    .end_date
                    <= date
                ):
                    perceptershipStatus(each, "past-due")
                    print(f"Preceptorship of id {each.id} status changed to past Due ")
            # If status is confirmed directly from pending
            elif (
                pre_obj.all().count() == 3
                and pre_obj.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if pre_obj.all()[0].alter_preceptorship_porposal.get().end_date <= date:
                    perceptershipStatus(each, "waiting-for-docs")
                    print(
                        f"Preceptorship of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif pre_obj.all().count() > 2:
                # If alternate
                if (
                    pre_obj.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        pre_obj.all()
                        .filter(is_active=True)[0]
                        .alter_preceptorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        perceptershipStatus(each, "past-due")
                        print(
                            f"Preceptorship of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        pre_obj.all()
                        .order_by("-id")[1]
                        .alter_preceptorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        perceptershipStatus(each, "waiting-for-docs")
                        print(
                            f"Preceptorship of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def perceptershipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["preceptorship_activity"] = each
            obj["is_active"] = True
            PreceptorshipStatus.objects.filter(
                preceptorship_activity__id=each.id
            ).update(is_active=False)
            obj["status"] = StatusConstantData.objects.get(code=code)
            PreceptorshipStatus.objects.create(**obj)
    except Exception as e:
        pass


# Change masterproctorship Status
def change_masterproctorship_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = MasterProctorship.objects.filter(
            master_proctorship_status__status__code__in=stat,
            master_proctorship_status__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total Confirmed MasterProctorship : {proctorships.count()}")
        for each in proctorships:
            # If status is only pending
            pre_obj = each.master_proctorship_status
            if pre_obj.all().count() <= 2:
                if (
                    pre_obj.all()
                    .order_by("id")[0]
                    .alter_master_proctorship_porposal.get()
                    .end_date
                    <= date
                ):
                    masterproctorshipStatus(each, "past-due")
                    print(
                        f"MasterProctorship of id {each.id} status changed to past Due "
                    )
            # If status is confirmed directly from pending
            elif (
                pre_obj.all().count() == 3
                and pre_obj.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if (
                    pre_obj.all()[0].alter_master_proctorship_porposal.get().end_date
                    <= date
                ):
                    masterproctorshipStatus(each, "waiting-for-docs")
                    print(
                        f"MasterProctorship of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif pre_obj.all().count() > 2:
                # If alternate
                if (
                    pre_obj.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        pre_obj.all()
                        .filter(is_active=True)[0]
                        .alter_master_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        masterproctorshipStatus(each, "past-due")
                        print(
                            f"MasterProctorship of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        pre_obj.all()
                        .order_by("-id")[1]
                        .alter_master_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        masterproctorshipStatus(each, "waiting-for-docs")
                        print(
                            f"MasterProctorship of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def masterproctorshipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["master_proctorship_activity"] = each
            obj["is_active"] = True
            MasterProctorshipStatus.objects.filter(
                master_proctorship_activity__id=each.id
            ).update(is_active=False)
            obj["status"] = StatusConstantData.objects.get(code=code)
            MasterProctorshipStatus.objects.create(**obj)
    except Exception as e:
        pass


# Speaking Event
def change_speakingevent_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = Event.objects.filter(
            event_status_event__status__code__in=stat,
            event_status_event__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total Confirmed SpeakingEvent : {proctorships.count()}")
        for each in proctorships:
            # If event_status_event is only pending
            pre_obj = each.event_status_event
            if pre_obj.all().count() <= 2:
                if pre_obj.all().order_by("id")[0].event_status.get().end_date <= date:
                    speakingeventshipStatus(each, "past-due")
                    print(f"SpeakingEvent of id {each.id} status changed to past Due ")
            # If status is confirmed directly from pending
            elif (
                pre_obj.all().count() == 3
                and pre_obj.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if pre_obj.all()[0].event_status.get().end_date <= date:
                    speakingeventshipStatus(each, "waiting-for-docs")
                    print(
                        f"SpeakingEvent of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif pre_obj.all().count() > 2:
                # If alternate
                if (
                    pre_obj.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        pre_obj.all()
                        .filter(is_active=True)[0]
                        .event_status.get()
                        .end_date
                        <= date
                    ):
                        speakingeventshipStatus(each, "past-due")
                        print(
                            f"SpeakingEvent of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        pre_obj.all().order_by("-id")[1].event_status.get().end_date
                        <= date
                    ):
                        speakingeventshipStatus(each, "waiting-for-docs")
                        print(
                            f"SpeakingEvent of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def speakingeventshipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["event"] = each
            obj["is_active"] = True
            EventStatus.objects.filter(event__id=each.id).update(is_active=False)
            obj["status"] = StatusConstantData.objects.get(code=code)
            EventStatus.objects.create(**obj)
    except Exception as e:
        pass


# Mics Perceptership
def change_mics_perceptership_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = MicsPreceptorship.objects.filter(
            mics_preceptorshipStatus_status__status__code__in=stat,
            mics_preceptorshipStatus_status__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total MicsPerceptership : {proctorships.count()}")
        for each in proctorships:
            # If event_status_event is only pending
            pre_obj = each.mics_preceptorshipStatus_status
            if pre_obj.all().count() <= 2:
                if (
                    pre_obj.all()
                    .order_by("id")[0]
                    .alter_mics_preceptorship_porposal.get()
                    .end_date
                    <= date
                ):
                    mics_perceptershipStatus(each, "past-due")
                    print(
                        f"MicsPerceptership of id {each.id} status changed to past Due "
                    )
            # If status is confirmed directly from pending
            elif (
                pre_obj.all().count() == 3
                and pre_obj.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if (
                    pre_obj.all()[0].alter_mics_preceptorship_porposal.get().end_date
                    <= date
                ):
                    mics_perceptershipStatus(each, "waiting-for-docs")
                    print(
                        f"MicsPerceptership of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif pre_obj.all().count() > 2:
                # If alternate
                if (
                    pre_obj.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        pre_obj.all()
                        .filter(is_active=True)[0]
                        .alter_mics_preceptorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        mics_perceptershipStatus(each, "past-due")
                        print(
                            f"MicsPerceptership of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        pre_obj.all()
                        .order_by("-id")[1]
                        .alter_mics_preceptorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        mics_perceptershipStatus(each, "waiting-for-docs")
                        print(
                            f"MicsPerceptership of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def mics_perceptershipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["mics_preceptorship_activity"] = each
            obj["is_active"] = True
            MicsPreceptorshipStatus.objects.filter(
                mics_preceptorship_activity__id=each.id
            ).update(is_active=False)
            obj["status"] = StatusConstantData.objects.get(code=code)
            MicsPreceptorshipStatus.objects.create(**obj)
    except Exception as e:
        pass


# Mics Proctortership
def change_first_mics_proctorship_status_confirmed():
    try:
        stat = ["alternative-proposal", "processing", "pending", "confirmed"]
        proctorships = MicsProctorship.objects.filter(
            mics_proctorship_status__status__code__in=stat,
            mics_proctorship_status__is_active=True,
        )
        # proctorships = Proctorship.objects.all()
        print(f"Total First MicsProctorship : {proctorships.count()}")
        for each in proctorships:
            # If event_status_event is only pending
            pre_obj = each.mics_proctorship_status
            if pre_obj.all().count() <= 2:
                if (
                    pre_obj.all()
                    .order_by("id")[0]
                    .mics_proctorship_porposal.get()
                    .end_date
                    <= date
                ):
                    mics_first_proctorshipStatus(each, "past-due")
                    print(
                        f"First MicsProctorship of id {each.id} status changed to past Due "
                    )
            # If status is confirmed directly from pending
            elif (
                pre_obj.all().count() == 3
                and pre_obj.filter(is_active=True)[0].status.code
                != "alternative-proposal"
            ):
                if pre_obj.all()[0].mics_proctorship_porposal.get().end_date <= date:
                    mics_first_proctorshipStatus(each, "waiting-for-docs")
                    print(
                        f"First MicsProctorship of id {each.id} status changed to Waiting for Docs "
                    )
            # If status has alternates
            elif pre_obj.all().count() > 2:
                # If alternate
                if (
                    pre_obj.filter(is_active=True)[0].status.code
                    == "alternative-proposal"
                ):
                    if (
                        pre_obj.all()
                        .filter(is_active=True)[0]
                        .mics_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        mics_first_proctorshipStatus(each, "past-due")
                        print(
                            f"First MicsProctorship of id {each.id} status changed to Past Due "
                        )
                # if confirmed
                else:
                    if (
                        pre_obj.all()
                        .order_by("-id")[1]
                        .mics_proctorship_porposal.get()
                        .end_date
                        <= date
                    ):
                        mics_first_proctorshipStatus(each, "waiting-for-docs")
                        print(
                            f"First MicsProctorship of id {each.id} status changed to Waiting for Docs "
                        )
    except Exception as e:
        print(e)
        pass


def mics_first_proctorshipStatus(each, code):
    try:
        with transaction.atomic():
            obj = {}
            obj["proctorship_activity"] = each
            obj["is_active"] = True
            MicsProctorshipStatus.objects.filter(
                proctorship_activity__id=each.id
            ).update(is_active=False)
            obj["status"] = StatusConstantData.objects.get(code=code)
            MicsProctorshipStatus.objects.create(**obj)
    except Exception as e:
        pass


add_activities_thread()

# change_first_mics_proctorship_status_confirmed()
