import dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect

APP_KEY = "2swacmcpls2cxk7"
APP_SECRET = "5wa5a37ec9nmd5j"

auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type="offline")
authorize_url = auth_flow.start()
print("1. Go to: " + authorize_url)
print("2. Click 'Allow' and copy the authorization code.")

auth_code = input("Enter the authorization code here: ").strip()
oauth_result = auth_flow.finish(auth_code)

print("ACCESS TOKEN:", oauth_result.access_token)
print("REFRESH TOKEN:", oauth_result.refresh_token)
