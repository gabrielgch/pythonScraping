import re
import string
import os
import json
import time
import argparse
import functools
from timer import timeit
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template
from exception_decorator import exception
import myScrape


JSON_FILEPATH = os.path.join(os.getcwd(), os.path.basename('/json'))
CSV_FILEPATH = os.path.join(os.getcwd(), os.path.basename('/csv'))
DATABASE_FILE = 'sqlite:///nba_players.db'
temp_export=[]
db = SQLAlchemy()   

def create_app(env='dev'):
    """Application factory for the command line."""
    global db
    if env == 'prod':
        env = 'PRODUCTION'
    else:
        env = 'DEVELOPMENT'
    
    app = Flask(__name__)
    app.config['ENV'] = env
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_FILE
    db = SQLAlchemy(app)
    db.create_all()

    class Player(db.Model):
        """Player model for the database."""
        player_id = db.Column(db.Integer, primary_key=True)
        first_name = db.Column(db.String(80), nullable=False)
        last_name = db.Column(db.String(80), nullable=False)
        college = db.Column(db.String(80), nullable=False)
        birthday = db.Column(db.String(80), nullable=True)
        height = db.Column(db.Float, nullable=False)
        weight = db.Column(db.Float, nullable=False)
        detail_link = db.Column(db.String(150), nullable=False)
        img_link = db.Column(db.String(150), nullable=True)

        def __init__(
                self, first_name,last_name,college,birthday,
                height,weight,detail_link, img_link):
            self.first_name = first_name
            self.last_name = last_name
            self.college = college
            self.birthday = birthday
            self.height = height
            self.weight = weight
            self.detail_link = detail_link
            self.img_link = img_link

    @timeit
    @exception
    @app.route('/', methods=['GET','POST'])
    def home():
        """Displays the landing (index) page."""
        return render_template('index.html')


    @timeit
    @exception
    @app.route('/export<frmt_export>/<caller>', methods=['GET', 'POST'])
    def export(frmt_export, caller):
        """Export data to a file in JSON or CSV.

        Keyword arguments:
        frmt_export -- the format to export; json or csv 
        caller -- the calling page of the website

        It sends the frmt_export parameter to auxiliary function to export.
        Assigns an error string in case the parameters are not valid.
        """
        global temp_export
        err_msg = ''
        html_file = 'database.html'
        if frmt_export == '' or frmt_export is None:
            err_msg = 'Error: export format was not specified...export aborted.'
        elif len(temp_export) < 0:
            err_msg = 'Error: no data to export...export aborted'
        elif frmt_export != 'csv' and frmt_export != 'json':
            err_msg = 'Error: file format is not accepted.'
        else:
            export_file(file_format=frmt_export)
        if caller == '' or caller is None or caller == 'scrape':
            html_file = 'scrape.html'

        return render_template(
            'database.html', action='start',
            all_players_list=[], result_size=len([]),
            err_msg=err_msg)


    @timeit
    @exception
    @app.route('/scrape/<action>', methods=['GET', 'POST'])
    def scrape(action):
        """Handles scrape requests by the user.

        Keyword arguments:
        action -- desired search parameter

        Checks user's search parameter for to request data from myScrape.
        Module. 
        It handles user error message if params are invalid.
        """
        global temp_export
        temp_export = []
        pattern = re.compile('^\w{1}$')
        err_msg = ''
        if action == 'all':
            alphabet = list(string.ascii_lowercase)
            all_players_list = myScrape.scrape_players_data(alphabet)
        elif action =='byname':
            name_tosearch = request.form.get('individual_name')
            if name_tosearch is not None and name_tosearch != '':
                all_players_list = myScrape.search_playerby_name(name_tosearch.lower())
            else:
                err_msg = 'Error: must fill desired field to search...aborted scraping'
                all_players_list = []
        elif pattern.match(action):
            letter = action
            all_players_list = myScrape.scrape_players_data(list(letter), lim=50)
        else:
            all_players_list = []
        temp_export = all_players_list
        return render_template(
            'scrape.html', action=action, all_players_list=all_players_list,
            result_size=len(all_players_list), err_msg=err_msg)

    @timeit
    @exception
    def get_data(data):
        """Formats Player db search result to dictionary.

        Keyword arguments
        data -- Player db result from flaskAlchemy query

        It transforms Player received to a dictionary for easier access.
        Used for standard formatting for the program.
        """
        keys = [
            'first', 'last', 'college', 'birthday',
            'height', 'weight', 'detail_link', 'img_link'
            ]
        values = []
        values.append(data.get('first'))
        values.append(data.get('last'))
        values.append(data.get('college'))
        values.append(data.get('birthday'))
        height = data.get('height')
        height = height.replace('-','.')
        values.append(height)
        values.append(data.get('weight'))
        values.append(data.get('detail_link'))
        values.append(data.get('img_link'))
        player = dict(zip(keys,values))

        return player


    @timeit
    @exception
    def check_notempty(data):
        """Checks if dictionary values of data are not empty."""
        valid = True
        if ((data['first'] == '' or None) or (data['last'] =='' or None)\
            or (data['college'] =='' or None) or (data['birthday'] == '' or None)\
            or (data['height'] == '' or None) or (data['weight'] == '' or None)\
            or (data['detail_link'] == '' or None) 
            or (data['img_link'] == '' or None)):
            valid = False
        
        return valid

    @timeit
    @exception
    def insert_player(player):
        """Inserts player into Flask-sqlAlchemy database.

        Keyword arguments:
        player -- player dictionary to export to database

        It inserts data of player into the database.
        Performs float type check for height and weight attributes.
        """
        err_msg = ''
        try:
            player['height'] = float(player['height'])
            player['weight'] = float(player['weight'])
            db.session.commit()
            toInsert = Player(
                player['first'], player['last'], player['college'],
                player['birthday'], player['height'], player['weight'],
                player['detail_link'], player['img_link'])
            db.session.add(toInsert)
            db.session.commit()
        except ValueError:
                err_msg = 'Error: Height and Weight values'\
                    ' must be decimal values...update aborted'
        return err_msg

    @timeit
    @exception
    @app.route('/delete_entry<player_id>')
    def delete_entry(player_id):
        """Deletes a player entry in Flask-sqlAlchemy db.

        Keyword arguments
        player_id -- id of Player row to delete

        Performs the deletion of a single row from Player.
        if player is not found, delete is ignored. 
        """
        player_found = Player.query.filter_by(player_id=player_id).first()
        if player_found is not None:
            db.session.delete(player_found)
            db.session.commit()
        return render_template('database.html', action='start')


    @timeit
    @exception
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        """Renders player view from scrape data."""
        if request.form:
            data = request.form
            player_data = get_data(data)
            return render_template(
                'profile.html', action='display',
                player=player_data)

    @timeit
    @exception
    @app.route('/update', methods=['GET', 'POST'])
    def update_entry():
        """Performs an update to a single Player row.

        It retrieves the data from the form in webpage.
        Performs float checks for height and weight.
        """
        err_msg = ''
        if request.form:
            data = request.form
            player_data = get_data(data)
            if check_notempty(player_data):
                player_id = data['player_id']
                player = Player.query.filter_by(player_id=player_id).first()
                player.first_name = player_data['first']
                player.last_name = player_data['last']
                player.college = player_data['college']
                player.birthday = player_data['birthday']
                player.height = player_data['height']
                player.weight = player_data['weight']
                player.detail_link = player_data['detail_link']
                player.img_link = player_data['img_link']
                try:
                    player_data['height'] = float(player_data['height'])
                    player_data['weight'] = float(player_data['weight'])
                    db.session.commit()
                except ValueError:
                    err_msg = 'Error: Height and Weight values must be'\
                        ' decimal values...update aborted'
            else:
                err_msg = 'Error: Empty value found...update aborted'
        return render_template(
            'database.html',
            action='start',
            err_msg=err_msg)

    @timeit
    @exception
    @app.route('/entry_find<player_id>')
    def get_data_update(player_id):
        """Finds player data to display in update page

        Keyword arguments
        player_id -- row id to get Player data from
        """
        player_found = Player.query.filter_by(player_id=player_id).first()
        if player_found is None:
            err_msg = 'Error: Player could not be found in database'
            return render_template('database.html', action='start',
                all_players_list=[], result_size=0, err_msg=err_msg)

        return render_template('update.html',player=player_found)

    @timeit
    @exception
    def format_for_export(data):
        """Transforms Player cols into a dictionary used for export."""
        d = [dict(x.__dict__) for x in data]
        for x in d:
            del x['_sa_instance_state']
        return d

    @timeit
    @exception
    @app.route('/search_all')
    def search_all():
        """Obtain all Player values from database."""
        global temp_export
        players = Player.query.all()
        res_size = len(players)
        temp_export = format_for_export(players)
        return render_template('database.html', action='all',
            all_players_list=players, result_size=res_size)

    @timeit
    @exception
    @app.route('/search<action>', methods=['GET','POST'])
    def search(action):
        """Performs search to database.

        Keyword arguments
        action -- search to do (name|collge|height)

        It determines what call to make to the database.
        Performs type check for height search and displays errors.
        """
        global temp_export
        temp_export = []
        err_msg = ''
        if request.form:
            name = request.form['name']
            if name == '' or None:
                err_msg = 'Please fill desired search field'
                players=[]
            elif action == 'name':
                players = Player.query.filter(
                    Player.first_name.like('%'+name+'%') 
                    | Player.last_name.like('%'+name+'%')).all()
            elif action == 'college':
                players = Player.query.filter(
                    Player.college.like('%'+name+'%')).all()
            elif action == 'height':
                try:
                    float(name)
                    players = Player.query.filter(Player.height == name).all()
                except ValueError:
                    err_msg = 'Error: height must be a decimal value'
                    players=[]
            res_size = len(players)
            temp_export = format_for_export(players)
            return render_template(
                'database.html', action=action, all_players_list=players,
                err_msg=err_msg, result_size=res_size)
        
        
    @timeit
    @exception
    @app.route('/database/<action>', methods=['GET', 'POST'])
    def database(action):
        """Displays database page and handles insertion to db.

        Keyword arguments
        action -- specifies action to perform (update|start)

        start refers to page without results. 
        update refers to perform an insertion into database.
        """
        err_msg = ''
        if request.form:
            if action == 'add':
                data = request.form
                player_data = get_data(data)
                if check_notempty(player_data):
                    err_msg = insert_player(player_data)
                    action = 'start'

        return render_template(
            'database.html', action=action,
            err_msg=err_msg)
    return app

