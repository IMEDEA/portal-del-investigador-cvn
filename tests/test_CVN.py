# -*- encoding: UTF-8 -*-

from django.test import TestCase
from cvn.models import CVN
from django.contrib.auth.models import User
from django.conf import settings as st
import os


class CVNTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='rabadmar')

    def test_insertXML(self):
        """ Insert the data of XML data in the database """
        try:
            XML = os.path.join(st.MEDIA_ROOT, 'cvn/xml/CVN-rabadmar.xml')
            fileXML = open(XML, 'r')
            cvn = CVN(xml_file=fileXML)
            cvn.insertXML(self.user.profile)
            self.assertEqual(self.user.profile.publicacion_set.filter(
                tipo_de_produccion='Articulo').count(), 0)
            self.assertEqual(self.user.profile.publicacion_set.filter(
                tipo_de_produccion='Libro').count(), 0)
            self.assertEqual(self.user.profile.publicacion_set.filter(
                tipo_de_produccion='Capitulo de Libro').count(), 0)
            self.assertEqual(self.user.profile.congreso_set.count(), 0)
            self.assertEqual(self.user.profile.convenio_set.count(), 0)
            self.assertEqual(self.user.profile.proyecto_set.count(), 1)
            self.assertEqual(self.user.profile.tesisdoctoral_set.count(), 0)
        except:
            raise