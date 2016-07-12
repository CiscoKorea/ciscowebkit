from django.template import loader
from django.http import HttpResponse
from ciscowebkit.common.platform import Manager

def action(request):
    sample_widgets = loader.get_template('dashboard_sample.html').render()
    return HttpResponse(Manager.GET().__render_dashboard__(sample_widgets, None))
    
    
    