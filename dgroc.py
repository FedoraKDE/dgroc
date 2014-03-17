#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import argparse
import ConfigParser
import json
import logging
import os
import subprocess
import warnings
from datetime import date

import pygit2
import requests


DEFAULT_CONFIG = os.path.expanduser('~/.config/dgroc')
COPR_URL = 'http://copr.fedoraproject.org/'


class DgrocException(Exception):
    ''' Exception specific to dgroc so that we will catch, we won't catch
    other.
    '''
    pass


def get_arguments():
    ''' Set the command line parser and retrieve the arguments provided
    by the command line.
    '''
    parser = argparse.ArgumentParser(
        description='Daily Git Rebuild On Copr')
    parser.add_argument(
        '--config', dest='config', default=DEFAULT_CONFIG,
        help='Configuration file to use for dgroc.')
    parser.add_argument(
        '--debug', dest='debug', action='store_true',
        default=False,
        help='Expand the level of data returned')

    return parser.parse_args()


def update_spec(spec_file, commit_hash, archive_name, packager, email):
    ''' Update the release tag and changelog of the specified spec file
    to work with the specified git commit_hash.
    '''

    release = '%sgit%s' % (date.today().strftime('%Y%m%d'), commit_hash)
    output = []
    version = None
    with open(spec_file) as stream:
        for row in stream:
            row = row.rstrip()
            if row.startswith('Version:'):
                version = row.split('Version:')[1].strip()
            if row.startswith('Release:'):
                if commit_hash in row:
                    raise DgrocException('Spec already up to date')
                row = 'Release:        1.%s%%{?dist}' % (release)
            if row.startswith('Source0:'):
                row = 'Source0:        %s' % (archive_name)
            if row.startswith('%changelog'):
                output.append(row)
                output.append('* %s %s <%s> - %s-%s' % (
                    date.today().strftime('%a %b %d %Y'), packager, email,
                    version, release)
                )
                output.append('- Update to git: %s' % commit_hash)
                row = ''
            output.append(row)

    with open(spec_file, 'w') as stream:
        for row in output:
            stream.write(row + '\n')

    print 'Spec file updated: %s' % spec_file


def get_rpm_sourcedir():
    ''' Retrieve the _sourcedir for rpm
    '''
    dirname = subprocess.Popen(
        ['rpm', '-E', '%_sourcedir'],
        stdout=subprocess.PIPE
    ).stdout.read()[:-1]
    return dirname


