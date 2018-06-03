from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.shortcuts import get_object_or_404, render

def index(request):

    return HttpResponse("正在设计中")



# Create your views here.
