# -*- coding: utf-8 -*-

from io import open  #
from lxml import etree
import urllib2              #
import inspect              # getfile, currentframe
import re                   #
import os                   # path.abspath, join, dirname
import urllib
import unicodedata
import json
import difflib

### Return dict value if all fields exists "" otherwise (to allow .isdigit()), avoid key errors
def Dict(var, *arg, **kwarg):  #Avoid TypeError: argument of type 'NoneType' is not iterable
    """ Return the value of an (imbricated) dictionnary, return "" if doesn't exist unless "default=new_value" specified as end argument
        Ex: Dict(variable_dict, 'field1', 'field2', default = 0)
    """
    for key in arg:
        if isinstance(var, dict) and key and key in var or isinstance(var, list) and isinstance(key, int) and 0<=key<len(var):  var = var[key]
        else:  return kwarg['default'] if kwarg and 'default' in kwarg else ""   # Allow Dict(var, tvdbid).isdigit() for example
    return kwarg['default'] if var in (None, '', 'N/A', 'null') and kwarg and 'default' in kwarg else "" if var in (None, '', 'N/A', 'null') else var
#Based on an answer by John Machin on Stack Overflow http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
def filterInvalidXMLChars(string):
    def isValidXMLChar(char):  c = ord(char);  return 0x20 <= c <= 0xD7FF or 0xE000 <= c <= 0xFFFD or 0x10000 <= c <= 0x10FFFF or c in (0x9, 0xA, 0xD)
    return filter(isValidXMLChar, string)

### natural sort function ### avoid 1 10 11...19 2 20...
def natural_sort_key(s):  return [int(text) if text.isdigit() else text for text in re.split(re.compile('([0-9]+)'), str(s).lower())]  # list.sort(key=natural_sort_key) #sorted(list, key=natural_sort_key) - Turn a string into string list of chunks "z23a" -> ["z", 23, "a"]

### Convert ISO8601 Duration format into seconds ###
def ISO8601DurationToSeconds(duration):
    def js_int(value):  return int(''.join([x for x in list(value or '0') if x.isdigit()]))  # js-like parseInt - https://gist.github.com/douglasmiranda/2174255
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
    return 3600 * js_int(match[0]) + 60 * js_int(match[1]) + js_int(match[2])

# ### Get media directory ###

def Start():
    HTTP.CacheTime = CACHE_1WEEK

def json_load(url):
    iteration = 0
    json_page = {}
    json      = {}
    while not json or Dict(json_page, 'nextPageToken') and Dict(json_page, 'pageInfo', 'resultsPerPage') !=1 and iteration<50:
        # Log.Info('{}'.format(Dict(json_page, 'pageInfo', 'resultsPerPage')))
        try:
            json_page = JSON.ObjectFromURL(url+'&pageToken='+Dict(json_page, 'nextPageToken') if Dict(json_page, 'nextPageToken') else url)
            # Log.Info('items: {}'.format(len(Dict(json_page, 'items'))))
        except Exception as e:
            json = JSON.ObjectFromString(e.content)
            raise ValueError('code: {}, message: {}'.format(Dict(json, 'error', 'code'), Dict(json, 'error', 'message')))
        if json:  json ['items'].extend(json_page['items'])
        else:     json = json_page
        iteration +=1
    # Log.Info('total items: {}'.format(len(Dict(json, 'items'))))
    return json

### Get media root folder ###
def GetLibraryRootPath(dir):
    library, root, path = '', '', ''
    for root in [os.sep.join(dir.split(os.sep)[0:x+2]) for x in range(0, dir.count(os.sep))]:
        for key in PLEX_LIBRARY.keys():
            r = key.replace(root, '')
            if len(r) == 0:
                library = PLEX_LIBRARY[key]
                path    = os.path.relpath(dir, key)
                return library, root, path
    return library, root, dir

