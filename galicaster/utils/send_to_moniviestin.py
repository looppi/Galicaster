# -*- coding: utf-8 -*-
import requests
from galicaster.utils.sidebyside import create_sbs
import os
from datetime import datetime


def create_sbs_video(sbs_location, sbs_layout, mp):
    audio = None  # 'camera'
    camera = screen = None
    for track in mp.getTracks():
        if track.getMimeType()[0:5] == 'audio':
            audio = track.getURI()
        else:
            if track.getFlavor()[0:9] == 'presenter':
                camera = track.getURI()
            if track.getFlavor()[0:12] == 'presentation':
                screen = track.getURI()

    create_sbs(sbs_location, camera, screen, audio, sbs_layout)


def send_to_moniviestin(mediapackage, dispatcher, logger, worker):
    sbs_layout = "sbs"

    from galicaster.core import context
    url = context.get_conf().get("moniviestin", "url")

    dispatcher.emit(
        'start-operation',
        'send-moniviestin',
        mediapackage
    )

    logger.info("Starting to send moniviestin")
    #create side-by-side video
    export_path = worker.export_path

    logger.info(
        'Executing SideBySide for MP {0}'.format(mediapackage.getIdentifier())
    )

    name = datetime.now().replace(microsecond=0).isoformat()
    sbs_location = os.path.join(export_path, name + '.mp4')
    logger.info("SBS_location: %s" % sbs_location)
    try:
        create_sbs_video(sbs_location, sbs_layout, mediapackage)
    except Exception, e:
        logger.exception("Failed to sbs", e)
        logger.info(
            "Failed to create sbs video, stopping send to moniviestin"
        )
        return

    logger.info("SBS creation successful")
    data = {
        'name': mediapackage.getIdentifier(),
        'description': mediapackage.getIdentifier(),
    }
    result = requests.post(url, data=data)
    if result.status_code != 200:
        logger.error("Error in mediapage creation: %r" % result.status_code)

    video_upload_url = result.json()['upload_url']
    logger.info(video_upload_url)
    logger.info("Created mediapage")

    files = {
        'file': open(sbs_location, 'rb')
    }
    logger.info("Created file dict")
    vupload_result = requests.post(
        video_upload_url,
        data={},
        files=files
    )
    logger.info(vupload_result.status_code)
    logger.info("Send to moniviestin seems to be successful")
    logger.debug(vupload_result.text)


    dispatcher.emit(
        'stop-operation',
        'send-moniviestin',
        mediapackage,
        True
    )
