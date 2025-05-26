from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Doc
from .models import ChatMessage
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
       
    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],    
            validated_data['password']
        )
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True,max_length=255)
    password = serializers.CharField(required = True , max_length=255, write_only=True)



# class DocSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Doc
#         fields = ('id', 'name','user')
#         read_only_fields = ('id',)

class DocSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doc
        fields = ('id', 'Title', 'discription', 'pdf_file', 'user', 'AI_description', 'AI_questions', 'Text')
        read_only_fields = ('id', 'user')
    


class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ChatMessage
        fields = ('id', 'user', 'user_message', 'assistant_response')
        read_only_fields = ('id', 'user', 'assistant_response')