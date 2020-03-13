#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.


import json
import os

from jupyterhub.auth import LocalAuthenticator
from oauthenticator.oauth2 import OAuthenticator, OAuthLoginHandler
from tornado import gen
from tornado.auth import OAuth2Mixin
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
from traitlets import Bool, Dict, Unicode


class GenericEnvMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = os.environ.get("OAUTH2_AUTHORIZE_URL", "")
    _OAUTH_ACCESS_TOKEN_URL = os.environ.get("OAUTH2_TOKEN_URL", "")


class FBLoginHandler(OAuthLoginHandler, GenericEnvMixin):
    pass


class FBAuthenticator(OAuthenticator):

    login_service = Unicode("Facebook", config=True)

    login_handler = FBLoginHandler

    token_url = Unicode(
        os.environ.get("OAUTH2_TOKEN_URL", ""),
        config=True,
        help="Access token endpoint URL",
    )
    extra_params = Dict(help="Extra parameters for first POST request").tag(config=True)

    tls_verify = Bool(
        os.environ.get("OAUTH2_TLS_VERIFY", "True").lower() in {"true", "1"},
        config=True,
        help="Disable TLS verification on http request",
    )

    async def _http_get(self, url):
        http_client = AsyncHTTPClient()
        headers = {"Accept": "application/json", "User-Agent": "JupyterHub"}
        req = HTTPRequest(
            url, method="GET", headers=headers, validate_cert=self.tls_verify
        )
        resp = await http_client.fetch(req)
        return json.loads(resp.body.decode("utf8", "replace"))

    async def _get_user_name(self, access_token):
        url = f"https://graph.facebook.com/me?fields=name&access_token={access_token}"
        resp_json = await self._http_get(url)
        return resp_json["name"]

    async def authenticate(self, handler, data=None):
        code = handler.get_argument("code")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.get_callback_url(handler),
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        params.update(self.extra_params)

        if self.token_url:
            url = self.token_url
        else:
            raise ValueError("Please set the OAUTH2_TOKEN_URL environment variable")

        url = url_concat(url, params)
        resp_json = await self._http_get(url)

        access_token = resp_json["access_token"]
        user_name = await self._get_user_name(access_token)
        return {
            "name": user_name,
            "auth_state": {
                "access_token": access_token,
                "fb_user": {"username": user_name},
            },
        }

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            return

        spawner.environment["FB_TOKEN"] = auth_state["access_token"]


class LocalFBAuthenticator(LocalAuthenticator, FBAuthenticator):
    """A version that mixes in local system user creation"""

    pass
