import os

from flask import Flask, session, redirect, request, url_for, jsonify
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = os.urandom(24)

client_id = r'psM7rv52RLCFdTsK_lQVWg'
redirect_uri = r'https://zoomcounter.herokuapp.com/callback'
auth_uri = r'https://zoom.us/oauth/authorize'
token_uri = r'https://zoom.us/oauth/token'
meetings_uri = r'https://api.zoom.us/v2/users/me/meetings'


@app.route('/login')
def login():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(auth_uri)
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/callback', methods=['GET'])
def callback():
    token = request.args.get('code')
    session['oauth_token'] = token
    return redirect(url_for('.counts'))


@app.route('/counts', methods=['GET'])
def counts():
    oauth = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(oauth.get(meetings_uri).json())
