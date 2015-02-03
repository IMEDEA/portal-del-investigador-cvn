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

from core.tests.factories import UserFactory
from core.tests.helpers import init, clean
from cvn import settings as st_cvn
from cvn.models import CVN
from cvn.parsers.read import parse_cvnitem
from cvn.parsers.write import CvnXmlWriter
from django.test import TestCase
from factories import (LearningPhdFactory, ProfessionFactory,
                       TeachingFactory, LearningFactory,)
from lxml import etree

import csv
import datetime
import os


class ParserWriterTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        init()

    @staticmethod
    def utf_8_encoder(unicode_csv_data):
        for line in unicode_csv_data:
            yield line.decode('iso-8859-10').encode('utf-8')

    @staticmethod
    def hash_to_unicode(dict_row):
        for key in dict_row:
            try:
                dict_row[key] = dict_row[key].decode('utf-8')
            except AttributeError:
                pass

    def test_cvnitem_factories(self):
        user = UserFactory.create()
        parser = CvnXmlWriter(user)
        cvnitem_dict = {}
        # Insert old and new professions in the CVN
        for i in range(0, 10):
            d = ProfessionFactory.create()
            cvnitem_dict[d['title']] = d
            parser.add_profession(**d)
        # Insert Phd the researcher has received
        for i in range(0, 10):
            d = LearningPhdFactory.create()
            cvnitem_dict[d['title']] = d
            parser.add_learning_phd(**d)
        # Insert teaching data
        for i in range(0, 10):
            d = TeachingFactory.create()
            cvnitem_dict[d['title']] = d
            parser.add_teaching(**d)
        # Insert bachelor, degree...data
        for i in range(0, 10):
            d = LearningFactory.create()
            cvnitem_dict[d['title']] = d
            parser.add_learning(**d)
        cvn = CVN.create(user, parser.tostring())
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        for item in cvn_items:
            cvnitem = parse_cvnitem(item)
            self.assertEqual(cmp(cvnitem, cvnitem_dict[cvnitem['title']]), 0)
        self.assertNotEqual(cvn, None)

    @classmethod
    def tearDownClass(cls):
        clean()
