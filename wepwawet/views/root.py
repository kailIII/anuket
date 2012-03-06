# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, forget, remember
from pyramid.view import view_config, forbidden_view_config, notfound_view_config
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from wepwawet.lib.i18n import MessageFactory as _
from wepwawet.forms import LoginForm
from wepwawet.security import USERS


def includeme(config):
    """Add root pages routes."""
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')


@notfound_view_config(renderer='404.mako')
@view_config(route_name='about', renderer='about.mako')
@view_config(route_name='home', renderer='index.mako')
def root_view(request):
    """Render the root pages."""
#    request.session.flash(u"warning message", 'warn')
#    request.session.flash(u"info message", 'info')
#    request.session.flash(u"error message", 'error')
#    request.session.flash(u"success message", 'success')
    return dict(username=authenticated_userid(request))


@forbidden_view_config()
def forbiden_view(request):
    """Redirect the 403 forbiden view to login or home page and add a
    flash message to display the relevant error.
    """
    username = authenticated_userid(request)
    #TODO: take care of csrf error
    if username:
        request.session.flash(_(u"You do not have the permission to do this!"), 'error')
        return HTTPFound(location=request.route_path('home'))
    else:
        request.session.flash(_(u"You are not connected, please log in."), 'error')
        return HTTPFound(location=request.route_path('login'))


@view_config(route_name='login', renderer='login.mako')
def login_view(request):
    """Render the login form."""
    form = Form(request, schema=LoginForm)
    if 'form_submitted' in request.params:
        username = request.params['username']
        password = request.params['password']
        if USERS.get(username) == password:
            headers = remember(request, username)
            request.session.flash(_(u"You have successfuly connected."), 'info')
            return HTTPFound(location=request.route_path('home'), headers=headers)
        else:
            request.session.flash(_(u"Please check your login credentials!"), 'error')
    return dict(renderer=FormRenderer(form))

@view_config(route_name='logout')
def logout_view(request):
    """Clear credentials and redirect to the login page."""
    headers = forget(request)
    return HTTPFound(location=request.route_path('login'), headers=headers)
