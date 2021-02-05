"""
The data is first encoded in JSON format, then converted to bytes.
The send message is then the length of the converted data, the separator, then the converted data
"""

import json

_HEADER_SEP = b'\xFF'  # Separator between the header and the message
_DEBUG_COMM = False  # Enable debug


def send(sock, data):
    """
    Send some data on the given socket

    Args:
        sock (Union[socket.socket, asyncore.dispatcher]):
        data (any): object that can be serialised in JSON format

    Returns:
        int: the message length, with the header
    """

    msg = json.dumps(data)
    msg = '{0}'.format(len(msg)).encode() + _HEADER_SEP + msg.encode()
    tot = 0
    while tot < len(msg):
        sent = sock.send(msg[tot:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        if _DEBUG_COMM:
            print("Send {0} bytes: {1}".format(sent, msg[tot:tot + sent]))
        tot += sent
    return tot


def recv(sock):
    """
    Receive some data from the socket

    Args:
        sock (Union[socket.socket, asyncore.dispatcher]):

    Returns:
        any: the retrieved data, or b'' if the connection is closed
    """
    header = b''
    while _HEADER_SEP not in header:
        chunk = sock.recv(1)
        if chunk == b'':
            return b''
        header += chunk
    msg_len = int(header[:-1])

    msg = b''
    tot = 0
    while tot < msg_len:
        chunk = sock.recv(msg_len - tot)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        if _DEBUG_COMM:
            print("Recv {0} bytes: {1}".format(len(chunk), chunk))
        msg += chunk
        tot += len(chunk)
    return json.loads(msg.decode())
