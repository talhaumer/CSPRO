from rest_framework import serializers
from django.db import transaction
from api.feedback.models import Reason, Rating, ProctorshipProctorFeedback, TraineeFeedback, MemoProctorFeedBack, \
    PercevelDriver, SoloSmartProctorFeedBack, ProctorshipCertificateForm


class ProctorFeedbackSerializer(serializers.ModelSerializer):
    proctorship = serializers.SerializerMethodField(read_only=True)
    num_of_patients = serializers.IntegerField(required=True)
    is_advance = serializers.BooleanField(required=True)
    implanted_patient = serializers.IntegerField(required=True)
    implanted_perceval = serializers.IntegerField(required=True)
    reason_low_num_patients = serializers.SerializerMethodField(read_only=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    is_trainee_implant = serializers.BooleanField(required=True)
    any_leason = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    proctorship_id = serializers.IntegerField(write_only=True)
    reason_low_num_patients_code = serializers.CharField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)

    class Meta:
        model = ProctorshipProctorFeedback
        fields = ('id', 'proctorship', 'num_of_patients', 'is_advance', 'implanted_patient', 'implanted_perceval',
                  'reason_low_num_patients', 'rate_of_experince', 'is_trainee_implant', 'any_leason', 'report',
                  'proctorship_id', 'reason_low_num_patients_code', 'rate_of_experince_code')

    def create(self, validated_data):
        with transaction.atomic():
            reason_low_num_patients_code = validated_data.pop('reason_low_num_patients_code')
            rate_of_experince_code = validated_data.pop('rate_of_experince_code')
            feedback = ProctorshipProctorFeedback.objects.create(**validated_data)
            feedback.reason_low_num_patients = Reason.objects.get(code=reason_low_num_patients_code)
            feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
            feedback.save()
            return feedback

    def update(self, instance, validated_data):
        instance.num_of_patients = validated_data.get('num_of_patients', instance.num_of_patients)
        instance.is_advance = validated_data.get('is_advance',  instance.is_advance )
        instance.implanted_patient = validated_data.get('implanted_patient', instance.implanted_patient)
        instance.implanted_perceval = validated_data.get('instance.implanted_perceval',  instance.implanted_perceval)
        instance.is_trainee_implant =validated_data.get('is_trainee_implant', instance.is_trainee_implant)
        instance.any_leason = validated_data.get('any_leason', instance.any_leason)
        instance.report = validated_data.get('report', instance.report)

        if 'reason_low_num_patients_code' in validated_data.keys():
            reason_low_num_patients_code = validated_data.pop('reason_low_num_patients_code')
            validated_data['reason_low_num_patients'] = Reason.objects.get(code=reason_low_num_patients_code)
            instance.reason_low_num_patients = validated_data.get('reason_low_num_patients', instance.reason_low_num_patients)

        if 'rate_of_experince_code' in validated_data.keys():
            rate_of_experince_code = validated_data.pop('rate_of_experince_code')
            validated_data['rate_of_experince'] = Rating.objects.get(code=rate_of_experince_code)
            instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)

        instance.save()
        return instance

    def get_reason_low_num_patients(self, obj):
        try:
            return obj.reason_low_num_patients.name
        except:
            return None

    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.name
        except:
            return None

    def get_proctorship(self,obj):
        try:
            return obj.proctorship.id
        except:
            return None

class TraineeFeedbackSerializer(serializers.ModelSerializer):
    trainee = serializers.SerializerMethodField(read_only=True)
    implanted_perceval = serializers.IntegerField(required=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    rate_of_training = serializers.CharField(read_only=True)
    need_further_training = serializers.BooleanField(required=True)
    plan_for_next = serializers.CharField(required=True)
    any_sugestion = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    is_memo_family = serializers.BooleanField(required=True)
    perceval_driver = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    trainee_id = serializers.IntegerField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)
    rate_of_training_code = serializers.CharField(write_only=True)
    is_solo_smart = serializers.BooleanField(required=True)
    is_perceval = serializers.BooleanField(required=True)
    activity_id = serializers.SerializerMethodField(read_only=True)
    number_patient = serializers.IntegerField(required=True)


    class Meta:
        model = TraineeFeedback
        fields = (
        'id', 'number_patient','trainee','activity_id', 'implanted_perceval', 'rate_of_experince', 'rate_of_training', 'need_further_training',
        'plan_for_next', 'any_sugestion', 'perceval_driver','report','is_memo_family', 'is_perceval','is_solo_smart','trainee_id', 'rate_of_training_code', 'rate_of_experince_code')


    def create(self, validated_data):
        with transaction.atomic():
            rate_of_training_code = validated_data.pop('rate_of_training_code')
            rate_of_experince_code = validated_data.pop('rate_of_experince_code')
            feedback = TraineeFeedback.objects.create(**validated_data)
            feedback.rate_of_training = Rating.objects.get(code=rate_of_training_code)
            feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
            feedback.save()
            return feedback

    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.name
        except:
            return None


    # def rate_of_training(self, obj):
    #     try:
    #         return obj.rate_of_training.name
    #     except:
    #         return None

    def get_trainee(self,obj):
        try:
            return obj.trainee.id
        except:
            return None

    def get_activity_id(self, obj):
        try:
            return obj.trainee.proctorship.id
        except:
            return None

