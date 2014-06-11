#!/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Daniel Vrátil <dvratil@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
#
#
# dgroc.conf generator
#

config = { 'username': 'dvratil',
           'realname': 'Daniel Vrátil',
           'email': 'dvratil@redhat.com',
           'copr_url': 'https://copr.fedoraproject.org/',
           'copr_name': 'kde-frameworks-unstable',
           'upload_command': 'cp %s /home/dvratil/pub/kf5/srpm/unstable',
           'upload_url': 'http://pub.progdan.cz/kf5/srpm/unstable/%s',
           'no_ssl_check': 'False',

           'spec_git_clone':   'https://github.com/FedoraKDE/fedora-kde-frameworks.git',
           'spec_git_push':    'git@github.com:FedoraKDE/fedora-kde-frameworks.git',
           'specBranch':       'master',
           'specPrivKey': '/home/progdan/.ssh/id_rsa.dgroc',
           'specPubKey': '/home/progdan/.ssh/id_rsa.dgroc.pub',
           'specDir':   '/home/progdan/kf5/fedora-kde-frameworks',
           'sourceDir': '/home/progdan/kf5/src',
           'logDir':  '/home/progdan/kf5/logs',

           'git_repo': 'git://anongit.kde.org',

            # For reporting
           'smtp_from': 'dgroc-kde-frameworks@valhalla',
           'smtp_to': 'dan@progdan.cz',
           'smtp_server': 'progdan.cz',
         }


#               git repository          package name            branch          [patch1, patch2, ...]
base	     = [('akonadi-qt5',		'akonadi-qt5')]

unstable     = [('kf5-gpgme++',		'kf5-gpgme++'),
	        ('kf5-akonadi',		'kf5-akonadi'),
		('kf5-kabc',		'kf5-kabc'),
		('kf5-kcalcore',	'kf5-kcalcore'),
		('kf5-kfilemetadata',	'kf5-kfilemetadata'),
		('kf5-kholidays',	'kf5-kholidays'),
		('kf5-kldap',		'kf5-kldap'),
		('kf5-kmime',		'kf5-kmime'),
		('kf5-kpimtextedit',	'kf5-kpimtextedit'),
		('kf5-kpimutils',	'kf5-kpimutils'),
		('kf5-kxmlrpcclient',	'kf5-kxmlrpcclient'),
		('kf5-microblog',	'kf5-microblog'),
		('kf5-kmodemmanagerqt',	'kf5-modemmanagerqt'),
		('kf5-qgpgme',		'kf5-qgpgme'),
		('kf5-syndication',	'kf5-syndication'),
		('kf5-kblog',		'kf5-kblog'),
		('kf5-kimap',		'kf5-kimap'),
		('kf5-kmbox',		'kf5-kmbox'),
		('kf5-kpimidentities',	'kf5-kpimidentities'),
		('kf5-kcalutils',	'kf5-kcalutils'),
		('kf5-ktnef',		'kf5-ktnef'),
		('kf5-akonadi-kmime',	'kf5-akonadi-kmime'),
		('kf5-kalarmcal'	'kf5-kalarmcal'),
		('kf5-mailtransport',	'kf5-mailtransport'),
		('kf5-akonadi-contact',	'kf5-akonadi-contact'),
		('kf5-akonadi-calendar','kf5-akonadi-calendar'),
		('kf5-akonadi-notes',	'kf5-akonadi-notes'),
		('kf5-akonadi-socialutils',	'kf5-akonadi-socialutils'),
		('kf5-baloo',		'kf5-baloo'),
		('kf5-baloo-widgets',	'kf5-baloo-widgets'),
		('kf5-ksysguard',	'kf5-ksysguard'),
		('kf5-kscreen',		'kf5-kscreen')
	       ]

modules    = [('base',			base),
    	      ('unstable',		unstable)
             ]

f = open('dgroc.conf', 'w')

f.write('[main]\n')
f.write('username = ' + config['username'] + '\n')
f.write('email = ' + config['email'] + '\n')
f.write('copr_url = ' + config['copr_url'] + '\n')
f.write('copr_name = ' + config['copr_name'] + '\n')
f.write('upload_command = ' + config['upload_command'] + '\n')
f.write('upload_url = ' + config['upload_url'] + '\n')
f.write('no_ssl_check = ' + config['no_ssl_check'] + '\n')
f.write('spec_git_clone = ' + config['spec_git_clone'] + '\n')
f.write('spec_git_push = ' + config['spec_git_push'] + '\n')
f.write('spec_git_pub_key = ' + config['specPubKey'] + '\n')
f.write('spec_git_priv_key = ' + config['specPrivKey'] + '\n')
f.write('spec_branch = ' + config['specBranch'] + '\n')
f.write('spec_dir = ' + config['specDir'] + '\n')
f.write('log_dir = ' + config['logDir'] + '\n')
f.write('\n')
f.write('[reporting]\n')
f.write('smtp_from = ' + config['smtp_from'] + '\n')
f.write('smtp_to = ' + config['smtp_to'] + '\n')
f.write('smtp_server = ' + config['smtp_server'] + '\n')
f.write('\n')


for module in modules:
        for framework in module[1]:
                specdir = config['specDir'] + '/spec/' + module[0] + '/' + framework[1] + '/';
                f.write('[' + framework[1] + ']\n')
                f.write('spec_file = ' + specdir + framework[1] + '.spec\n')
                f.write('git_url = ' + config['git_repo'] + '/' + framework[0] + '.git\n')
                f.write('git_folder = ' + config['sourceDir'] +'/' + framework[1] + '\n')
                if len(framework) == 3:
                        f.write('git_branch = ' + framework[2] + '\n')
                if len(framework) == 4:
                        patches = []
                        for patch in framework[3]:
                                patches.append(specdir + patch)
                        f.write('patch_files = ' + (",".join(patches)) + '\n')
                f.write('\n')

f.close()

