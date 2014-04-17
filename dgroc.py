#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>
   Daniel Vrátil <dvratil@redhat.com>

License: GPLv3 or any later version.
"""

import argparse
import ConfigParser
import datetime
import logging
import os
import subprocess
import shutil
import time
import warnings
from datetime import date
import time

import pygit2
import requests

import smtplib
from email.mime.text import MIMEText

DEFAULT_CONFIG = os.path.expanduser('~/.config/dgroc')
COPR_URL = 'http://copr.fedoraproject.org/'
# Initial simple logging stuff
logging.basicConfig(format='%(message)s')
LOG = logging.getLogger("dgroc")


class DgrocException(Exception):
    ''' Exception specific to dgroc so that we will catch, we won't catch
    other.
    '''
    pass


def _get_copr_auth():
    ''' Return the username, login and API token from the copr configuration
    file.
    '''
    LOG.debug('Reading configuration for copr')
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

    return (username, login, token)


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
    parser.add_argument(
        '--srpm-only', dest='srpmonly', action='store_true',
        default=False,
        help='Generate the new source rpm but do not build on copr')
    parser.add_argument(
        '--no-monitoring', dest='monitoring', action='store_false',
        default=True,
        help='Generate the new source rpm but do not build on copr')
    parser.add_argument(
        '--force', dest='force', action='store_true',
        default=False,
        help='Write SRPM even when there were no changes.')
    parser.add_argument(
        '--no-upload', dest='noupload', action='store_true',
        default=False,
        help='Skip uploading SRPMs.')

    return parser.parse_args()


def update_spec(spec_file, commit_hash, archive_name, packager, email):
    ''' Update the release tag and changelog of the specified spec file
    to work with the specified git commit_hash.
    '''
    LOG.debug('Update spec file: %s', spec_file)
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
                LOG.debug('Release line before: %s', row)
                rel_num = row.split('ase:')[1].strip().split('%{?dist')[0]
                rel_num = rel_num.split('.')[0]
                LOG.debug('Release number: %s', rel_num)
                row = 'Release:        %s.%s%%{?dist}' % (rel_num, release)
                LOG.debug('Release line after: %s', row)
            if row.startswith('Source0:'):
                row = 'Source0:        %s' % (archive_name)
                LOG.debug('Source0 line after: %s', row)
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

    LOG.info('Spec file updated: %s', spec_file)


def get_rpm_sourcedir():
    ''' Retrieve the _sourcedir for rpm
    '''
    dirname = subprocess.Popen(
        ['rpm', '-E', '%_sourcedir'],
        stdout=subprocess.PIPE
    ).stdout.read()[:-1]
    return dirname


def generate_new_srpm(config, project, force):
    ''' For a given project in the configuration file generate a new srpm
    if it is possible.
    '''
    LOG.debug('Generating new source rpm for project: %s', project)
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
        LOG.info('Cloning %s', git_url)
        pygit2.clone_repository(git_url, git_folder)


    if config.has_option(project, 'git_branch'):
        branch = config.get(project, 'git_branch')
    else:
        branch = 'master'

    # git checkout origin/branch
    repo = pygit2.Repository(git_folder)
    ref = repo.lookup_branch('origin/' + branch, pygit2.GIT_BRANCH_REMOTE)
    repo.checkout(ref.name)

    # git pull remote branch
    cwd = os.getcwd()
    os.chdir(git_folder)
    pull = subprocess.Popen(
        ["git", "pull", config.get(project, 'git_url'), branch],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = pull.communicate()
    os.chdir(cwd)
    if pull.returncode:
        LOG.info('Strange result of the git pull:\n%s', out[0])
        return

    # Retrieve last commit
    commit = repo[repo.head.target]
    commit_hash = commit.oid.hex[:8]
    LOG.info('Last commit: %s -> %s', commit.oid.hex, commit_hash)

    # Check if commit changed
    changed = False
    if not config.has_option(project, 'git_hash'):
        config.set(project, 'git_hash', commit_hash)
        changed = True
    elif config.get(project, 'git_hash') == commit_hash:
        changed = False
    elif config.get(project, 'git_hash') != commit_hash:
        changed = True

    if not changed and not force:
        return

    # Build sources
    cwd = os.getcwd()
    os.chdir(git_folder)
    archive_name = "%s-%s.tar" % (project, commit_hash)
    cmd = ["git", "archive", "--format=tar", "--prefix=%s/" % project,
           "-o%s/%s" % (get_rpm_sourcedir(), archive_name), "HEAD"]
    LOG.debug('Command to generate archive: %s', ' '.join(cmd))
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

    try:
        update_spec(
            spec_file,
            commit_hash,
            archive_name,
            config.get('main', 'realname') if config.has_option('main', 'realname') else config.get('main', 'username'),
            config.get('main', 'email'))
    except DgrocException, err:
        if not force:
            # FIXME: Return valid path to SRPM
            return

    # Copy patches
    if config.has_option(project, 'patch_files'):
        LOG.info('Copying patches')
        patches = config.get(project, 'patch_files').split(',')
        patches = [patch.strip() for patch in patches]
        for patch in patches:
            LOG.debug('Copying patch: %s', patch)
            patch = os.path.expanduser(patch)
            if not patch or not os.path.exists(patch):
                LOG.info('Patch not found: `%s`', patch)
                continue
            filename = os.path.basename(patch)
            dest = os.path.join(get_rpm_sourcedir(), filename)
            LOG.debug('Copying from %s, to %s', patch, dest)
            shutil.copy(
                patch,
                dest
            )

    # Generate SRPM
    build = subprocess.Popen(
        ["rpmbuild", "-bs", spec_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = build.communicate()
    os.chdir(cwd)
    if build.returncode:
        LOG.info(
            'Strange result of the rpmbuild -bs:\n  stdout:%s\n  stderr:%s',
            out[0],
            out[1]
        )
        return
    srpm = out[0].split('Wrote:')[1].strip()
    LOG.info('SRPM built: %s', srpm)

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
        LOG.debug('Uploading source rpm: %s', srpm)
        cmd = upload_command % srpm
        outcode = subprocess.call(cmd, shell=True)
        if outcode:
            LOG.info('Strange result with the command: `%s`', ' '.join(cmd))


def copr_build(config, srpmname):
    ''' Using the information provided in the configuration file,
    run the build in copr.
    '''

    ## dgroc config check
    if not config.has_option('main', 'upload_url'):
        raise DgrocException(
            'No `upload_url` specified in the `main` section of the dgroc '
            'configuration file.')

    if not config.has_option('main', 'copr_name'):
        raise DgrocException(
            'No `copr_name` specified in the `main` section of the dgroc '
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

    username, login, token = _get_copr_auth()

    ## Build project/srpm in copr
    srpmurl = config.get('main', 'upload_url') % srpmname;

    URL = '%s/api/coprs/%s/%s/new_build/' % (
        copr_url,
        username,
        config.get('main', 'copr_name'))

    data = {
        'pkgs': srpmurl,
    }

    req = requests.post(
        URL, auth=(login, token), data=data, verify=not insecure)

    if '<title>Sign in Coprs</title>' in req.text:
        LOG.info("Invalid API token")
        return -1

    if req.status_code == 404:
        LOG.info("Project %s/%s not found.", user['username'], project)

    try:
        output = req.json()
    except ValueError:
        LOG.info("Unknown response from server.")
        LOG.debug(req.url)
        LOG.debug(req.text)
        return -1
    if req.status_code != 200:
        LOG.info("Something went wrong:\n  %s", output['error'])
        return -1

    LOG.info(output)
    ids = output['ids'];
    if len(ids) != 1:
        return -1

    return output['ids'][0]


def check_copr_build(config, build_id):
    ''' Check the status of builds running in copr.
    '''

    ## dgroc config check
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

    username, login, token = _get_copr_auth()

    ## Build project/srpm in copr
    URL = '%s/api/coprs/build_status/%s/' % (
        copr_url,
        build_id)

    req = requests.get(
        URL, auth=(login, token), verify=not insecure)

    if '<title>Sign in Coprs</title>' in req.text:
        LOG.info("Invalid API token")
        return 'unknown'

    if req.status_code == 404:
        LOG.info("Build %s not found.", build_id)
        return 'unknown'

    try:
        output = req.json()
    except ValueError:
        LOG.info("Unknown response from server.")
        LOG.debug(req.url)
        LOG.debug(req.text)
        return 'unknown'
    if req.status_code != 200:
        LOG.info("Something went wrong:\n  %s", output['error'])
        return 'unknown'
    LOG.debug('  Build %s: %s', build_id, output)

    return output['status']


def main():
    '''
    '''
    # Retrieve arguments
    args = get_arguments()

    global LOG
    #global LOG
    if args.debug:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    logfile = 'dgroc-' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '.log'
    fh = logging.FileHandler(logfile)
    LOG.addHandler(fh)

    # Read configuration file
    config = ConfigParser.ConfigParser()
    config.read(args.config)

    if not config.has_option('main', 'username'):
        raise DgrocException(
            'No `username` specified in the `main` section of the '
            'configuration file.')

    if not config.has_option('main', 'email'):
        raise DgrocException(
            'No `email` specified in the `main` section of the '
            'configuration file.')

    srpms = []
    for project in config.sections():
        if project == 'main' or project == 'reporting':
            continue
        LOG.info('Processing project: %s', project)
        try:
            srpm = generate_new_srpm(config, project, args.force)
            if not srpm:
                LOG.info('Skipping project %s', project)
                continue;
            srpms.append(srpm)
        except DgrocException, err:
            LOG.info('%s: %s', project, err)
    #endfor

    LOG.info('%s srpms generated', len(srpms))
    if not srpms:
        return

    if args.srpmonly:
        return

    if not args.noupload:
        try:
            upload_srpms(config, srpms)
        except DgrocException, err:
            LOG.info(err)
    #endif


    report = ''
    failed = 0
    for srpm in srpms:
        try:
                srpmname = srpm.rsplit('/', 1)[1]
                build_id = copr_build(config, srpmname)
                if build_id == -1:
                        report += '%s : Failed to start build\n' % srpmname
                        continue

                msg = '%s: Started build ID %s' % (srpmname, build_id)
                report += msg + '\n'
                LOG.info(msg)
                unknownErrors = 0
                while True:
                        time.sleep(60)
                        status = check_copr_build(config, build_id)
                        if status == 'running' or status == 'pending':
                                continue
                        elif status == 'unknown':
                                unknownErrors += 1
                                if unknownErrors < 10:
                                        LOG.info('Build %s UNKNOWN - failed to update status' % build_id)
                                        continue
                        elif status == 'failed':
                                failed += 1
                                report += '[FAILED] ' + srpm + '\n'
                                LOG.info('Build %s FAILED' % build_id)
                                break
                        elif status == 'done':
                                report += '[SUCCESS] ' + srpm + '\n'
                                LOG.info('Build %s SUCCESSFUL' % build_id)
                                break
                        # endif
                # while True
        except DgrocException, err:
                LOG.info(err)
    #endfor

    if config.has_option('reporting', 'smtp_from') and config.has_option('reporting', 'smtp_to') and config.has_option('reporting', 'smtp_server'):
        msg = MIMEText(report)
        if failed > 0:
                status += '[FAILED] '
        if successful:
                status += '[SUCCESS] '
        msg['Subject'] = status + 'DGROC ' + config.get('main', 'copr_name') + ' nightly build report'
        msg['From'] = config.get('reporting', 'smtp_from')
        msg['To'] = config.get('reporting', 'smtp_to')
        smtp = smtplib.SMTP(config.get('reporting', 'smtp_server'))
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()
    #endif


if __name__ == '__main__':
    main()
    #build_ids = [6065]
    #config = ConfigParser.ConfigParser()
    #config.read(DEFAULT_CONFIG)
    #print 'Monitoring builds...'
    #build_ids = check_copr_build(config, build_ids)
    #while build_ids:
        #time.sleep(45)
        #print datetime.datetime.now()
        #build_ids = check_copr_build(config, build_ids)
