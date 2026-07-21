from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import sys

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials_file = "credentials.json"
token_file = "token.pickle"

flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file, 
    SCOPES,
    redirect_uri='http://localhost:8099/'
)

auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')

with open("auth_url.txt", "w", encoding="utf-8") as f:
    f.write(auth_url)

print("URL_SAVED", flush=True)

creds = flow.run_local_server(port=8099, open_browser=False)

with open(token_file, 'wb') as token:
    pickle.dump(creds, token)

print("SUCCESS_TOKEN_CREATED", flush=True)
