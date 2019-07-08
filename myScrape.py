# -*- coding: utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import string
import re

url_base = 'https://www.basketball-reference.com'


def get_player_image(player_detail_link):

    # get players picture
    # must open new connection with the detail link we found

    client = urlopen(player_detail_link)
    soup = BeautifulSoup(client.read(), 'html.parser')
    client.close()

    # only one image in the page

    player_image = soup.find(id='info')

    # meta information of the player

    meta = player_image.find(id='meta')

    # not all players have an image so we must check if it exists

    if meta.div.find('img') not None:
        img = meta.div.img['src']  # player had an image
        print('>>' + img)
    else:
        img = 'not_found'  # player did not have an image """

    return img


def scrape_players_data(list_letters):
    players_list = []
    for x in list_letters:
        print(('Players Whose name starts with ', x))
        url = url_base + '/players/' + x + '/'

        # open connection

        client = urlopen(url)

        # get data into soup

        soup = BeautifulSoup(client.read(), 'html.parser')

        # close connection

        client.close()

        # find the table body where the players info is placed in rows

        table_body = soup.find('tbody')

        # get all player rows in tbody

        player_rows = table_body.findAll('tr', limit=10)
        for row in player_rows:

            # get players basic info from td tags of the row

            player_data = row.findAll('td')

            # check year when they entered the league

            if int(player_data[1].text) >= 1950:

                # get name from tag that contains a tag with the name of player

                name = row.th.a.text

                # split name to have first and last(s) names

                name = name.split(' ', 1)
                player_info = {'first_name': name[0],
                               'last_name': name[1]}
                player_info['height'] = player_data[3].text
                player_info['weight'] = player_data[4].text
                player_info['birthday'] = player_data[5].text
                player_info['college'] = player_data[6].text
                if player_info['college'] == '':
                    player_info['college'] = 'not_found'
                player_info['detail_link'] = url_base + row.th.a['href']

                # find player image

                player_info['img_link'] = \
                    get_player_image(player_info['detail_link'])

                # add each player dictionary to list

                players_list.append(player_info)
            if len(players_list) == 50:
                break
        if len(players_list) == 50:
            break
    return players_list


def search_playerby_name(name_search):
    print(name_search)
    pattern = re.compile('%' + name_search.lower() + '%')
    players_list = []
    alphabet = [x for x in string.ascii_lowercase if x != 'x']
    for x in alphabet:
        print(('Players Whose name starts with ', x))
        url = url_base + '/players/' + x + '/'

        # open connection

        client = urlopen(url)

        # get data into soup

        soup = BeautifulSoup(client.read(), 'html.parser')

        # close connection

        client.close()

        # find the table body where the players info is placed in rows

        table_body = soup.find('tbody')

        # get all player rows in tbody

        player_rows = table_body.findAll('tr')
        for row in player_rows:

            # get players basic info from td tags of the row

            player_data = row.findAll('td')

            # check year when they entered the league

            name = row.th.a.text
            name = name.split(' ', 1)
            if int(player_data[1].text) >= 1950 and name[0].lower().find(name_search) != -1:
                player_info = {'first_name': name[0], 'last_name': name[1]}
                player_info['year_in'] = player_data[1].text
                player_info['year_out'] = player_data[2].text
                player_info['height'] = player_data[3].text
                player_info['weight'] = player_data[4].text
                player_info['birthday'] = player_data[5].text
                player_info['college'] = player_data[6].text
                if player_info['college'] == '':
                    player_info['college'] = 'not_found'
                player_info['detail_link'] = url_base + row.th.a['href']

                # add each player dictionary to list

                players_list.append(player_info)
            if len(players_list) == 50:
                break
        if len(players_list) == 50:
            break
    for player in players_list:

        # find player image

        player['img_link'] = get_player_image(player['detail_link'])
    return players_list