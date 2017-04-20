
# coding: utf-8

# This notebook will attempt to get song information for the artists in the `ARTISTS` list using the [Genius API](https://docs.genius.com/). For every song it finds it will write out a CSV file that includes some of the metadata, and an external text file that contains the lyrics for the song.
# 
# To use the notebook you will need to set `GENIUS_ACCESS_TOKEN` in your environment before starting Jupyter. To easily get your token go over to the [Genius API documentation](https://docs.genius.com/) and click on the *Authenticate with the Docs App to try* button. This should result in you seeing your key displayed in the page next to *Authorization: Bearer*. If you don't want to set it in your environment you can always put it inline in the notebook.

# In[1]:

import os
import re
import bs4
import csv
import json
import time
import requests


# In[2]:

ARTISTS = [
    'The Roots',
    'Eve',
    'DJ Jazzy Jeff & The Fresh Prince',
    'Ludacris',
    'T.I.',
    'Kanye West',
    'Chance the Rapper',
    'Common',
    'Gucci Mane',
    'Migos',
    'OutKast',
    'Twista',
    'Crucial Conflict',
    'Lupe Fiasco',
    'Digital Underground',
    '2Pac',
    'Trouble Funk'
]


# Create an HTTP session using the `GENIUS_ACCESS_TOKEN` that is set in the environment.

# In[3]:

http = requests.Session()
http.headers.update({'Authorization': 'Bearer {0}'.format(os.environ['GENIUS_ACCESS_TOKEN'])})


# `get_artist_songs` will get all the song metadata and lyrics for a given artist name

# In[4]:

def get_artist_songs(name, primary=False):
    artist_id = get_artist_id(name)
    for song in get_songs(artist_id, primary):
        yield song


# `get_artist_id` will get the Genius identifier for a given artist name

# In[5]:

def get_artist_id(name):
    page = 1
    while True:
        r = http.get('https://api.genius.com/search', params={'q': name, 'page': page})
        if r.status_code != 200:
            return None
        for hit in r.json()['response'].get('hits', []):
            if hit['result']['primary_artist']['name'].lower() == name.lower():
                return hit['result']['primary_artist']['id']
        page += 1
    return None


# `get_songs` will go and get all the songs and lyrics for a given artist id. When the `primary` parameter is set to `True` only songs where the artist is the primary artist will be returned.

# In[6]:

def get_songs(artist_id, primary=False):
    page = 1
    while True:
        r = http.get('https://api.genius.com/artists/{0}/songs'.format(artist_id), params={'page': page})
        resp = r.json()['response']
        if 'songs' in resp and len(resp['songs']) != 0:
            for song in resp['songs']:
                if song['primary_artist']['id'] == artist_id or not primary:
                    yield get_song(song['id'])
        else:
            return
        page += 1


# `get_song` will fetch the metadata for a particular song using the song identifier, and also get the lyrics for that song.

# In[7]:

def get_song(song_id):
    r = http.get('https://api.genius.com/songs/{0}'.format(song_id))
    song = r.json()['response'].get('song')
    song['lyrics'] = get_lyrics(song['url'])
    return song


# In[8]:

def get_lyrics(url):
    doc = bs4.BeautifulSoup(requests.get(url).text, 'lxml')
    return [line.text.strip() for line in doc.select(".lyrics a")]


# In[9]:

def slug(s):
    return re.sub("[/ ,]", '-', s)


# `write_lyrics` will write the lyrics for a song to the filesystem using the artist name and the song title to determine the filename.

# In[1]:

def write_lyrics(song):
    if not song['lyrics']:
        return
    dir_name = "lyrics/" + song['primary_artist']['name']
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    filename = str(song['id']) + '-' + slug(song['title']) + '.txt'
    fh = open(os.path.join(dir_name, filename), 'w')
    for line in song['lyrics']:
        fh.write(line + "\n")
    fh.close()


# In[25]:

def samples(song):
    artists = []
    for rel in song['song_relationships']:
        if rel['type'] == 'samples':
            for sampled_song in rel['songs']:
                artists.append(sampled_song['primary_artist']['name'])
    return artists
            


# This is where all the work is coordinated. For each artist we go get the song metadata and write it to a CSV. In addition the lyrics for each song are written to the filesystem as a separate file.

# In[ ]:

fh = open('songs.csv', 'w')
songs_file = csv.writer(fh)
songs_file.writerow(["ID", "Title", "Artist", "URL", "Producers", "Featured Artists"])

for artist_name in ARTISTS:
    for song in get_artist_songs(artist_name, primary=True):
        print(artist_name, song['title'])
        producer_artists = ','.join([p['name'] for p in song['producer_artists']])
        featured_artists = ','.join([f['name'] for f in song['featured_artists']])
        sampled_artists = ','.join(samples(song))
        songs_file.writerow([
            song['id'],
            song['title'],
            song['primary_artist']['name'],
            song['url'],
            producer_artists,
            featured_artists,
            sampled_artists,
        ])
        write_lyrics(song)
        time.sleep(0.25)

fh.close()

