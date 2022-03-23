import os

from flask import Flask, session, redirect, request, url_for, jsonify
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

client_id = r'psM7rv52RLCFdTsK_lQVWg'
client_secret = r'qLE3u890k24CUL0fgQd8SbsjAHOftS4s'
redirect_uri = r'https://zoomcounter.herokuapp.com/callback'
auth_uri = r'https://zoom.us/oauth/authorize'
token_uri = r'https://zoom.us/oauth/token'
meetings_uri = r'https://api.zoom.us/v2/users/me/meetings'


@app.route('/')
def main():
    return "Nothing to see here."


@app.route('/login')
def login():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, _ = oauth.authorization_url(auth_uri)

    return redirect(authorization_url)


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    session['oauth_state'] = state

    oauth = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = oauth.fetch_token(token_uri,
                              code=code,
                              client_secret=client_secret,
                              kwargs={'grant_type': 'authorization_code'})
    session['oauth_token'] = token

    return redirect(url_for('.counts'))


@app.route('/counts', methods=['GET'])
def counts():
    oauth = OAuth2Session(client_id, token=session['oauth_token'])

    r = oauth.get(meetings_uri).json()
    meetings = r['meetings']
    print(meetings)

    meeting_count = {}
    if len(meetings) > 0:
        for meeting in meetings:
            if meeting['type'] == 2:
                meeting_id = meeting['id']
                print(meeting_id)
                part_uri = f'https://api.zoom.us/v2/metrics/meetings/{meeting_id}/participants'
                r = oauth.get(part_uri, params={'page_size': 300}).json()
                print(r)
                users = r['participants']
                meeting_count[meeting_id] = len(users)
        return jsonify(meeting_count)
    else:
        return "No results found."
