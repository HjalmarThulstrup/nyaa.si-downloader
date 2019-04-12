# nyaa.si Downloader
I made this script to make it easier to download all the anime you watch in a season without having to go onto nyaa.si and make a search for every single show, and then find the right rip you want to download.

This script takes a search query and finds the title and accompanying magnet link for the show and episode you want to download with the highest resolution and largest amount of seeders.

I have programmed it to download the 1080p resolution file with the highest amount of seeders, and if there aren't any 1080p versions available, it downloads the 720p resolution file with most seeders, and if that isn't available either, it doesn't download anything because non-HD isn't acceptable.

The script takes both a single search query and a list of search queries, and you can define the destination of where you want to save the files.

After the script gathers the necessary magnet links and titles, it opens qbitTorrent and starts the downloads automatically.