# Agent definition
########################################################################
class YouTubeMusicAgent(Agent.Artist):
    name = 'Youtube Music'
    languages = [Locale.Language.Korean, Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang, manual):
        YOUTUBE_API_KEY = Prefs['YouTube-Agent_youtube_api_key']

        Log(''.ljust(157, '='))
        # Search for artist.
        Log('Artist search: ' + media.artist)
        if manual:
            Log('Running custom search...')
            # Added 2016.3.25
            media_name = unicodedata.normalize(
                'NFKC', unicode(media.artist)).strip()
        else:
            media_name = media.artist
        
        unquote_filename = urllib.unquote(media.filename)
        Log('[fullname]:{}'.format(os.path.dirname(unquote_filename)))

        dir                 = os.path.dirname(unquote_filename)
        library, root, path = GetLibraryRootPath(dir)
        art_dir = os.path.basename(os.path.dirname(path))
        album_dir = os.path.basename(path)

        Log.Info('[ ] dir:        "{}"'.format(dir    ))
        Log.Info('[ ] library:    "{}"'.format(library))
        Log.Info('[ ] root:       "{}"'.format(root   ))
        Log.Info('[ ] artist:     "{}"'.format(art_dir))
        Log.Info('[ ] album:      "{}"'.format(album_dir))
        
        display_name = re.sub(r'\[.*\]', '', art_dir).strip()
        media.artist = display_name
        
        array = [('YOUTUBE_REGEX_PLAYLIST', YOUTUBE_REGEX_PLAYLIST),
            ('YOUTUBE_REGEX_CHANNEL', YOUTUBE_REGEX_CHANNEL),
            ('YOUTUBE_REGEX_VIDEO', YOUTUBE_REGEX_VIDEO)]

        try:
            for regex, url in array:
                result = url.search(path)
                if result:
                    guid = result.group('id')
                    Log.Info(
                        'search() - YouTube ID found - regex: {}, youtube ID: "{}"'.format(regex, guid))
                    results.Append(MetadataSearchResult(
                        id='youtube|{}|{}'.format(guid, art_dir),
                        name=display_name, year=None, score=100, lang=Locale.Language.Korean))
                    
                    return
                else:
                    Log.Info(
                        'search() - YouTube ID not found - regex: "{}"'.format(regex))
            else:
                guid = None
        except Exception as e:
            guid = None
            Log('search() - filename: "{}" Regex failed to find YouTube id: "{}", error: "{}"'.format(filename, regex, e))
            
        

    def update(self, metadata, media, lang):
        YOUTUBE_API_KEY = Prefs['YouTube-Agent_youtube_api_key']

        Log(''.ljust(157, '='))
        temp, guid, art = metadata.id.split("|")
        # res = YOUTUBE_REGEX_PLAYLIST.search(metadata.album)
        # album_id = res.group('id') if res else ''

        Log.Info('[ ] metadata.id : "{}"'.format(metadata.id))
        
        Log.Info('[ ] temp:       "{}"'.format(temp))
        Log.Info('[ ] guid:       "{}"'.format(guid))
        Log.Info('[ ] artist:     "{}"'.format(art))
        # Log.Info('[ ] album:      "{}"'.format(metadata.album))

        channel_id = guid if guid.startswith('UC') or guid.startswith('HC') else ''
        metadata.title = re.sub(r'\[.*\]', '', art).strip()

        Log.Info('[ ] title :       "{}"'.format(metadata.title))
        
        try:
            URL_CHANNEL_DETAILS   = '{}&id={}&key={}'.format(YOUTUBE_CHANNEL_DETAILS,guid, YOUTUBE_API_KEY)
            Log.Info('[?] url: {}'.format(URL_CHANNEL_DETAILS))
            json_channel_details  = json_load(URL_CHANNEL_DETAILS)['items'][0]
        except Exception as e:  Log('exception: {}, url: {}'.format(e, guid))
        else:
            Log.Info('[?] json_channel_details: {}'.format(json_channel_details.keys()))
            Log.Info('[ ] title:       "{}"'.format(Dict(json_channel_details, 'snippet', 'title'      )))

            if Dict(json_channel_details, 'snippet', 'description'):  metadata.summary =  Dict(json_channel_details, 'snippet', 'description');
            #elif guid.startswith('PL'):  metadata.summary = 'No Playlist nor Channel summary'
            else:
                summary  = 'Channel with {} videos, '.format(Dict(json_channel_details, 'statistics', 'videoCount'     ))
                summary += '{} subscribers, '.format(Dict(json_channel_details, 'statistics', 'subscriberCount'))
                summary += '{} views'.format(Dict(json_channel_details, 'statistics', 'viewCount'      ))
                metadata.summary = filterInvalidXMLChars(summary) #or 'No Channel summary'
                Log.Info('[ ] summary:     "{}"'.format(Dict(json_channel_details, 'snippet', 'description').replace('\n', '. ')))  #

            thumb_channel = Dict(json_channel_details, 'snippet', 'thumbnails', 'medium', 'url') or Dict(json_channel_details, 'snippet', 'thumbnails', 'high', 'url')   or Dict(json_channel_details, 'snippet', 'thumbnails', 'default', 'url')
            thumb = Dict(json_channel_details, 'brandingSettings', 'image', 'bannerTvLowImageUrl' ) or Dict(json_channel_details, 'brandingSettings', 'image', 'bannerTvMediumImageUrl') \
                or Dict(json_channel_details, 'brandingSettings', 'image', 'bannerTvHighImageUrl') or Dict(json_channel_details, 'brandingSettings', 'image', 'bannerTvImageUrl'      )

            metadata.art [thumb] = Proxy.Preview(HTTP.Request(thumb).content, sort_order=1)
            Log('[ ] art:       {}'.format(thumb))
            
            metadata.posters [thumb_channel] = Proxy.Preview(HTTP.Request(thumb_channel), sort_order=1)
            Log('[ ] posters:   {}'.format(thumb_channel))


        metadata.id = unicode(metadata.id)
        # title, summary, posters, genres, similar, art

        # metadata.posters[VARIOUS_ARTISTS_POSTER] = Proxy.Media(
        #         HTTP.Request(VARIOUS_ARTISTS_POSTER))

