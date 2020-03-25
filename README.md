# JupyterHub Facebook Authenticator
JupyterHub Facebook Authenticator is a Facebook OAuth authenticator built on top of OAuthenticator


## How FBAuthenticator works
Enable FBAuthenticator in jupyterhub_config.py
```python
from fbauthenticator.authenticator import FBAuthenticator
c.JupyterHub.authenticator_class = FBAuthenticator
c.FBAuthenticator.client_id = 'app_id'
c.FBAuthenticator.client_secret = 'app_secret'
```

See the [CONTRIBUTING](CONTRIBUTING.md) file for how to help out.

## License
JupyterHub Facebook Authenticator is licensed under the [LICENSE](LICENSE) file in the root directory of this source tree.
