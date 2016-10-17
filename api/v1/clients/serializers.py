from clients.models import Client
from rest_framework import serializers
from django.contrib.auth import get_user_model  # If used custom user model


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('email', 'bdate', 'first_name', 'last_name', 'is_active', 'code')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = get_user_model()
