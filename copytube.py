"""CopyTube's main module.

This module contains all the functionality of CopyTube allowing a user to copy
a public playlist of up to 195 videos (due to API quota restrictions) to a
private playlist on their own channel after configuring their own API key and
client_secret file through YouTube's Data V3 API.

"""

import os
from typing import Any, List, Dict
from urllib.parse import urlparse, parse_qs
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import config

scopes: List[str] = ["https://www.googleapis.com/auth/youtube.force-ssl"]
"""List[str]: Scope of requests to be made by CopyTube.

The scope for requests was determined from this source,
https://developers.google.com/youtube/v3/docs/playlistItems/insert,
under the section, Authorization.
"""


def main():

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name: str = "youtube"
    api_version: str = "v3"

    header: str = """
 ######   #######  ########  ##    ## ######## ##     ## ########  ######## 
##    ## ##     ## ##     ##  ##  ##     ##    ##     ## ##     ## ##       
##       ##     ## ##     ##   ####      ##    ##     ## ##     ## ##       
##       ##     ## ########     ##       ##    ##     ## ########  ######   
##       ##     ## ##           ##       ##    ##     ## ##     ## ##       
##    ## ##     ## ##           ##       ##    ##     ## ##     ## ##       
 ######   #######  ##           ##       ##     #######  ########  ######## 


        """

    print(header)

    print("With a valid YouTube playlist url, CopyTube can copy a public playlist of up to 195 videos.")

    # Request URL from user
    url_input: str = input('Enter playlist URL: ')

    # URL validation
    while not valid_input(url_input):
        # Reenter url
        print(url_input, 'is not a valid youtube playlist\n')
        url_input = input('Please enter a valid url or q to quit: ')

    credentials = get_credentials(config.CLIENT_SECRETS_FILE)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials,
        developerKey=config.DEVELOPER_KEY)

    id: str = get_playlist_id(url_input)

    information = get_song_ids(youtube, id) # Dict[str, List[str], str, str] 
    playlist_title: str = information['title']
    song_ids: List[str] = information['songs']

    # Create new playlist
    new_playlist_id: str = create_new_playlist(youtube, playlist_title)

    # Add videos to new playlist
    add_videos_to_playlist(youtube, new_playlist_id, song_ids)


def valid_input(url_to_check: str) -> bool:
    """Checks for valid URL input from user.

    Checks for a quit signal or a YouTube URL with a 'list' query parameter.

    Parameters
    ----------
    url_to_check : str
        String containing the URL input by the user.
    
    Returns
    -------
    bool
        True, if the URL is YouTube URL with a 'list' parameter. False,
        otherwise. If the user inputs the quit signal 'q', the program exits.

    """
    if url_to_check == 'q':
        sys.exit()

    else:
        result = urlparse(url_to_check)

        if ('youtube.com' not in result.netloc) and ('youtube.com' not in result.path):
            return False

        if not ('list' in parse_qs(result.query).keys()):
            return False

        return True


def get_credentials(secret: str) -> Any:
    """Obtains credentials necessary to interact with YouTube's API

    Parameters
    ----------
    secret : str
        String containing the file name of the client secret JSON file
    
    Returns
    -------
    Instance
        Credentials instance for use with the YouTube API client

    """
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        secret, scopes)

    return flow.run_console()


def get_playlist_id(playlist_url: str) -> str:
    """Retrieves ID of playlist from URL provided using a URL parser.

    Parameters
    ----------
    playlist_url : str
        String of URL that points to a YouTube playlist
    
    Returns
    -------
    str
        String of the playlist ID
    
    """
    parse_result: Any = urlparse(playlist_url)
    queries = parse_qs(parse_result.query)

    return queries['list'][0]


def create_new_playlist(client: Any, title: str) -> str:
    """Creates a new playlist on the user's YouTube account.

    Inserts a playlist into the user's YouTube account with the name following
    the format: <playlist to be copied title>-Copy

    Parameters
    ----------
    client : Any
        Instance of YouTube API client to make requests through
    title : str
        Title of the playlist to be copied
    
    Returns
    -------
    str
        String of the new playlist's ID

    """
    request = client.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title + '-Copy',
                "description": "Copied " + title,
                "tags": [
                    "sample playlist",
                    "API call",
                    "MUSIC"
                ],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        })

    response = request.execute()

    return response['id']


def get_song_ids(client: Any, playlist_id: str) -> Dict[str, Any]:
    """Retrieves a list of the song IDs in a YouTube playlist

    Parameters
    ----------
    client : Any
        YouTube API client to make requests through
    playlist_id : str
        Playlist ID of the YouTube playlist to retrieve song IDs from
    
    Returns
    -------
    Dict[str: Any]
        Returns a dictionary containing the following information:

            {
                'songs': List of song IDs,
                'title': Title of playlist to be copied
            }
    
    """
    curr_page: str = ""
    playlist_title: str = ""
    song_ids: List[str] = []

    # Requests playlist information and retrieves video IDs
    while True:

        # Building request
        request = client.playlistItems().list(
            part="contentDetails, snippet",
            playlistId=playlist_id,
            pageToken=curr_page,
            maxResults=50
        )
        response = request.execute()

        playlist_title = response['items'][0]['snippet']['channelTitle']

        # Adding video IDs to songIDs list
        for video in response['items']:
            song_ids.append(video['contentDetails']['videoId'])

        # Checking for last page
        if 'nextPageToken' not in response:
            break

        curr_page = response['nextPageToken']

    info = {
        'songs': song_ids,
        'title': playlist_title
    }

    return info


def add_videos_to_playlist(client: Any, playlist_id: str, songs: List[str]):
    """Inserts videos from list to new playlist.

    Loops through the list of song IDs obtained and uses the YouTube API client
    to insert the songs into the newly created playlist.

    Parameters
    ----------
    client : Any
        YouTube API client to make requests through
    playlist : str
        String of the new playlist ID
    songs : List[str]
        List of song IDs to be added to the new playlist

    """
    counter = 0
    new_playlist_length = min(195, len(songs))

    while counter < new_playlist_length:
        request = client.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "position": 0,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": songs[counter]
                    }
                }
            }
        )

        request.execute()

        printProgressBar(counter, new_playlist_length)

        counter += 1

    # Check for playlist private
    printProgressBar(counter, new_playlist_length)

    print(counter, " songs added to new playlist at www.youtube.com/playlist?list=", playlist_id, sep="")


# Print iterations progress
# Source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, 
    length=100, fill='█', printEnd="\r"):
    """Progress bar that prints progress of songs added to new playlist.
    
    Source of progress bar can be found here:
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    
    Parameters
    ----------
    iteration : int
        current iteration
    total : int
        total iterations
    prefix : str, optional
        prefix string
    suffix : str, optional
        suffix string
    decimals : int, optional
        positive number of decimals in percent complete
    length : int, optional
        character length of bar
    fill : str, optional
        bar fill character
    printEnd : str, optional
        end character (e.g. "\\r", "\\r\\n")

    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == "__main__":
    main()
