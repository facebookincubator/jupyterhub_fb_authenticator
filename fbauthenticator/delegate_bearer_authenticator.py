#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Custom Jupyterhub Authenticator to use Facebook OAuth with a delegate endpoint.
i.e. delegate the authorizer decision to a custom authorizer
"""

import urllib
import urllib.error

from tornado.web import HTTPError

from traitlets import Enum, List, Unicode

from .authenticator import FBAuthenticator


class FBDelegateBearerAuthenticator(FBAuthenticator):

    EXPECTED_ERROR_CODES = [400, 401, 403]

    # Override if necessary
    scope = List(Unicode(), ["email"], config=True, help="The OAuth scopes to request.")

    # Override to value of the endpoint you wish to call.
    endpoint = Unicode(config=True, help="Bearer endpoint to auth via.")

    auth_header = Unicode(
        "Authorization", config=True, help="Header to use for Bearer validation."
    )

    auth_header_format = Unicode(
        r"Bearer {}", config=True, help="Header format string to use for Bearer."
    )

    auth_http_verb = Enum(
        ["POST", "GET"],
        "POST",
        config=True,
        help="Whether to use a POST or GET for the request.",
    )

    async def authorize(self, access_token, user_id):
        # call the endpoint, and verify we get a 200 response
        header_value = self.auth_header_format.format(access_token)
        headers = {}
        headers[self.auth_header] = header_value
        data = b"" if self.auth_http_verb == "POST" else None

        try:
            self.log.info(
                "Attempting to authorize user %s via endpoint %s",
                user_id,
                self.endpoint,
            )
            auth_req = urllib.request.Request(self.endpoint, data=data, headers=headers)
            with urllib.request.urlopen(auth_req) as response:
                # If we're here, the user has passed authorization via the delegate.
                body = response.read()
                self.log.info("Auth response for user %s: %s", user_id, body)
                return {
                    "name": user_id,
                    "auth_state": {
                        "access_token": access_token,
                        "fb_user": {"username": user_id},
                    },
                }
        except urllib.error.HTTPError as e:
            if e.code in self.EXPECTED_ERROR_CODES:
                self.log.warning("User failed delegate Auth Check", exc_info=True)
                raise HTTPError(
                    403, f"You are not authorized (delegate code: {e.code})"
                )
            else:
                self.log.exception(
                    "Authorization failed with an unexpected HTTPError code"
                )
                # We don't expect this code - treat as internal server error.
                raise HTTPError(500, f"Authorization failed (delegate code: {e.code})")

        except Exception:
            # We don't expect this exception - treat as internal server error.
            self.log.exception("Authorization failed with an unexpected exception")
            raise HTTPError(500, "Authorization failed")
