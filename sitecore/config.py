"""
Sitecore config module for setting the Shortcode Parser delimiters.
Note: it was not possible to set these as part of the SiteSettings approach, as that
works on a per site basis. At the validator stage, the site context is NOT available,
and hence it's not possible to retrieve settings for an unknown site.
:Authors: Louise Lever <louise.lever@manchester.ac.uk>
:Copyright: Research IT, IT Services, The University of Manchester
"""

START = '['
END = ']'
ESC = '\\'
