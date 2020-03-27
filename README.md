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

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
JupyterHub Facebook Authenticator is licensed under the [LICENSE](LICENSE) file in the root directory of this source tree.
