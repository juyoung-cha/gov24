from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials_file = "credentials.json"
token_file = "token.pickle"

flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file, 
    SCOPES, 
    redirect_uri='http://localhost:8080/'
)

print("Starting local server on port 8080...")
creds = flow.run_local_server(port=8080, open_browser=False)

with open(token_file, 'wb') as token:
    pickle.dump(creds, token)

print("SUCCESS_TOKEN_CREATED")
