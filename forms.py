# -*- encoding: UTF-8 -*-

from cvn.models import CVN
from django import forms
from cvn import settings as stCVN
from cvn.helpers import setCVNFileName
from django.core.files.base import ContentFile
import datetime


class UploadCVNForm(forms.ModelForm):

    def clean_cvn_file(self):
        fileCVN = self.cleaned_data['cvn_file']
        if fileCVN.content_type != stCVN.PDF:
            raise forms.ValidationError("El CVN debe estar en formato PDF.")
        else:
            return fileCVN

    def save(self, user=None, fileXML=None, commit=True):
        cvn = super(UploadCVNForm, self).save(commit=False)
        cvn.fecha_up = datetime.date.today()
        if user:
            cvn.cvn_file.name = setCVNFileName(user)
        if fileXML:
            cvn.xml_file.save(cvn.cvn_file.name.replace('pdf', 'xml'),
                              ContentFile(fileXML), save=False)
            cvn.fecha_cvn = CVN().getXMLDate(fileXML)
        if commit:
            cvn.save()
        return cvn

    class Meta:
        model = CVN
        fields = ['cvn_file']
