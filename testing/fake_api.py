"""A fake server for Sourcerer API testing."""

__copyright__ = '2018 Sourcerer'
__author__ = 'Sergey Surkov (sergey@sourcerer.io)'

import argparse
import json
import http.server
import socketserver

from urllib.parse import urlparse, parse_qs

PORT = 8000


class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urlparse(self.path)
        qs = parse_qs(parts.query)
        resp = {}

        if parts.path == '/api/face/hof/match':
            usernames = qs['names'][0].split(',')
            for u in usernames:
                if u in user_mapping:
                    resp[u] = user_mapping[u]

        elif parts.path == '/api/face/hof/token':
            if 'Authorization' not in self.headers:
                self.send_error(403)
                return
            resp['token'] = github_token

        else:
            self.send_error(404)
            return

        data = bytes(json.dumps(resp), 'utf-8')
        self._set_headers()
        self.wfile.write(data)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()


def load_user_mapping(filename):
    data = open(filename).read()
    lines = data.strip().split('\n')
    users = {}
    for line in lines:
        github_user, sourcerer_user = line.strip().split(',')
        users[github_user] = sourcerer_user
    return users


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--mapping', type=str, default='users.txt',
                        help='GitHub to Sourcerer user mapping file')
    parser.add_argument('--github_token', type=str,
                        help='GitHub token to serve')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    user_mapping = load_user_mapping(args.mapping)
    github_token = args.github_token

    print('i Loaded user mapping from %s' % args.mapping)

    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print("i Serving at port", PORT)
        httpd.serve_forever()
