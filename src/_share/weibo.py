#!/usr/bin/python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import config
import urlparse
import pycurl
import StringIO
import urllib
import json
import time
import hashlib
import hmac
import commands
import subprocess
from mimetypes import guess_type
import tencent

CONFIG = config.WeiboConfig()

def get_file_type(filename):
    '''get image file type'''
    file_type = guess_type(filename)
    if file_type is None or file_type[0] is None:
        return None
    return file_type[0]

def _encode_multipart(**kw):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            ext = ''
            filename = getattr(v, 'name', '')
            n = filename.rfind('.')
            if n != (-1):
                ext = filename[n:].lower()
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, filename))
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % get_file_type(filename))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary

class OAuth(object):
    '''Weibo OAuth'''
    def __init__(self, t_type=''):
        self.config = CONFIG
        self.t_type = t_type
    
    def get(self, opt=None):
        '''get info'''
        return self.config.get(self.t_type, opt)
    
    def set(self, **kw):
        '''set info'''
        self.config.set(self.t_type, **kw)
    
    def __getattr__(self, kw):
        ''' __getattr__'''
        return self.get(kw)

class Curl(object):
    '''Curl Class'''
    def twitter_get(self, url, header=None):
        '''get url for twitter'''
        crl = pycurl.Curl()
        #crl.setopt(pycurl.VERBOSE,1)

        # set proxy
        crl.setopt(pycurl.URL, 'http://facebook.com')
        crl.setopt(pycurl.PROXY, '127.0.0.1')
        crl.setopt(pycurl.PROXYPORT, 8087)
        # set ssl
        crl.setopt(pycurl.SSL_VERIFYPEER, 0)
        crl.setopt(pycurl.SSL_VERIFYHOST, 0)
         
        crl.setopt(pycurl.CONNECTTIMEOUT, 10)
        crl.setopt(pycurl.TIMEOUT, 300)
        crl.setopt(pycurl.HTTPPROXYTUNNEL,1)

        if header:
            crl.setopt(pycurl.HTTPHEADER, header)

        crl.fp = StringIO.StringIO()
         
        if isinstance(url, unicode):
            url = str(url)
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        try:
            crl.perform()
        except:
            return None
        crl.close()
        con = crl.fp.getvalue()
        crl.fp.close()
        return con

    def get(self, url, header=None):
        '''get to url'''
        crl = pycurl.Curl()
        #crl.setopt(pycurl.VERBOSE,1)

        # set proxy
        crl.setopt(pycurl.URL, 'http://facebook.com')
        crl.setopt(pycurl.PROXY, '127.0.0.1')
        crl.setopt(pycurl.PROXYPORT, 8087)
        # set ssl
        crl.setopt(pycurl.SSL_VERIFYPEER, 0)
        crl.setopt(pycurl.SSL_VERIFYHOST, 0)
         
        crl.setopt(pycurl.CONNECTTIMEOUT, 10)
        crl.setopt(pycurl.TIMEOUT, 300)
        crl.setopt(pycurl.HTTPPROXYTUNNEL,1)

        if header:
            crl.setopt(pycurl.HTTPHEADER, header)

        crl.fp = StringIO.StringIO()
         
        if isinstance(url, unicode):
            url = str(url)
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        try:
            crl.perform()
        except:
            return None
        crl.close()
        try:
            back = json.loads(crl.fp.getvalue())
            crl.fp.close()
            return back
        except:
            return None
    
    def post(self, url, data, header=None):
        '''post to url'''
        crl = pycurl.Curl()
        #crl.setopt(pycurl.VERBOSE,1)

        # set proxy
        crl.setopt(pycurl.URL, 'http://facebook.com')
        crl.setopt(pycurl.PROXY, '127.0.0.1')
        crl.setopt(pycurl.PROXYPORT, 8087)
        # set ssl
        crl.setopt(pycurl.SSL_VERIFYPEER, 0)
        crl.setopt(pycurl.SSL_VERIFYHOST, 0)
         
        crl.setopt(pycurl.CONNECTTIMEOUT, 10)
        crl.setopt(pycurl.TIMEOUT, 300)
        crl.setopt(pycurl.HTTPPROXYTUNNEL,1)

        if header:
            crl.setopt(pycurl.HTTPHEADER, header)

        crl.fp = StringIO.StringIO()
         
        crl.setopt(crl.POSTFIELDS, urllib.urlencode(data))  # post data
        #crl.setopt(crl.POSTFIELDS, data)
        if isinstance(url, unicode):
            url = str(url)
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        try:
            crl.perform()
        except:
            return None
        crl.close()
        try:
            back = json.loads(crl.fp.getvalue())
            crl.fp.close()
            return back
        except:
            return None
    
    def upload(self, url, data, header=None):
        '''upload to url'''
        print "upload:", url, data, header
        crl = pycurl.Curl()
        #crl.setopt(pycurl.VERBOSE,1)

        # set proxy
        crl.setopt(pycurl.URL, 'http://facebook.com')
        crl.setopt(pycurl.PROXY, '127.0.0.1')
        crl.setopt(pycurl.PROXYPORT, 8087)
        # set ssl
        crl.setopt(pycurl.SSL_VERIFYPEER, 0)
        crl.setopt(pycurl.SSL_VERIFYHOST, 0)
         
        crl.setopt(pycurl.CONNECTTIMEOUT, 60)
        crl.setopt(pycurl.TIMEOUT, 300)
        crl.setopt(pycurl.HTTPPROXYTUNNEL,1)
        
        #crl.setopt(pycurl.HTTPHEADER, ["Expect: "])
        if header:
            crl.setopt(pycurl.HTTPHEADER, header)

        crl.fp = StringIO.StringIO()
              
        if isinstance(url, unicode):
            url = str(url)
        crl.setopt(pycurl.URL, url)
        crl.setopt(pycurl.HTTPPOST, data)   # upload file
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        crl.perform()
        crl.close()
        conn = crl.fp.getvalue()
        print "upload------------------------\n", conn
        try:
            #back = json.loads(crl.fp.getvalue())
            back = json.loads(conn)
            crl.fp.close()
            return back
        except:
            return None
        
