from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.urls import path

admin.autodiscover()

app_name = 'register'

urlpatterns = [
    path('', views.index, name='index'),
    path('regist/', views.regist, name='results'),

]