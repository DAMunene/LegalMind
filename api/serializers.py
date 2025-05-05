from rest_framework import serializers
from .models import CustomUser, Contract, RiskAnalysis
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ('id', 'title', 'file', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class RiskAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAnalysis
        fields = ('id', 'contract', 'risk_score', 'summary', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, data):
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        if len(data['password']) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long'})
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect credentials")
