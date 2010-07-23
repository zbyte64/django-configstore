from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Library

from configstore.configs import get_config

register = Library()

class WithConfigNode(Node):
    def __init__(self, var, name, nodelist):
        self.var = var
        self.name = name
        self.nodelist = nodelist

    def __repr__(self):
        return "<WithConfigNode>"

    def render(self, context):
        val = self.var.resolve(context)
        context.push()
        context[self.name] = get_config(val)
        output = self.nodelist.render(context)
        context.pop()
        return output

def do_with_config(parser, token):
    """
    Adds config store entry to the context

    For example::

        {% withconfig "recaptcha" as recaptcha %}
            {{ recaptcha.public_key }}
        {% endwithconfig %}
    """
    bits = list(token.split_contents())
    if len(bits) != 4 or bits[2] != "as":
        raise TemplateSyntaxError("%r expected format is 'key as name'" %
                                  bits[0])
    var = parser.compile_filter(bits[1])
    name = bits[3]
    nodelist = parser.parse(('endwithconfig',))
    parser.delete_first_token()
    return WithConfigNode(var, name, nodelist)
do_with_config = register.tag('withconfig', do_with_config)
