# -*- coding: utf-8 -*-
"""Implements a simple wrapper around urlopen."""
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
#import urllib.request

#from pytube.compat import urlopen
# 403 forbidden fix

import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse, urlsplit, parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError


	# Aufruf streams: class Stream, method download
def get(
	url=None, headers=False,
	streaming=False, chunk_size=8 * 1024,):
	"""Send an http GET request.

	:param str url:
		The URL to perform the GET request for.
	:param bool headers:
		Only return the http headers.
	:param bool streaming:
		Returns the response body in chunks via a generator.
	:param int chunk_size:
		The size in bytes of each chunk.
	"""

	# https://github.com/nficano/pytube/pull/465
	# req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	response = urlopen(req); #print "get_url: " + url
	

	if streaming:
		return stream_response(response, chunk_size)
	elif headers:
		# https://github.com/nficano/pytube/issues/160
		return {k.lower(): v for k, v in response.info().items()}
	return (
		response
		.read()
		.decode('utf-8')
	)


def stream_response(response, chunk_size=8 * 1024):
	"""Read the response in chunks."""
	while True:
		buf = response.read(chunk_size)
		if not buf:
			break
		yield buf
