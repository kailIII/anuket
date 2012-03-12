# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.security import unauthenticated_userid
from pyramid.session import UnencryptedCookieSessionFactoryConfig
##from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from wepwawet.lib import subscribers
from wepwawet.models import DBSession, RootFactory
from wepwawet.security import groupfinder
from wepwawet.views import root, tools, user


def get_auth_user(request):

    #TODO: bind to user model
    auth_user = unauthenticated_userid(request)
    return auth_user


def add_static_views(config):
    """ Congigure the static view."""
    config.add_static_view('static', 'static', cache_max_age=3600)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # configure SQLAlchemy
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    config = Configurator(settings=settings)
    # configure the root factory (used for Auth & Auth)
    root_factory = RootFactory
    config.set_root_factory(root_factory)
    # configure session
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config.set_session_factory(session_factory)

    # configure auth & auth
    authorization_policy = ACLAuthorizationPolicy()
##    authentication_policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    authentication_policy = SessionAuthenticationPolicy(callback=groupfinder)
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    # set an auth_user object
    config.set_request_property(get_auth_user, 'auth_user', reify=True)

    # configure subscribers
    config.include(subscribers)
    # configure static views
    config.include(add_static_views)
    # configure routes
    config.include(root)
    config.include(tools)
    config.include(user)
    # configure views
    config.scan()
    # configure i18n
    config.add_translation_dirs('wepwawet:locale')
    config.set_locale_negotiator('wepwawet.lib.i18n.locale_negotiator')
    return config.make_wsgi_app()
