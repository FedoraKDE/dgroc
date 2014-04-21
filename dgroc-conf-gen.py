#!/bin/python
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
           'copr_name': 'kde-frameworks-nightly',
           'upload_command': 'scp -i ~/.ssh/kf5-nightly.id_rsa %s dvratil@progdan.cz:~/pub/kf5/srpm/nightly',
           'upload_url': 'http://pub.progdan.cz/kf5/srpm/nightly/%s',
           'no_ssl_check': 'False',

           'spec_git_clone':   'https://github.com/FedoraKDE/fedora-kde-frameworks.git',
           'spec_git_push':    'git@github.com:FedoraKDE/fedora-kde-frameworks.git',
           'specBranch':       'nightly',
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
base       = [#('libmm-qt',              'libmm-qt5'),
              #('libnm-qt',              'libnm-qt5'),
              ('polkit-qt-1',           'polkit-qt5',           'qt5',          ['Doxyfile'])
             ]

# Tier 1 Frameworks
tier1      = [('attica',                'kf5-attica'),
              ('karchive',              'kf5-karchive'),
              ('kcodecs',               'kf5-kcodecs'),
              ('kconfig',               'kf5-kconfig'),
              ('kcoreaddons',           'kf5-kcoreaddons'),
              ('kdbusaddons',           'kf5-kdbusaddons'),
              ('kglobalaccel',          'kf5-kglobalaccel'),
              ('kguiaddons',            'kf5-kguiaddons'),
              ('kidletime',             'kf5-kidletime'),
              ('kimageformats',         'kf5-kimageformats'),
              ('kitemmodels',           'kf5-kitemmodels'),
              ('kitemviews',            'kf5-kitemviews'),
              ('kjs',                   'kf5-kjs'),
              ('kplotting',             'kf5-kplotting'),
              ('kwidgetsaddons',        'kf5-kwidgetsaddons',   'master',       ['kwidgetsaddons-button-box-access.patch']),
              ('kwindowsystem',         'kf5-kwindowsystem'),
              ('solid',                 'kf5-solid'),
              ('sonnet',                'kf5-sonnet'),
              ('threadweaver',          'kf5-threadweaver'),
              ('kf5umbrella',           'kf5-umbrella'),
              ('libmm-qt',              'kf5-modemmanagerqt')
        ]

# Tier 2 Frameworks
tier2      = [('kauth',                 'kf5-kauth'),
              ('kcompletion',           'kf5-kcompletion'),
              ('kcrash',                'kf5-kcrash',           'master',       ['kcrash-find-drkonqi-in-path.patch']),
              ('kdnssd',                'kf5-kdnssd'),
              ('kdoctools',             'kf5-kdoctools',        'master',       ['kdoctools-update.patch']),
              ('ki18n',                 'kf5-ki18n'),
              ('kjobwidgets',           'kf5-kjobwidgets'),
              ('libnm-qt',              'kf5-networkmanagerqt')
        ]

# Tier 3 Frameworks (order matters!)
tier3      = [('kconfigwidgets',        'kf5-kconfigwidgets'),
              ('kiconthemes',           'kf5-kiconthemes'),
              ('kservice',              'kf5-kservice'),
              ('knotifications',        'kf5-knotifications'),
              ('ktextwidgets',          'kf5-ktextwidgets'),
              ('kxmlgui',               'kf5-kxmlgui'),
              ('kbookmarks',            'kf5-kbookmarks'),
              ('kcmutils',              'kf5-kcmutils'),
              ('kio',                   'kf5-kio',              'master',       ['kio-remove-public-dependencies.patch']),
              ('kdeclarative',          'kf5-kdeclarative'),
              ('kparts',                'kf5-kparts'),
              ('kwallet',               'kf5-kwallet'),
              ('kdewebkit',             'kf5-kdewebkit'),
              ('kinit',                 'kf5-kinit',            'master',       ['kinit-respect-env-paths.patch']),
              ('kded',                  'kf5-kded'),
              ('kjsembed',              'kf5-kjsembed'),
              ('kunitconversion',       'kf5-kunitconversion'),
              ('kdesignerplugin',       'kf5-kdesignerplugin'),
              ('kpty',                  'kf5-kpty'),
              ('kdesu',                 'kf5-kdesu'),
              ('knotifyconfig',         'kf5-knotifyconfig'),
              ('kross',                 'kf5-kross'),
              ('knewstuff',             'kf5-knewstuff'),
              ('kemoticons',            'kf5-kemoticons'),
              ('kmediaplayer',          'kf5-kmediaplayer'),
              ('kactivities',           'kf5-kactivities'),
              ('plasma-framework',      'kf5-plasma'),
              ('krunner',               'kf5-krunner')
        ]

# Tier 4 Frameworks
tier4      = [('frameworkintegration',  'kf5-frameworkintegration'),
              ('kapidox',               'kf5-kapidox'),
              ('kdelibs4support',       'kf5-kdelibs4support'),
              ('kfileaudiopreview',     'kf5-kfileaudiopreview'),
              ('khtml',                 'kf5-khtml')
        ]


# Workspaces & Applications
kde5       = [('kde-workspace',         'kde5-workspace'),
              ('kde-runtime',           'kde5-runtime',         'frameworks'),
              ('konsole',               'kde5-konsole',         'frameworks')
        ]


modules    = [('base',                  base),
              ('tier1',                 tier1),
              ('tier2',                 tier2),
              ('tier3',                 tier3),
              ('tier4',                 tier4),
              ('kde5',                  kde5)
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