def generate_new_srpm(config, project):
    ''' For a given project in the configuration file generate a new srpm
    if it is possible.
    '''

    if not config.has_option(project, 'git_folder'):
        raise DgrocException(
            'Project "%s" does not specify a "git_folder" option'
            % project)

    if not config.has_option(project, 'git_url') and not os.path.exists(
            config.get(project, 'git_folder')):
        raise DgrocException(
            'Project "%s" does not specify a "git_url" option and its '
            '"git_folder" option does not exists' % project)

    if not config.has_option(project, 'spec_file'):
        raise DgrocException(
            'Project "%s" does not specify a "spec_file" option'
            % project)

    # git clone if needed
    git_folder = config.get(project, 'git_folder')
    if '~' in git_folder:
        git_folder = os.path.expanduser(git_folder)

    if not os.path.exists(git_folder):
        git_url = config.get(project, 'git_url')
        print 'Cloning %s' % git_url
        pygit2.clone_repository(git_url, git_folder)

    # git pull
    cwd = os.getcwd()
    os.chdir(git_folder)
    pull = subprocess.Popen(
        ["git", "pull"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = pull.communicate()
    os.chdir(cwd)
    if pull.returncode:
        print 'Strange result of the git pull:'
        print out[0]
        return

    # Retrieve last commit
    repo = pygit2.Repository(git_folder)
    commit = repo[repo.head.target]
    commit_hash = commit.oid.hex[:8]
    print 'last commit: %s -> %s' % (commit.oid.hex, commit_hash)

    # Check if commit changed
    changed = False
    if not config.has_option(project, 'git_hash'):
        config.set(project, 'git_hash', commit_hash)
        changed = True
    elif config.get(project, 'git_hash') == commit_hash:
        changed = False
    elif config.get(project, 'git_hash') != commit_hash:
        changed = True

    if not changed:
        return

    # Build sources
    cwd = os.getcwd()
    os.chdir(git_folder)
    archive_name = "%s-%s.tar" % (project, commit_hash)
    cmd = ["git", "archive", "--format=tar", "--prefix=%s/" %  project,
           "-o%s/%s" % (get_rpm_sourcedir(), archive_name), "HEAD"]
    pull = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = pull.communicate()
    os.chdir(cwd)

    # Update spec file
    spec_file = config.get(project, 'spec_file')
    if '~' in spec_file:
        spec_file = os.path.expanduser(spec_file)

    update_spec(
        spec_file,
        commit_hash,
        archive_name,
        config.get('main', 'fas_user'),
        config.get('main', 'email'))

    # Generate SRPM
    build = subprocess.Popen(
        ["rpmbuild", "-bs", spec_file ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = build.communicate()
    os.chdir(cwd)
    if build.returncode:
        print 'Strange result of the rpmbuild -bs:'
        print out[0]
        print out[1]
        return
    srpm = out[0].split('Wrote:')[1].strip()
    print 'SRPM built: %s' %  srpm

    return srpm


def upload_srpms(config, srpms):
    ''' Using the information provided in the configuration file,
    upload the src.rpm generated somewhere.
    '''
    if not config.has_option('main', 'upload_command'):
        raise DgrocException(
            'No `upload_command` specified in the `main` section of the '
            'configuration file.')

    upload_command = config.get('main', 'upload_command')

    for srpm in srpms:
        cmd = upload_command % srpm
        outcode = subprocess.call(cmd, shell=True)
        if outcode:
            print 'Strange result with the command:'
            print cmd


def copr_build(config, srpms):
    ''' Using the information provided in the configuration file,
    run the build in copr.
    '''

    ## dgroc config check
    if not config.has_option('main', 'upload_url'):
        raise DgrocException(
            'No `upload_url` specified in the `main` section of the dgroc '
            'configuration file.')

    if not config.has_option('main', 'copr_url'):
        warnings.warn(
            'No `copr_url` option set in the `main` section of the dgroc '
            'configuration file, using default: %s' % COPR_URL)
        copr_url = COPR_URL
    else:
        copr_url = config.get('main', 'copr_url')

    if not copr_url.endswith('/'):
        copr_url = '%s/' % copr_url

    insecure = False
    if not config.has_option('main', 'no_ssl_check') \
            or config.get('main', 'no_ssl_check'):
        warnings.warn(
            "Option `no_ssl_check` was set to True, we won't check the ssl "
            "certificate when submitting the builds to copr")
        insecure = config.get('main', 'no_ssl_check')

    ## Copr config check
    copr_config_file = os.path.expanduser('~/.config/copr')
    if not os.path.exists(copr_config_file):
        raise DgrocException('No `~/.config/copr` file found.')

    copr_config = ConfigParser.ConfigParser()
    copr_config.read(copr_config_file)

    if not copr_config.has_option('copr-cli', 'username'):
        raise DgrocException(
            'No `username` specified in the `copr-cli` section of the copr '
            'configuration file.')
    username = copr_config.get('copr-cli', 'username')

    if not copr_config.has_option('copr-cli', 'login'):
        raise DgrocException(
            'No `login` specified in the `copr-cli` section of the copr '
            'configuration file.')
    login = copr_config.get('copr-cli', 'login')

    if not copr_config.has_option('copr-cli', 'token'):
        raise DgrocException(
            'No `token` specified in the `copr-cli` section of the copr '
            'configuration file.')
    token = copr_config.get('copr-cli', 'token')

    ## Build project/srpm in copr
    for project in srpms:
        srpms = [
            config.get('main', 'upload_url') % (
                srpms[project].rsplit('/', 1)[1])
        ]

        URL = '%s/api/coprs/%s/%s/new_build/' % (
            copr_url,
            username,
            project)

        data = {
            'pkgs': ' '.join(srpms),
        }

        req = requests.post(
            URL, auth=(login, token), data=data, verify=not insecure)

        if '<title>Sign in Coprs</title>' in req.text:
            print "Invalid API token"
            return

        if req.status_code == 404:
            if copr is None:
                print "User %s is unknown." % user['username']
            else:
                print "Project %s/%s not found." % (user['username'], copr)
            return
        try:
            output = json.loads(req.text)
        except ValueError:
            sys.stderr.write("Unknown response from server.")
            return
        if req.status_code != 200:
            print "Something went wrong:\n  %s" % (output['error'])
            return
        print output


def main():
    '''
    '''
    # Retrieve arguments
    args = get_arguments()

    # Read configuration file
    config = ConfigParser.ConfigParser()
    config.read(args.config)

    if not config.has_option('main', 'fas_user'):
        raise DgrocException(
            'No `fas_user` specified in the `main` section of the '
            'configuration file.')

    if not config.has_option('main', 'email'):
        raise DgrocException(
            'No `email` specified in the `main` section of the '
            'configuration file.')

    srpms = {}
    for project in config.sections():
        if project == 'main':
            continue
        try:
            srpms[project] = generate_new_srpm(config, project)
        except DgrocException, err:
            print '%s: %s' % (project, err)

    print '%s srpms generated' % len(srpms)
    if not srpms:
        return

    try:
        upload_srpms(config, srpms.values())
    except DgrocException, err:
        print err

    try:
        copr_build(config, srpms)
    except DgrocException, err:
        print err


if __name__ == '__main__':
    main()