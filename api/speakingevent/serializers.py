from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from api.models import EventType, Speciality, Hcp_role, AreaOfExperties, Hospital
from api.proctors.models import Proctors
from api.serializers import AudienceSerializer, SolutionSerializer, RegionSerializer, LanguagesSerializer
from api.speakingevent.models import SpeakingEvent, Speaker, Event, EventStatus, SpeakingEventFeedBack, TopicRating, \
    AttendanceFormSpeakingEvent, CognosId
import json

from api.status.models import StatusConstantData
from api.users.models import User
from cspro.utilities.convert_boolean import boolean
from cspro.utils import activity_id


class SpeakerSerializer(serializers.ModelSerializer):
    # event = serializers.SerializerMethodField(read_only = True)
    speaker_role = serializers.CharField(required=True)
    specialty = serializers.CharField(required=True)
    duration = serializers.IntegerField(required=True, allow_null=True)
    speech_focus = serializers.SerializerMethodField(read_only=True)
    proctor = serializers.SerializerMethodField(read_only=True)
    proctor_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    event_id = serializers.IntegerField(write_only=True)
    speech_focus_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    focus_not_listed = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    depart_employee = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    name_employee = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    new_mics = serializers.BooleanField(required=True)
    signed_letter = serializers.FileField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    revoke = serializers.BooleanField(read_only=True)
    other_proctor = serializers.CharField(read_only=True)
    # speech_focus_id = serializers.StringRelatedField(read_only=True)
    # proctor_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Speaker
        fields = ["id","speech_focus_id","new_mics", "name_employee", "depart_employee",
                  "focus_not_listed", "title", "speech_focus_id", "event_id", "notes", "proctor_id",
                  "proctor", "speech_focus", "duration", "specialty", "speaker_role", "signed_letter",
                  "status", "other_proctor", "revoke"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = validated_data.pop("user")
                if 'speech_focus_id' in validated_data.keys():
                    speech_focus_id = validated_data.pop('speech_focus_id')
                    if speech_focus_id:
                        validated_data['speech_focus'] = AreaOfExperties.objects.get(id=speech_focus_id)
                if 'proctor_id' in validated_data.keys():
                    proctor_id = validated_data.pop('proctor_id')
                    if proctor_id:
                        validated_data['proctor'] = Proctors.objects.get(id=proctor_id)
                specialty = validated_data.pop('specialty')
                validated_data['specialty'] = Speciality.objects.get(code=specialty)
                speaker_role = validated_data.pop('speaker_role')
                validated_data['speaker_role'] = Hcp_role.objects.get(code=speaker_role)
                speaker = Speaker.objects.create(**validated_data)

                # status_data = {'status': StatusConstantData.objects.get(code='processing'),
                #                'event': Event.objects.get(id=validated_data["event_id"]), 'user': user}
                # status_data = EventStatus.objects.create(**status_data)
                # speaker.save()
                return speaker
        except Exception as e:
            return e

    def get_speech_focus(self, obj):
        try:
            return obj.speech_focus.name
        except:
            return None

    def get_proctor(self, obj):
        try:
            return obj.proctor.user.name
        except:
            return None

    def get_speech_focus_id(self, obj):
        try:
            return obj.speech_focus.name
        except:
            return None

    def get_proctor_id(self, obj):
        try:
            return obj.proctor.id
        except:
            return None


class SpeakingEventSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    event_name = serializers.CharField(required=True)
    event_type = serializers.CharField(required=True)
    event_location = serializers.CharField(required=True)
    event_id = serializers.IntegerField(write_only=True)
    solution = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    solution_id = serializers.ListField(write_only=True)
    participants = serializers.IntegerField(required=True)
    audience_type = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    audience_type_id = serializers.ListField(write_only=True)
    audience_region = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    audience_region_id = serializers.ListField(write_only=True)
    notes = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    language_id = serializers.ListField(write_only=True)

    class Meta:
        model = SpeakingEvent
        fields = ['id', 'user_id', 'start_date', 'end_date', 'event_name', 'event_type', 'event_location', 'event_id',
                  'solution', 'solution_id', 'participants', 'audience_type',
                  'audience_type_id', 'audience_region', 'audience_region_id', 'notes', 'language_id']

    def string_to_list(self, data):
        if data != "":
            a_list = data.split(',')
            map_object = map(int, a_list)
            list_of_integers = list(map_object)
            print(list_of_integers)
            return list_of_integers

    def create(self, validated_data):
        with transaction.atomic():
            user_id = validated_data.pop('user_id')
            event_id = validated_data.pop('event_id')
            qs = EventStatus.objects.filter(event__id=event_id, is_active=True)
            qs.update(is_active=False)
            status_data = {'status': StatusConstantData.objects.get(code='alternative-proposal'),
                           'event': Event.objects.get(id=event_id), 'user': User.objects.get(id=user_id),
                           "is_active" :True}
            status_data = EventStatus.objects.create(**status_data)

            solution = validated_data.pop('solution_id')
            audience_type = validated_data.pop('audience_type_id')
            audience_region = validated_data.pop('audience_region_id')
            languages = validated_data.pop('language_id')
            event_type = validated_data.pop('event_type')
            validated_data['event_type'] = EventType.objects.get(code=event_type)
            validated_data['event_status'] = status_data
            speaking_event = SpeakingEvent.objects.create(**validated_data)
            if solution:
                speaking_event.solution.add(*solution)

            if audience_type:
                speaking_event.audience_type.add(*audience_type)

            if audience_region:
                speaking_event.audience_region.add(*audience_region)

            if languages:
                speaking_event.language.add(*languages)

            speaking_event.save()
            return speaking_event


class EventSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    event_country = serializers.SerializerMethodField(read_only=True)
    event_country_id = serializers.IntegerField(write_only=True)
    agenda = serializers.FileField(required=True, allow_null=True)
    no_speach = serializers.BooleanField(required=True)
    speaking_event = serializers.CharField(required=True)
    speaker = serializers.CharField(required=True)
    is_global = serializers.BooleanField(required=True)


    class Meta:
        model = Event
        fields = ['user_id', 'is_global', 'event_country', 'event_country_id', 'agenda', 'no_speach', 'speaking_event',
                  'speaker']

    def create(self, validated_data):
        try:
            with transaction.atomic():
                speaking_event = json.loads(validated_data.pop('speaking_event'))
                speaker = json.loads(validated_data.pop('speaker'))
                user_id = validated_data.pop('user_id')
                event = Event.objects.create(**validated_data)
                num = event.id
                char = "SG"
                if not event.is_global:
                    char = "SL"
                event.activity_id = activity_id(char, num)

                for each in speaker:
                    each['event'] = event
                    each['speaker_role'] = Hcp_role.objects.get(code=each.pop('speaker_role'))
                    each['specialty'] = Speciality.objects.get(code=each.pop('specialty'))
                    if 'speech_focus_id' in each.keys():
                        pk = each.pop('speech_focus_id')
                        if pk:
                            each['speech_focus'] = AreaOfExperties.objects.get(id=pk)
                    if 'proctor_id' in each.keys():
                        pid = each.pop('proctor_id')
                        if pid:
                            each['proctor'] = Proctors.objects.get(id=pid)
                    speaker = Speaker.objects.create(**each)

                status_data = {'status': StatusConstantData.objects.get(code='pending'),
                               'event': event, 'user': User.objects.get(id=user_id)}
                status_data = EventStatus.objects.create(**status_data)
                speaking_event['event_status'] = status_data
                solution = speaking_event.pop('solution_id')
                audience_type = speaking_event.pop('audience_type_id')
                audience_region = speaking_event.pop('audience_region_id')
                event_type = speaking_event.pop('event_type')
                language = speaking_event.pop('language_id')
                speaking_event['event_type'] = EventType.objects.get(code=event_type)
                speaking_event = SpeakingEvent.objects.create(**speaking_event)

                if solution:
                    speaking_event.solution.add(*solution)

                if audience_type:
                    speaking_event.audience_type.add(*audience_type)

                if audience_region:
                    speaking_event.audience_region.add(*audience_region)

                if language:
                    speaking_event.language.add(*audience_region)

                event.save()
                return event
        except Exception as e:
            return e


class SpeakingEventViewSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    event_name = serializers.CharField(required=True)
    event_type = serializers.SerializerMethodField(read_only=True)
    event_location = serializers.CharField(required=True)
    solution = serializers.SerializerMethodField(read_only=True)
    participants = serializers.IntegerField(required=True)
    audience_type = serializers.SerializerMethodField(read_only=True)
    audience_region = serializers.SerializerMethodField(read_only=True)
    language = serializers.SerializerMethodField(read_only=True)
    notes = serializers.CharField(required=True, allow_blank=True, allow_null=True)

    class Meta:
        model = SpeakingEvent
        # fields = ['id', 'start_date', 'end_date', 'event_name', 'event_type', 'event_location', 'solution',
        #           'participants', 'audience_type', 'audience_region', 'notes', 'language']
        fields = "__all__"

    def get_audience_type(self, obj):
        try:
            return AudienceSerializer(obj.audience_type.all(), many=True).data
        except:
            return None

    def get_solution(self, obj):
        try:
            return SolutionSerializer(obj.solution.all(), many=True).data
        except:
            return None

    def get_audience_region(self, obj):
        try:
            return RegionSerializer(obj.audience_region.all(), many=True).data
        except:
            return None

    def get_event_type(self, obj):
        try:
            return obj.event_type.code
        except:
            return None

    def get_language(self, obj):
        try:
            return LanguagesSerializer(obj.language.all(), many=True).data
        except:
            return None


class StatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(read_only=True)
    reason = serializers.CharField(read_only=True)
    date = serializers.DateField(read_only=True)
    code = serializers.SerializerMethodField(read_only=True)
    speaking_event = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventStatus
        fields = ['user', 'status', 'reason', 'date', 'speaking_event', 'code']

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_speaking_event(self, obj):
        try:
            return SpeakingEventViewSerializer(SpeakingEvent.objects.get(event_status__id=obj.id)).data
        except:
            return None

    def get_code(self, obj):
        try:
            return obj.status.code
        except:
            return None


class EventViewSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField(read_only=True)
    event_country = serializers.SerializerMethodField(read_only=True)
    agenda = serializers.FileField(read_only=True)
    meeting_docs = serializers.FileField(read_only=True)
    no_speach = serializers.BooleanField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    is_global = serializers.BooleanField(read_only=True)
    activity_id = serializers.CharField(read_only=True)

    # speaker = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'is_global', 'event_country', 'agenda', 'no_speach', 'status', "activity_id", "meeting_docs"]

    # def get_user(self, obj):
    #     try:
    #         return obj.user.name
    #     except:
    #         return None

    def get_event_country(self, obj):
        try:
            return obj.event_country.name
        except:
            return None

    def get_status(self, obj):
        try:
            return StatusSerializer(EventStatus.objects.filter(event__id=obj.id), many=True).data
        except:
            return None


class StatusAddSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    status = serializers.CharField(required=True)
    reason = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    event_id = serializers.IntegerField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        model = EventStatus
        fields = ['user_id', 'date', 'user', 'status', 'reason', 'event_id']

    def create(self, validated_data):
        try:
            with transaction.atomic():
                status = validated_data.pop('status')
                validated_data['status'] = StatusConstantData.objects.get(code=status)
                EventStatus.objects.filter(event__id=validated_data['event_id']).update(is_active=False)
                status = EventStatus.objects.create(**validated_data)
                status.save()
                return status
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None


class SignedLetterSerializer(serializers.ModelSerializer):
    signed_letter = serializers.FileField(required=True)

    class Meta:
        model = Speaker
        fields = ['signed_letter']

    def update(self, instance, validated_data):
        try:
            instance.signed_letter = validated_data.get('signed_letter', instance.signed_letter)
            instance.save()
            return instance
        except Exception as e:
            return e


class AgendaSerailizers(serializers.ModelSerializer):
    agenda = serializers.FileField(required=True)

    class Meta:
        model = Event
        fields = ['agenda']

    def update(self, instance, validated_data):
        try:
            instance.agenda = validated_data.get('agenda', instance.agenda)
            instance.save()
            return instance
        except Exception as e:
            return e


class SpeakerUpdateSerializer(serializers.ModelSerializer):
    speaker_role = serializers.CharField(required=False)
    specialty = serializers.CharField(required=False)
    duration = serializers.IntegerField(required=False)
    proctor_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    speech_focus_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=False)
    focus_not_listed = serializers.CharField(required=False, allow_blank=True)
    other_proctor = serializers.CharField(required=False, allow_blank=True)
    depart_employee = serializers.CharField(required=False, allow_blank=True)
    name_employee = serializers.CharField(required=False, allow_blank=True)
    new_mics = serializers.BooleanField(required=False)

    class Meta:
        model = Speaker
        fields = ['id', 'speaker_role', 'specialty', 'duration', 'speech_focus', 'notes', 'proctor_id','notes', 'speech_focus_id',
                  'title', 'focus_not_listed', 'depart_employee', 'name_employee', 'new_mics', 'other_proctor']
        # fields = "__all__"

    def update(self, instance, validated_data):
        try:
            if 'speech_focus_id' in validated_data.keys():
                speech_focus_id = validated_data.pop('speech_focus_id')
                if speech_focus_id:
                    validated_data['speech_focus'] = AreaOfExperties.objects.get(id=speech_focus_id)
                    instance.speech_focus = validated_data.get('speech_focus', instance.speech_focus)
            if 'proctor_id' in validated_data.keys():
                proctor_id = validated_data.pop('proctor_id')
                if proctor_id:
                    validated_data['proctor'] = Proctors.objects.get(id=proctor_id)
                    instance.proctor = validated_data.get('proctor', instance.proctor)

            if "specialty" in validated_data.keys():
                specialty = validated_data.pop('specialty')
                if specialty:
                    validated_data['specialty'] = Speciality.objects.get(code=specialty)
                    instance.specialty = validated_data.get('specialty', instance.specialty)

            if "speaker_role" in validated_data.keys():
                speaker_role = validated_data.pop('speaker_role')
                if speaker_role:
                    validated_data['speaker_role'] = Hcp_role.objects.get(code=speaker_role)
                    instance.speaker_role = validated_data.get('speaker_role', instance.speaker_role)

            instance.duration = validated_data.get('duration', instance.duration)
            instance.title = validated_data.get('title', instance.title)
            instance.notes = validated_data.get('notes', instance.notes)
            instance.focus_not_listed = validated_data.get('focus_not_listed', instance.focus_not_listed)
            instance.other_proctor = validated_data.get('other_proctor', instance.other_proctor)
            instance.depart_employee = validated_data.get('depart_employee', instance.depart_employee)
            instance.name_employee = validated_data.get('name_employee', instance.name_employee)
            instance.new_mics = validated_data.get('new_mics', instance.new_mics)
            instance.save()
            return instance
        except Exception as e:
            return e


