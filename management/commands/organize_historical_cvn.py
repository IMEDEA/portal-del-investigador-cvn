# -*- encoding: UTF-8 -*-

#
#    Copyright 2014-2015
#
#      STIC-Investigación - Universidad de La Laguna (ULL) <gesinv@ull.edu.es>
#
#    This file is part of CVN.
#
#    CVN is free software: you can redistribute it and/or modify it under
#    the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CVN is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with CVN.  If not, see
#    <http://www.gnu.org/licenses/>.
#

from cvn.fecyt import pdf2xml
from cvn.models import OldCvnPdf
from cvn.parsers.read_helpers import parse_nif
from django.conf import settings as st
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db.models import Q
from lxml import etree

import datetime
import os


class Command(BaseCommand):
    help = u'Asigna a los usuarios sus antiguos CVNs'

    OLD_PDF_ROOT = os.path.join(st.MEDIA_ROOT, 'cvn/old_cvn/')

    def handle(self, *args, **options):
        for cvn in os.listdir(self.OLD_PDF_ROOT):
            username = cvn.split('-')[1]
            user = None
            try:
                user = User.objects.get(
                    Q(username=username) | Q(profile__documento=username))
            except ObjectDoesNotExist:
                cvn_file = open(os.path.join(self.OLD_PDF_ROOT, cvn))
                (xml, error) = pdf2xml(cvn_file.read(), cvn_file.name)
                if error:
                    print('Fichero no aceptado por la FECYT: ' + cvn_file.name)
                    continue
                tree_xml = etree.XML(xml)
                documento = parse_nif(tree_xml)
                try:
                    user = User.objects.get(
                        profile__documento__iexact=documento)
                except ObjectDoesNotExist:
                    print '%s (%s) not found' % (username, cvn)

            if user is not None:
                self.cvn2user(cvn, user)

    def cvn2user(self, cvn, user):
        filename = 'CVN-%s-%s' % (
            user.profile.documento, '-'.join(cvn.split('-')[2:]))
        cvn_pdf_path = os.path.join(self.OLD_PDF_ROOT, cvn)
        cvn_pdf = open(cvn_pdf_path)
        old_cvn_file = SimpleUploadedFile(
            filename, cvn_pdf.read(), content_type="application/pdf")
        cvn_old = OldCvnPdf(
            user_profile=user.profile, cvn_file=old_cvn_file,
            uploaded_at=datetime.datetime.strptime(
                ','.join(cvn.replace('.pdf', '').split('-')[2:]), '%Y,%m,%d'))
        cvn_old.save()
        os.remove(cvn_pdf_path)
