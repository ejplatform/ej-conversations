from django.urls import include, re_path as url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from ej_conversations.api import register_routes


router = register_routes(DefaultRouter(), register_user=True)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
]