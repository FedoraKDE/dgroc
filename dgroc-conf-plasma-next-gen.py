#!/usr/bin/python
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
           'copr_name': 'plasma-next',
           #'upload_command': 'scp -i ~/.ssh/kf5-nightly.id_rsa %s dvratil@progdan.cz:~/pub/kf5/srpm/',
	   'upload_command': 'cp %s ~/pub/kde5/srpm/unstable',
           'upload_url': 'http://pub.progdan.cz/kde5/srpm/unstable/%s',
           'no_ssl_check': 'False',

           'spec_git_clone':   'https://github.com/FedoraKDE/fedora-kde-frameworks.git',
           'spec_git_push':    'git@github.com:FedoraKDE/fedora-kde-frameworks.git',
           'specBranch':       'nightly',
           'specPrivKey': '/home/dvratil/.ssh/id_rsa.dgroc',
           'specPubKey': '/home/dvratil/.ssh/id_rsa.dgroc.pub',
           'specDir':   '/home/dvratil/kf5/fedora-kde-frameworks',
           'sourceDir': '/home/dvratil/kf5/src',
           'logDir':  '/home/dvratil/kf5/logs',

           'git_repo': 'git://anongit.kde.org',

            # For reporting
           'smtp_from': 'dgroc-plasma-next@valhalla',
           'smtp_to': 'dan@progdan.cz',
           'smtp_server': 'progdan.cz',
         }

#               git repository          package name            branch          [patch1, patch2, ...]
kde5 	      =[('kde5-filesystem',	'kde5-filesystem'),
		('kde5-breeze',		'kde5-breeze'),
		('kde5-kate',		'kde5-kate'),
		('kde5-khelpcenter',	'kde5-khelpcenter'),
		('kde5-baseapps',	'kde5-baseapps'),
		('kde5-kio-extras',	'kde5-kio-extras'),
		('kde5-kwin',		'kde5-kwin'),
		('kde5-kmenuedit',	'kde5-kmenuedit'),
		('kde5-kinfocenter',	'kde5-kinfocenter'),
		('kde5-ksysguard',	'kde5-ksysguard'),
		('kde5-konsole',	'kde5-konsole'),
		('kde5-kwrited',	'kde5-kwrited'),
		('kde5-milou',		'kde5-milou'),
		('kde5-oxygen',		'kde5-oxygen'),
		('kde5-plasma-workspace','kde5-plasma-workspace'),
		('kde5-systemsettings',	'kde5-systemsettings'),
		('kde5-khotkeys',	'kde5-khotkeys'),
		('kde5-powerdevil',	'kde5-powerdevil'),
		('kde5-plasma-nm',	'kde5-plasma-nm'),
		('kde5-plasma-desktop',	'kde5-plasma-desktop')
	      ]

modules    = [('kde5',                  kde5)
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

