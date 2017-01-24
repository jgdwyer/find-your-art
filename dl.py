import requests
import urllib.request
from urllib.error import HTTPError
import xmltodict
from xml.parsers.expat import ExpatError
from bs4 import BeautifulSoup
import pandas as pd

def run_art():
    with open('./google_art_cats.txt') as f:
        catnames = f.read().splitlines()
    # Loop over artist names
    for i, catname in enumerate(catnames):
        list_of_dicts = []
        filenames = files_from_cat(catname)
        # Loop over artist works
        for filename in filenames:
            x = xml_from_file(filename)
            if x is not None:
                d = dict_from_xml(x, catname)
                list_of_dicts.append(d)
        if i==0:
            df = pd.DataFrame(list_of_dicts)
        else:
            if len(list_of_dicts) > 0:
                df = df.append(list_of_dicts, ignore_index=True)
        if i%10 == 0:
            print(i)
            df.to_pickle('./art.pickle')

def files_from_cat(catname):
    # Make url query request via api
    url = "https://commons.wikimedia.org/w/api.php?action=query" + \
          "&list=categorymembers&cmtype=file&cmtitle=Category:" + \
          catname + "&format=json&formatversion=2&cmlimit=500"
    print(url, end='\r')
    r = requests.get(url)
    # Convert return to json
    j = r.json()
    # Get filenames from json object
    filenames = []  # Initialize list
    for line in j['query']['categorymembers']:
        ti = line['title'][5:]  # First 5 characters are "File:"
        filenames.append(ti.replace(" ", "_"))  # Replace spaces with _
    return filenames


def xml_from_file(filename):
    # Make xml url from filename
    url = "https://tools.wmflabs.org/magnus-toolserver/commonsapi.php" + \
          "?image=" + filename + "&languages=en&meta&forcehtml" + \
          "&thumbwidth=400&thumbheight=400"
    try:
        r = urllib.request.urlopen(url)
    except HTTPError as e:
        print('Server error. Ignoring ' + filename)
        return None
    except UnicodeEncodeError:
        print('non-ascii characters for ' + filename + '...ignoring')
        return None
    rin = r.read()
    r.close()
    try:
        x = xmltodict.parse(rin)
    except ExpatError:
        print('xml-to-dict parsing error..skipping ' + filename)
        return None
    return x


def dict_from_xml(x, catname):
    d = init_dict()
    d['artist_name'] = catname[28:].replace("_", " ")  # stripping out "Google Art Project works by "
    # some dictionary shorthands
    try:
        xr = x['response']
        xrf = xr['file']
        d['url_to_im'] = xrf['urls']['file']
        d['url_to_descrip'] = xrf['urls']['description']
        d['url_to_thumb'] = xrf['urls']['thumbnail']
        d['width'] = int(xrf['width'])
        d['height'] = int(xrf['height'])
        # Calculate width to height ratio
        d['wh_aspect_ratio'] = float(d['width']) / float(d['height'])
        d['size'] = int(xrf['size'])
        d['date'] = xrf['date']  # string for now...can be a range or say "circa"
        d['categories'] = '||'.join(xr['categories']['category'])  # strs delimited with ||
        try:
            lic = [od['name'] for od in xr['licenses']['license']]  # list of strs
            d['licenses'] = '||'.join(lic) # strs delimited with ||
        except TypeError:
            pass
        # Extract source html - should be google art project url
        try:
            source_soup = BeautifulSoup(x['response']['file']['source'], 'lxml')
            d['source_html'] = source_soup.a['href']
            if d['source_html'][0:2] == '//':
                d['source_html'] = d['source_html'][2:]
        except TypeError:
            pass
        d['author_html'] = xrf['author']
        d['permission'] = xrf['permission']
        d['filename_spaces'] = xrf['name']
        d['filename_nospaces'] = xrf['title'][5:]
        d['uploader'] = xrf['uploader']
        d['upload_date'] = xrf['upload_date']
        d['hashcode'] = xrf['sha1']
        d['@version'] = xr['@version']
        if 'meta' in xr:
            try:
                d['meta'] = xr['meta']['item']['@name'] + xr['meta']['item']['#text']
            except TypeError:
                pass
        d['description'] = xr['description']
    except KeyError:
        pass
    return d


def init_dict():
    columns = ['artist_name',
               'url_to_im',
               'url_to_descrip',
               'url_to_thumb',
               'width',
               'height',
               'wh_aspect_ratio',
               'size',
               'date',
               'categories',
               'licenses',
               'source_html',
               'author_html',
               'permission',
               'filename_spaces',
               'filename_nospaces',
               'uploader',
               'upload_date',
               'hashcode',
               '@version',
               'meta',
               'description']
    d = dict()
    for c in columns:
        d[c] = None
    return d


def write_cats_to_list(fname, thelist):
    thefile = open(fname, 'w')
    for item in thelist:
        thefile.write('{:s}\n'.format(item))


# def init_df():
def get_all_cats(debug=False):
    t, n, p = [], [], []
    u = ''
    while True:
        t1, n1, p1, u = _get_all_cats(u)
        t = t + t1
        n = n + n1
        p = p + p1
        if debug is True:
            print(len(t))
        if u is None:
            break
    return t, n, p


def _get_all_cats(url_addon=''):
    supercategory = 'Google_Art_Project_works_by_artist'
    baseurl = 'https://commons.wikimedia.org/w/api.php?action=query&' + \
        'list=categorymembers&cmtitle=Category:' + \
        supercategory + '&cmsort=sortkey&cmdir=asc&cmlimit=500&format=json' + \
        url_addon
    r = requests.get(baseurl)
    j = r.json()
    q = j['query']['categorymembers']
    # Initialize
    # nss, pageids, titles = [], [], []
    # List comprehension on all returned queries
    nss = [item['ns'] for item in q]
    pageids = [item['pageid'] for item in q]
    titles = [item['title'] for item in q]
    if 'continue' in j:
        url_addon = '&cmcontinue=' + j['continue']['cmcontinue']
    else:
        url_addon = None
    return titles, nss, pageids, url_addon


def query(request):
    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {'continue': ''}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the last result.
        req.update(lastContinue)
        # Call API
        result = requests.get('http://commons.wikimedia.org/w/api.php', params=req).json()
        if 'error' in result:
            raise ValueError(result['error'])
        if 'warnings' in result:
            print(result['warnings'])
        if 'query' in result:
            yield result['query']
        if 'continue' not in result:
            break
        lastContinue = result['continue']
