#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Custom Jupyterhub Authenticator to use Facebook OAuth with business manager check.
"""

import json
import os
import urllib

from tornado.web import HTTPError

from .authenticator import FBAuthenticator


class FBBusinessAuthenticator(FBAuthenticator):

    BUSINESS_ID = os.environ.get("BUSINESS_ID")

    async def authorize(self, access_token, user_id):
        # check if the user has business management permission
        if not await self._check_permission(access_token, "business_management"):
            self.log.warning(
                "User %s doesn't have business management permission", user_id
            )
            raise HTTPError(
                403, "Your access token doesn't have the required permission"
            )
        self.log.info("User %s passed business management permission check", user_id)

        # check if the user is in the business
        if not await self._check_in_business(access_token):
            self.log.warning(
                "User %s is not in the business %s", user_id, self.BUSINESS_ID
            )
            raise HTTPError(403, "Your are not in the business yet")
        self.log.info("User %s passed business check", user_id)

        return {
            "name": user_id,
            "auth_state": {
                "access_token": access_token,
                "fb_user": {"username": user_id},
            },
        }

    async def _check_permission(self, access_token, permission):
        """
        Return true if the user has the given permission, false if not.
        Throw a HTTP 500 error otherwise.
        """
        try:
            url = f"{FBAuthenticator.FB_GRAPH_EP}/me/permissions/?permission={permission}&access_token={access_token}"
            with urllib.request.urlopen(url) as response:
                body = response.read()
                permission = json.loads(body).get("data")
                return permission and permission[0]["status"] == "granted"
        except Exception:
            raise HTTPError(500, "Failed to check permission")

    async def _check_in_business(self, access_token):
        """
        Return true if the user is in the given business, false if not.
        Throw a HTTP 500 error otherwise.
        """
        # TODO: Handle pagenation
        try:
            url = f"{FBAuthenticator.FB_GRAPH_EP}/me/business_users/?business={self.BUSINESS_ID}&access_token={access_token}"
            with urllib.request.urlopen(url) as response:
                body = response.read()
                body_json = json.loads(body)
                return body_json["data"]
        except Exception:
            raise HTTPError(500, "Authorization failed")
