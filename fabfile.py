from fabric.api import *
from coach.settings import FABRIC_HOSTS, FABRIC_ENV, DATABASES, FABRIC_BASE
import os
import shutil
from time import time
env.hosts = FABRIC_HOSTS

def prod():
  
  supervisor('stop', 'runreport')
  supervisor('start', 'runreport_celery')
  
  with cd(FABRIC_BASE):
    pull()
    with virtualenv(FABRIC_ENV):
      update_requirements()
      submodules()
      migrate_db()

  # Start again
  supervisor('stop', 'runreport')
  supervisor('start', 'runreport_celery')

def syncdb():
  # Backup actual sqlite db
  db = DATABASES['default']
  if db['ENGINE'].endswith('sqlite3'):
    db_src = db['NAME']
    if os.path.exists(db_src):
      db_backup = '%s.%s' % (db_src, time())
      print 'Backuped local db in %s' % db_backup
      shutil.copyfile(db_src, db_backup)
      os.remove(db_src)

  # Import dump from server
  prod_dump = '/tmp/runreport.json'
  local_dump = 'prod.json'
  apps = ('auth.User', 'auth.Group', 'run', 'users', 'club', 'page')
  with cd(FABRIC_BASE):
    with virtualenv(FABRIC_ENV):
      run('./manage.py dumpdata --indent=4 -e sessions %s > %s' % (' '.join(apps), prod_dump))
      get(prod_dump, local_dump)

  # Re create db & load dump
  local('./manage.py syncdb --noinput --migrate')
  local('./manage.py loaddata %s' % local_dump)
  os.remove(local_dump)

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
