from django.views.generic import TemplateView
from django.shortcuts import render


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404,)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403,)


def server_error(request):
    return render(request, template_name='pages/500.html', status=500,)
