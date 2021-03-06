from googleapiclient.errors import HttpError
from utils import write_history, COLORS as c, YT_KEY, MAX_PLAYLIST, load_playlist_name, load_playlist_file
import datetime
from PyInquirer import prompt
from googleapiclient.discovery import build
from player import play_music

youtube = build("youtube", 'v3', developerKey=YT_KEY)
global playlist_items
playlist_items = []


def load_playlist(playlistId, formatted: bool = True):
    global playlist_items
    request = youtube.playlistItems().list(
        part='id, snippet',
        maxResults=MAX_PLAYLIST,
        playlistId=playlistId
    )
    try:
        r = request.execute()
    except HttpError:
        return None
    write_history("res/usr/playlist-history.txt", datetime.datetime.now(), f"Playlist --> {playlistId}\n")
    playlist_list_dict = []
    if formatted:
        for i, item in enumerate(r['items']):
            if i % 10 == 0 and i != 50 and i != 0:
                playlist_items.append(('break', 'break', 'break'))
            snippet = item.get('snippet')
            title = snippet.get('title')
            channel = snippet.get("videoOwnerChannelTitle")
            videoId = snippet.get("resourceId").get("videoId")
            playlist_list_dict.append(
                {
                    'name': title + " -> " + channel,
                    'value': i
                }
            )
            playlist_items.append((title, videoId, channel))
        playlist_list_dict.append({'name': 'Return', 'value': 'none'})
        return playlist_list_dict
    for item in r['items']:
        playlist_list_dict.append((item.get("snippet").get("resourceId").get("videoId"),
                                   item.get("snippet").get("title"), item.get("snippet").get("videoOwnerChannelTitle")))
    return playlist_list_dict


def load_playlist_from_name(playlist_name):
    playlist = load_playlist_name(playlist_name)
    if playlist is None:
        return None
    name = playlist.get('name')
    items = playlist.get('videos')
    playlist_list_dict = []
    print(f'{c.HEADER}Playlist:{c.ENDC} {c.OKBLUE}{name}{c.ENDC}')
    for i, item in enumerate(items):
        title = item[0]
        videoId = item[1]
        channel = item[2]
        playlist_items.append((title, videoId, channel))
        playlist_list_dict.append(
            {
                'name': title + " -> " + channel,
                'value': i
            }
        )
    playlist_list_dict.append({'name': 'Return', 'value': 'none'})
    return playlist_list_dict


def list_playlists(name: str = None):
    data = load_playlist_file()
    names = []
    if name is None:
        for playlist in data:
            names.append(playlist.get("name").capitalize())
        return names
    else:
        for playlist in data:
            if playlist.get("name").lower() == name.lower():
                return "\n".join([i[0] for i in playlist.get("videos")])
        return None


def play_playlist(t):
    global playlist_items
    item = playlist_items[t:]
    break_question = [
        {
            'type': 'confirm',
            'message': 'Do you want to continue the playlist?',
            'name': 'conf',
            'default': True
        }
    ]
    count = 0
    while len(item) != 0 and count < len(item):
        if count % 10 == 0 and count != 0 and count != len(item):
            conf = prompt(break_question)['conf']
            if conf:
                count += 1
                continue
            else:
                playlist_items.clear()
                return False
        name, videoId = item.pop(count)[0] + " -> " + item.pop(count)[2], item.pop(count)[1]
        print(f'{c.HEADER}Playing:{c.ENDC} {c.OKBLUE}{name}{c.ENDC}')
        s = play_music(videoId)
        if s == 'Break':
            conf = prompt(break_question)['conf']
            if conf:
                count += 1
                continue
            else:
                playlist_items.clear()
                return False
        count += 1
    playlist_items.clear()  # Just in case if the list isn't empty
    return True
