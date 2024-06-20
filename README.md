# JupyterHub Facebook Authenticator
JupyterHub Facebook Authenticator is a Facebook OAuth authenticator built on top of OAuthenticator


## How FBAuthenticator works
1. Extend FBAuthenticator by implementing the authorize function
2. Enable the new authenticator in Jupyterhub_config.py
Example:
```python
from fbauthenticator.business_authenticator import FBBusinessAuthenticator
c.JupyterHub.authenticator_class = FBBusinessAuthenticator
c.FBBusinessAuthenticator.client_id = 'app_id'
c.FBBusinessAuthenticator.client_secret = 'app_secret'
```
## authenticator.py
### Functions
```python
async def authenticate(self, handler, data=None)
# Authenticates a user with self-set OAuth parameters
async def _http_get(self, url)
# Fetches JSON data using the token URL + params
async def _get_user_id(self, access_token)
# Return user id of the given user; throw a HTTP 500 error otherwise
async def authorize(self, access_token, user_id)
# To be implemented
def _get_app_secret_proof(self, access_token)
# Generate the app_secret_proof
def pre_spawn_start(self, user, spawner)
# Sets user's access token in spawner environment for use in spawned processes, if it exists
```
## business_authenticator.py
### Functions
```python
async def authorize(self, access_token, user_id)
# Authorizes user if this user has the business management role and/or if this user is in the business
async def _check_permission(self, access_token, permission, proof)
# Return true if the user has the given permission, false if not; throw a HTTP 500 error otherwise
async def _check_in_business(self, access_token, proof)
# Return true if the user is in the given business, false if not; throw a HTTP 500 error otherwise
async def _check_in_page(self, body_json, current_page)
# Return false if the current page is larger than the threshold. Return true if the user is in the given page. Then recursively check the next page if it exists, return false if not. Throw a HTTP 500 error otherwise.
def _has_business(self, data)
# Given the data of one page of business users, check if the user is in the business. Return true if the user is in the business, false otherwise.
```
## delegate_bearer_authenticator.py
### Functions
```python
async def authorize(self, access_token, user_id)
# Authorizes the user via a specified endpoint
```

## Example
See example_jupyterhub_config.py for an example configuration

## Contributions

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
JupyterHub Facebook Authenticator is licensed under the [LICENSE](LICENSE) file in the root directory of this source tree.
