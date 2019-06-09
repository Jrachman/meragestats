from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix

# In case the `redirect_url` does not implement https
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Credentials you get from registering a new application
client_id = '86w4tfg7kx22i0'
client_secret = 'o8luvlt8hoYOC0LN'
redirect_url = 'http://localhost:3000/auth/linkedin/callback'

# OAuth endpoints given in the LinkedIn API documentation (check for updates)
authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

# Authorized Redirect URL (from LinkedIn config)
linkedin = OAuth2Session(client_id, redirect_uri=redirect_url)
linkedin = linkedin_compliance_fix(linkedin)

# Redirect user to LinkedIn for authorization
authorization_url, state = linkedin.authorization_url(authorization_base_url)
print('Please go here and authorize,', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('Paste the full redirect URL here:').strip()

# Fetch the access token
linkedin.fetch_token(token_url, include_client_id=True, client_secret=client_secret, authorization_response=redirect_response)

# Fetch a protected resource, i.e. user profile
r = linkedin.get('https://api.linkedin.com/v2/people/~?format=json')
print(r.content)