class Weibo():
    '''Weibo base class'''
    def __init__(self, t_type, webkit):
        self.webkit = webkit
        self.t_type = t_type
        self.oauth = OAuth(t_type)
        self.curl = Curl()

    def set_box(self, box):
        '''set a gtk.Box'''
        self.box = box

    def get_box(self):
        '''get a gtk.Box'''
        return self.box
    
    def get(self, opt=None):
        '''get config value'''
        return self.oauth.get(opt)
    
    def set(self, **kw):
        '''set config value'''
        self.oauth.set(**kw)
    
    # use webkit open authorize page
    def request_oauth(self):
        '''request oauth access token'''
        self.webkit.load_uri(self.ACCESS_URL)
    
    def parse_url(self, uri=''):
        ''' parse url '''
        if not uri:
            return None
        url = urlparse.urlparse(uri)
        if url.fragment:
            query = urlparse.parse_qs(url.fragment, True)
        else:
            query = urlparse.parse_qs(url.query, True)
        return (url.hostname, query)
    
    # upload image
    def upload(self, upload_data):
        '''upload image'''
        return self.curl.upload(self.UPLOAD_URL, upload_data)

class Sina(Weibo):
    '''Sina Weibo'''
    def __init__(self, webkit):
        Weibo.__init__(self, 'Sina', webkit)
        self.APP_KEY = '2282689712'
        self.APP_SECRET = '7097d3c42cc0edc648f93807cff289a7'
        self.CALLBACK_URL = 'http://app.xefan.com'

        version = 2
        self.ACCESS_URL = 'https://api.weibo.com/oauth2/authorize?client_id=%s&redirect_uri=%s&display=mobile' % (self.APP_KEY,self.CALLBACK_URL)
        self.OAUTH2_URL = 'https://api.weibo.com/oauth2/access_token'
        self.USERS_URL = 'https://api.weibo.com/%d/%s' % (version, 'users/show.json')
        self.USER_ID_URL = 'https://api.weibo.com/%d/%s' % (version, 'account/get_uid.json')
        self.UPLOAD_URL = 'https://upload.api.weibo.com/%d/%s' % (version, 'statuses/upload.json')
        self.code = None

    def get_code(self):
        '''get oauth code'''
        self.code = None
        uri = self.webkit.get_property('uri')
        if not uri.startswith(self.CALLBACK_URL):
            return None
        parse = self.parse_url(uri)
        if parse is None:
            self.code = None
        if 'code' in parse[1]:
            self.code = parse[1]['code'][0]
        else:
            self.code = None
        return self.code

    def access_token(self):
        '''access token'''
        if self.get_code() is None:
            return False
        url = '%s?client_id=%s&client_secret=%s&grant_type=authorization_code&code=%s&redirect_uri=%s' % (
            self.OAUTH2_URL, self.APP_KEY, self.APP_SECRET, self.code, self.CALLBACK_URL)
        back = self.curl.post(url, [])
        if back is None:
            return False
        if 'access_token' in back:
            self.oauth.set(access_token=back['access_token'], expires_in=back['expires_in']+int(time.time()))
            return True
        else:
            return False
    
    # get user name
    def get_user_name(self):
        ''' get user name'''
        url = '%s?access_token=%s' % (self.USER_ID_URL, self.oauth.get('access_token'))
        back = self.curl.get(url)
        #print "uid:", back
        if back is None:
            return None
        if 'error_code' in back:
            return None
        url = '%s?access_token=%s&uid=%d' % (self.USERS_URL, self.oauth.get('access_token'), back['uid'])
        back = self.curl.get(url)
        #print "user:", back
        if back is None:
            return None
        if 'error_code' in back:
            return None
        return back['name']
    
    def upload_image(self, img, mesg='', annotations=None):
        '''upload image'''
        data = [
            ('access_token', self.oauth.get('access_token')),
            ('pic', (pycurl.FORM_FILE, img)),
            ('status', mesg)]
        if annotations:
            data.append(('annotations', annotations))
        back = self.upload(data)
        if back is None:
            return False
        if 'error_code' in back:
            return False
        return True

