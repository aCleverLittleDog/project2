import os
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, session, render_template, request, g, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'
socketio = SocketIO(app)
metadata = MetaData()
engine = create_engine(os.getenv("PROJECT1_DATABASE"))
Session = sessionmaker(bind=engine)
db = Session()
Base = declarative_base()
Base.metadata.create_all(engine)
channelList = {}


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

@app.before_request
def before():
    session.permanent = True
    if 'last' in session:
        last = session['last']
        session.pop('last', None)
        return redirect(url_for('channel', channelName = last))

@app.route('/')
def index():
    if 'last' in session and 'username' in session:
        return redirect(url_for('channel', channelName=session['last']))
    else:
        return redirect(url_for('home'))

@app.route("/home")
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        if db.query(Users).filter(Users.username == request.form['username'])\
        .count() >= 1 and db.query(Users).filter(Users.username==\
        request.form['username']).first().password==request.form['password']:
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        elif db.query(Users).filter(Users.username==request.form['username']).count()==0:
            newUser=Users(username=request.form['username'], password=request.form['password'])
            db.add(newUser)
            db.commit()
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            session.pop('username', None)
            return render_template('login.html', failed=True)
    else:
        session.pop('username', None)
        return render_template('login.html')

@app.route('/channels')
def channels():
    if 'username' in session:
        return render_template('channels.html', channelList=channelList, username=session['username'])
    else:
        return redirect(url_for('home'))

@app.route('/channel/<channelName>')
def channel(channelName):
    if 'username' in session:
        session['last'] = channelName
        return render_template('channel.html', previous=channelList[channelName][1:], channelName=channelName, username=session['username'])
    else:
        return redirect(url_for('home'))

@socketio.on('new message')
def send(data):
    message = data['message']
    author = data['author']
    currentTime = time.asctime()
    channelName = data['channel']
    channelList[channelName].append('{} {}: {}'.format(author, currentTime, message))
    socketio.emit('messages updated', channelList, broadcast=True)

@app.route('/createChannel', methods = ['GET', 'POST'])
def createChannel():
    if 'username' in session:
        if request.method == 'POST':
            if request.form['channelName'] in channelList:
                return render_template('createChannel.html', failed=True)
            else:
                channelList[request.form['channelName']] = [session['username']]
                return redirect(url_for('channels'))
        else:
            return render_template('createChannel.html')
    else:
        redirect(url_for('home'))
