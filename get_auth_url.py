from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger']
credentials_file = "credentials.json"

flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file, 
    SCOPES, 
    redirect_uri='http://localhost:8080/'
)
auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

print("AUTH_URL_START")
print(auth_url)
print("AUTH_URL_END")