########################################################################

class YouTubeMusicAlbumAgent(Agent.Album):
    name = 'Youtube Music'
    languages = [Locale.Language.Korean, Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang, manual):
        YOUTUBE_API_KEY = Prefs['YouTube-Agent_youtube_api_key']
        Log.Info('YouTubeMusicAlbumAgent search')
        if media.parent_metadata.id is None:
            return

        unquote_filename = urllib.unquote(media.filename)
        Log('[fullname]:{}'.format(os.path.dirname(unquote_filename)))

        dir                 = os.path.dirname(unquote_filename)
        library, root, path = GetLibraryRootPath(dir)
        art_dir = os.path.dirname(path)
        album_dir = os.path.basename(path)

        temp, guid, art = media.parent_metadata.id.split("|")
        res = YOUTUBE_REGEX_PLAYLIST.search(album_dir)
        album_id = res.group('id') if res else 'unknown'
        if album_id == 'unknown':
            album = '알수없는 앨범'
        else:     
            album = re.sub(r'\[.*\]', '', album_dir).strip()

        Log.Info('[ ] metadata.id : "{}"'.format(media.parent_metadata.id))
        
        Log.Info('[ ] temp:       "{}"'.format(temp))
        Log.Info('[ ] guid:       "{}"'.format(guid))
        Log.Info('[ ] album_id:   "{}"'.format(album_id))
        Log.Info('[ ] artist:     "{}"'.format(art))
        Log.Info('[ ] album:      "{}"'.format(album))

        # album found
        if album_id != 'unknown':
            try:
                URL_PLAYLIST_DETAILS  = '{}&id={}&key={}'.format(YOUTUBE_PLAYLIST_DETAILS, album_id, YOUTUBE_API_KEY)
                Log.Info('[ ] json_playlist_url: {}'.format(URL_PLAYLIST_DETAILS))
                json_playlist_details = json_load(URL_PLAYLIST_DETAILS)['items']
            except Exception as e:  Log('[!] json_playlist_details exception: {}, url: {}'.format(e, YOUTUBE_PLAYLIST_DETAILS.format(guid)))
            else:
                Log.Info('[?] length of json_playlist_details: {}'.format(len(json_playlist_details)))
                
                # play list to albums
                for pl in json_playlist_details:
                    Log.Info('[ ] snippet title :    {} - {}'.format(pl['snippet']['title'], pl['id']))
                    if album_id == pl['id']:
                        results.Append(MetadataSearchResult(
                            id=pl['id'],
                            name=pl['snippet']['title'],
                            lang=Locale.Language.Korean,
                            score=100))
        # unknown album
        else:
            results.Append(MetadataSearchResult(
                            id=album_id,
                            name='알수없는 앨범',
                            lang=Locale.Language.Korean,
                            score=100))
                
            

    def update(self, metadata, media, lang):
        YOUTUBE_API_KEY = Prefs['YouTube-Agent_youtube_api_key']
        guid = metadata.id
        Log.Info('[ ] album id:    {}'.format(guid))
        # Log.Info('[ ] keys:        {}'.format(inspect.getmembers(metadata)))

        # 'rating': float, 
        # 'art': 
        # 'duration': int,
        # 'genres': 
        # 'title': str, 
        # 'rating_count':int 
        # 'collections':
        # 'available_at': 
        # 'tags': 
        # 'audience_rating_image': str
        # 'rating_image': 
        # 'producers': oo
        # 'audience_rating': 
        # 'tracks': 
        # 'studio': str 
        # 'posters': 
        # 'originally_available_at': 
        # 'countries': 
        # 'title_sort': 
        # 'original_title': 
        # 'summary': 
        # 'reviews': 
        # 'artist':
        
        # playlist exists
        if guid != 'unknown':
            Log.Info('[?] json_playlist_details')
            try:
                URL_PLAYLIST_DETAILS  = '{}&id={}&key={}'.format(YOUTUBE_PLAYLIST_DETAILS, guid, YOUTUBE_API_KEY)
                json_playlist_details = json_load(URL_PLAYLIST_DETAILS)['items'][0]
            except Exception as e:  Log('[!] json_playlist_details exception: {}, url: {}'.format(e, YOUTUBE_PLAYLIST_DETAILS.format(guid)))
            else:
                Log.Info('[?] json_playlist_details: {}'.format(json_playlist_details.keys()))
                
                # title
                metadata.title   = filterInvalidXMLChars(Dict(json_playlist_details, 'snippet', 'title'))
                Log.Info('[ ] title:      "{}"'.format(metadata.title))

                # summary
                if Dict(json_playlist_details, 'snippet', 'description'):
                    metadata.summary = Dict(json_playlist_details, 'snippet', 'description')
                
                # posters
                if Dict(json_playlist_details, 'snippet', 'thumbnails', 'standard', 'url'):
                    poster_url = Dict(json_playlist_details, 'snippet', 'thumbnails', 'standard', 'url')
                    Log.Info('[ ] poster:      "{}"'.format(poster_url))
                    metadata.posters[poster_url] = Proxy.Preview(HTTP.Request(poster_url), sort_order=1)
        
        # only video(Unknown playlist)
        else:
            Log.Info('[ ] unknown album')



