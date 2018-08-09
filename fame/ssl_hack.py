"""SSL hack for disabling HTTPS host check.

Source: https://www.python.org/dev/peps/pep-0476/
"""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer'

import ssl


def disable_ssl_host_check():
    """Never use in production!"""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default.
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification.
        ssl._create_default_https_context = _create_unverified_https_context
