from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from confapp.models import (
    DBSession,
    Base,
    )

from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
	""" This function returns a Pyramid WSGI application.
	"""
	#work around for uwsgi logging
	#logging.config.fileConfig(settings["logging.config"], disable_existing_loggers=False)
	
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	Base.metadata.bind = engine
	
	config = Configurator(settings=settings)
	config.set_session_factory(SignedCookieSessionFactory(settings["session.secret"], hashalg="md5"))
	
	config.add_route('home', '/')
	config.add_route('admin_home', '/')
	config.add_route('admin_person_new', '/person/edit/')
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
	
	config.add_route('admin_times', '/TIMES/')
	
	config.add_route('admin_special_list', '/special/{day}/')
	config.add_route('admin_special_home', '/special/')
	config.add_route('admin_day_list', '/{day}/')
	
	config.add_route('admin_day_search', '/{day}/search/{code}/{name}')
	config.add_route('admin_day_search_n', '/{day}/name/{name}')
	config.add_route('admin_day_search_c', '/{day}/code/{code}')
	
	config.add_route('admin_day_edit', '/{day}/{person}/{session}')
	config.add_route('admin_day_edit_c', '/{day}/{person}/{session}/code/{code}')
	config.add_route('admin_day_edit_n', '/{day}/{person}/{session}/name/{name}')
	config.add_route('admin_day_edit_nc', '/{day}/{person}/{session}/{code}/{name}')
	
	config.scan()
	return config.make_wsgi_app()
