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

from .forms import UploadCVNForm
from .models import (Congreso, Proyecto, Convenio, TesisDoctoral, Articulo,
                     Libro, CVN, Capitulo, Patente, OldCvnPdf)
from core.models import UserProfile
from core.widgets import FileFieldURLWidget
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from forms import UploadCVNForm, UserProfileAdminForm
from models import (Congreso, Proyecto, Convenio, TesisDoctoral, Articulo,
                    Libro, CVN, Capitulo, Patente, OldCvnPdf)
import admin_basic  # Don't delete


class CVNAdmin(admin.ModelAdmin):

    def xml_file_link(self):
        if self.xml_file:
            return "<a href='%s'>%s</a>" % (self.xml_file.url, self.xml_file)
    xml_file_link.short_description = u'XML'
    xml_file_link.allow_tags = True

    model = CVN

    form = UploadCVNForm

    list_display = (
        'cvn_file', 'user_profile', 'fecha', 'status', xml_file_link,
        'uploaded_at', 'updated_at', 'is_inserted', )

    list_filter = ('status', 'is_inserted', )

    search_fields = (
        'user_profile__user__username',
        'user_profile__documento',
        'user_profile__rrhh_code',
        'user_profile__user__first_name',
        'user_profile__user__last_name'
    )

    ordering = ('-updated_at', )

    def has_add_permission(self, request):
        return False


class CVNInline(admin.TabularInline):

    model = CVN

    form = UploadCVNForm

    fields = ('cvn_file', 'xml_file', 'fecha', 'uploaded_at', 'status',
              'is_inserted')

    readonly_fields = ('fecha', 'uploaded_at', 'status', 'is_inserted')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'xml_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(CVNInline, self).formfield_for_dbfield(db_field, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


class OldCvnPdfInline(admin.TabularInline):

    model = OldCvnPdf

    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(OldCvnPdfInline, self).formfield_for_dbfield(
            db_field, **kwargs)

    readonly_fields = ('uploaded_at', )

    fields = ('cvn_file', 'uploaded_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):

    form = UserProfileAdminForm

    list_display = ('user', 'get_first_name', 'get_last_name', 'documento',
                    'rrhh_code', )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = _(u'Nombre')

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = _(u'Apellidos')

    search_fields = ['user__username', 'documento', 'rrhh_code',
                     'user__first_name', 'user__last_name', ]

    readonly_fields = ('rrhh_code', )

    inlines = [
        CVNInline, OldCvnPdfInline,
    ]

    def has_add_permission(self, request):
        return False


class ProductionAdmin(admin.ModelAdmin):
    search_fields = (
        'titulo',
        'user_profile__user__username',
        'user_profile__documento',
        'user_profile__user__first_name',
        'user_profile__user__last_name',
        'user_profile__rrhh_code',
    )
    ordering = ('created_at',)


class OldCVNAdmin(admin.ModelAdmin):

    def cvn_file_link(self):
        if self.cvn_file:
            return "<a href='%s'>%s<a/>" % (self.cvn_file.url, self.cvn_file)
    cvn_file_link.short_description = u'PDF'
    cvn_file_link.allow_tags = True

    model = OldCvnPdf

    list_display = (
        'user_profile', cvn_file_link, 'uploaded_at', 'created_at', )

    search_fields = (
        'user_profile__user__username',
        'user_profile__documento',
        'user_profile__rrhh_code',
        'user_profile__user__first_name',
        'user_profile__user__last_name'
    )

    ordering = ('-uploaded_at', )

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return tuple(OldCvnPdf._meta.get_all_field_names())


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CVN, CVNAdmin)
admin.site.register(Articulo, ProductionAdmin)
admin.site.register(Libro, ProductionAdmin)
admin.site.register(Capitulo, ProductionAdmin)
admin.site.register(TesisDoctoral, ProductionAdmin)
admin.site.register(Congreso, ProductionAdmin)
admin.site.register(Proyecto, ProductionAdmin)
admin.site.register(Convenio, ProductionAdmin)
admin.site.register(Patente, ProductionAdmin)
admin.site.register(OldCvnPdf, OldCVNAdmin)
