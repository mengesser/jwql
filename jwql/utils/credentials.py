"""Utility functions related to accessing remote services and databases.

Authors
-------

    - Johannes Sahlmann

Use
---

    This module can be imported as such:

    >>> import credentials
    token = get_mast_token()

 """
import os

from astroquery.mast import Mast

from jwql.utils.utils import get_config


def get_mast_token(request=None):
    """Return MAST token."""
    if Mast.authenticated():
        print('Authenticated with Astroquery MAST magic')
        return None
    else:
        if request is not None:
            token = str(request.POST.get('access_token'))
            if token != 'None':
                print('Authenticated with cached MAST token.')
                return token
        try:
            # check if token is available via config file
            settings = get_config()
            token = settings['mast_token']
            print('Authenticated with config.json MAST token.')
            return token
        except KeyError:
            # check if token is available via environment variable
            # see https://auth.mast.stsci.edu/info
            try:
                token = os.environ['MAST_API_TOKEN']
                print('Authenticated with MAST token environment variable.')
                return token
            except KeyError:
                return None
