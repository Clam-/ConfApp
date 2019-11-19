from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from confapp.models import (
	DBSession,
	Base,
	Person,
	Session,
	Association,
	DayType,
	HandoutType,
	PersonType,
	TripLogger,
	Helper,
	CLASSMAPPER,
	sortstripstring,
	)


config_uri = "development.ini"
setup_logging(config_uri)
settings = get_appsettings(config_uri)
engine = engine_from_config(settings, 'sqlalchemy.')
DBSession.configure(bind=engine)
Base.metadata.create_all(engine)
