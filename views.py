# -*- encoding: UTF-8 -*-

from cvn import settings as stCVN
from cvn.forms import UploadCVNForm
from cvn.models import FECYT, CVN
from cvn.utils import saveScientificProductionToContext, getDataCVN, movOldCVN
from django.conf import settings as st
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)


@login_required
def index(request):
    context = {}
    user = request.user
    if 'message' in request.session:
        context['message'] = request.session['message']
        del request.session['message']

    if 'attributes' in request.session:
        context['user'] = request.session['attributes']
    else:
        return HttpResponseRedirect(reverse('logout'))
    cvn = user.profile.cvn
    context['form'] = UploadCVNForm()
    if request.method == 'POST':
        formCVN = UploadCVNForm(request.POST, request.FILES)
        if formCVN.is_valid():
            filePDF = request.FILES['cvn_file']
            (xmlFECYT, errorCode) = FECYT().getXML(filePDF)
            if xmlFECYT and CVN().can_user_upload_cvn(user, xmlFECYT):
                if cvn:
                    movOldCVN(cvn)
                    cvn.delete()
                if cvn and cvn.xml_file:
                    cvn.xml_file.delete()
                cvn = formCVN.save(user=user, fileXML=xmlFECYT, commit=True)
                user.profile.cvn = cvn
                user.profile.save()
                cvn.insertXML(user.profile)
                context['message'] = _(u'CVN actualizado con éxito.')
            else:
                if not xmlFECYT:
                    formCVN.errors['cvn_file'] = ErrorList(
                        [_(stCVN.ERROR_CODES[errorCode])])
                else:
                    formCVN.errors['cvn_file'] = ErrorList(
                        [_(u'El NIF/NIE del CVN no coincide'
                           ' con el de su usuario.')])
        context['form'] = formCVN
    if cvn:
        context['CVN'] = True
        context.update(getDataCVN(cvn))
        saveScientificProductionToContext(user.profile, context)
    return render(request, "index.html", context)


@login_required
def download_cvn(request):
    user = request.user
    cvn = user.profile.cvn
    if cvn:
        logger.info("Download CVN: " + user.username + ' - '
                    + user.profile.documento)
    try:
        filename = st.MEDIA_ROOT + '/' + cvn.cvn_file.name
        download_name = cvn.cvn_file.name.split('/')[-1]
        with open(filename, 'r') as pdf:
            response = HttpResponse(pdf.read(), mimetype='application/pdf')
            response['Content-Disposition'] = 'inline; filename=%s' % (
                download_name)
        pdf.closed
    except (TypeError, IOError):
        raise Http404
    return response


@login_required
def ull_report(request):
    context = {}
    saveScientificProductionToContext(request.user.profile, context)
    return render(request, "ull_report.html", context)
