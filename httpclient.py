#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def parse_url(self, data):
        # parse the URL to get all its parts
        parsed_url = urllib.parse.urlparse(data)

        # get the host, port and path from the parsed url
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path

        if not port: # if no port is given use the default of 80
            port = 80
        if not path: # change an empty path to '/'
            path = '/'

        return host, port, path

    def get_code(self, data):
        # Take the data then extract the status code
        data = data.split("\n") # Split on new line data[0] will contain Status code
        data = data[0].strip().split() # Strip empty space then split data data[1] will be Status code
        code = int(data[1]) # Cast the Status code to int
        return code

    def get_headers(self, data):
        # Split the data on '\r\n\r\n' as that indicates split between headers and body
        data = data.split("\r\n\r\n")
        headers = data[0] # data[0] is the headers and data[1] will be body
        return headers

    def get_body(self, data):
        # Split the data on '\r\n\r\n' as that indicates split between headers and body
        data = data.split("\r\n\r\n")
        body = data[1] # data[0] is the headers and data[1] will be body
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        try:
            # parse the URL to get all its parts
            host, port, path = self.parse_url(url)

            # establish connection
            self.connect(host, port)

            # format the GET request and send it
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: Closed\r\n\r\n"
            self.sendall(request)

            # recieve the response
            response = self.recvall(self.socket)
        except:
            print("Some Error Occured")
            return
        finally:
            # close connection
            self.close()

            # return the response
            code = self.get_code(response)
            body = self.get_body(response)
            return HTTPResponse(code, body)

    def POST(self, url, args=None):
        try:
            # parse the URL to get all its parts
            host, port, path = self.parse_url(url)

            # establish connection
            self.connect(host, port)

            # format the GET request and send it
            # this code was inspired by an example at https://www.geeksforgeeks.org/python-convert-dictionary-to-concatenated-string/
            # concatenates dictionary key-value pairs into a string in the form 'key=value&key2=value2'
            content = ' ' # content of the POST request that we will be sending
            for value in args:
                content = content + f"{value}={str(args[value])}&"
            content = content[:-1].strip() # remove trailing '&' and any empty space

            content_type = "application/x-www-form-urlencoded" # set the content type
            content_length = len(content) # get the length of the content
            
            request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nConnection: Closed\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n{content}"
            
            self.sendall(request)

            # recieve the response
            response = self.recvall(self.socket)
        except:
            print("An error occured!")
            return
        finally:
            # close connection
            self.close()
            code = self.get_code(response)
            body = self.get_body(response)
            return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

    # get_test = "http://www.httpbin.org/get"
    # post_test = "http://www.httpbin.org/post"
    # post_data = {
    #     "Name" : "Kratos",
    #     "Age" : "1055"
    # }

    # print(client.GET(get_test))
    # print(client.POST(post_test, post_data))