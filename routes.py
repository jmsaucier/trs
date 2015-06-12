from datetime import datetime
from flask import render_template, session, redirect, request, make_response, url_for
import json
from app import app
from oauth import OAuthSignIn
import twitchrecommender


@app.route('/', methods=['GET','POST'])
def home():
    if 'oauth_access_token' in session and session['oauth_access_token'] != '':
        try:
            return render_template('index.jade',title = 'Home Page',year = datetime.now().year, username=session['username'])
        except Exception as e:
            print e, 'A'
    else:
        try:

            return render_template('index.jade',title = 'Home Page',year = datetime.now().year, username='')

        except Exception as e:
            print e, 'C'

@app.route('/recommend/')
def recommend():
    try:
        recommendations = twitchrecommender.generateRecommendationListForUser(session['username'])
        return make_response(json.dumps(recommendations))
    except Exception as e:
        print e, 'B'

@app.route('/preauth', methods=['GET','POST'])
def preauth():
    #if(request.method == 'POST'):
    #    auth = OAuthSignIn()
    #    return auth.authorize()
    try:
        return render_template('preauth.jade', title = 'Pre Auth', UrlFor = url_for('preauth'))
    except Exception as e:
        print e
@app.route('/error')
def error():
    return render_template()

@app.route('/contact')
def contact():
    return render_template(
        'contact.jade',
        title = 'Contact',
        year = datetime.now().year,
        message = 'Your contact page.'
    )

@app.route('/authorize/')
def oauth_authorize():
    auth = OAuthSignIn()
    return auth.authorize()

@app.route('/callback/')
def oauth_callback():
    auth = OAuthSignIn()
    return auth.callback()

@app.route('/logout')
def logout():
    if('oauth_access_token' in session):
        session['oauth_access_token'] = ''
        session['username'] = ''
    return redirect(url_for('home'))
@app.route('/about')
def about():
    return render_template(
        'about.jade',
        title = 'About',
        year = datetime.now().year,
        message = 'Your application description page.'
    )
