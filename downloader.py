import re
import sys
import argparse
import time
import bs4
import urllib.request as urllib
import urllib.parse as urlparse
from qbittorrent import Client
import subprocess
import psutil 

# TODO
# 1. Implement functionality to make the script take an argument of a list of dir paths so you can save each show in its respective folder
# 2. Make the script take an argument of episode numbers, either a single number or a number in a range (like 5-8, both included).
# Make it loop thru a list of searches where only the episode number is changed
# 3. Implement functionality to download whole seasons at a time (Torrents where it's the whole season in 1 download or download every ep seperatly)
# 4. Implement functionality to create new directories for the files you download that are from the same show
# 5. Make script turn on VPN automatically and possibly turn it off afterwards


def get_search_url(search_str):
    search = search_str.replace('"', '')
    search = search.replace('&', '%26')
    search = re.sub(r"[^a-zA-Z0-9-:!%]+", '+', search)
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
    try:
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
            magnet_name_dict.update({name: magnet})
        return magnet_name_dict
    except:
        print('No search results found.')
        sys.exit()


def check_res(magnet_dict):
    res = ['1080p', '720p']
    is720 = False
    name_720 = ''
    for name_key in magnet_dict.items():
        name_str = str(name_key)
        if name_str.find(res[0]) != -1:
            return name_key
        elif name_str.find(res[1]) != -1:
            is720 = True
            name_720 = name_key
    if is720:
        return name_720
    else:
        return False


def get_episode_nums(ep_str):
    nums = []
    if ep_str != None:
        if ep_str.find('-') != -1:
            nums = ep_str.split('-')
        if len(nums) == 2:
            nums = list(range(int(nums[0]), int(nums[1])+1))
            return nums
        elif len(nums) > 2:
            return nums
        else:
            return ep_str
    else:
        return ep_str


def process_check(name):
    return name in (p.name() for p in psutil.process_iter())

def open_vpn():
    if not process_check("openvpn-gui.exe"):
        subprocess.Popen("E:\\Programs\\OpenVPN\\bin\\openvpn-gui.exe --connect nl-256b.ovpn")
        time.sleep(17)
    #subprocess.call(
    #    'E:\\Programs\\OpenVPN\\bin\\openvpn-gui.exe --connect nl-256b.ovpn')


def open_qb():
    if not process_check("qbittorrent.exe"):
        subprocess.Popen('C:\\Program Files\\qBittorrent\\qbittorrent.exe')
        time.sleep(1.5)


def open_and_read_file(path):
    searches = []
    with open(path) as f:
        for line in f:
            searches.append(line)
    if len(searches) > 0:
        return searches
    else:
        print('The specified file has no text in it.')
        sys.exit()


def start_download(magnet, name, path):
    open_qb()
    try:
        qb = Client('http://127.0.0.1:8080/')
        qb.login()
        qb.download_from_link(magnet, savepath=path)
        print(name + " started downloading. The files will be saved to " + path + "\n")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A script that gets magnet links from a nyaa.si search with english subtitles and starts downloading the torrent with the highest res and amount of seeders.')
    parser.add_argument(
        '-s', '--search', help='The search you want to make on nyaa.si')
    parser.add_argument('-d', '--destination',
                        help='The absolute path to the directory where you want the save the files.', type=str)
    parser.add_argument(
        '-l', '--list', help='The list of searches you want to make on nyaa.si', type=str)
    parser.add_argument(
        '-f', '--file', help='The absoulute path to a text file containing all the search queries you want. Please make a new line for every search in your file.')
    parser.add_argument('-e', '--episodes', help='The episode(s) you want to download. Write a single number if you want to download one episode, but you can also download multiple episodes if you write "01-12" for example. You can also download multiple single episodes, simply devide the episode numbers by dashes, i.e. "1-3-5-6"')
    args = parser.parse_args()
    if args.search == None:
        if args.list == None:
            if args.file == None:
                parser.print_help()
                sys.exit()
    if args.search == "test":
        print("Search: " + str(args.search))
        print("Destination: " + str(args.destination))
        print("Search List:" + str(args.list))
        sys.exit()
    dest = args.destination
    eps = get_episode_nums(args.episodes)
    if dest != None:
        if dest[-1:] != "/" or dest[-1:] != "\\":
            dest = dest + "/"
    if args.list != None and args.file != None:
        print('Please only use one of either the list or file argument, not both.')
        sys.exit()
    if args.list != None:
        open_vpn()
        search_list = [str(item) for item in args.list.split(',')]
        for search in search_list:
            magnet_links_dict = get_magnet_links(
                get_html(get_search_url(search)))
            res = check_res(magnet_links_dict)
            if res != False:
                name_key = res[0]
                magnet_link = magnet_links_dict.get(name_key)
                start_download(magnet_link, name_key, dest)
    elif args.file != None:
        open_vpn()
        search_list = open_and_read_file(args.file)
        for search in search_list:
            magnet_links_dict = get_magnet_links(
                get_html(get_search_url(search)))
            res = check_res(magnet_links_dict)
            if res != False:
                name_key = res[0]
                magnet_link = magnet_links_dict.get(name_key)
                start_download(magnet_link, name_key, dest)
    else:
        open_vpn()
        if eps != None:
            for e in eps:
                num = int(e)
                if 1 <= num <= 9:
                    num = "0" + str(num)
                s = args.search + " " + str(num)
                magnet_links_dict = get_magnet_links(
                    get_html(get_search_url(s)))
                res = check_res(magnet_links_dict)
                if res != False:
                    name_key = res[0]
                    magnet_link = magnet_links_dict.get(name_key)
                    #print(name_key + " - " + magnet_link)
                    start_download(magnet_link, name_key, dest)
        else:
            magnet_links_dict = get_magnet_links(
                get_html(get_search_url(args.search)))
            res = check_res(magnet_links_dict)
        if res != False:
            name_key = res[0]
            magnet_link = magnet_links_dict.get(name_key)
            #print(name_key + " - " + magnet_link)
            start_download(magnet_link, name_key, dest)
