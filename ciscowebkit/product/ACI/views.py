from django.http import HttpResponse
from ciscowebkit.common.platform import Manager

# Create your views here.

def action(request):
    return Manager.GET().action(request)
