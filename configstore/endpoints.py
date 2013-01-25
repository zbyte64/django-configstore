from hyperadmin.resources.models.endpoints import ListEndpoint, CreateEndpoint as BaseCreateEndpoint, DetailEndpoint, DeleteEndpoint, CreateLinkPrototype as BaseCreateLinkPrototype


class CreateLinkPrototype(BaseCreateLinkPrototype):
    def get_link_kwargs(self, **kwargs):
        form_kwargs = kwargs.pop('form_kwargs', None)
        if form_kwargs is None:
            form_kwargs = {}
        form_kwargs = self.resource.get_form_kwargs(**form_kwargs)
        form_kwargs.setdefault('initial', {})
        
        method = 'POST'
        if kwargs.get('link_factor', None) in ('LO', 'LT'):
            method = 'GET'
        
            if self.resource.requires_select_configuration():
                #TODO this is a hack?
                if kwargs.get('rel', None) != 'breadcrumb':
                    kwargs['link_factor'] = 'LT'
                form_class = self.resource.get_select_configuration_form_class()
            else:
                form_class = self.resource.get_form_class()
        else:
            form_class = self.resource.get_form_class()
        
        link_kwargs = {'url':self.get_url(),
                       'resource':self,
                       'method':method,
                       'form_kwargs':form_kwargs,
                       'form_class': form_class,
                       'prompt':'create',
                       'rel':'create',}
        link_kwargs.update(kwargs)
        return super(CreateLinkPrototype, self).get_link_kwargs(**link_kwargs)

class CreateEndpoint(BaseCreateEndpoint):
    create_prototype = CreateLinkPrototype
