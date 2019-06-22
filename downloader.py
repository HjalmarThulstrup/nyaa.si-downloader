import re
import sys
import argparse
import time
import bs4
import os
import urllib.request as urllib
import urllib.parse as urlparse
from qbittorrent import Client
import subprocess
import psutil
from pynput.keyboard import Key, Controller

# TODO
# 1. Implement functionality to make the script take an argument of a list of dir paths so you can save each show in its respective folder
# 2. Implement functionality to download whole seasons at a time (Torrents where it's the whole season in 1 download or download every ep seperatly)
# 3. Implement functionality to create new directories for the files you download that are from the same show
# 4. Perhaps implement a function that returns the top n search results and make the user choose which one he wants to download.


def get_search_url(search_str):
    search = search_str.replace('"', '')
    search = search.replace('&', '%26')
    search = re.sub(r"[^a-zA-Z0-9-:!%]+", '+', search)
    return "https://nyaa.si/?f=0&c=1_2&q=" + search + "&s=id&o=desc"
    


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


def get_magnet_links(html, search):
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
        p = 'No search results of "' + search + '" found.'
        print(p.replace('\n', ''))
        #sys.exit()


def check_res(magnet_dict, search):
    res = ['1080p', '720p']
    is1080 = ''
    is720 = ''
    ## Try 1080p
    for name_key in magnet_dict.items():
        is1080 = check_name(name_key, search, res[0])
        if is1080 != False:
            return is1080
    ## Try 720p
    for name_key in magnet_dict.items():
        is720 = check_name(name_key, search, res[1])
        if is720 != False:
            return is720
    return False


def check_name(name, search, res):
    name_str = str(name[0])
    name_str = re.sub(r'[^a-zA-Z0-9-!&]', ' ', name_str).lower()
    search_arr = search.lower().split(" ")
    search_arr.append(res)
    for w in search_arr:
        if not contains_word(name_str, w):
            #print(w + " not in " + name_str)
            return False
    return name

def contains_word(s, w):
    return (' ' + w + ' ') in (' ' + s + ' ')

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


def onetonine(num):
    if 1 <= num <= 9:
        return "0" + str(num)
    else:
        return num


def open_vpn():
    if not process_check("openvpn.exe"):
        keyboard = Controller()
        subprocess.Popen(
            "E:\\Programs\\OpenVPN\\bin\\openvpn-gui.exe --connect nl-256b.ovpn")
        time.sleep(1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(7)
    # subprocess.call(
    #    'E:\\Programs\\OpenVPN\\bin\\openvpn-gui.exe --connect nl-256b.ovpn')


def open_qb():
    if not process_check("qbittorrent.exe"):
        subprocess.Popen('C:\\Program Files\\qBittorrent\\qbittorrent.exe')
        time.sleep(1.5)


def check_qb():
    if process_check("qbittorrent.exe"):
        qb = Client('http://127.0.0.1:8080/')
        while len(qb.torrents()) > 0:
            print("Downloading...")
            time.sleep(5)
        else:
            return True
    else:
        return False


def kill_process():
    if check_qb():
        os.system("taskkill /F /IM qbittorrent.exe")
        time.sleep(1)
    if process_check("openvpn.exe"):
        os.system("taskkill /F /IM openvpn.exe")
        time.sleep(1)
    if process_check("openvpn-gui.exe"):
        os.system("taskkill /F /IM openvpn-gui.exe")
    # sys.exit()


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

def dl(search, dest):
    print("Searching for " + search)
    magnet_links_dict = get_magnet_links(get_html(get_search_url(search)), search)
    if magnet_links_dict != None:
        res = check_res(magnet_links_dict, search)
        #print(res)
        if res != False:
            # name_key = res[0]
            # magnet_link = magnet_links_dict.get(name_key)
            start_download(res[1], res[0], dest)
        else:
            print("No results")

def ep_dl(eps, search, dest):
    for e in eps:
        num = onetonine(int(e))
        s = search + " " + str(num)
        dl(s, dest)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A script that gets magnet links from a nyaa.si search with english subtitles and starts downloading the torrent with the highest res and amount of seeders.')
    parser.add_argument(
        '-s', '--search', help='The search you want to make on nyaa.si')
    parser.add_argument(
        '-d', '--destination', help='The absolute path to the directory where you want the save the files.', type=str)
    parser.add_argument(
        '-l', '--list', help='The list of searches you want to make on nyaa.si', type=str)
    parser.add_argument(
        '-f', '--file', help='The absoulute path to a text file containing all the search queries you want. Please make a new line for every search in your file.')
    parser.add_argument('-e', '--episodes', help='The episode(s) you want to download. Write a single number if you want to download one episode, but you can also download multiple episodes if you write "01-12" for example. You can also download multiple single episodes, simply devide the episode numbers by dashes, i.e. "1-3-5-6"')
    parser.add_argument(
        '-k', '--kill', help='Kills the VPN and qBitTorrent processes when the downloads are finished.', action='store_true')
    parser.add_argument(
        '-t', '--test', help='Test', action='store_true')
    args = parser.parse_args()
    if args.search == None:
        if args.list == None:
            if args.file == None:
                if args.test == None:
                    parser.print_help()
                    sys.exit()
    if args.test:
        print("Search: " + str(args.search))
        print("Destination: " + str(args.destination))
        print("Search List:" + str(args.list))
        # TEST
        #open_vpn()
        #sys.exit()
        #open_qb()
        search = "Shoumetsu Toshi 10"
        magnet_dict_test = get_magnet_links(get_html(get_search_url(search)), search)
        res = check_res(magnet_dict_test, search)
        print(res)
        sys.exit()
        # if res != False:
        #     name_key = res[0]
        #     magnet_link = magnet_dict_test.get(name_key)
        #     start_download(magnet_link, name_key, "E:\\VIDEO\\animu\\Test")
        # start_download(magnet_dict_test[0].key, magnet_dict_test[0].value, "E:\\VIDEO\\animu\\Test")
        # kill_process()

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
            if eps != None:
                ep_dl(eps, search, dest)
            else:
                dl(search, dest)
        if args.kill:
            kill_process()
    elif args.file != None:
        open_vpn()
        search_list = open_and_read_file(args.file)
        for search in search_list:
            if eps != None:
                ep_dl(eps, search, dest)
            else:
                dl(search.replace("\n", ""), dest)
        if args.kill:
            kill_process()
    else:
        open_vpn()
        if eps != None:
            ep_dl(eps, args.search, dest)
            if args.kill:
                kill_process()
        else:
            dl(args.search, dest)
            if args.kill:
                kill_process()