########################################################################
VARIOUS_ARTISTS_POSTER = 'http://userserve-ak.last.fm/serve/252/46209667.png'

### Variables ###
YOUTUBE_API_BASE_URL = 'https://www.googleapis.com/youtube/v3/'

YOUTUBE_VIDEO_SEARCH = YOUTUBE_API_BASE_URL + 'search?&maxResults=1&part=snippet'                                        # &q=string             &key=apikey
YOUTUBE_VIDEO_DETAILS = YOUTUBE_API_BASE_URL + 'videos?part=snippet,contentDetails,statistics'                            # &id=string            &key=apikey
# &id=string            &key=apikey
YOUTUBE_PLAYLIST_DETAILS = YOUTUBE_API_BASE_URL + 'playlists?part=snippet,contentDetails'
YOUTUBE_PLAYLIST_ITEMS = YOUTUBE_API_BASE_URL + 'playlistItems?part=snippet&maxResults=50'                                 # &playlistId=string    &key=apikey
YOUTUBE_CHANNEL_DETAILS = YOUTUBE_API_BASE_URL + 'channels?part=snippet%2CcontentDetails%2Cstatistics%2CbrandingSettings'   # &id=string            &key=apikey
YOUTUBE_CHANNEL_ITEMS = YOUTUBE_API_BASE_URL + 'search?order=date&part=snippet&type=video&maxResults=50'                  # &channelId=string     &key=apikey
YOUTUBE_CHANNEL_PLAYLISTS = YOUTUBE_API_BASE_URL + ''

