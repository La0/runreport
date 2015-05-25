from fabric.api import *
from fabric.operations import prompt
from coach.settings import FABRIC_HOSTS, DATABASES # Mandatory
try:
  from coach.settings import FABRIC_ENV, FABRIC_BASE, FABRIC_SUPERVISORS # Optional
except Exception:
  FABRIC_SUPERVISORS = []
  pass
import os
env.hosts = FABRIC_HOSTS
from datetime import date

def prod():

  # Stop services
  supervisors('stop')

  # Brutally kill celery workers as supervisor
  # doesn't do its job :(
  if 'runreport_celery' in FABRIC_SUPERVISORS:
    with settings(warn_only=True):
      run("ps auxww | grep 'celery -A coach worker' | grep -v grep | awk '{print $2}' |xargs kill -9")

  with cd(FABRIC_BASE):
    pull()
    with virtualenv(FABRIC_ENV):
      update_requirements()
      submodules()
      migrate_db()
      static()

  # Start again
  supervisors('start')

def syncdb(update=False):

  # Import dump from server
  local_dump = 'prod.json'
  if os.path.exists(local_dump):
    # Adk for reuse of local_dump
    keep_dump = prompt('Found a local dump (%s). Use it [y/n] ?' % local_dump)
    if keep_dump.lower() != 'y':
      os.unlink(local_dump)

  if not os.path.exists(local_dump):
    if update:
      print 'Try to update Database dump'
      prod_dump = '/tmp/runreport.json'
      apps = ('sport', 'users', 'club', 'page', 'messages', 'friends', 'plan')
      with cd(FABRIC_BASE):
        with virtualenv(FABRIC_ENV):
          run('./manage.py dumpdata --indent=4 -e sessions %s > %s' % (' '.join(apps), prod_dump))
          get(prod_dump, local_dump)
    else:
      print 'Use today dump on server'
      prod_dump = '~/db/%s.json' % date.today().strftime('%Y%m%d')
      get(prod_dump, local_dump)

  # Re create db & load dump
  createdb(False) # no fixtures here
  local('./manage.py loaddata %s' % local_dump)
  os.remove(local_dump)

def createdb(use_fixtures=True):
  '''
  Create the Pgsql database
   * delete old database if exists
   * create new one through psql
  '''
  # Drop old database manually
  db = DATABASES['default']
  psql('drop database if exists %s' % db['NAME'], 'postgres')

  # Create new database
  psql('create database %(NAME)s with owner = %(USER)s' % db, 'postgres')

  # Init Postgis on database
  psql('create extension postgis')

  # Create structure
  local('./manage.py migrate')

  if use_fixtures:
    # Load some basic fixtures
    fixtures = (
      'sport/data/sports.json',
      'users/data/categories.json',
      'users/data/demo.json',
      'club/data/demo.json',
    )
    for f in fixtures:
      local('./manage.py loaddata %s' % f)

def psql(sql, dbname=None):
  '''
  Run a pgsql command through cli
  '''
  db = DATABASES['default']
  print db
  suffix = db['ENGINE'][db['ENGINE'].rindex('.') + 1:]
  if suffix not in ('postgis',):
    raise Exception('Only PostGis is supported')

  cmd = 'PGPASSWORD="%(PASSWORD)s" psql --username=%(USER)s --host=%(HOST)s' % db
  cmd += ' --dbname=%s' % (dbname or db['NAME'])
  cmd += ' --command="%s"' % sql
  local(cmd)

def virtualenv(name='django'):
  '''
  Source a virtualenv on prefix
  '''
  return prefix('source %s/bin/activate' % name)

def update_requirements():
  '''
  Update through pip & bower
  '''
  run('pip install -r requirements.txt')
  run('bower install')

def pull():
  '''
  Pull from github
  '''
  run('git pull')

def migrate_db():
  '''
  Update db using South migrations
  '''
  run('./manage.py migrate')

def supervisors(cmd):
  for s in FABRIC_SUPERVISORS:
    supervisor(cmd, s)

def supervisor(cmd, process):
  '''
  Control processes through supervisor
  '''
  run('supervisorctl %s %s' % (cmd, process))

def submodules():
  run('git submodule init')
  run('git submodule update')

def static():
  run('./manage.py collectstatic --clear --noinput --ignore "tracks" --ignore "posts" --ignore "avatars"')
