from __future__ import unicode_literals
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import sys,threading,spotify,logging

logging.basicConfig()
logger = logging.getLogger(__name__)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'test.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()
session.login('12157628198', 'Fault#123')

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()

# Connect an audio sink
audio = spotify.AlsaSink(session)

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()

def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

def on_end_of_track(self):
    end_of_track.set()

# Register event listeners
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

# Assuming a previous login with remember_me=True and a proper logout
# session.relogin()

logged_in.wait()

track=None

@csrf_exempt
def play(request):
    try:
        global track
        if 'song' in request.GET:
            song = request.GET.get('song')
            if not track or (track.is_loaded and track.link.uri != song):
                track = session.get_track(song).load()
                session.player.load(track)
                session.player.play()
            elif session.player.state == spotify.player.PlayerState.PAUSED:
                session.player.play()
        elif session.player.state == spotify.player.PlayerState.PAUSED:
            session.player.play()

    except Exception as e:
        logger.exception(e)

    return HttpResponse(status=200)

@csrf_exempt
def pause(request):
    try:
        session.player.pause()
        return HttpResponse(status=200)
    except Exception as e:
        logger.exception(e)