class MemoProctorFeedbackSerializer(serializers.ModelSerializer):
    proctorship = serializers.SerializerMethodField(read_only=True)
    implanted_memo = serializers.IntegerField(required=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    is_trainee_implant = serializers.BooleanField(required=True)
    any_leason = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    proctorship_id = serializers.IntegerField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)

    class Meta:
        model = MemoProctorFeedBack
        fields = (
        'id', 'proctorship', 'implanted_memo', 'rate_of_experince', 'is_trainee_implant', 'any_leason', 'report',
        'proctorship_id', 'rate_of_experince_code')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                rate_of_experince_code = validated_data.pop('rate_of_experince_code')
                feedback = MemoProctorFeedBack.objects.create(**validated_data)
                feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
                feedback.save()
                return feedback
        except Exception as e:
            return e

    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.name
        except:
            return None

    def get_proctorship(self, obj):
        try:
            return obj.proctorship.id
        except:
            return None

class MemoProctorUpdateFeedbackSerializer(serializers.ModelSerializer):
    implanted_memo = serializers.IntegerField(required=False)
    is_trainee_implant = serializers.BooleanField(required=False)
    any_leason = serializers.CharField(required=False)
    report = serializers.FileField(required=False)
    rate_of_experince_code = serializers.CharField(write_only=False)

    class Meta:
        model = MemoProctorFeedBack
        fields = ('id', 'implanted_memo', 'is_trainee_implant', 'any_leason', 'report', 'rate_of_experince_code')

    def update(self, instance, validated_data):
        try:

            instance.implanted_memo = validated_data.get('implanted_memo', instance.implanted_memo)
            instance.is_trainee_implant = validated_data.get('is_trainee_implant', instance.is_trainee_implant)
            instance.any_leason = validated_data.get('any_leason', instance.any_leason)
            instance.report = validated_data.get('report', instance.report)
            if 'rate_of_experince_code' in validated_data.keys():
                validated_data['rate_of_experince_code'] = Rating.objects.get(code= validated_data.pop('rate_of_experince_code'))
                instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)

            instance.save()
            return instance
        except Exception as e:
            return e




class TraineeMemoFeedbackSerializer(serializers.ModelSerializer):
    implanted_perceval = serializers.IntegerField(required=True)
    number_patient = serializers.IntegerField(required=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    rate_of_training = serializers.SerializerMethodField(read_only=True)
    need_further_training = serializers.BooleanField(required=True)
    plan_for_next = serializers.CharField(required=True)
    any_sugestion = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    is_memo_family = serializers.BooleanField(required=True)
    rate_of_experince_code = serializers.CharField(write_only=True)
    rate_of_training_code = serializers.CharField(write_only=True)


    class Meta:
        model = TraineeFeedback
        fields = ('id', 'number_patient','implanted_perceval', 'rate_of_experince', 'rate_of_training', 'need_further_training',
        'plan_for_next', 'any_sugestion','report','is_memo_family', 'rate_of_training_code', 'rate_of_experince_code')


    def create(self, validated_data):
        try:
            with transaction.atomic():
                rate_of_training_code = validated_data.pop('rate_of_training_code')
                rate_of_experince_code = validated_data.pop('rate_of_experince_code')
                feedback = TraineeFeedback.objects.create(**validated_data)
                feedback.rate_of_training = Rating.objects.get(code=rate_of_training_code)
                feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
                feedback.save()
                return feedback
        except Exception as e:
            return e


    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.name
        except:
            return None


    def rate_of_training(self, obj):
        try:
            return obj.rate_of_training.name
        except:
            return None

    def get_proctorship(self,obj):
        try:
            return obj.proctorship.id
        except:
            return None


class TraineeMemoUpdateFeedbackSerializer(serializers.ModelSerializer):
    implanted_perceval = serializers.IntegerField(required=False)
    need_further_training = serializers.BooleanField(required=False)
    plan_for_next = serializers.CharField(required=False)
    any_sugestion = serializers.CharField(required=False)
    report = serializers.FileField(required=False)
    is_memo_family = serializers.BooleanField(required=False)
    rate_of_experince_code = serializers.CharField(write_only=False)
    rate_of_training_code = serializers.CharField(write_only=False)


    class Meta:
        model = TraineeFeedback
        fields = ('id', 'implanted_perceval', 'need_further_training', 'plan_for_next', 'any_sugestion','report','is_memo_family', 'rate_of_training_code', 'rate_of_experince_code')


    def update(self, instance, validated_data):
        try:
            instance.implanted_perceval = validated_data.get('implanted_perceval', instance.implanted_perceval)
            instance.need_further_training = validated_data.get('need_further_training', instance.need_further_training)
            instance.plan_for_next = validated_data.get('plan_for_next', instance.plan_for_next)
            instance.any_sugestion = validated_data.get('any_sugestion', instance.any_sugestion)
            instance.report = validated_data.get('report', instance.report)
            instance.is_memo_family = validated_data.get('is_memo_family', instance.is_memo_family)
            if 'rate_of_experince_code' in validated_data.keys():
                validated_data['rate_of_experince'] =Rating.objects.get(code = validated_data.pop('rate_of_experince_code'))
                instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)
            if 'rate_of_training_code' in validated_data.keys():
                validated_data['rate_of_training'] = Rating.objects.get(code = validated_data.get('rate_of_training_code'))
                instance.rate_of_training = validated_data.get('rate_of_training', instance.rate_of_training)

            return instance
        except Exception as e:
            return e

class ReasonDataSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True)
	code = serializers.SlugField(read_only=True)
	class Meta:
		model = Reason
		fields = ['name', 'code']


class RatingDataSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True)
	code = serializers.SlugField(read_only=True)
	class Meta:
		model = Rating
		fields = ['name', 'code']


class PercevelDriverDataSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True)
	code = serializers.SlugField(read_only=True)
	class Meta:
		model = PercevelDriver
		fields = ['name', 'code']


class SoloSmartProctorFeedbackSerializer(serializers.ModelSerializer):
    proctorship = serializers.SerializerMethodField(read_only=True)
    implanted_solo_smart = serializers.IntegerField(required=True)
    rate_of_experince = serializers.CharField(read_only=True)
    is_trainee_implant = serializers.BooleanField(required=True)
    any_leason = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    proctorship_id = serializers.IntegerField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)

    class Meta:
        model = SoloSmartProctorFeedBack
        fields = (
        'id', 'proctorship', 'implanted_solo_smart', 'rate_of_experince', 'is_trainee_implant', 'any_leason', 'report',
        'proctorship_id', 'rate_of_experince_code')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                rate_of_experince_code = validated_data.pop('rate_of_experince_code')
                feedback = SoloSmartProctorFeedBack.objects.create(**validated_data)
                feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
                feedback.save()
                return feedback
        except Exception as e:
            return e

    # def get_rate_of_experince(self, obj):
    #     try:
    #         return obj.rate_of_experince.name
    #     except:
    #         return None

    def get_proctorship(self, obj):
        try:
            return obj.proctorship.id
        except:
            return None




class SoloSmartUpdateFeedbackSerializer(serializers.ModelSerializer):
    proctorship = serializers.SerializerMethodField(read_only=True)
    implanted_solo_smart = serializers.IntegerField(required=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    is_trainee_implant = serializers.BooleanField(required=True)
    any_leason = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    proctorship_id = serializers.IntegerField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)

    class Meta:
        model = SoloSmartProctorFeedBack
        fields = (
        'id', 'proctorship', 'implanted_solo_smart', 'rate_of_experince', 'is_trainee_implant', 'any_leason', 'report',
        'proctorship_id', 'rate_of_experince_code')

    def update(self, instance, validated_data):
        instance.implanted_solo_smart = validated_data.get('implanted_solo_smart', instance.implanted_solo_smart)
        instance.is_trainee_implant = validated_data.get('is_trainee_implant',instance.is_trainee_implant)
        instance.any_leason = validated_data.get('any_lesson', instance.any_leason)
        instance.report = validated_data.get('report',  instance.report)
        if 'rate_of_experince_code' in validated_data.keys():
            validated_data['rate_of_experince'] = Rating.objects.get(code=validated_data.pop('rate_of_experince_code'))
            instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)

        instance.save()
        return instance



