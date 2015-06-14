from datetime import datetime
from flask import render_template, session, redirect, request, make_response, url_for
import json
from app import app
from oauth import OAuthSignIn
import twitchrecommender
import time


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
        _recommendations = twitchrecommender.generateRecommendationListForUser(session['username'])
        session['recommendations'] = _recommendations
        session['recTimeOut'] = time.time() + 900
        return redirect(url_for('recommendations', id=1))
    except Exception as e:
        print e, 'B'

@app.route('/recommendations/<int:id>')
def recommendations(id):
    if not ('recTimeOut' in session and 'recommendations' in session):
        return redirect(url_for('recommend'))

    _recommendations = session['recommendations']

    if (id < 1 or id > len(_recommendations)):
        return redirect(url_for('recommend'))

    return render_template('recommendations.jade', channel = session['recommendations'][id])

@app.route('/preauth', methods=['GET','POST'])
def preauth():
    try:
        print request.method
        if(request.method == 'POST'):

            scope_list =  list(request.form)
            auth_scope = 'user_read'
            if(len(scope_list) > 0):
                for i in range(0, len(scope_list)):
                    auth_scope += '+' + scope_list[i]
            auth = OAuthSignIn()
            return auth.authorize(auth_scope)
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
