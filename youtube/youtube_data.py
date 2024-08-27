import urllib
import json
import isodate
import numpy as np
from youtube_transcript_api import YouTubeTranscriptApi


# channels
# https://www.youtube.com/@townoffortfairfield39/videos

# playlists
# https://www.youtube.com/playlist?list=PLTnWtZMTeHrPFsC4tDpzMFerszY_EQlvH
# https://www.youtube.com/playlist?list=PLbIrbnT9Im6H3QXtoI8hpSqTcf9W-yl5T



def get_all_video_in_channel(api_key, channel_id, max_results=70, part="snippet,id"):
    """function to get video urls + metadata such as statistics from a youtube channel
    -returns the response and also a list of items of the videos"""
    
    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/search?'

    first_url = f"{base_search_url}key={api_key}&channelId={channel_id}&part={part}&order=date&maxResults={max_results}"
    

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            if i['id']['kind'] == "youtube#video":
                video_link = base_video_url + i['id']['videoId']
                i["video_link"] = video_link
                video_links.append(i)

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break

    return resp, video_links



def chunks(l, n):
    """Yield n number of sequential chunks from l."""
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d + 1) * (i if i < r else r) + d * (0 if i < r else i - r)
        yield l[si:si + (d + 1 if i < r else d)]


def get_videos_from_list(api_key, video_id_list, max_results=70, part="id,statistics,contentDetails"):
    
    """takes in a list of video ids and retrieves metadata and statistics about the items"""
    
    
    base_search_url = 'https://www.googleapis.com/youtube/v3/videos?'
    video_id = ",".join(video_id_list)

    first_url = f"{base_search_url}key={api_key}&id={video_id}&part={part}&order=date&maxResults={max_results}"



    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)

        for i in resp['items']:
            new_i = {}
            
            if i['kind'] == "youtube#video":
                new_i["videoId"] = i["id"]
                s = isodate.parse_duration(i["contentDetails"]["duration"]).total_seconds()
                new_i["duration_seconds"] = s
                new_i["duration_approx_minutes"] = np.round(s/60)
                for k, v in i["statistics"].items():
                    new_i[k] =v
                
                video_links.append(new_i)
        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break

    return resp, video_links


def get_transcript_from_video_id(video_id):
    """retrieve the available transcript from video id - returns only text"""
    transcript_ = " ".join(v.get("text", "") for v in YouTubeTranscriptApi.get_transcript(video_id=video_id))
    return transcript_

def get_all_video_in_playlist(api_key, playlist_id, max_results=70, part="snippet,id"):
    """function to get video urls from a playlist -- must use one playlist id at a time"""
    
    base_video_url = 'https://www.youtube.com/watch?v='
    base_search_url = 'https://www.googleapis.com/youtube/v3/playlistItems?'

    first_url = f"{base_search_url}key={api_key}&playlistId={playlist_id}&part={part}&order=date&maxResults={max_results}"
    

    video_links = []
    url = first_url
    while True:
        inp = urllib.request.urlopen(url)
        resp = json.load(inp)
        for i in resp['items']:
            if i["snippet"]["resourceId"]["kind"] == "youtube#video":
                video_link = base_video_url + i["snippet"]["resourceId"]["videoId"]
                i["video_link"] = video_link
                i["video_id"] =  i["snippet"]["resourceId"]["videoId"]
                video_links.append(i)

        try:
            next_page_token = resp['nextPageToken']
            url = first_url + '&pageToken={}'.format(next_page_token)
        except:
            break

    return resp, video_links
