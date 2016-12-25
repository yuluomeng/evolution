import json


def send_msg(msg, sock):
    """sends a message over the sender

    :param msg: message to send
    :type msg: JSON

    :param sender: socket to send message over
    :type sender: socket.socket

    :returns: reply message
    :type msg: JSON
    """
    sock.sendall(json.dumps(msg).encode())


def read_msg(sock):
    """listens for a message on the receiver

    :param sock: the thing
    :type sock: socket.socket

    :returns: the messsage it hears
    :rtype: JSON
    """

    msg = b''
    while True:
        data = sock.recv(1)
        if not data:
            return

        msg += data
        try:
            return json.loads(msg.decode('utf-8').strip())
        except ValueError:
            continue
