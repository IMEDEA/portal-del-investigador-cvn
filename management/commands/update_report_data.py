# -*- encoding: UTF-8 -*-

#
#    Copyright 2015
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

from django.core.management.base import BaseCommand
from cvn.models import ReportArea, ReportDept, ReportMember
from django.utils.translation import ugettext as _
from optparse import make_option


class Command(BaseCommand):
    help = _(u'Import department and area info from WebServices')

    option_list = BaseCommand.option_list + (
        make_option(
            "-d",
            "--delete",
            dest="delete",
            default=False,
            action="store_true",
            help="Specify if the reports information should be just deleted"
        ),
        make_option(
            "-y",
            "--year",
            dest="year",
            help="Specify the reports year"
        ),
    )

    def handle(self, *args, **options):
        ReportArea.objects.all().delete()
        ReportDept.objects.all().delete()
        ReportMember.objects.all().delete()
        if not options['delete']:
            ReportMember.create_all()
            ReportArea.load(options['year'])
            ReportDept.load(options['year'])
