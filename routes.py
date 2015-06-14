from datetime import datetime
from flask import render_template, session, redirect, request, make_response, url_for
import json
from app import app
from oauth import OAuthSignIn
import twitchrecommender
import time
import sys

@app.route('/', methods=['GET','POST'])
def home():

    if( not 'isAnonymous' in session):
        if('oauth_access_token' in session and session['oauth_access_token'] != ''):
            session['isAnonymous'] = False
        else:
            auth = OAuthSignIn(app)
            #random username used for recommendation storage
            session['username'] = auth.generateRandomUsername()
            session['isAnonymous'] = True

    if ('oauth_access_token' in session and session['oauth_access_token'] != '') or ('isAnonymous' in session and session['isAnonymous'] == False):
        try:
            return render_template('index.jade',title = 'Home Page',year = datetime.now().year, username=session['username'], isAnonymous = session['isAnonymous'])
        except Exception as e:
            print e, 'A'
    else:
        try:
            return render_template('index.jade',title = 'Home Page',year = datetime.now().year, username='', isAnonymous = session['isAnonymous'])

        except Exception as e:
            print e, 'C'
            return redirect(url_for('error'))

@app.route('/recommend/')
def recommend():
    try:

        _recommendations = twitchrecommender.generateRecommendationListForUser(session['username'])

        #if user is not logged in or does not have a random username assigned, then we should give them one
        if((not 'username' in session) or session['username'] == ''):
            auth = OAuthSignIn(app)
            session['username'] = auth.generateRandomUsername()
            session['isAnonymous'] = True

        twitchrecommender.storeFollowerRecommendations(session['username'],_recommendations)
        session['rec_time_out'] = time.time() + 900
        session['dir'] = 'up'
        return redirect(url_for('recommendations', rank=1))
    except Exception as e:

        print e, 'B', sys.exc_traceback.tb_lineno

@app.route('/recommendations/<int:rank>')
def recommendations(rank):
    if not ('rec_time_out' in session) or time.time() > session['rec_time_out']:
        return redirect(url_for('recommend'))



    recommendation = twitchrecommender.retrieveFollowerRecommendation(session['username'], rank - 1)

    channelInfo = twitchapiretriever.getChannelInfo(app.)

    if(channelInfo["stream"] == None):
        return render_template('recommendations.jade',
            isAnonymous = session['isAnonymous'],
            channel = recommendation[0],
            game=recommendation[1],
            offline = True,
            rank = rank)
    else:
            return render_template('recommendations.jade',
                isAnonymous = session['isAnonymous'],
                channel = recommendation[0],
                game=recommendation[1],
                offline = False,
                logo = channelInfo["stream"]["logo"],
                banner = channelInfo["stream"]["banner"],
                display_name = channelInfo["stream"]["display_name"],
                rank = rank)

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
            auth = OAuthSignIn(app)
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
    auth = OAuthSignIn(app)
    return auth.authorize()

@app.route('/callback/')
def oauth_callback():
    try:
        auth = OAuthSignIn(app)
        return auth.callback()
    except Exception as e:
        print e
        auth = OAuthSignIn(app)
        session['username'] = auth.generateRandomUsername()
        session['isAnonymous'] = True
        return redirect(url_for('home'))

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
