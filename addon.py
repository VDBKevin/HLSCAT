# HLSCAT

import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import re

try: # PYTHON 3
    from urllib.request import urlopen
    from urllib.parse import unquote
    from urllib.error import HTTPError
    from urllib.error import URLError
except ImportError: # PYTHON 2
    from urllib import urlopen
    from urllib import unquote
    from urllib2 import HTTPError
    from urllib2 import URLError
    
NAME = 'HLSCAT'
URL = 'http://www.hlscat.com'

re_country = re.compile(r'<a href=\"(.*)\" class=\"regions country\">(.*)</a>')
re_pages = re.compile(r'data-ci-pagination-page="(\d*)"><i class="icon-last"></i>')
re_name = re.compile(r"<span class='channel_name'>(.*)</span>")
re_checked = re.compile(r"<span class='titile_span checked_title'>Checked: </span><span class='minor_content'>(.*)</span>")
re_liveliness = re.compile(r"<div class='live green' style='background-color: rgba\(76, 175, 80, (?:.*)'\)'>(\d*)</div>")
re_status = re.compile(r"<div class='state span (?:online|offline)' title='(\w*)'></div>")
re_formats = re.compile(r"<span class='titile_span formats'>Formats: </span><span class='minor_content'> (.*)</span>")
re_stream = re.compile(r'title="copu m3u8" data-clipboard-text="(.*)"')

def showCountry():
    listing = []
    country = re.findall(re_country, fetchHtml(URL))

    for index in country:
         listing.append((sys.argv[0] + '?url=' + index[0], xbmcgui.ListItem(label=index[1]), True))

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), listing, len(listing))
    xbmcplugin.endOfDirectory(int(sys.argv[1])) 
  
def showStream():
    listing = []
    url = unquote(sys.argv[2].split('?country=')[1])
    html = fetchHtml(url)
    pages = re.search(re_pages, html)
    name = re.findall(re_name, html)
    checked = re.findall(re_checked, html)
    liveliness = re.findall(re_liveliness, html)
    status = re.findall(re_status, html)
    formats = re.findall(re_formats, html)
    stream = re.findall(re_stream, html)

    if pages:
        for index in range(2, int(pages.group(1)) + 1):
            html = fetchHtml(url + '/' + str(index))
            name.extend(re.findall(re_name, html))
            checked.extend(re.findall(re_checked, html))
            liveliness.extend(re.findall(re_liveliness, html))
            status.extend(re.findall(re_status, html))
            formats.extend(re.findall(re_formats, html))
            stream.extend(re.findall(re_stream, html))

    total = len(name)
    online = 0
    offline = 0

    for index in range(total):
        item = xbmcgui.ListItem(label=name[index])
        item.setProperty('IsPlayable', 'true')

        if status[index] == 'Online':
            item.setInfo(type='Video', infoLabels={'Plot': 'Name: [B]' + name[index] + '[/B][CR]Checked: [B]' + checked[index] + '[/B][CR]Liveliness: [B]' + liveliness[index] + '[/B][CR]Status: [B][COLOR green]Online[/COLOR][/B][CR]Formats: [B]' + formats[index] + '[/B][CR]Stream: [B]' + stream[index] + '[/B]'})
            online += 1
            listing.append((stream[index], item, False))
        else:
            if xbmcaddon.Addon().getSettingBool('offline'):
                item.setInfo(type='Video', infoLabels={'Plot': 'Name: [B]' + name[index] + '[/B][CR]Checked: [B]' + checked[index] + '[/B][CR]Liveliness: [B]' + liveliness[index] + '[/B][CR]Status: [B][COLOR red]Offline[/COLOR][/B][CR]Formats: [B]' + formats[index] + '[/B][CR]Stream: [B]' + stream[index] + '[/B]'})
                listing.append((stream[index], item, False))              
            offline += 1
    
    xbmcgui.Dialog().notification(NAME, str(total) + ' channels ' + str(online) + ' online '  + str(offline) + ' offline', xbmcgui.NOTIFICATION_INFO, 5000) 
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    xbmcplugin.addDirectoryItems(int(sys.argv[1]), listing, len(listing))
    xbmcplugin.endOfDirectory(int(sys.argv[1])) 


def fetchHtml(url):
    try:
        return urlopen(url).read().decode('utf-8')
    except HTTPError as e:
        xbmcgui.Dialog().notification(NAME, 'Unable to connect to the server.' + str(e.reason), xbmcgui.NOTIFICATION_ERROR, 5000)
    except URLError as e:
        xbmcgui.Dialog().notification(NAME, 'Unable to connect to the server.' + str(e.reason), xbmcgui.NOTIFICATION_ERROR, 5000)

if sys.argv[2].startswith('?url='):
    showStream()
else:
    showCountry()
