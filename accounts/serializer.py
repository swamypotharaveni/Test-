from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    model=Profile
    fields=['profile_image']
class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(format="%m-%d-%y %H:%M:%S %Z")
    date_joined=serializers.DateTimeField(format="%m-%d-%y %H:%M:%S %Z")
    profile = ProfileSerializer(read_only=True)


    class Meta:
        model=User
        fields=["id","username","email","password","last_login",'date_joined','profile_image']
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields=["id",'last_login','date_joined']
    def create(self, validated_data):
        user=User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user