# serializers.py

from rest_framework import serializers, viewsets
from .models import User
from authentication.models import FieldOfActivity

class FieldOfActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfActivity
        fields = ['id', 'name']


class SpecialistSerializer(serializers.ModelSerializer):
    fields_of_activity = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'patronymic', 'last_name', 'photo', 'city', 'fields_of_activity', 'profession', 'registered', 'workplace_name', ]
