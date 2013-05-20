from fabric.api import *
from coach.settings import FABRIC_HOSTS, FABRIC_ENV, DATABASES
import os
import shutil
from time import time
env.hosts = FABRIC_HOSTS

def prod():
  
  stop_fcgi()
  
  with cd('~/coach'):
    pull()
    with virtualenv(FABRIC_ENV):
      migrate_db()
      start_fcgi()
  restart_lighttpd()

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
  prod_dump = '/tmp/coach.json'
  local_dump = 'prod.json'
  apps = ('auth.User', 'auth.Group', 'run', 'users', 'club')
  with cd('~/coach'):
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
  return prefix('source ~/%s/bin/activate' % name)

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

def stop_fcgi(pidfile='coach.pid'):
  '''
  Kill the fast cgi process
  '''
  with settings(warn_only=True):
    output = run('kill -9 `cat %s`' % pidfile)
    if output.failed:
      print 'No pid found, server not stopped.'
      return
    run('rm %s' % pidfile)

def start_fcgi(pidfile='coach.pid'):
  '''
  Start the fast cgi process
  '''
  run('./manage.py runfcgi workdir=~/coach protocol=scgi pidfile=~/coach.pid host=localhost port=8300 outlog=~/cgi-coach-out.log errlog=~/cgi-coach-err.log')

def restart_lighttpd():
  '''
  Restart lighttpd
  '''
  pass
