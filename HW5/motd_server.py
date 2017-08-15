# create an INET, STREAMing socket
import socket
import threading
import struct
import pickle


def get_response(message):
    return {
        "msg": "SUCCESS"
    }


MSGLEN = 10


def client_thread(socketobj):
    chunks = ""
    bytes_recd = 0
    print("starting socket read")
    print("reading header / message length")

    payload = None
    while True:
        chunk = socketobj.recv(2048)
        if chunk == '':
            print("socket connection broken")
            break

        chunks += chunk

        bytes_recd = bytes_recd + len(chunk)

        if bytes_recd >= 4:
            (total_message_size,) = struct.unpack("!I", chunks[0:4])

            if bytes_recd >= 4 + total_message_size:
                payload = pickle.loads(chunks[4:])
                break

    if payload != None:  # no error
        print("Here's what we got from the server:")
        print(payload)

    print("Sending response")
    response_payload = get_response(payload)

    response_payload_packed = pickle.dumps(response_payload)

    pack = struct.pack("!I", len(response_payload_packed))
    socketobj.send(pack)

    totalsent = 0
    while totalsent < len(response_payload_packed):
        sent = socketobj.send(response_payload_packed[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

    print("done:")


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind(('', 5000))
# become a server socket
serversocket.listen(5)

while 1:
    # accept connections from outside
    print("waiting for accept")
    (clientsocket, address) = serversocket.accept()
    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    ct = threading.Thread(target=client_thread, args=(clientsocket,))
    ct.start()
