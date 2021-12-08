from oauth2_provider.models import RefreshToken
from .models import User, UserInfo, Role
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from api.zone.models import Countries, Zone


class AuthenticateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = User
        fields = ('email', 'password')


class UserViewSerializer(serializers.ModelSerializer):
    zone = serializers.SerializerMethodField(read_only=True)
    mail_notification = serializers.BooleanField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInfo
        fields = ['id', 'mail_notification', 'zone', 'image', 'role', 'email', 'country', 'name', 'is_active']

    def get_zone(self, obj):
        try:
            return obj.zone.name
        except:
            return None

    def get_name(self, obj):
        return obj.user.name

    def get_country(self, obj):
        return obj.user.country.name

    def get_email(self, obj):
        return obj.user.email

    def get_image(self, obj):
        try:
            return obj.user.image.url
        except:
            return None

    def get_role(self, obj):
        try:
            return obj.user.role.code
        except:
            return None

    def get_is_active(self, obj):
        try:
            return obj.user.is_active
        except:
            return None


class UserSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(write_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    zone_id = serializers.IntegerField(write_only=True)
    country_id = serializers.IntegerField(write_only=True)
    mail_notification = serializers.BooleanField(write_only=True)
    image = serializers.ImageField(required=True, allow_null=True, allow_empty_file=True)
    is_active = serializers.BooleanField(required=True)
    user_info = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'role', 'role_code', 'country', 'mail_notification', 'user_info', 'image', 'is_active',
                  'country_id', 'zone_id', 'role', 'name', 'email']

    def create(self, validated_data):
        with transaction.atomic():
            mail_notification = validated_data.pop("mail_notification")
            zone_id = validated_data.pop('zone_id')
            role_code = validated_data.pop('role_code')
            validated_data['role'] = Role.objects.get(code=role_code)
            user = User.objects.create(**validated_data)
            adm_usr = {}
            adm_usr["user"] = user
            adm_usr["mail_notification"] = mail_notification
            adm_usr["zone"] = Zone.objects.get(id=zone_id)
            adm_usr = UserInfo.objects.create(**adm_usr)
            user.save()
            return user

    def get_user_info(self, obj):
        data = UserViewSerializer(obj.admin_user.all(), many=True).data
        return data

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_role(self, obj):
        try:
            return obj.role.code
        except:
            return None


class PasswordSerializers(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['password']


class UpdateProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    # password = serializers.CharField(write_only=False)
    mail_notification = serializers.BooleanField(required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'image', 'mail_notification']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        if "image" in validated_data.keys():
            instance.image = validated_data.get('image', instance.image)

        if "mail_notification" in validated_data.keys():
            UserInfo.objects.filter(user__id=instance.id).update(
                mail_notification=validated_data.pop('mail_notification'))

        # instance.set_password(validated_data.pop('password'))
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def create(self, validated_date):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)
        # for data in user:
        # 	print(data)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        try:
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            update_last_login(None, user)
            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'email': user.email,
                'role': user.role,
                'id': user.id,
            }
            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")


class UserFormUpdateSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    is_active = serializers.BooleanField(required=False)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    zone_id = serializers.IntegerField(write_only=True)
    country_id = serializers.IntegerField(write_only=True)
    mail_notification = serializers.BooleanField(required=False)
    image = serializers.ImageField(required=False)
    role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'image', 'role_code', 'is_active', 'mail_notification', 'country_id', 'zone_id', 'password',
                  'role', 'name', 'email']

    def update(self, instance, validated_data):
        try:
            instance.name = validated_data.get('name', instance.name)
            if "image" in validated_data.keys():
                image = validated_data.pop('image')
                validated_data['image'] = image
                instance.image = validated_data.get('image', instance.image)
            # instance.role = validated_data.get('role', instance.role)

            instance.is_active = validated_data.get('is_active', instance.is_active)

            # if 'email' in validated_data.keys():
            #     instance.email = validated_data.get('email', instance.email)

            if 'role_code' in validated_data.keys():
                validated_data['role'] = Role.objects.get(code=validated_data.pop('role_code'))
                instance.role = validated_data.get('role', instance.role)

            if "country_id" in validated_data.keys():
                validated_data['country'] = Countries.objects.get(pk=validated_data.pop('country_id'))
                instance.country = validated_data.get('country', instance.country)

            if "zone_id" in validated_data.keys():
                zone_obj = Zone.objects.get(id = validated_data.pop('zone_id'))
                UserInfo.objects.filter(user__id=instance.id).update(zone=zone_obj)

            if "mail_notification" in validated_data.keys():
                UserInfo.objects.filter(user__id=instance.id).update(
                    mail_notification=validated_data.pop('mail_notification'))

            instance.save()
            return instance
        except Exception as e:
            return e

    def get_country(self, obj):
        try:
            return obj.country.id
        except:
            return None

    def get_role(self, obj):
        try:
            return obj.role.code
        except:
            return None



class UpdateProfileDataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    # password = serializers.CharField(write_only=False)
    mail_notification = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['name', 'image', 'mail_notification']


    def get_mail_notification(self, obj):
        try:
            return obj.admin_user.mail_notification
        except:
            return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password"]



