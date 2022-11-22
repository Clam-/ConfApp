import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'bcrypt',
    'plaster_pastedeploy==0.7',
    'plaster==1.0',
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'PasteScript==3.2.1',
    'Paste==3.5.0',
    'PasteDeploy==2.1.1',
    'unicodecsv',
    'paginate==0.5.6', # pagination helpers
    'paginate_sqlalchemy==0.3.0',
	]

setup(name='ConfApp',
      version='0.0',
      description='ConfApp',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='confapp',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = confapp:main
      [console_scripts]
      initialize_ConfApp_db = confapp.scripts.initializedb:main
      """,
      )
