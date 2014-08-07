from fabric.api import *
from coach.settings import FABRIC_HOSTS, DATABASES # Mandatory
try:
  from coach.settings import FABRIC_ENV, FABRIC_BASE # Optional
except Exception:
  pass
import os
import shutil
from time import time
env.hosts = FABRIC_HOSTS
from datetime import date

def prod():

  supervisor('stop', 'runreport')
  supervisor('stop', 'runreport_celery')

  # Brutally kill celery workers as supervisor
  # doesn't do its job :(
  with settings(warn_only=True):
    run("ps auxww | grep 'celery -A coach worker' | awk '{print $2}' |xargs kill -9")

  with cd(FABRIC_BASE):
    pull()
    with virtualenv(FABRIC_ENV):
      update_requirements()
      submodules()
      migrate_db()

  # Start again
  supervisor('start', 'runreport')
  supervisor('start', 'runreport_celery')

def syncdb(update=False):

  # Import dump from server
  local_dump = 'prod.json'
  if update:
    print 'Try to update Database dump'
    prod_dump = '/tmp/runreport.json'
    apps = ('sport', 'users', 'club', 'page')
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

  # Create structure
  local('./manage.py syncdb --noinput --all')
  local('./manage.py migrate --fake')

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
  if not db['ENGINE'].endswith('postgresql_psycopg2'):
    raise Exception('Only Postgresql is supported')

  cmd = 'PGPASSWORD="%(PASSWORD)s" psql --username=%(USER)s --host=%(HOST)s' % db
  cmd += ' --dbname=%s' % dbname or db['NAME']
  cmd += ' --command="%s"' % sql
  local(cmd)

def virtualenv(name='django'):
  '''
  Source a virtualenv on prefix
  '''
  return prefix('source %s/bin/activate' % name)

def update_requirements():
  '''
  Update through pip
  '''
  run('pip install -r requirements.txt')

def pull():
  '''
  Pull from github
  '''
  run('git pull origin master')

def migrate_db():
  '''
  Update db using South migrations
  '''
  run('./manage.py migrate')

def supervisor(cmd, process):
  '''
  Control processes through supervisor
  '''
  run('supervisorctl %s %s' % (cmd, process))

def submodules():
  run('git submodule init')
  run('git submodule update')
