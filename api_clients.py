import time
import discogs_client
import pylast

class ApiClients:
    def __init__(self, lastfm_username, lastfm_password, discogs_token, lastfm_key, lastfm_secret):
        
        self.discogs_client = discogs_client.Client('ScrobblerApp/0.1', user_token=discogs_token)

        password_hash = pylast.md5(lastfm_password)
        self.lastfm_network = pylast.LastFMNetwork(
            api_key=lastfm_key,
            api_secret=lastfm_secret,
            username=lastfm_username,
            password_hash=password_hash,
        )

    def get_discogs_release(self, release_id: str):
        try:
            release = self.discogs_client.release(int(release_id))
            tracklist = [
                {'position': track.position, 'title': track.title, 'duration': track.duration}
                for track in release.tracklist
            ]
            return {
                'artist': release.artists[0].name,
                'album': release.title,
                'tracks': tracklist
            }
        except Exception as e:
            print(f"Discogs data import error: {e}")
            return None

    def scrobble_to_lastfm(self, artist: str, album: str, tracks_to_scrobble: list, timestamp=None):
        
        if timestamp is None:
            current_timestamp = int(time.time())
        else:
            current_timestamp = timestamp

        for track in reversed(tracks_to_scrobble):
            track['timestamp'] = current_timestamp
            current_timestamp -= track['duration']

        print("Scrobbling...")
        for track in tracks_to_scrobble:
            print(f"  -> {artist} - {track['title']}")
            try:
                self.lastfm_network.scrobble(
                    artist=artist,
                    title=track['title'],
                    timestamp=track['timestamp'],
                    album=album
                )
            except Exception as e:
                print(f"Couldn't scrobble track: '{track['title']}': {e}")
        print("Scrobbled successfully.")