class MemoProctorUpdateFeedbackSerializer(serializers.ModelSerializer):
    implanted_memo = serializers.IntegerField(required=False)
    is_trainee_implant = serializers.BooleanField(required=False)
    any_leason = serializers.CharField(required=False)
    report = serializers.FileField(required=False)
    rate_of_experince_code = serializers.CharField(write_only=False)

    class Meta:
        model = MemoProctorFeedBack
        fields = ('id', 'implanted_memo', 'is_trainee_implant', 'any_leason', 'report', 'rate_of_experince_code')

    def update(self, instance, validated_data):
        try:

            instance.implanted_memo = validated_data.get('implanted_memo', instance.implanted_memo)
            instance.is_trainee_implant = validated_data.get('is_trainee_implant', instance.is_trainee_implant)
            instance.any_leason = validated_data.get('any_leason', instance.any_leason)
            instance.report = validated_data.get('report', instance.report)
            if 'rate_of_experince_code' in validated_data.keys():
                validated_data['rate_of_experince'] = Rating.objects.get(code= validated_data.pop('rate_of_experince_code'))
                instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)

            instance.save()
            return instance
        except Exception as e:
            return e



class TraineeUpdateFeedbackSerializer(serializers.ModelSerializer):
    implanted_perceval = serializers.IntegerField(required=False)
    number_patient = serializers.IntegerField(required=False)
    need_further_training = serializers.BooleanField(required=False)
    plan_for_next = serializers.CharField(required=False)
    any_sugestion = serializers.CharField(required=False)
    report = serializers.FileField(required=False)
    perceval_driver = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    rate_of_experince_code = serializers.CharField(required=False)
    rate_of_training_code = serializers.CharField(required=False)
    # is_solo_smart = serializers.BooleanField(required=False)
    # is_perceval = serializers.BooleanField(required=False)
    # is_memo_family = serializers.BooleanField(required=False)


    class Meta:
        model = TraineeFeedback
        fields = ('id', 'number_patient','implanted_perceval', 'need_further_training','plan_for_next', 'any_sugestion', 'perceval_driver','report', 'rate_of_training_code', 'rate_of_experince_code')


    def update(self, instance, validated_data):
        instance.implanted_perceval = validated_data.get('implanted_perceval', instance.implanted_perceval)
        instance.rate_of_experince = validated_data.get('rate_of_experince', instance.rate_of_experince)
        instance.rate_of_training = validated_data.get('rate_of_training',  instance.rate_of_training)
        instance.need_further_training = validated_data.get('need_further_training', instance.need_further_training)
        instance.plan_for_next = validated_data.get('plan_for_next',instance.plan_for_next)
        instance.any_sugestion= validated_data.get('any_sugestion',instance.any_sugestion)

        if 'report' in validated_data.keys():
            instance.report= validated_data.get('report',instance.report)

        # instance.is_memo_family= validated_data.get('is_memo_family',instance.is_memo_family)
        instance.perceval_driver= validated_data.get('perceval_driver',instance.perceval_driver)

        if 'rate_of_experince_code' in validated_data.keys():
            rate_of_experince_code = validated_data.pop('rate_of_experince_code')
            validated_data['rate_of_experince'] = Rating.objects.get(code = rate_of_experince_code)
            instance.rate_of_experince= validated_data.get('rate_of_experince',instance.rate_of_experince)

        if 'rate_of_training_code' in validated_data.keys():
            rate_of_training_code = validated_data.pop('rate_of_training_code')
            validated_data['rate_of_training'] = Rating.objects.get(code = rate_of_training_code)
            instance.rate_of_training  =  validated_data.get('rate_of_training',instance.rate_of_experince)

        instance.number_patient =  validated_data.get('number_patient',instance.number_patient)
        # instance.is_perceval =  validated_data.get('rate_of_experince_code',instance.is_perceval)
        instance.save()
        return instance

class CertificateFormSerailizers(serializers.ModelSerializer):
    # proctorship_id = serializers.IntegerField(write_only=True)
    certificate = serializers.FileField(required=True)
    class Meta:
        model = ProctorshipCertificateForm
        fields = ["id","certificate"]

    def create(self, validated_data):
        with transaction.atomic():
            attendace_form = ProctorshipCertificateForm.objects.create(**validated_data)
            attendace_form.save()
            return attendace_form

class CertificateFormUpdateSerailizers(serializers.ModelSerializer):
    certificate = serializers.FileField(required=True)

    class Meta:
        model = ProctorshipCertificateForm
        fields = ["id", "certificate"]

    def update(self, instance, validated_data):
        instance.certificate = validated_data.get('certificate', instance.certificate)
        instance.save()
        return instance
