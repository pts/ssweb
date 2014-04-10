#! /usr/bin/python
# by pts@fazekas.hu at Thu Apr 10 11:48:24 CEST 2014

if 0: print 0  # Python 2.x needed; make sure it doesn't compile in Python 3.x.

import socket


def SingleShotWebserver(res_body='Shot.', res_content_type='text/plain'):
  """Create and return a HTTP server which can serve a single request.

  The HTTP server runs on localhost (127.0.0.1) on a random available port,
  and waits for a single request, which it servers by returning a specified
  dummy response.

  Example usage:

    url, server = SingleShotWebserver()
    import thread
    import urllib
    thread.start_new_thread(lambda: urllib.urlopen(url).read(), ())
    print server()

  See another example usage at the end of the source file.

  Args:
    res_body: The dummy HTTP response body to return.
    res_content_type: The dummy HTTP response Content-Type to return.
  Returns:
    (url, server), where server is function without arguments, which -- when
    called -- waits for the incoming HTTP request, handles it, closes the
    connection and the server socket, and returns the info about the request:
    {'client_addr': (str(ip), port), 'req_head': str(...), 'req_body': str(...),
     'res_head': str(...), 'res_body': str(...)}.
  """
  if not isinstance(res_body, str):
    raise TypeError
  ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
  ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  ssock.bind(('127.0.0.1', 0))
  ssock.listen(4)
  saddr = ssock.getsockname()
  url = 'http://127.0.0.1:%d/' % saddr[1]

  def Server():
    try:
      sock, addr = ssock.accept()
      f = sock.makefile()
    finally:
      ssock.close()  # Single-shot server, doesn't accept any more requests.
    try:
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
      res_head = (
          'HTTP/1.0 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n' %
          (res_content_type, len(res_body)))
      sock.sendall(res_head + res_body)
      body = f.read(content_length)
      return {'client_addr': addr, 'req_head': ''.join(head), 'req_body': body,
              'res_head': res_head, 'res_body': res_body}
    finally:
      f.close()
      sock.close()

  return url, Server


if __name__ == '__main__':
  url, server = SingleShotWebserver()
  url += 'foo'
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
  print server()  # Waits for incoming connection, serves it, returns info.
  print response_body
