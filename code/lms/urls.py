from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from core.apiv1 import apiv1

def home(request):
    return HttpResponse("Welcome to Simple LMS 🚀")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/v1/', apiv1.urls),
]