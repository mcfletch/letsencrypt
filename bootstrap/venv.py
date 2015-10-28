#! /usr/bin/env python
#
# Installs and updates letencrypt virtualenv
#
# USAGE: python bootstrap/venv.py
from __future__ import print_function
import os
import logging
import subprocess
import argparse
HERE = os.path.dirname(__file__)
log = logging.getLogger('venv')

def default_virtualenv():
    """Decide on the default virtualenv location"""
    XDG_DATA_HOME=os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    return os.path.join( XDG_DATA_HOME, 'letsencrypt' )

def command( command, *args, **named):
    log.info("Running: %s", " ".join(command))
    named['stdout'] = subprocess.PIPE
    named['stderr'] = subprocess.STDOUT
    pipe = subprocess.Popen( command, *args, **named )
    stdout,_ = pipe.communicate()
    if pipe.returncode:
        log.error("Failure running %s: \n%s"," ".join( command ),stdout)
        raise RuntimeError( pipe.returncode, command )
    return stdout

def get_options():
    parser = argparse.ArgumentParser(description="Create developer's virtualenv for letsencrypt")
    default = default_virtualenv()
    parser.add_argument(
        '-e','--env', 
        metavar='DIRECTORY',
        help="Full path to the target directory, default: %s"%(default,), 
        default=default
    )
    parser.add_argument(
        '-f','--force',
        action='store_true',
        default=False,
    )
    return parser

def main():
    logging.basicConfig(level=logging.INFO)
    if os.environ.get("VIRTUAL_ENV"):
        log.warn("To avoid issues, we will not run with an active virtualenv: run deactivate first")
        print( '' )
        raise SystemExit(1)
    parser = get_options()
    options = parser.parse_args()
    target = os.path.normpath( options.env )
    log.info("Target directory %s",target)
    
    pip = os.path.join( target, 'bin','pip' )
    python = os.path.join( target, 'bin','python' )
    
    new_environment = False
    if not os.path.exists( target ):
        log.info("Creating target virtualenv")
        command([
            'virtualenv',
                '--no-site-packages',
                '--python', 'python2',
                target,
        ])
        command([pip,'install','-U','setuptools'])
        command([pip,'install','-U','pip'])
        new_environment = True
    if new_environment or options.force:
        root = os.path.normpath( os.path.join( HERE, '..' ))
        for subproject in [
            os.path.join( root, 'acme'),
            root,
            os.path.join( root, 'letsencrypt-apache'),
            os.path.join( root, 'letsencrypt-nginx'),
        ]:
            log.info("Running setup.py develop for %s", subproject )
            command([ python, os.path.join( subproject,'setup.py'), 'develop' ])
    
    log.info("You can activate the virtualenv with\n    source $(python %s)", __file__ )
    print( os.path.join(target,'bin','activate') )

if __name__ == "__main__":
    main()
