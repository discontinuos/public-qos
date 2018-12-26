import urllib.request
import MultipartFormdataEncoder

import http
import math
import random
import datetime

import socket 

from Ssl2 import SSLContext
from _ssl import SSLEOFError

from urllib.parse import urlsplit
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from Functions import Functions
from Codes import Codes


class WebClient:
    ContentType = None
    Cookies = None
    RandomAgent = True
    Verbose = False

    def GetFixedAgent():
        #firefox
        return "Mozilla/5.0 (Windows NT 6.0; rv:50.0) Gecko/20100101 Firefox/50.0"

    def GetRandomAgent():
        list = [ 
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.0; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Mozilla/5.0 (Windows NT 6.1.1; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Mozilla/5.0 (X11; U; Linux i586; de; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/11.04 Chromium/14.0.825.0 Chrome/14.0.825.0 Safari/535.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.824.0 Safari/535.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Mozilla/5.0 (Macintosh; PPC MacOS X; rv:5.0) Gecko/20110615 Firefox/5.0",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)",
            "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",
            "Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)",
            "Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00",
            "Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1"]
        item = random.randrange(0, len(list))
        return list[item] 
    def Head(self, url, timeout, followRedirects=100):
        return self.open("HEAD", url, timeout, followRedirects)

    def Post(self, url, args, timeout):
        formArgs = urlencode(args).encode()
        self.ContentType = "application/x-www-form-urlencoded"
        return self.open("POST", url, timeout, 0, formArgs)

    def Get(self, url, timeout, followRedirects=100):
        return self.open("GET", url, timeout, followRedirects)

    def open(self, method, url, timeout, followRedirects, body = None):
        result = 0xFF
        ret = {}
        ret['text'] = ''
        ret['cookies'] = ''
        ret['error_description'] = "generic error on: " + url
        if self.Verbose:
            print ("[Verbose] " + method + ' ' + url)
        try:
            data, request = self.navigate(method, url, timeout, body)
            loops = 0
            lastUrl = url

            while (self.RetryForTheCookies(request) or request.code == 303 or request.code == 302 or request.code == 301) and loops < followRedirects:
                headers = dict(request.getheaders())
                cookies = self.ProcessCookies(request)
                if cookies != None:
                    self.Cookies = cookies 
        
                target = headers.get('Location', headers.get('location', ''))
                if target == "":
                    target = lastUrl

                if target.startswith("/"):
                    baseUrl = urllib.parse.urlsplit(lastUrl)
                    target = baseUrl.scheme + "://" + baseUrl.netloc + target
    
                data, request = self.navigate(method, target, timeout)
                lastUrl = target
                loops += 1

            return self.buildRetFromRequest(data, request)

        except HTTPError as e:
            result = Codes.GetCodeFromHTTPStatus(e.code)
            ret['code'] = e.code 

        except Exception as e:
            if str(e) == 'timed out' or str(e) == "<urlopen error timed out>":
                result = Codes.R_TIMEOUT
            elif str(e).find("An existing connection was forcibly closed by the remote host") != -1:
                result = Codes.R_CONNECTION_CLOSED
            else:
                ret['error_description'] = 'No fue posible navegar la URL: ' + url + '. Error: ' + str(e)
                result = Codes.R_ERROR
        
        ret['result'] = result
        return ret

    def RetryForTheCookies(self, request):
        if request.code == 401:
            headers = dict(request.getheaders())
            if headers.get('www-authenticate', '').lower() == 'negotiate':
                return True
        return False

    def buildRetFromRequest(self, data, request):
        ret = {}
        code = request.code
        ret['code'] = code
        ret['cookies'] = self.ProcessCookies(request)
        ret['result'] = Codes.GetCodeFromHTTPStatus(code)
        ret['error_description'] = ""
        if data == None:
            ret['text'] = None
            ret['bytes'] = None
        else:
            ret['text'] = self.decode(data)
            ret['bytes'] = data 
        request.close()
        return ret

    def ProcessCookies(self, result):
        cookies = ""
        for elem in result.getheaders():
            if elem[0].lower() == 'set-cookie':
                if cookies != "": cookies += "; "
                cookies += elem[1].split(";")[0]
        if cookies == "":
            return None
        else:
            return cookies

    def navigate(self, method, fullUrl, timeout, body = None):
        url = urllib.parse.urlsplit(fullUrl)
        retries = 0
        start = datetime.datetime.now()
        currentTimeout = timeout
        protocol = 3
        while(True):
            if self.Verbose:
                print ("[Verbose] Effective URL: " + fullUrl)
            if url.scheme == 'http':
                con = http.client.HTTPConnection(url.netloc, timeout = currentTimeout)
            elif url.scheme == 'https':
                context = SSLContext(protocol = protocol) 
                con = http.client.HTTPSConnection(url.netloc, context= context, timeout = currentTimeout)
            else:
                raise Exception("Unsupported resource type: " + fullUrl)
            urlpath = url.path
            if urlpath == "":
                urlpath = "/"
            if url.query != "":
                urlpath += "?" + url.query

            try:
                headers = self.CreateHeaders(url.hostname)
                try:
                    con.request(method, urlpath, body = body, headers=headers)
                except SSLEOFError as e:
                    go_on = True
                result = con.getresponse()
                data = result.read()
                if self.Verbose:
                    print ("[Verbose] Result: " + str(result.code))
                if result.code == 403:
                    failed = True

                con.close()
                return [data, result]
            except Exception as e:
                if self.Verbose:
                    print ("[Verbose] Error: " + str(e))
                if retries == 1 or url.scheme == 'http':
                    con.close()
                    raise
                retries += 1
                ellapsedSecs = math.ceil((datetime.datetime.now() - start).total_seconds())
                currentTimeout = timeout - ellapsedSecs
                if protocol == 3: protocol = 2
                if currentTimeout < 1:
                    con.close()
                    raise

    def CreateHeaders(self, host):
        if self.RandomAgent:
            headers = {"User-Agent": WebClient.GetRandomAgent() }
        else:
            headers = {"User-Agent": WebClient.GetFixedAgent() }
        headers['Host'] = host
        if self.ContentType != None:
            headers['Content-Type'] = self.ContentType
        if self.Cookies != None:
            headers['cookie'] = self.Cookies
        headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers['Accept-Language'] = "en-US,en;q=0.5"
        return headers

    def decode(self, bytes):
        cad = bytes.decode(encoding="utf-8", errors="ignore")
        return cad

    def PostFiles(self, url, params, fileNames):
        files = {}
        for field, file_name in fileNames.items():
            fileOnly = Functions.getFilename(file_name)
            with open(file_name, "rb") as f:
                c = f.read()
            files[field] = {'filename': fileOnly, 'content': c }
        ret = {}
        ret['text'] = ''
        ret['msg'] = ''
        ret['code'] = 500
        try:
            datagen, headers = MultipartFormdataEncoder.encode_multipart(params, files)
            request = urllib.request.Request(url, \
                                        datagen, headers)
            response = urllib.request.urlopen(request)
            text = self.decode(response.read())
            ret['text'] = text
            ret['code'] = response.code
        except HTTPError as e:
            res['msg'] = str(e.code)
            ret['code'] = e.code
        except Exception as e:
            res['msg'] = str(e)
        return ret
