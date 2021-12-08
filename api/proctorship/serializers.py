from django.db import transaction
from rest_framework import serializers
from api.proctorship.models import Proctorship, ConstantData
from api.models import Products
from api.proctors.models import Proctors
from api.status.models import Status, StatusConstantData, Proposal, ProctorshipProctors
from api.trainee.serializers import TrainSerializer
from api.trainee.models import TraineeProfile
from api.models import Hospital
from api.zone.models import Countries, ZoneCountries
from api.users.models import User
from api.status.serializers import StatusSerializer, StatusViewSerializer, ProctorshipProctorsSerializer
from cspro.utils import activity_id


class ProctorshipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField(read_only=True)
    secondary_product = serializers.SerializerMethodField(read_only=True)
    proctor = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    # activity_area_type = serializers.CharField(required = True)
    training_type = serializers.CharField(required=True)
    types_of_first_training = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    new_center = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    type_advance_training = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    specific_training = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    other_num_of_implants = serializers.IntegerField(default=0, allow_null=True)
    ETQ_number = serializers.IntegerField(default=0, allow_null=True)
    not_implant_regularly = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    other_advanced_training = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    memo_surgeon_implant = serializers.IntegerField(default=0, allow_null=True)
    rechord_surgeon_implant = serializers.IntegerField(default=0, allow_null=True)
    issue = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    hotel = serializers.CharField(required=True)
    number_of_cases = serializers.IntegerField(required=True)
    transplant_time = serializers.TimeField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    country_id = serializers.IntegerField(write_only=True, allow_null=True)
    hospital_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)
    proctor_id = serializers.ListField(write_only=True)
    zone_countries_id = serializers.IntegerField(write_only=True, allow_null=True)
    trainee_profile = TrainSerializer(many=True, write_only=True)
    secondary_product_id = serializers.IntegerField(write_only=True, allow_null=True)
    trainees = serializers.SerializerMethodField(read_only=True)
    is_global = serializers.BooleanField(required=True, allow_null=True)
    zone_id = serializers.IntegerField(write_only=True, allow_null=True)
    note_related_to_proctor = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    first_proctorship_num = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Proctorship
        fields = "__all__"

    def create(self, validated_data):
        try:
            with transaction.atomic():
                training_type = validated_data.pop('training_type')
                start_date = validated_data.pop('start_date')
                end_date = validated_data.pop('end_date')
                user_id = validated_data.pop('user_id')
                new_center = validated_data.pop('new_center')
                types_of_first_training = validated_data.pop('types_of_first_training')
                type_advance_training = validated_data.pop('type_advance_training')
                other_advanced_training = validated_data.pop('other_advanced_training')
                specific_training = validated_data.pop('specific_training')
                not_implant_regularly = validated_data.pop('not_implant_regularly')
                zone_countries_id = validated_data.pop('zone_countries_id')
                zone_id = validated_data.pop('zone_id')
                trainee = validated_data.pop('trainee_profile')
                proctor_id = validated_data.pop('proctor_id')
                validated_data['user_id'] = user_id

                proctorship = Proctorship.objects.create(**validated_data)

                num = proctorship.id
                char = "PG"
                if not proctorship.is_global:
                    char = "PL"
                proctorship.activity_id = activity_id(char, num)

                if training_type:
                    proctorship.training_type = ConstantData.objects.get(code=training_type)

                if types_of_first_training:
                    proctorship.types_of_first_training = ConstantData.objects.get(code=types_of_first_training)

                if type_advance_training:
                    proctorship.type_advance_training = ConstantData.objects.get(code=type_advance_training)

                if other_advanced_training:
                    proctorship.other_advanced_training = ConstantData.objects.get(code=other_advanced_training)
                if specific_training:
                    proctorship.specific_training = ConstantData.objects.get(code=specific_training)

                if not_implant_regularly:
                    proctorship.not_implant_regularly = ConstantData.objects.get(code=not_implant_regularly)

                if new_center:
                    proctorship.new_center = ConstantData.objects.get(code=new_center)

                if zone_countries_id and zone_id:
                    proctorship.zone_countries = ZoneCountries.objects.get(zone__id=zone_id,
                                                                           countries__id=zone_countries_id, status=True)

                for trainee_profile in trainee:
                    TraineeProfile.objects.create(
                        proctorship=proctorship,
                        name=trainee_profile['name'],
                        surname=trainee_profile['surname'],
                        title=ConstantData.objects.get(code=trainee_profile['title']),
                        mvr_case_per_year=trainee_profile['mvr_case_per_year'],
                        current_preferential=ConstantData.objects.get(code=trainee_profile['current_preferential']),
                        mvr_case_per_year_by_trainee=trainee_profile['mvr_case_per_year_by_trainee'],
                        note=trainee_profile['note'],
                        corcym_accompanying_rep=trainee_profile['corcym_accompanying_rep'],
                        country=Countries.objects.get(id=trainee_profile['country_id']),
                        hospital=Hospital.objects.get(id=trainee_profile['hospital_id']),
                        interest_invasive=trainee_profile['interest_invasive'],
                        status=True
                    )

                status_data = {'status': StatusConstantData.objects.get(code='pending'),
                               'proctorship_activity': proctorship, 'user': User.objects.get(id=user_id)}
                status_data = Status.objects.create(**status_data)
                if start_date and end_date:
                    dates = {'start_date': start_date, 'end_date': end_date, 'status': status_data}
                    dates = Proposal.objects.create(**dates)

                if proctor_id:
                    for each in range(len(proctor_id)):
                        proctors = {
                            'porposal': dates,
                            'proctors': Proctors.objects.get(id=proctor_id[each]),
                            'proctor_order': each + 1
                        }
                        ProctorshipProctors.objects.create(**proctors)

                proctorship.save()
                return proctorship
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_secondary_product(self, obj):
        try:
            return obj.secondary_product.product_name
        except:
            return None

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_proctor(self, obj):
        try:
            li = []
            user_name = obj.proctorship_id.all()
            for each in user_name:
                da = {'proctor_name': each.proctors.user.name, 'order': each.proctor_order}
                li.append(da)
            return li
        except:
            return None

    def get_trainees(self, obj):
        try:
            return TrainSerializer(obj.trainee_proctorship.filter(proctorship__id=obj.id), many=True).data
        except:
            return None


class ProctorshipViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    secondary_product = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    training_type = serializers.CharField(required=True)
    hotel = serializers.CharField(required=True)
    transplant_time = serializers.TimeField(required=True)
    zone_countries = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    is_global = serializers.BooleanField(read_only=True)
    product_id = serializers.SerializerMethodField(read_only=True)
    zone_country_id = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    types_of_first_training = serializers.CharField(read_only=True)
    type_advance_training = serializers.CharField(read_only=True)
    other_advanced_training = serializers.CharField(read_only=True)
    specific_training = serializers.CharField(read_only=True)
    not_implant_regularly = serializers.CharField(read_only=True)
    new_center = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    other_num_of_implants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Proctorship
        # fields = ['id', 'user', 'country', 'zone_country_id','zone_countries', 'hospital', 'is_global', 'product', 'product_id',
        #           'training_type','number_of_cases', 'other_num_of_implants','secondary_product', 'note', 'hotel', 'transplant_time', 'status', 'country_id', 'hospital_id', 'types_of_first_training','type_advance_training','other_advanced_training','specific_training','not_implant_regularly','new_center']

        fields = "__all__"
    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_country_id(self, obj):
        try:
            return obj.country.id
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_secondary_product(self, obj):
        try:
            return obj.secondary_product.product_name
        except:
            return None

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_product_id(self, obj):
        try:
            return obj.product.id
        except:
            return None

    def get_zone_country_id(sel, obj):
        try:
            return obj.zone_countries.countries.id
        except:
            return None

    def get_hospital_id(self, obj):
        try:
            return obj.hospital.id
        except:
            return None

    # def get_proctor(self, obj):
    #     try:
    #         li = []
    #         user_name = obj.proctorship_id.all()
    #         for each in user_name:
    #             da = {'proctor_name': each.proctors.user.name, 'order': each.proctor_order, 'id': each.proctors.id}
    #             li.append(da)
    #         return li
    #     except:
    #         return None

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_zone_countries(self, obj):
        try:
            return obj.zone_countries.countries.name
        except:
            return None

    def get_status(self, obj):
        try:
            return StatusViewSerializer(obj.proctorship_status.all(), many=True).data
        except:
            return None


class ConstantDataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    code = serializers.SlugField(read_only=True)
    field = serializers.CharField(read_only=True)

    class Meta:
        model = ConstantData
        fields = ['id', 'name', 'code', 'field']



class ProctorshipListingViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    secondary_product = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    training_type = serializers.CharField(required=True)
    hotel = serializers.CharField(required=True)
    transplant_time = serializers.TimeField(required=True)
    zone_countries = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    is_global = serializers.BooleanField(read_only=True)
    product_id = serializers.SerializerMethodField(read_only=True)
    zone_country_id = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    types_of_first_training = serializers.CharField(read_only=True)
    type_advance_training = serializers.CharField(read_only=True)
    other_advanced_training = serializers.CharField(read_only=True)
    specific_training = serializers.CharField(read_only=True)
    not_implant_regularly = serializers.CharField(read_only=True)
    new_center = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    other_num_of_implants = serializers.IntegerField(read_only=True)
    cognos_id = serializers.SerializerMethodField(read_only=True)
    proctor = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    activity_id = serializers.CharField(read_only=True)

    class Meta:
        model = Proctorship
        # fields = ['id', 'user', 'country', 'zone_country_id','zone_countries', 'hospital', 'is_global', 'product', 'product_id',
        #           'training_type','number_of_cases', 'other_num_of_implants','secondary_product', 'note', 'hotel', 'transplant_time', 'status', 'country_id', 'hospital_id', 'types_of_first_training','type_advance_training','other_advanced_training','specific_training','not_implant_regularly','new_center']

        fields = "__all__"
    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_country_id(self, obj):
        try:
            return obj.country.id
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_cognos_id(self, obj):
        try:
            return obj.hospital.cognos_id
        except:
            return None

    def get_secondary_product(self, obj):
        try:
            return obj.secondary_product.product_name
        except:
            return None

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_product_id(self, obj):
        try:
            return obj.product.id
        except:
            return None

    def get_zone_country_id(sel, obj):
        try:
            return obj.zone_countries.countries.id
        except:
            return None

    def get_hospital_id(self, obj):
        try:
            return obj.hospital.id
        except:
            return None


    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_zone_countries(self, obj):
        try:
            return obj.zone_countries.countries.name
        except:
            return None

    def get_status(self, obj):
        try:
            return StatusViewSerializer(obj.proctorship_status.latest("timestamp")).data['code']
        except:
            return None

    def get_proctor(self, obj):
        try:
            return ProctorshipProctorsSerializer(obj.proctorship_status.filter(alter_proctorship_porposal__isnull=False).latest('created_on').alter_proctorship_porposal.filter(proctor_porposal__isnull=False).latest('created_on').proctor_porposal.filter(status = True), many=True).data
        except:
            return None

    def get_date(self, obj):
        try:
            return obj.proctorship_status.filter(alter_proctorship_porposal__isnull=False).latest('created_on').alter_proctorship_porposal.get().start_date
        except:
            return None