@timeit
@exception
def export_file(file_format='csv'):
    """Exports result data to a file with given format.

    Keyword arguments
    file_format -- format to export data to (default csv)

    Exports last queried result from db or scraped data from web.
    It can export either one but not both at the same time.
    Results can be found in folder named after the used format
    Only CSV and JSON are supported. 
    """
    global temp_export
    unique = datetime.now().strftime('%d-%m-%Y_%H%M%S')
    filename = 'data-'+unique
    if file_format == 'csv':
        f = open(os.path.join(CSV_FILEPATH,filename+'.csv'), 'w')
        headers = 'first name, last name, birthday, college,\
            height, weight, detail link, img link\n'
        f.write(headers)
        for datum in temp_export:
            f.write(
                datum['first_name']+','+datum['last_name']+','
                +datum['birthday'].replace(',','-')+','
                +datum['college'].replace(',','-')+','
                +str(datum['height'])+','+str(datum['weight'])
                +','+datum['detail_link']+','+datum['img_link']+'\n')
        f.close()
    elif file_format == 'json':
        with open(os.path.join(JSON_FILEPATH,filename+'.json'), 'w') as f:
            json.dump(temp_export,f)    

def print_results(data):
    """Prints dictionary data to cl."""
    for player in data:
        print("---------------------------------------")
        for keys,values in player.items():
            print(keys+":"+values)
        

