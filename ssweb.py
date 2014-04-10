#! /usr/bin/python
# by pts@fazekas.hu at Thu Apr 10 11:48:24 CEST 2014

import socket

def SingleShotWebserver():
  ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
  ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  ssock.bind(('127.0.0.1', 0))
  ssock.listen(4)
  saddr = ssock.getsockname()
  yield 'http://127.0.0.1:%d/' % saddr[1]
  sock, addr = ssock.accept()
  f = sock.makefile()
  head = []
  content_length = 0
  while True:
    line = f.readline()
    if not line:
      break
    head.append(line)
    if line in ('\r\n', '\n'):
      break
    if line.lower().startswith('content-length:'):
      content_length = max(0, int(line[line.find(':') + 1:]))
  sock.sendall('HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nShot.')
  body = f.read(content_length)
  yield addr, ''.join(head), body
  

if __name__ == '__main__':
  ssweb = SingleShotWebserver()
  url = ssweb.next() + 'foo'
  import sys
  response_body = None
  if len(sys.argv) <= 1:
    print 'URL: %s' % url
    import thread
    import urllib
    response_body = []
    thread.start_new_thread(
        lambda: response_body.append(urllib.urlopen(url).read()), ())
  else:
    print 'Please visit URL: %s' % url
  addr, head, body = ssweb.next()
  print repr(response_body)
  print repr(addr)
  print repr(head)
  print repr(body)
