from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^spider_api$', views.spider_api, name='spider_api')
]