import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Base,
    User,
    UserRole,
    Settings,
    TimeCode,
    )
from ..libs.helpers import CODE_TIMEMAP

def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd)))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        root = User(username='root', role=UserRole.SuperAdmin)
        root.set_password("superRoot12")
        DBSession.add(root)
        settings = Settings(evals=False, handouts=False, helpers=False)
        DBSession.add(settings)
        for key,value in CODE_TIMEMAP.items():
            DBSession.add(TimeCode(prefix=key, time=value[1], day=value[0]))
