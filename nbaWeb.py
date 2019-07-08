from flask import Flask, request
from flask import render_template
import myScrape
import re, string, os, json
from datetime import datetime

app = Flask(__name__)
temp_export=[]
JSON_FILEPATH = os.path.join(os.getcwd(), os.path.basename("/json"))
CSV_FILEPATH = os.path.join(os.getcwd(), os.path.basename("/csv"))

@app.route('/', methods=["GET","POST"])
def home():
    return render_template('index.html')

@app.route("/export<frmt_export>/<caller>", methods=["GET", "POST"])
def export(frmt_export,caller):
    global temp_export
    err_msg = ""
    html_file = "database.html"
    if frmt_export == "" or frmt_export is None:
        print("HEE")
        err_msg = "Error: export format was not specified...export aborted"
    elif len(temp_export) < 0:
        print("GEG")
        err_msg = "Error: no data to export...export aborted"
    else:
        print("ENTERED")
        export_file(file_format=frmt_export)
    if caller == "" or caller is None or caller == "scrape":
        html_file = "scrape.html"

    return render_template(html_file, action='start', all_players_list=[],\
        result_size=len([]), err_msg = err_msg)


@app.route('/scrape/<action>', methods=["GET", "POST"])
def scrape(action):
    global temp_export
    temp_export = []
    pattern = re.compile("^\w{1}$")
    err_msg = ""
    if action =="all":
        print("HERERE")
        alphabet = list(string.ascii_lowercase)
        all_players_list = myScrape.scrape_players_data(alphabet)
    elif action =="byname":
        name_tosearch = request.form.get('individual_name')
        if name_tosearch is not None and name_tosearch!="":
            all_players_list = myScrape.search_playerby_name(name_tosearch.lower())
        else:
            err_msg = "Error: must fill desired field to search...aborted scraping"
            all_players_list = []
    elif pattern.match(action):
        print("ENTERED HERE")
        letter = action
        all_players_list = myScrape.scrape_players_data(list(letter))
    else:
        all_players_list = []
    temp_export = all_players_list
    return render_template('scrape.html', action=action, all_players_list=all_players_list,\
        result_size=len(all_players_list), err_msg = err_msg)

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
    detail_link = db.Column(db.String(150), nullable=False, )
    img_link = db.Column(db.String(150), nullable=True, )

    def __init__(self, first_name,last_name,college,birthday,height,weight,detail_link, img_link):
        self.first_name = first_name
        self.last_name = last_name
        self.college = college
        self.birthday = birthday
        self.height = height
        self.weight = weight
        self.detail_link = detail_link
        self.img_link = img_link

db.create_all()

def getData(data):
    keys = ["first", "last", "college", "birthday", "height", "weight", "detail_link", "img_link"]
    values = []
    values.append(data.get('first'))
    values.append(data.get('last'))
    values.append(data.get('college'))
    values.append(data.get('birthday'))
    height = data.get('height')
    height = height.replace("-",".")
    values.append(height)
    values.append(data.get('weight'))
    values.append(data.get('detail_link'))
    values.append(data.get('img_link'))
    player = dict(zip(keys,values))

    return player

def check_notempty(data):
    valid = True
    if (data['first'] == "" or None) or (data['last']=="" or None) or (data['college']=="" or None)\
        or (data['birthday']=="" or None) or (data['height']=="" or None) or (data['weight']=="" or None)\
        or (data['detail_link']=="" or None) or (data['img_link']=="" or None):
            valid = False
    
    return valid

