from django.conf.urls import url
from mysite import views

urlpatterns = [
    url(r'^play', views.play),
    url(r'^pause', views.pause)
]
