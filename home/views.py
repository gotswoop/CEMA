from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
	return render(request, 'home/home.html')

@login_required()
def dashboard(request):
	return render(request, 'home/dashboard.html')

def ping(request):
    ip = get_client_ip(request)
    return HttpResponse('<html>OK<br/>' + ip + '</html>')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
