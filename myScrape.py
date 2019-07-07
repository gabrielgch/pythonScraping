from urllib.request import urlopen
from bs4 import BeautifulSoup
import string

alphabet = list(string.ascii_lowercase)
url_base = "https://www.basketball-reference.com/"

def get_player_image(player_detail):
    #get players picture
    #must open new connection with the detail link we found
    url = url_base+player_detail
    client = urlopen(url)
    soup = BeautifulSoup(client.read(), 'html.parser')
    client.close()
    #only one image in the page
    player_image = soup.find(id="info")
    #meta information of the player
    meta = player_image.find(id="meta")
    #not all players have an image so we must check if it exists
    if meta.div.find("img") != None:
        img = meta.div.img['src'] #player had an image
    else:
        img = "" #player did not have an image """
    
    return img

def scrape_players_data():
    players_list= []
    for x in ['a']:
        print("Players Whose name starts with ", x )
        url = url_base+"players/" + x + "/"
        #open connection
        client = urlopen(url)
        #get data into soup
        soup = BeautifulSoup(client.read(),'html.parser')
        #close connection
        client.close()
        #find the table body where the players info is placed in rows
        table_body = soup.find("tbody")
        #get all player rows in tbody
        player_rows = table_body.findAll("tr")
        for row in player_rows:
            #get name from th tag that contains an a tag with the text name of player
            name = row.th.a.text
            #split name to have first and last(s) names
            name = name.split(" ", 1)
            player_info={"first_name": name[0],"last_name":name[1]}
            #get players basic info from td tags of the row
            player_data = row.findAll("td")
            player_info["year_in"] = player_data[1].text
            player_info["year_out"] = player_data[2].text
            player_info["height"] = player_data[3].text
            player_info["weight"] = player_data[4].text
            player_info["birthday"] = player_data[5].text
            player_info["college"] = player_data[6].text
            if player_info['college'] == "":
                player_info['college'] = "no"
            player_info["detail_link"] = row.th.a['href']
            #find player image
            #player_info['img_link'] = get_player_image(player_info['detail_link'])
            #add each player dictionary to list
            players_list.append(player_info)
    return players_list

def searchPlayer(name_search):
    pass