from django.contrib import admin
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django import template

from models import Configuration
from configs import CONFIGS

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'site')

    def get_fieldsets(self, request, obj=None):
        #consider it might be nice delegate more of this functionality to the ConfigurationInstance
        form_builder = self.get_form(request, obj)
        return [(None, {'fields': form_builder().fields.keys()})]

    def get_form(self, request, obj=None, **kwargs):
        #use the key to get the form
        if obj:
            return CONFIGS[obj.key].get_form_builder()
        return CONFIGS[request.GET['key']].get_form_builder()
    
    def add_view(self, request, form_url='', extra_context=None):
        if 'key' in request.GET:
            return super(ConfigurationAdmin, self).add_view(request, form_url, extra_context)
        #render a listing of links ?key={{configkey}}
        #consider can we also select the site?
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        obj = None
        configs = CONFIGS.items()
        def sort_by_label(a, b):
            return cmp(a[1].name, b[1].name)
        configs.sort(sort_by_label)
        context = {
            'title': _('Select %s') % force_unicode(opts.verbose_name),
            'configs': configs,
            #'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            #'media': mark_safe(media),
            #'inline_admin_formsets': inline_admin_formsets,
            #'errors': helpers.AdminErrorList(form, formsets),
            'root_path': getattr(self.admin_site, 'root_path', ''),
            'app_label': app_label,
            'add': True,
            'change': False,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': False, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        }
        context.update(extra_context or {})
        return render_to_response(self.change_form_template or [
            "admin/%s/%s/add_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/add_form.html" % app_label,
        ], context, context_instance=template.RequestContext(request))

admin.site.register(Configuration, ConfigurationAdmin)
