import re, sys, argparse
import bs4
import urllib.request as urllib
import urllib.parse as urlparse

def get_search_url(search_str):
    search = search_str.replace('"', '')
    search = re.sub(r"[^a-zA-Z0-9-]+", '+', search)
    return "https://nyaa.si/?f=0&c=1_2&q=" + search + "&s=seeders&o=desc"

def get_html(url):
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}
        req = urllib.Request(url, headers=hdr)
        res = urllib.urlopen(req)
        txt = res.read()
        txtstr = txt.decode("utf-8")
        return txtstr
    except Exception as e:
        print(e)
        parser.print_help()
        sys.exit()

def get_magnet_links(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    tbody = soup.find('tbody')
    results = tbody.find_all('tr')
    magnet_name_dict = {}
    for r in results:
        tds = r.find_all('td')
        name_td = tds[1]
        name_as = name_td.find_all('a')
        name = name_as[len(name_as)-1].text
        magnet_td = tds[2]
        magnet_as = magnet_td.find_all('a')
        magnet = magnet_as[1]['href']
        magnet_name_dict.update({name:magnet})

    return magnet_name_dict


def check_res(magnet_dict):
    res = ['1080p', '720p']
    is1080 = False
    is720 = False
    name_1080 = ''
    name_720 = ''
    for name_key in magnet_dict.items():
        name_str = str(name_key)
        if name_str.find(res[0]) != -1:
            is1080 = True
            name_1080 = name_key
        elif name_str.find(res[1]) != -1:
            is720 = True
            name_720 = name_key
    if is1080:
        return name_1080
    elif is720:
        return name_720
    else:
        print("No files with 720p+ resolution")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A script that gets magnet links from a nyaa.si search with english subtitles and starts downloading the torrent with highest amount of seeders.')
    parser.add_argument(
        '-s', '--search', help='The search you want to make on nyaa.si')
    args = parser.parse_args()
    print(check_res(get_magnet_links(get_html(get_search_url(args.search)))))

