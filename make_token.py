from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

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

with open("url.txt", "w", encoding="utf-8") as f:
    f.write(auth_url)

print("URL_WRITTEN_SUCCESS")

creds = flow.run_local_server(port=PORT, open_browser=False)

with open(token_file, 'wb') as token:
    pickle.dump(creds, token)

print("SUCCESS_TOKEN_CREATED")
