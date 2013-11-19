# -*- coding: utf-8 -*-
from galicaster.core import context
import requests


def init():
    try:
        dispatcher = context.get_dispatcher()
        dispatcher.connect('stop-operation', send_to_moniviestin)
    except ValueError:
        pass


def send_to_moniviestin(dispatcher, operation, mediapackage, success):
    if operation == "ingest":
        conf = context.get_conf()
        url = conf.get("moniviestin", "url")
        print url
        print dispatcher
        print operation
        print mediapackage
        videos = mediapackage.getTracks("presenter/source")
        for video in videos:
            print video
        print success
