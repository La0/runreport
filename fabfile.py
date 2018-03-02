from fabric.api import local, env, get, prefix
from fabric.operations import prompt
import sys
sys.path += ['./src', ]
from runreport.settings import FABRIC_HOSTS, DATABASES
import os
env.hosts = FABRIC_HOSTS

def syncdb():
  '''
  For dev only, passwords will be reset !
  '''

  # Import dump from server
  local_encrypted = 'current_prod.gpg.tar'
  local_dump = 'current_prod.tar'
  if os.path.exists(local_dump):
    # Adk for reuse of local_dump
    keep_dump = prompt('Found a local dump (%s). Use it [y/n] ?' % local_dump)
    if keep_dump.lower() != 'y':
      os.unlink(local_dump)

  if not os.path.exists(local_dump):
    # Download
    prod_dump = '~/backups/current/db.tar'
    get(prod_dump, local_dump)

    # Decrypt
    #decrypt = 'gpg --decrypt %s > %s' % (local_encrypted, local_dump)
    #local(decrypt)

    # Cleanup
    #os.remove(local_encrypted)

  # Re create db
  createdb()

  # Restore db from dump
  cmd = pg(command='pg_restore')
  cmd += ' -n public --no-owner %s' % local_dump
  local(cmd)

  # Run migrations
  local('./manage.py migrate')

  # Reset passwords
  local('./manage.py reset_passwords')

  # Build stats cache
  local('./manage.py build_stats')

  # Cleanup
  os.remove(local_dump)

def createdb():
  '''
  Create the Pgsql database
   * delete old database if exists
   * create new one through psql
  '''
  # Drop old database manually
  db = DATABASES['default']
  pg('drop database if exists %s' % db['NAME'], 'postgres')

  # Create new database
  pg('create database %(NAME)s with owner = %(USER)s' % db, 'postgres')

  # Init Postgis on database
  pg('create extension postgis')

def pg(sql=None, dbname=None, command='psql'):
  '''
  Run a pgsql command through cli
  '''
  db = DATABASES['default']
  suffix = db['ENGINE'][db['ENGINE'].rindex('.') + 1:]
  if suffix not in ('postgis',):
    raise Exception('Only PostGis is supported')
  db['COMMAND'] = command

  cmd = 'PGPASSWORD="%(PASSWORD)s" %(COMMAND)s --username=%(USER)s --host=%(HOST)s --port=%(PORT)s' % db
  cmd += ' --dbname=%s' % (dbname or db['NAME'])
  if sql:
    cmd += ' --command="%s"' % sql
    local(cmd)
  return cmd

def virtualenv(name='django'):
  '''
  Source a virtualenv on prefix
  '''
  return prefix('source %s/bin/activate' % name)