class SpeakingEventFeedBackSerializers(serializers.ModelSerializer):
    event = serializers.SerializerMethodField(read_only=True)
    speaker = serializers.SerializerMethodField(read_only=True)
    specialty = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    rate_event = serializers.IntegerField(required=True)
    rate_logistic_organization = serializers.IntegerField(required=True)
    scientific_content = serializers.IntegerField(required=True)
    message = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    suggestions = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    event_id = serializers.IntegerField(write_only=True)
    speaker_id = serializers.IntegerField(write_only=True)
    specialty_id = serializers.IntegerField(write_only=True)
    country_id = serializers.IntegerField(write_only=True)
    rate_topic = serializers.ListField(write_only=True)

    class Meta:
        model = SpeakingEventFeedBack
        fields = ["id", "event", "speaker", "specialty", "country", "rate_event", "rate_logistic_organization",
                  "scientific_content", "message", "suggestions", "event_id", "speaker_id", "specialty_id",
                  "country_id", 'rate_topic']

    def create(self, validate_data):
        try:
            with transaction.atomic():
                rate_topic = validate_data.pop('rate_topic')
                speaking_evnt_feedback = SpeakingEventFeedBack.objects.create(**validate_data)
                for each in rate_topic:
                    TopicRating.objects.create(rate_topic = each['rate_topic'],
                                               speaking_event_feedBack = speaking_evnt_feedback,
                                               speaker = Speaker.objects.get(id = each['speaker_id']))
                speaking_evnt_feedback.save()
                return speaking_evnt_feedback
        except Exception as e:
            return e

    def get_event(self, obj):
        try:
            return obj.event.id
        except:
            return None

    def get_speaker(self, obj):
        try:
            return obj.speaker.id
        except:
            return None

    def get_specialty(self, obj):
        try:
            return obj.specialty.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None