if __name__ == '__main__':
    """Will check the command line options for scraping and running webapp."""
    parser = argparse.ArgumentParser(description='Flask NBA app')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-n', '--name', required=False, dest='name', type=str,
        help='Scrapes first name of nba players since 1950.'
        +' Limit 50 results.')
    group.add_argument(
        '-l', '--letter', required=False, dest='letter', type=str,
        help='Scrapes players whose last name starts with given letter.'
            +' Limit of 50 results.'
    )
    group.add_argument(
        '-a', '--all', required=False, action='store_true',
        help='Scrapes all names from a-z. Limit 50 results.'
    )
    group.add_argument(
        '-e', '--env', choices=['dev', 'local', 'prod'],
        dest='env', required=False,
        help='application environment.')
    parser.add_argument(
        '-x', '--export', required=False, dest='export',
        choices=['csv', 'json'], help='Exports scraped data to file JSON or CSV.'
    )
    parser.add_argument(
        '-s', '--silent', required=False, action='store_true',
        help='Does not print results to command line.'
    )
    args = parser.parse_args()
    if args.name:
        results = myScrape.search_playerby_name(args.name)
        if args.silent == False:
            print_results(results)
        if args.export:
            temp_export = results
            export_file(args.export)
    elif args.letter:
        char = args.letter
        char = char[0]
        results = myScrape.scrape_players_data(list(char),lim=50)
        if args.silent == False:
            print_results(results)
        if args.export:
            temp_export = results
            export_file(args.export)
    elif args.all:
        results = myScrape.scrape_players_data(list(string.ascii_lowercase))
        if args.silent == False:
            print_results(results)
        if args.export:
            temp_export = results
            export_file(args.export)
    elif args.env:
        app = create_app(args.env)
        app.run()