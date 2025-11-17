from django.shortcuts import HttpResponse, render

# Create your views here.


def users_tmp_view(request):
    return HttpResponse('Users app is working!')