class SoeakingEventAttendanceSerailizers(serializers.ModelSerializer):
    proctorship_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)
    class Meta:
        model = AttendanceFormSpeakingEvent
        fields = ["id",'proctorship_id',"attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = AttendanceFormSpeakingEvent.objects.create(**validated_data)
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None



class AttendanceSpeakingEventSerailizers(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)
    class Meta:
        model = AttendanceFormSpeakingEvent
        fields = ["id",'event_id',"attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = AttendanceFormSpeakingEvent.objects.create(**validated_data)
                attendace_form.save()
                return attendace_form

        except Exception as e:
            return None




class AttendanceFormSpeakingEventUpdateSerailizers(serializers.ModelSerializer):
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceFormSpeakingEvent
        fields = ["id", "attendance_form"]
    def update(self, instance, validated_data):
        instance.attendance_form = validated_data.get('attendance_form', instance.attendance_form)
        instance.save()
        return instance




class SpeakingEventListingViewSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    event_name = serializers.CharField(required=True)
    event_type = serializers.SerializerMethodField(read_only=True)
    event_location = serializers.CharField(required=True)
    solution = serializers.StringRelatedField(read_only=True)
    participants = serializers.IntegerField(required=True)
    audience_type = serializers.StringRelatedField(read_only=True)
    audience_region = serializers.StringRelatedField(read_only=True)
    language = serializers.StringRelatedField(read_only=True)
    notes = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    class Meta:
        model = SpeakingEvent
        fields = ['start_date', 'end_date','audience_region', 'event_name', 'event_type','event_location','solution','participants','audience_type', 'language', 'notes']

    def get_event_type(self, obj):
        try:
            return obj.event_type.code
        except:
            return None


class EventViewListingSerializer(serializers.ModelSerializer):
    event_country = serializers.SerializerMethodField(read_only=True)
    agenda = serializers.FileField(read_only=True)
    no_speach = serializers.BooleanField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    is_global = serializers.BooleanField(read_only=True)
    event_datails = serializers.SerializerMethodField(read_only=True)
    speakers = serializers.SerializerMethodField(read_only=True)
    activity_id = serializers.CharField(read_only=True)
    # event_name
    # event_type
    # event_location
    # solution
    # language
    # participants
    # audience_type
    # audience_region
    # notes

    class Meta:
        model = Event
        fields = ['id', "activity_id",'is_global', 'event_country', 'agenda', 'no_speach', 'status', 'event_datails', 'speakers']


    def get_event_country(self, obj):
        try:
            return obj.event_country.name
        except:
            return None

    def get_status(self, obj):
        try:
            return obj.event_status_event.latest('timestamp').status.code
        except:
            return None

    def get_event_datails(self, obj):
        try:
            return SpeakingEventListingViewSerializer(SpeakingEvent.objects.filter(event_status__event__id=obj.id).latest('created_on')).data
        except:
            return None

    def get_speakers(self, obj):
        try:
            return SpeakerSerializer(Speaker.objects.filter(event__id = obj.id), many = True).data
        except:
            return None




class CognosIdSerailizers(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)
    cognos = serializers.ListField(required=True)
    class Meta:
        model = CognosId
        fields = ["id",'event_id',"cognos"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                cognos = validated_data.pop('cognos')
                cognos_id = CognosId.objects.create(**validated_data)
                cognos_id.cognos.add(*cognos)
                cognos_id.save()
                return cognos_id
        except Exception as e:
            return None




class CognosIdUpdateSerailizers(serializers.ModelSerializer):
    cognos = serializers.ListField(required=True)
    class Meta:
        model = CognosId
        fields = ["id", "cognos"]
    def update(self, instance, validated_data):
        try:
            cognos = validated_data.pop('cognos')
            if cognos:
                instance.cognos.clear()
                instance.cognos.add(*cognos)
            instance.save()
            return instance
        except Exception as e:
            return e



class CognosIdViewSerailizers(serializers.ModelSerializer):
    event_id = serializers.IntegerField(read_only=True)
    cognos = serializers.StringRelatedField(read_only=True, many=True)
    cognos_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CognosId
        fields = ["id",'event_id',"cognos", "cognos_id"]

    def get_cognos_id(self, obj):
        try:
            res = []
            for each in Hospital.objects.filter(cognos_id_speaker__event__id = obj.event.id):
                dic = {}
                dic["id"] = each.id
                dic["cognos_id"] = each.cognos_id
                res.append(dic)
            return res
        except:
            return None

class MeetingDocsSerailizers(serializers.ModelSerializer):
    meeting_docs = serializers.FileField(required=True)

    class Meta:
        model = Event
        fields = ['meeting_docs']

    def update(self, instance, validated_data):
        try:
            instance.meeting_docs = validated_data.get('meeting_docs', instance.meeting_docs)
            instance.save()
            return instance
        except Exception as e:
            return e


class AttendanceEventSerailizers(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = AttendanceFormSpeakingEvent
        fields = ["id",'event_id',"attendance_form", "user_id"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user_id =validated_data.pop("user_id")
                attendace_form = AttendanceFormSpeakingEvent.objects.create(**validated_data)
                EventStatus.objects.filter(event__id=validated_data['event_id']).update(is_active=False)
                status_data = {'status': StatusConstantData.objects.get(code='closed'),
                               'event': Event.objects.get(id=validated_data["event_id"]),
                               'user': User.objects.get(id=user_id)}
                status_data = EventStatus.objects.create(**status_data)
                attendace_form.save()
                return attendace_form

        except Exception as e:
            return None



class MeetingDocsStatusSerailizers(serializers.ModelSerializer):
    meeting_docs = serializers.FileField(required=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Event
        fields = ['meeting_docs', 'user_id']

    def update(self, instance, validated_data):
        try:
            user_id =validated_data.pop("user_id")
            instance.meeting_docs = validated_data.get('meeting_docs', instance.meeting_docs)
            EventStatus.objects.filter(event__id=validated_data['event_id']).update(is_active=False)
            status_data = {'status': StatusConstantData.objects.get(code='closed'),
                           'event': Event.objects.get(id=instance.id),
                           'user': User.objects.get(id=user_id)}
            status_data = EventStatus.objects.create(**status_data)
            instance.save()
            return instance
        except Exception as e:
            return e
