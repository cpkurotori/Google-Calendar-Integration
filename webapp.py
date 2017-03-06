import json

import flask
import httplib2

from quickstart import createEventBody

from apiclient import discovery
from oauth2client import client



app = flask.Flask(__name__)

@app.route('/')
def index():
  return app.send_static_file("index.html")

@app.route('/main', methods=['POST'])
def main():
  course = flask.request.form['course']
    section = flask.request.form['section']
    course_sec = course+'-'+section
    desc = flask.request.form['description']
    days = ""
    da = ['MO','TU','WE','TH','FR','SA']
    for x in da:
      if not flask.request.form[x]=="":
        if not days == "":
          days = x
        else:
          days = days + "," + x
    startt_uf = flask.request.form['startt']
    startd = flask.request.form['startd']
    endt_uf = flask.request.form['endt']
    endd_uf = flask.request.form['endd']
    endd = endd_uf.replace("-","")
    startt = startt_uf+":00-08:00"
    endt = endt_uf+":00-08:00"
    notes = flask.request.form['notes']
  if 'credentials' not in flask.session:
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    page_token = None
    dupCalFound = False
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == "2017 Spring Schedule":
          calendarid = calendar_list_entry['id']
          dupCalFound = True
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    if not dupCalFound:
      calendar = {
        'summary' : '2017 Spring Schedule',
        'timeZone' : 'America/Los_Angeles'
      }
      created_calendar = service.calendars().insert(body=calendar).execute()
      print('Calendar Created...')
      calendarid = created_calendar['id']
    event = createEventBody(course_sec,desc,days,startt,startd,endt,endd,notes)
    event = service.events().insert(calendarId=str(calendarid), body=event).execute()
    return flask.redirect(flask.url_for('index'))
@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secret2.json',
      scope='https://www.googleapis.com/auth/calendar',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = True
  app.run()