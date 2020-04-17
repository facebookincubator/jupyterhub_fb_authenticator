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

    scope = ["business_management", "email"]

    BUSINESS_ID = os.environ.get("BUSINESS_ID")
    PAGE_THRESHOLD = 100

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
        try:
            url = f"{FBAuthenticator.FB_GRAPH_EP}/me/business_users?access_token={access_token}"
            with urllib.request.urlopen(url) as response:
                body = response.read()
                body_json = json.loads(body)
                return await self._check_in_page(body_json, 1)
        except Exception:
            raise HTTPError(500, "Authorization failed")

    async def _check_in_page(self, body_json, current_page):
        """
        Return false if the current page is larger thatn the threshold.
        Return true if the user is in the given page.
        Then recursively check the next page if it exists, return false if not.
        Throw a HTTP 500 error otherwise.
        """
        if current_page > self.PAGE_THRESHOLD:
            return False

        if self._has_business(body_json["data"]):
            return True

        paging = body_json.get("paging", {})
        if "next" not in paging:
            return False

        try:
            next_page_url = paging["next"]
            with urllib.request.urlopen(next_page_url) as response:
                body = response.read()
                return await self._check_in_page(json.loads(body), current_page + 1)
        except Exception:
            raise HTTPError(500, "Authorization failed")

    def _has_business(self, data):
        """
        Given the data of one page of business users, check if the user is in the business.
        Return true if the user is in the business, false otherwise.
        """
        return any(
            "business" in entry
            and "id" in entry["business"]
            and entry["business"]["id"] == self.BUSINESS_ID
            for entry in data
        )