def export_file(file_format="csv"):
    global temp_export
    unique = datetime.now().strftime("%d-%m-%Y_%H%M%S")
    filename = "data-"+unique
    if file_format == "csv":
        print(">>>>"+CSV_FILEPATH+"___"+filename)
        f = open(os.path.join(CSV_FILEPATH,filename+".csv"), 'w')
        headers = "first name, last name, birthday, college, height, weight, detail link, img link\n"
        f.write(headers)
        for datum in temp_export:
            f.write(datum['first_name']+","+datum['last_name']+","+datum['birthday'].replace(",","-")+","+\
                datum['college'].replace(",","-")+","+str(datum['height'])+","+str(datum['weight'])+\
                ","+datum['detail_link']+","+datum['img_link']+"\n")
        f.close()
    elif file_format == "json":
        with open(os.path.join(JSON_FILEPATH,filename+".json"), "w") as f:
            json.dump(temp_export,f)

def insertPlayer(player):
    err_msg=""
    try:
        player['height'] = float(player['height'])
        player['weight'] = float(player['weight'])
        db.session.commit()
        toInsert = Player(player['first'],player['last'],player['college'],player['birthday'],\
            player['height'],player['weight'],player['detail_link'], player['img_link'])
        db.session.add(toInsert)
        db.session.commit()
    except ValueError:
        err_msg = "Error: Height and Weight values must be decimal values...update aborted"
    return err_msg

@app.route('/delete_entry<player_id>')
def delete_entry(player_id):
    player_found = Player.query.filter_by(player_id=player_id).first()
    if player_found is not None:
        db.session.delete(player_found)
        db.session.commit()
    return render_template('database.html', action='start')

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if request.form:
        data = request.form
        player_data = getData(data)
        return render_template('profile.html', action='display', player=player_data)

@app.route('/update', methods=["GET", "POST"])
def update_entry():
    err_msg = ""
    if request.form:
        data = request.form
        player_data = getData(data)
        if check_notempty(player_data):
            player_id = data['player_id']
            player = Player.query.filter_by(player_id = player_id).first()
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
                err_msg = "Error: Height and Weight values must be decimal values...update aborted"
        else:
            err_msg = "Error: Empty value found...update aborted"
    return render_template('database.html', action='start', err_msg = err_msg)

@app.route('/entry_find<player_id>')
def get_data_update(player_id):
    player_found = Player.query.filter_by(player_id=player_id).first()
    if player_found is None:
        err_msg="Error: Player could not be found in database"
        render_template('database.html', action='start', all_players_list=[], result_size=0, err_msg=err_msg)
    return render_template('update.html',player=player_found)

def formatfor_export(data):
    d = [dict(x.__dict__) for x in data]
    for x in d:
        del x['_sa_instance_state']
    
    return d

@app.route('/search_all')
def search_all():
    global temp_export
    players = Player.query.all()
    res_size = len(players)
    temp_export = formatfor_export(players)
    return render_template('database.html', action='all', all_players_list=players, result_size=res_size)

@app.route('/search<action>', methods=["GET","POST"])
def search(action):
    global temp_export
    temp_export = []
    err_msg = ""
    if request.form:
        name = request.form['name']
        if name == "" or None:
            err_msg = "Please fill desired search field"
            players=[]
        elif action == "name":
            players = Player.query.filter(Player.first_name.like("%"+name+"%") |\
                Player.last_name.like("%"+name+"%")).all()
        elif action == "college":
            players = Player.query.filter(Player.college.like("%"+name+"%")).all()
        elif action == "height":
            try:
                float(name)
                players = Player.query.filter(Player.height == name).all()
            except ValueError:
                err_msg = "height must be a decimal value"
                players=[]
        res_size = len(players)
        temp_export = formatfor_export(players)
        return render_template('database.html', action=action, all_players_list=players,\
            err_msg=err_msg, result_size=res_size)
    

@app.route('/database/<action>', methods=["GET", "POST"])
def database(action):
    err_msg = ""
    if request.form:
        if action == "add":
            data = request.form
            player_data =getData(data)
            if check_notempty(player_data):
                err_msg = insertPlayer(player_data)
                return render_template('database.html', action = 'start', err_msg = err_msg)
    return render_template('database.html', action = action, err_msg = err_msg)