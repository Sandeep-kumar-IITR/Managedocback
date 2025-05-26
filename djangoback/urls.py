
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from myapp.views import Listdoc, Detaildoc, CreateDoc, DeleteDoc
from myapp.views import RegisterView, LoginView, DashboardView


from myapp.views import CreateChatMessage,Listuser_message



from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from myapp.views import DisplayPDFView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/api/auth/login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),

    path('ap/', Listdoc.as_view(), name='listdoc'),
    path('ap/<int:pk>/', Detaildoc.as_view(), name='detaildoc'),
    path('ap/create/', CreateDoc.as_view(), name='createdoc'),
    path('ap/delete/<int:pk>/', DeleteDoc.as_view(), name='deletedoc'),
    path('chatlist/',Listuser_message.as_view(), name='chatlist'),
    path('chat/', CreateChatMessage.as_view(), name='chat'),


    path('pdfs/<str:filename>/', DisplayPDFView.as_view(), name='display_pdf'),
]

# Add this block to serve media files during development

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
