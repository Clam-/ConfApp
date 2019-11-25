from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from confapp.models import (
    DBSession,
    Base,
    )

from confapp.security import groupfinder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    #work around for uwsgi logging
    #logging.config.fileConfig(settings["logging.config"], disable_existing_loggers=False)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy(
    	settings["auth.secret"], callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory='confapp.models.RootFactory')
    config.set_session_factory(SignedCookieSessionFactory(settings["session.secret"], hashalg="md5"))

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_static_view('files', 'files', cache_max_age=3600)
    config.add_route('admin_home', '/')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('admin_del_4real', '/del/{type}/{id}', request_method="POST")
    config.add_route('admin_del', '/del/{type}/{id}')

    config.add_route('admin_person_new', '/person/edit/')
    config.add_route('admin_person_session', '/person/edit/s/{code}')
    config.add_route('admin_person_edit', '/person/edit/{id}')
    config.add_route('admin_person_list', '/person/')

    config.add_route('admin_helper_new', '/helper/edit/')
    config.add_route('admin_helper_edit', '/helper/edit/{id}')

    config.add_route('admin_helper_returned', '/helper/returned/{id}')
    config.add_route('admin_helper_returned_list', '/helper/returned/{id}')
    config.add_route('admin_helper_list', '/helper/')
    config.add_route('admin_helper_update', '/helperupdate/')

    config.add_route('admin_session_new', '/session/edit/')
    config.add_route('admin_session_edit', '/session/edit/{id}')
    config.add_route('admin_session_list', '/session/')

    config.add_route('admin_user_new', '/user/edit/')
    config.add_route('admin_user_edit', '/user/edit/{id}')
    config.add_route('admin_user_list', '/user/')

    config.add_route('nuke_go', '/nuke', request_method="POST")
    config.add_route('nuke', '/nuke')
    config.add_route('admin_admin', '/admin')
    config.add_route('upload', '/upload', request_method="POST")

    config.add_route('admin_room_new', '/location/edit/')
    config.add_route('admin_room_edit', '/location/edit/{id}')
    config.add_route('admin_room_list', '/location/')

    config.add_route('admin_times', '/TIMES/')

    config.add_route('admin_special_list', '/special/{day}/')
    config.add_route('admin_special_home', '/special/')
    config.add_route('admin_csv_list', '/csv/')
    config.add_route('admin_day_list', '/{day}/')

    config.add_route('admin_day_search', '/{day}/search/{code}/{name}')
    config.add_route('admin_day_search_n', '/{day}/name/{name}')
    config.add_route('admin_day_search_c', '/{day}/code/{code}')

    config.add_route('admin_day_edit', '/{day}/{person}/{session}')
    config.add_route('admin_day_edit_c', '/{day}/{person}/{session}/code/{code}')
    config.add_route('admin_day_edit_n', '/{day}/{person}/{session}/name/{name}')
    config.add_route('admin_day_edit_nc', '/{day}/{person}/{session}/{code}/{name}')
    config.add_route('nopresenter', '/nopresenter')

    config.scan()

    config.add_renderer(name='csv', factory='confapp.renderers.CSVRenderer')
    return config.make_wsgi_app()
