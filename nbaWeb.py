from flask import Flask, request
from flask import render_template
import myScrape

app = Flask(__name__)

@app.route('/', methods=["GET","POST"])
def home():
    return render_template('index.html')

@app.route('/scrape/<action>', methods=["GET", "POST"])
def scrape(action):
    if action =="all":
        all_players_list = myScrape.scrape_players_data()
        result_size = len(all_players_list)
        return render_template('scrape.html', action=action, all_players_list=all_players_list, result_size=result_size)
    if action == "individual":
        #result = myScrape.searchPlayer()
        pass
    return render_template('scrape.html', action=action)

from flask_sqlalchemy import SQLAlchemy

database_file = "sqlite:///nba_players.db"
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Player(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False, )
    last_name = db.Column(db.String(80), nullable=False, )
    college = db.Column(db.String(80), nullable=False, )
    birthday = db.Column(db.String(80), nullable=True, )
    height = db.Column(db.Float, nullable=False, )
    weight = db.Column(db.Float, nullable=False, )
    detail_link = db.Column(db.String(100), nullable=False, )
    """missing year_in, year_out, image""" #!IMPORTANT

    def __init__(self, first_name,last_name,college,birthday,height,weight,detail_link):
        self.first_name = first_name
        self.last_name = last_name
        self.college = college
        self.birthday = birthday
        self.height = height
        self.weight = weight
        self.detail_link = detail_link

db.create_all()

def getData(data):
    keys = ["first", "last", "college", "birthday", "height", "weight", "detail_link"]
    values = []
    values.append(data.get('first'))
    values.append(data.get('last'))
    values.append(data.get('college'))
    values.append(data.get('birthday'))
    height = data.get('height')
    height = height.replace("-",".")
    values.append(float(height))
    values.append(float(data.get('weight')))
    values.append(data.get('detail_link'))
    player = dict(zip(keys,values))

    return player

def insertPlayer(player):
    toInsert = Player(player['first'],player['last'],player['college'],player['birthday'],player['height'],\
        player['weight'],player['detail_link'])
    db.session.add(toInsert)
    db.session.commit()
    print("INSERTED")

@app.route('/delete_entry<player_id>')
def delete_entry(player_id):
    print(">>"+player_id)
    player_found = Player.query.filter_by(player_id=player_id).first()
    if player_found is not None:
        db.session.delete(player_found)
        db.session.commit()
    return render_template('database.html', action='start')

@app.route('/search_all')
def search_all():
    players = Player.query.all()
    res_size = len(players)
    print(players[0].player_id)
    return render_template('database.html', action='all', all_players_list=players, result_size=res_size)
    

@app.route('/database/<action>', methods=["GET", "POST"])
def database(action):
    print("CALLING  ")
    if request.form:
        if action == "add":
            data = request.form
            player_data =getData(data)
            insertPlayer(player_data)
            return render_template('database.html', action='start')
    return render_template('database.html', action=action)