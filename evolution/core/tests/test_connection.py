import json
import socket
from queue import Queue
from threading import Thread

from evolution.core.connection import send_msg, read_msg


def test_send_msg():
    host, port = 'localhost', 45678

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()

    def mock_client(host, port, reply, queue):
        client_sock = socket.create_connection((host, port))
        msg = b''
        while True:
            msg += client_sock.recv(1)
            try:
                queue.put(json.loads(msg.decode('utf-8')))
                client_sock.send(json.dumps(reply).encode())
                break
            except ValueError:
                continue

    client_queue = Queue()
    sent_msg = 'hello world'
    expected_reply = 'hello_world2'

    client_thread = Thread(
        target=mock_client,
        args=((host, port, expected_reply, client_queue)))
    client_thread.daemon = True
    client_thread.start()

    conn, _ = server_sock.accept()
    send_msg(sent_msg, conn)

    assert read_msg(conn) == expected_reply
    assert client_queue.get() == sent_msg
