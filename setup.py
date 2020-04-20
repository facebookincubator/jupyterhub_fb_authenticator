#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup


setup(
    name="jupyterhub-fbauthenticator",
    version="0.1",
    description="FB Authenticator for Jupyterhub",
    author="Facebook",
    author_email="researchtool-help@fb.com",
    url="https://www.facebook.com/",
    packages=["fbauthenticator"],
)
