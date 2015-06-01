from datetime import datetime
from flask import render_template, session, redirect, request, make_response
import json
from app import app
from oauth import OAuthSignIn
import twitchrecommender


@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():


    if 'oauth_access_token' in session and session['oauth_access_token'] != '':

        return render_template(
            'index.jade',
            title = 'Home Page',
            year = datetime.now().year,
        )
    else:
        auth = OAuthSignIn()
        return auth.authorize()

@app.route('/recommend/')
def recommend():
    try:
        recommendations = twitchrecommender.generateRecommendationListForUser(session['username'])
    except Exception as e:
        print e
    return make_response(json.dumps(recommendations))

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
        del session['oauth_access_token']

@app.route('/about')
def about():
    return render_template(
        'about.jade',
        title = 'About',
        year = datetime.now().year,
        message = 'Your application description page.'
    )

