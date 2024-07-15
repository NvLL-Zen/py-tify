# Spot-Scrape by Nvll-Zen
import time, os, yt_dlp
from playwright.sync_api import sync_playwright, TimeoutError

import os
import yt_dlp

def intro():
    intro_str = """
██████  ██    ██       ████████ ██ ███████ ██    ██ 
██   ██  ██  ██           ██    ██ ██       ██  ██  
██████    ████   █████    ██    ██ █████     ████   
██         ██             ██    ██ ██         ██    
██         ██             ██    ██ ██         ██ 
"""
    print(intro_str)

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch5:{query}", download=False)
    
    return result['entries']

def download_audio_as_mp3(url, output_folder='output', custom_filename=None):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, custom_filename)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '44100'],
        'prefer_ffmpeg': True,
        'quiet': True  # Set to True to suppress informational messages
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def checkQuery():
    print("[!] Please check the queries")
    for i in range(len(songs_list)):
        print(f"{songs_list[i]} by {artist_list[i]}")
    print("[?] Are these correct?")
    answer = 0
    while answer != "Y" or answer != "y":
        answer = input("Y/N: ")
        if answer == "Y" or answer == "y":
            break
        elif answer == "N" or answer == "n":
            print("[!] Aborting")
            exit()
        else:
            print("Answer not given")

div_xpath = "/html/body/div[3]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div"
title_xpath = "/div/div[2]/div/"
song_title_xpath = "/a/div"
artist_title_xpath = "span/div/a"

songs_list = []
artist_list = []
# https://open.spotify.com/playlist/6zLxVj27rt8fnBvDdFRlVr?si=KjeGrj9qSwu-INlMvWwGFg

with sync_playwright() as p:
    intro()
    print("[HELLO] Welcome to py-tify!")
    playlist_regex = "open.spotify.com/playlist/"
    while True:
        full_url = input("Please input the spotify playlist link: ")
        if full_url[7:33] == playlist_regex or full_url[8:34] == playlist_regex or full_url[0:26] == playlist_regex:
            if len(full_url) > 26:
                break
        else:
            print("[X] Incorrect link")

    if full_url.startswith("http://"):
            full_url = f"https://{full_url[7:]}"
    if not full_url.startswith("https://"):
        full_url = f"https://{full_url}"
    
    print("[!] Scanning playlist")
    browser = p.chromium.launch(headless=True, slow_mo=50)
    page = browser.new_page()
    page.goto(full_url)
    time.sleep(1)
    
    iteration = 0
    while True:
        iteration += 1
        try:
            song_title = page.locator(f"xpath={div_xpath}[{iteration}]{title_xpath}{song_title_xpath}")
            artist_title = page.locator(f"xpath={div_xpath}[{iteration}]{title_xpath}{artist_title_xpath}")
            
            # Wait for the elements to be available
            song_title.wait_for(timeout=3000)
            artist_title.wait_for(timeout=3000)
            
            songs_list.append(song_title.inner_html())
            artist_list.append(artist_title.inner_html())
        except (TimeoutError, Exception):
            try:
                artist_title_locator = f"xpath={div_xpath}[{iteration}]{title_xpath}{artist_title_xpath}[1]"
                artist_title = page.locator(artist_title_locator)
                
                # Wait for the fallback element to be available
                artist_title.wait_for(timeout=3000)
                
                songs_list.append(song_title.inner_html())
                artist_list.append(artist_title.inner_html())
            except (TimeoutError, Exception):
                break
    
    browser.close()

checkQuery()

for j in range(len(songs_list)):
    blacklist_result = ["music video", "mv", "Music Video", "MV", "(official music video)", "(music video)", "instrumental", "(instrumental)", "Instrumental", "(Instrumental)"]
    query = f"{songs_list[j]} by {artist_list[j]}"
    search_results = search_youtube(query)
    choice = 0
    for b_l in blacklist_result:
        if b_l in search_results[choice]['title']:
            choice += 1
            break
        else:
            pass
    print(f"[!] found: {search_results[choice]['title']}")
    video_url = search_results[choice]['url']
    print(f"[+] downloading {search_results[choice]['title']}")
    try:
        download_audio_as_mp3(video_url, "output", f"{songs_list[j]} - {artist_list[j]}")
        print(f"[+] downloaded {songs_list[j]} - {artist_list[j]} \n")
    except:
        print("[!] Download failed, trying again")
        try:
            download_audio_as_mp3(video_url, "output", f"{songs_list[j]} - {artist_list[j]}")
            print(f"[+] downloaded {songs_list[j]} - {artist_list[j]} \n")
        except:
            print("[X] please restart the program")