class Tencent(Weibo):
    '''Tencent Weibo'''
    def __init__(self, webkit):
        Weibo.__init__(self, 'Tencent', webkit)
        self.APP_KEY = '801229685'
        self.APP_SECRET = 'e6d5a0f59ca11f4ef6c5a52197959739'
        self.CALLBACK_URL = 'http://app.xefan.com'

        self.oauth_version = '2.a'
        self.client_ip = '127.0.0.1'    # TODO clientip
        self.ACCESS_URL = 'https://open.t.qq.com/cgi-bin/oauth2/authorize?client_id=%s&response_type=token&redirect_uri=%s&wap=2' % (self.APP_KEY,self.CALLBACK_URL)
        self.USERS_URL = 'https://open.t.qq.com/api/user/info'
        self.UPLOAD_URL = 'https://open.t.qq.com/api/t/add_pic'
        self.api = tencent.APIClient(self.APP_KEY, self.APP_SECRET, self.CALLBACK_URL)
        self.set_api_access_token()
    
    def set_api_access_token(self):
        '''set api access_token'''
        try:
            self.api.set_access_token(self.oauth.get('access_token'),
                self.oauth.get('openid'), self.oauth.get('expires_in'))
            return True
        except:
            return False

    def access_token(self):
        '''access token'''
        url = self.webkit.get_property('uri')
        if not url.startswith(self.CALLBACK_URL):
            return False
        back = self.parse_url(url)
        parse = back[1]
        if 'access_token' in parse:
            self.oauth.set(access_token=parse['access_token'][0],
                expires_in=int(parse['expires_in'][0])+int(time.time()),
                openid=parse['openid'][0], openkey=parse['openkey'][0])

            self.api.set_access_token(parse['access_token'][0],
                parse['openid'][0], expires_in=int(parse['expires_in'][0])+int(time.time()))
            return True
        return False
    
    def get_user_name(self):
        '''get user info'''
        try:
            back = self.api.get.user__info()
        except Exeption, e:
            print e
            return None
        if back['errcode'] != 0:
            return None
        return back['data']['nick']
    
    def upload_image(self, img, mesg=''):
        '''upload image'''
        try:
            back = self.api.upload.t__add_pic(content=mesg, clientip=self.client_ip, pic=open(img,'rb'))
        except:
            return False
        print back
        if back['errcode'] != 0:
            return False
        return True

