from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from  rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import DocSerializer
from .models import Doc

from .permission import IsOwner , IsOwnerdelete , IsOwnerupdate
from .models import Doc

import json


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import os
import google.generativeai as genai
from .models import Doc
from .serializers import DocSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer

from .permission import IsOwnerchatlist 
from django.http import FileResponse, Http404

from .aidiscription import generate_ai_description_from_pdf_text, extract_text_from_pdf , generate_ai_user_response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            return Response({'message': 'Invalid credentials'}, status=400)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'message': 'Welcome to the dashboard!'
        },200)
    

#CRUD

class Listdoc(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = DocSerializer

    def get_queryset(self):
        user = self.request.user
        return Doc.objects.filter(user=user)



class Detaildoc(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doc.objects.all()
    serializer_class = DocSerializer
    permission_classes = [IsAuthenticated, IsOwnerupdate]
    lookup_field = 'pk'




class CreateDoc(generics.CreateAPIView):
    queryset = Doc.objects.all()
    serializer_class = DocSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Save the Doc instance first (to get the file on disk)
        doc = serializer.save(user=self.request.user)

        try:
            pdf_path = os.path.join(settings.MEDIA_ROOT, doc.pdf_file.name)
            pdf_text = extract_text_from_pdf(pdf_path)
            ai_desc = generate_ai_description_from_pdf_text(pdf_text+doc.discription)
        except Exception as e:
            ai_desc = "AI description could not be generated."

        # Update the saved instance with AI description
        doc.AI_description =    ai_desc.get('description', '')
        doc.AI_questions = json.dumps(ai_desc.get('questions', []))
        doc.Text = pdf_text
        doc.save()



class DeleteDoc(generics.DestroyAPIView):
    queryset = Doc.objects.all()
    serializer_class = DocSerializer
    permission_classes = [IsAuthenticated, IsOwnerdelete]





# Dummy AI function (replace with your actual model logic)
def get_ai_response(message):
    return f"Echo: {message}"


class Listuser_message(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,IsOwnerchatlist] 
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(user=user)


class CreateChatMessage(generics.CreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        doc = serializer.save(user=self.request.user)

        try:
            ai_response = generate_ai_user_response(self.request.user , doc.user_message)
            
        except Exception as e:
            ai_response = "AI description could not be generated."

        # Update the saved instance with AI description
        doc.assistant_response = ai_response
        
        doc.save()




class DisplayPDFView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Add IsOwner here if needed
    queryset = Doc.objects.all()  # Needed for `get_object()` to work
    print("Entered GET method")

    def get(self, request, filename):
        try:
            # Only allow access to the current user's files (optional but recommended)
            doc = self.get_queryset().get(user=request.user, pdf_file=filename)
            pdf_path = os.path.join(settings.MEDIA_ROOT, doc.pdf_file.name)
            print(pdf_path)
        except Doc.DoesNotExist:
            raise Http404(f"PDF not found{filename}")

        if os.path.exists(pdf_path):
            return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        else:
            raise Http404("PDF file missing on server")