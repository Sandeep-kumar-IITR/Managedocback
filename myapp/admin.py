from django.contrib import admin

# Register your models here.
from myapp.models import Doc
from myapp.models import ChatMessage

admin.site.register(Doc)
admin.site.register(ChatMessage)