class Twitter(Weibo):
    '''Twitter Weibo'''
    def __init__(self, webkit):
        Weibo.__init__(self, 'Twitter', webkit)
        self.APP_KEY = 'Tqq9bqCRIcJqdOQhXyaQ'
        self.APP_SECRET = 'ozG94zT6G8KDsdqfE1NGEThqFsnUgYqWouyE9NeaY'
        self.CALLBACK_URL = 'http://www.linuxdeepin.com'

        self.oauth_token_secret = ''
        self.oauth_token = ''
        self.oauth_verifier = ''
        self._access_token_secret = ''
        self._access_token = ''

        self.REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
        self.AUTHORIZE_UTL = 'https://api.twitter.com/oauth/authorize'
        self.ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
        self.USERS_URL = 'https://api.twitter.com/1/users/show.json'
        self.UPLOAD_URL = 'https://upload.twitter.com/1/statuses/update_with_media.json'
    
    def signature_base_string(self, method, params, url, secret_key=''):
        http_method = method
        base_url = url
        params.sort()
        url_params = urllib.quote(urllib.urlencode(params))
        base_string = "%s&%s&%s"%(http_method, urllib.quote(base_url, safe=''), url_params)
        #print "base_string:", base_string
        app_secret = self.APP_SECRET
        hmac_sha1 = hmac.new(app_secret+'&'+secret_key, base_string, hashlib.sha1)
        hmac_sha1_string = hmac_sha1.digest()
        signature_base_string = hmac_sha1_string.encode('base64').rstrip()

        request_url = base_url + '?'
        headers = 'Authorization: OAuth'
        for args in params:
            request_url += '%s=%s&' % (args[0], args[1])
            headers += ' %s="%s",' % (args[0], args[1])
        request_url += '%s=%s' % ('oauth_signature', signature_base_string)
        headers += ' %s="%s"' % ('oauth_signature', urllib.quote(signature_base_string, safe=''))
        
        return (signature_base_string, request_url, headers)

    def get_request_token_url(self):
        '''get request_token url'''
        timestamp = str(int(time.time()))
        params = [
            ('oauth_consumer_key', self.APP_KEY), # App Key
            ('oauth_signature_method', 'HMAC-SHA1'), 
            ('oauth_timestamp', timestamp),
            ('oauth_nonce', hashlib.md5(timestamp).hexdigest()),
            ('oauth_version', '1.0'),
            ('oauth_callback', self.CALLBACK_URL)]
        request_token = self.signature_base_string("GET", params, self.REQUEST_TOKEN_URL)
        print request_token
        return request_token[1]

    def request_token(self):
        '''request token and return authorize url'''
        back = self.curl.twitter_get(self.get_request_token_url())
        url = urlparse.urlparse(back)
        parse = urlparse.parse_qs(url.path, True)
        try:
            self.oauth_token_secret = parse['oauth_token_secret'][0]
            self.oauth_token = parse['oauth_token'][0]
        except KeyError: # request token failed
            return None
        authorize_url = "%s?oauth_token=%s" % (self.AUTHORIZE_UTL, self.oauth_token)
        return authorize_url

    def authorize(self, url):
        '''authorize and get oauth_token, oauth_verifier'''
        back = self.parse_url(url)
        parse = back[1]
        if 'oauth_token' in parse:
            self.oauth_token = parse['oauth_token'][0]
            self.oauth_verifier = parse['oauth_verifier'][0]
            return True
        return False

    def get_access_token_url(self):
        '''get access_token url'''
        timestamp = str(int(time.time()))
        params = [
            ('oauth_consumer_key', self.APP_KEY), # App Key
            ('oauth_signature_method', 'HMAC-SHA1'), 
            ('oauth_timestamp', timestamp),
            ('oauth_nonce', hashlib.md5(timestamp).hexdigest()),
            ('oauth_version', '1.0'),
            ('oauth_verifier', self.oauth_verifier),
            ('oauth_token', self.oauth_token)]
        access_token = self.signature_base_string("GET", params, self.ACCESS_TOKEN_URL)
        print access_token
        return access_token[1]

    def access_token(self):
        '''access token'''
        back = self.curl.twitter_get(self.get_access_token_url())
        if back is None:
            return False
        url = urlparse.urlparse(back)
        parse = urlparse.parse_qs(url.path, True)
        try:
            self._access_token_secret = parse['oauth_token_secret'][0]
            self._access_token = parse['oauth_token'][0]
            self._user_id = parse['user_id'][0]
            self._name = parse['screen_name'][0]
            self.oauth.set(
                access_token_secret=parse['oauth_token_secret'][0],
                access_token=parse['oauth_token'][0],
                user_id=parse['user_id'][0])
        except KeyError: # access token failed
            return False
        return True

    # use webkit open authorize page
    def request_oauth(self):
        '''request oauth access token'''
        self.webkit.load_uri(self.get_access_token_url())
    
    def get_user_name(self):
        '''get user name'''
        timestamp = str(int(time.time()))
        params = [
            ('oauth_consumer_key', self.APP_KEY), # App Key
            ('oauth_signature_method', 'HMAC-SHA1'), 
            #('oauth_timestamp', "1346817848"),
            #('oauth_nonce', "f2630d5bcc1bf3debaba8b03d766645f"),
            ('oauth_timestamp', timestamp),
            ('oauth_nonce', hashlib.md5(timestamp).hexdigest()),
            ('oauth_version', '1.0'),
            ('user_id', self.oauth.get('user_id')),
            ('oauth_token', self.oauth.get('access_token'))]
        user_name = self.signature_base_string("GET", params, self.USERS_URL, self.oauth.get('access_token_secret'))
        user_url = "%s?user_id=%s" % (self.USERS_URL, self.oauth.get('user_id'))
        back = self.curl.get(user_url, [user_name[2]])
        #user_url = "%s&user_id=%s" % (user_name[1], self.oauth.get('user_id'))
        #back = self.curl.get(user_url)
        if back is None:
            return None
        if 'errors' in back or 'error' in back:
            return None
        return back['screen_name']

    def upload_image(self, img, mesg=""):
        '''upload image'''
        file_type = get_file_type(img)
        if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
            return False
        timestamp = str(int(time.time()))
        params = [
            ('oauth_consumer_key', self.APP_KEY), # App Key
            ('oauth_signature_method', 'HMAC-SHA1'), 
            ('oauth_timestamp', timestamp),
            ('oauth_nonce', hashlib.md5(timestamp).hexdigest()),
            ('oauth_version', '1.0'),
            ('oauth_token', self.oauth.get('access_token'))]
        upload = self.signature_base_string("POST", params, self.UPLOAD_URL, self.oauth.get('access_token_secret'))
        header = upload[2]
        url = self.UPLOAD_URL
        #data = [('meida[]', (pycurl.FORM_FILE, img)), ("status", (pycurl.FORM_CONTENTS, mesg))]
        #data = [('meida[]', (pycurl.FORM_FILE, img)), ("status", mesg)]
        #url = "%s?%s" % (self.UPLOAD_URL, urllib.urlencode([("status", mesg)]))
        #data = [('meida[]', (pycurl.FORM_FILE, img))]
        #data = _encode_multipart(media=open(img,'rb'), status=mesg)
        #back = self.curl.upload(url, data, header)
        #back = self.curl.post(url, data, header)
        curl_cmd = """curl -k %s -F media[]="@%s" -F 'status=%s' --request 'POST' '%s' --header '%s' --header '%s'""" %("-x 127.0.0.1:8087", img, mesg, url, header, "Expect: ")
        print curl_cmd
        cmd = subprocess.Popen(curl_cmd, shell=True, stdout=subprocess.PIPE)
        if cmd.wait() != 0:
            return False
        back = json.loads(cmd.stdout.read())
        print back
        if back is False:
            return False
        if 'errors' in back or 'error' in back:
            return False
        return True

if __name__ == '__main__':
    #t = Tencent(None)
    #print t.get_user_name()
    #print t.upload_image('cairo_text.png', '微博api上传图片测试')

    t = Twitter(None)
    #print t.request_token()
    #print t.get_access_token_url()
    #url = raw_input("authorize url:")
    #if t.authorize(url):
        #print t.access_token()
    #print t.get_user_name()
    print t.upload_image('image.png', "上传图片api")