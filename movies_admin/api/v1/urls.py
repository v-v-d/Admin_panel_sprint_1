from django.urls import path, include
from rest_framework import routers

from api.v1 import views

router = routers.DefaultRouter()
router.register('movies', views.FilmWorkViewSet, basename='movies')


urlpatterns = [
    path('movies/', include(router.urls)),
]
