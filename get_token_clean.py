import os
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import wsgiref.simple_server
from urllib.parse import urlunparse

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials_file = "credentials.json"
token_file = "token.pickle"
PORT = 8099

flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file, 
    SCOPES,
    redirect_uri=f'http://localhost:{PORT}/'
)

auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')

with open("clean_url.txt", "w", encoding="utf-8") as f:
    f.write(auth_url)

print("URL_READY", flush=True)

auth_response = None

def app(environ, start_response):
    global auth_response
    scheme = environ['wsgi.url_scheme']
    netloc = environ['HTTP_HOST']
    path = environ['PATH_INFO']
    query = environ.get('QUERY_STRING', '')
    auth_response = urlunparse((scheme, netloc, path, '', query, ''))
    
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return ["<h1>인증 성공! 이 탭을 닫으셔도 됩니다.</h1>".encode('utf-8')]

httpd = wsgiref.simple_server.make_server('localhost', PORT, app)
httpd.handle_request()

flow.fetch_token(authorization_response=auth_response)

with open(token_file, 'wb') as token:
    pickle.dump(flow.credentials, token)

print("SUCCESSFULLY_SAVED_TOKEN", flush=True)