# https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId=UCqXwKu6dKobXEQFhdKtiJLQ&key=AIzaSyAhv5XYUsrF-kfkjhQgQ1IFqbkFS9f9RpM

YOUTUBE_REGEX_VIDEO = Regex('\[(?:youtube\-)?(?P<id>[a-z0-9\-_]{11})\]', Regex.IGNORECASE) # https://regex101.com/r/BFKkGc/3/
YOUTUBE_REGEX_PLAYLIST = Regex('\[(?:youtube\-)?(?P<id>PL[^\[\]]{16}|PL[^\[\]]{32}|OL[^\[\]]{39}|UU[^\[\]]{22}|FL[^\[\]]{22}|LP[^\[\]]{22}|RD[^\[\]]{22}|UC[^\[\]]{22}|HC[^\[\]]{22})\]',  Regex.IGNORECASE)  # https://regex101.com/r/37x8wI/2
YOUTUBE_REGEX_CHANNEL = Regex('\[(?:youtube\-)?(?P<id>UC[a-zA-Z0-9\-_]{22}|HC[a-zA-Z0-9\-_]{22})\]')  # https://regex101.com/r/IKysEd/1
YOUTUBE_CATEGORY_ID      = {'1': 'Film & Animation'     ,  '2': 'Autos & Vehicles'     , '10': 'Music'                , '15': 'Pets & Animals',
                              '17': 'Sports',                '18': 'Short Movies',          '19': 'Travel & Events',       '20': 'Gaming',
                              '21': 'Videoblogging',         '22': 'People & Blogs',        '23': 'Comedy',                '24': 'Entertainment',
                              '25': 'News & Politics',       '26': 'Howto & Style',         '27': 'Education',             '28': 'Science & Technology',
                              '29': 'Nonprofits & Activism', '30': 'Movies',                '31': 'Anime/Animation',       '32': 'Action/Adventure',
                              '33': 'Classics',              '34': 'Comedy',                '35': 'Documentary',           '36': 'Drama',
                              '37': 'Family',                '38': 'Foreign',               '39': 'Horror',                '40': 'Sci-Fi/Fantasy',
                              '41': 'Thriller',              '42': 'Shorts',                '43': 'Shows',                 '44': 'Trailers'
                              }
PlexRoot                 = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", "..", "..", ".."))
PLEX_LIBRARY_URL         = "http://127.0.0.1:32400/library/sections/"    # Allow to get the library name to get a log per library https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
PLEX_LIBRARY             = {}

### Plex Library XML ###
Log.Info("Library: "+PlexRoot)  #Log.Info(file)
if os.path.isfile(os.path.join(PlexRoot, "X-Plex-Token.id")):
    Log.Info("'X-Plex-Token.id' file present")
    token_file=Data.Load(os.path.join(PlexRoot, "X-Plex-Token.id"))
    if token_file:  PLEX_LIBRARY_URL += "?X-Plex-Token=" + token_file.strip()  #Log.Info(PLEX_LIBRARY_URL) ##security risk if posting logs with token displayed
try:
    library_xml = etree.fromstring(urllib2.urlopen(PLEX_LIBRARY_URL).read())
    for library in library_xml.iterchildren('Directory'):
        for path in library.iterchildren('Location'):
            PLEX_LIBRARY[path.get("path")] = library.get("title")
            Log.Info( path.get("path") + " = " + library.get("title") )
except Exception as e:  Log.Info("Place correct Plex token in X-Plex-Token.id file in logs folder or in PLEX_LIBRARY_URL variable to have a log per library - https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token" + str(e))
