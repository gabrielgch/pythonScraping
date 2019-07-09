import string
import re
import time
import functools
from timer import timeit
from urllib.request import urlopen
from bs4 import BeautifulSoup
from exception_decorator import exception

URL_BASE = 'https://www.basketball-reference.com'


@timeit
@exception
def get_player_image(player_detail_link):
    """Obtains the image url for the player.

    Keyword arguments
    player_detail_link - url for the player profile

    Opens the link provided to scrape for an image of the player.
    If no result is found the value is assigned as 'not_found'.
    """
    client = urlopen(player_detail_link)  # Open url to scrape
    soup = BeautifulSoup(client.read(), 'html.parser')
    client.close()
    player_image = soup.find(id='info')  # Find info tag of player
    meta = player_image.find(id='meta')
    if meta.div.find('img') != None:  # Check if player has image
        img = meta.div.img['src']
    else:
        img = 'not_found'
    
    return img

@timeit
@exception
def scrape_players_data(list_letters):
    """Scrapess for players whose first name starts with parameter.

    Keyword arguments
    list_letters -- contains first letter of name to look for

    It scrapes page with given initial letter for players' first name.
    Which start with that letter.
    It is a list to expand in a future to find by many letters.
    It can be slow since it opens each player's page to find image.
    It has a limit of 50 items. 
    """
    players_list= []
    for x in list_letters:
        print('Players Whose name starts with ', x )
        url = URL_BASE+"/players/" + x + "/"
        client = urlopen(url)
        soup = BeautifulSoup(client.read(),'html.parser')  # Get soup tags
        client.close()
        table_body = soup.find('tbody')  # Get tag where player info is
        player_rows = table_body.findAll('tr', limit=10)
        for row in player_rows:
            player_data = row.findAll('td')  # Get player row data
            if int(player_data[1].text) >= 1950:
                name = row.th.a.text
                name = name.split(' ', 1)  # Split first & last name
                player_info={'first_name': name[0], 'last_name':name[1]}
                player_info['height'] = player_data[3].text
                player_info['weight'] = player_data[4].text
                player_info['birthday'] = player_data[5].text
                player_info['college'] = player_data[6].text
                if player_info['college'] == '':
                    player_info['college'] = 'not_found'
                player_info['detail_link'] = URL_BASE + row.th.a['href']
                player_info['img_link'] = get_player_image(
                    player_info['detail_link'])
                players_list.append(player_info)
            if(len(players_list) ==50):
                break
        if(len(players_list) ==50):
            break
    return players_list

@timeit
@exception
def search_playerby_name(name_search):
    """Scrapes for players by first name.

    Keyword arguments
    name_search -- name to look for (can be partial or complete first)

    It searches through the pages for players a-z for the name.
    It can be slow since it opens each player's page to find image.
    It has a limit of 50 items. 
    """
    pattern = re.compile("%"+name_search.lower()+"%")
    players_list= []
    alphabet = [x for x in string.ascii_lowercase if x !='x']
    for x in alphabet:        
        url = URL_BASE + "/players/" + x + "/"
        client = urlopen(url)
        soup = BeautifulSoup(client.read(),'html.parser')
        client.close()
        table_body = soup.find('tbody')
        player_rows = table_body.findAll('tr')
        for row in player_rows:
            player_data = row.findAll('td')
            name = row.th.a.text
            name = name.split(' ', 1)
            if (int(player_data[1].text) >= 1950 and
                name[0].lower().find(name_search)!=-1):
                player_info={'first_name': name[0], 'last_name':name[1]}
                player_info['year_in'] = player_data[1].text
                player_info['year_out'] = player_data[2].text
                player_info['height'] = player_data[3].text
                player_info['weight'] = player_data[4].text
                player_info['birthday'] = player_data[5].text
                player_info['college'] = player_data[6].text
                if player_info['college'] == '':
                    player_info['college'] = 'not_found'
                player_info['detail_link'] = URL_BASE + row.th.a['href']
                players_list.append(player_info)
            if(len(players_list) ==50):
                break
        if(len(players_list) ==50):
            break
    for player in players_list:
        #find player image
        player['img_link'] = get_player_image(player['detail_link'])
    return players_list