from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Your credentials from the JSON file
CLIENT_ID = "591932580986-12oao8majro9aft4hfejdl8qsbvat9o0.apps.googleusercontent.com"
CLIENT_SECRET = "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"

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Create flow
flow = InstalledAppFlow.from_client_secrets_file(
    "YT Bot.json",  # Your JSON file
    scopes=SCOPES
) 

# Run local server auth
credentials = flow.run_local_server(port=8080)

# Print refresh token
print("=" * 50)
print("REFRESH TOKEN:")
print(credentials.refresh_token)
print("=" * 50)