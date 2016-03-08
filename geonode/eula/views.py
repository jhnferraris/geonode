from django.shortcuts import (
    redirect, get_object_or_404, render, render_to_response)
from django.http import HttpResponse, HttpResponseRedirect
from geonode.layers.forms import AnonDownloaderForm
from .models import AnonDownloader
from django.template import RequestContext

from pprint import pprint

#@register.inclusion_tag('eula_text.html')(eula_text)
def eula_form(request):
    if request.method == 'POST':
        pprint(request.POST)
        form = AnonDownloaderForm(request.POST)
        if form.is_valid():
            out['success'] = True
            pprint(form.cleaned_data)
            form.save()
        else:
            for e in form.errors.values():
                errormsgs.extend([escape(v) for v in e])
            out['success'] = False
            out['errors'] = form.errors
            out['errormsgs'] = errormsgs
        if out['success']:
            status_code = 200
        else:
            status_code = 400
        #Handle form
        return HttpResponse(status=status_code)
    else:
        #Render form
        form = AnonDownloaderForm()
    return render(request, 'eula_nested_anonymous.html',{'form': form})
