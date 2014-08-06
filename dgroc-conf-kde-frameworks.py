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
           'copr_name': 'kde-frameworks',
           'upload_command': 'cp %s /home/dvratil/pub/kf5/srpm/5.0.0',
           'upload_url': 'http://pub.progdan.cz/kf5/srpm/5.0.0/%s',
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
base       = [('extra-cmake-modules',	'extra-cmake-modules')
             ]

# Tier 1 Frameworks
tier1      = [('kf5-attica',                'kf5-attica'),
              ('kf5-karchive',              'kf5-karchive'),
              ('kf5-kcodecs',               'kf5-kcodecs'),
              ('kf5-kconfig',               'kf5-kconfig'),
              ('kf5-kcoreaddons',           'kf5-kcoreaddons'),
              ('kf5-kdbusaddons',           'kf5-kdbusaddons'),
	      ('kf5-kdnssd',	   	    'kf5-kdnssd'),
              ('kf5-kglobalaccel',          'kf5-kglobalaccel'),
              ('kf5-kguiaddons',            'kf5-kguiaddons'),
              ('kf5-ki18n',                 'kf5-ki18n'),
              ('kf5-kidletime',             'kf5-kidletime'),
              ('kf5-kimageformats',         'kf5-kimageformats'),
              ('kf5-kitemmodels',           'kf5-kitemmodels'),
              ('kf5-kitemviews',            'kf5-kitemviews'),
              ('kf5-kjs',                   'kf5-kjs'),
              ('kf5-kplotting',             'kf5-kplotting'),
              ('kf5-kwidgetsaddons',        'kf5-kwidgetsaddons'),
              ('kf5-kwindowsystem',         'kf5-kwindowsystem'),
              ('kf5-solid',                 'kf5-solid'),
              ('kf5-sonnet',                'kf5-sonnet'),
              ('kf5-threadweaver',          'kf5-threadweaver')
        ]

# Tier 2 Frameworks
tier2      = [('kf5-kauth',                 'kf5-kauth'),
              ('kf5-kcompletion',           'kf5-kcompletion'),
              ('kf5-kcrash',                'kf5-kcrash'),
              ('kf5-kdoctools',             'kf5-kdoctools'),
              ('kf5-kjobwidgets',           'kf5-kjobwidgets'),
	      ('kf5-kpty',		    'kf5-kpty'),
	      ('kf5-kunitconversion',	    'kf5-kunitconversion')
        ]

# Tier 3 Frameworks (order matters!)
tier3      = [('kf5-kconfigwidgets',        'kf5-kconfigwidgets'),
              ('kf5-kiconthemes',           'kf5-kiconthemes'),
              ('kf5-kservice',              'kf5-kservice'),
              ('kf5-knotifications',        'kf5-knotifications'),
              ('kf5-ktextwidgets',          'kf5-ktextwidgets'),
              ('kf5-kxmlgui',               'kf5-kxmlgui'),
              ('kf5-kbookmarks',            'kf5-kbookmarks'),
              ('kf5-kcmutils',              'kf5-kcmutils'),
              ('kf5-kwallet',               'kf5-kwallet'),
              ('kf5-kio',                   'kf5-kio'),
              ('kf5-kdeclarative',          'kf5-kdeclarative'),
              ('kf5-kparts',                'kf5-kparts'),
	      ('kf5-ktexteditor',	    'kf5-ktexteditor'),
              ('kf5-kdewebkit',             'kf5-kdewebkit'),
              ('kf5-kinit',                 'kf5-kinit'),
              ('kf5-kded',                  'kf5-kded'),
              ('kf5-kjsembed',              'kf5-kjsembed'),
              ('kf5-kdesignerplugin',       'kf5-kdesignerplugin'),
              ('kf5-kdesu',                 'kf5-kdesu'),
              ('kf5-knotifyconfig',         'kf5-knotifyconfig'),
              ('kf5-kross',                 'kf5-kross'),
              ('kf5-knewstuff',             'kf5-knewstuff'),
              ('kf5-kemoticons',            'kf5-kemoticons'),
              ('kf5-kmediaplayer',          'kf5-kmediaplayer'),
              ('kf5-kactivities',           'kf5-kactivities'),
              ('kf5-plasma-framework',      'kf5-plasma'),
              ('kf5-krunner',               'kf5-krunner')
        ]

# Tier 4 Frameworks
tier4      = [('kf5-frameworkintegration',  'kf5-frameworkintegration'),
              ('kf5-kapidox',               'kf5-kapidox'),
              ('kf5-kdelibs4support',       'kf5-kdelibs4support'),
              ('kf5-khtml',                 'kf5-khtml')
        ]

modules    = [('base',                  base),
              ('tier1',                 tier1),
              ('tier2',                 tier2),
              ('tier3',                 tier3),
              ('tier4',                 tier4),
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

