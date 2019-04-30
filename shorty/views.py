from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import random, string
from shorty.models import Short_Urls

@login_required()
def all_links(request):

	links = Short_Urls.objects.filter(active=1).order_by('-ts_updated')
	site = ('https://' if request.is_secure() else 'http://') + request.get_host() + '/l/'

	context = {
		'title': "Shortened Links",
		'links': links,
		'site': site,
	}
	return render(request, 'shorty/all.html', context)

# TODO Make sure this is not a permanent redirect !!!!!!!!!!!!!!!!!!!!!!!
# currently doing 302 redirects
# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#3xx_Redirection
def redirect_url(request, short_url):
	
	try:
		shorty_obj = Short_Urls.objects.get(url_short=short_url, active = 1)
	except Short_Urls.DoesNotExist:
		return HttpResponse("Invalid or expired link.")
	
	return redirect(shorty_obj.url_long)

@login_required()
def gen_short_urls(request):	
	x = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
	print(x)
