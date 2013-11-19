# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       test/plugins/cleanstale
#
# Copyright (c) 2012, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of 
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California, 94105, USA.

"""
Test Send to Moniviestin functionality
"""
from shutil import rmtree
from tempfile import mkdtemp, mkstemp
import datetime

from unittest import TestCase
from os import path

from galicaster.core.conf import Conf
from galicaster.mediapackage import repository
from galicaster.mediapackage import mediapackage

from galicaster.plugins import send_to_moniviestin

from galicaster.core import context
from tests import get_resource


class TestMoniviestin(TestCase):

    baseDir = get_resource('mediapackage')
    path_track1 = path.join(baseDir, 'SCREEN.mpeg')
    path_track2 = path.join(baseDir, 'CAMERA.mpeg')
    path_catalog = path.join(baseDir, 'episode.xml')
    path_attach = path.join(baseDir, 'attachment.txt')
    path_other = path.join(baseDir, 'manifest.xml')
    path_gc = path.join(baseDir, 'galicaster.xml')

    def setUp(self):
        self.tmppath = mkdtemp()

        repo = repository.Repository(self.tmppath)
        context.set('repository', repo)

        conf = Conf()
        context.set('conf', conf)
        
    def tearDown(self):
        rmtree(self.tmppath)

    def create_mediapackage(self):
        now = datetime.datetime.utcnow()

        mp = mediapackage.Mediapackage(
            identifier="5",
            title='MP#5',
            date=(now + datetime.timedelta(days=30))
        )
        mp.add(mediapackage.Track(
            uri=self.path_track1,
            duration=532,
            flavor="presentation/source",
            mimetype="video/mpeg")
        )
        mp.add(mediapackage.Track(
            uri=self.path_track2,
            duration=532,
            flavor="presenter/source",
            mimetype="video/mpeg")
        )
        mp.add(mediapackage.Catalog(
            uri=self.path_catalog,
            flavor="dublincore/episode",
            mimetype="text/xml")
        )
        mp.add(mediapackage.Catalog(
            uri=self.path_gc,
            flavor="galicaster",
            mimetype="text/xml")
        )
        return mp

    def test_send_to_moniviestin_plugin(self):
        dispatcher = context.get_dispatcher()
        repo = context.get_repository()
        conf = context.get_conf()
        conf.set("moniviestin", "url", "http://yska.psy.jyu.fi:8080/uliuli")

        mp = self.create_mediapackage()
        repo.add(mp)
        send_to_moniviestin.init()

        self.assertEqual(len(repo), 1)
        dispatcher.emit('stop-operation', 'ingest', mp, True)
        self.assertEqual(len(repo), 1)
        dispatcher.emit('stop-operation', 'ingest', mp, False)
        self.assertEqual(len(repo), 1)
