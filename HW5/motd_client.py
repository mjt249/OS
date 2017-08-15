import socket
import struct
import pickle

MSGLEN = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("localhost", 5000))
totalsent = 0

payload = {
    "msg": "Hello dis puppy.",
    "command": "SET"
}

payload_packed = pickle.dumps(payload)

pack = struct.pack("!I", len(payload_packed))
s.send(pack)

while totalsent < len(payload_packed):
    sent = s.send(payload_packed[totalsent:])
    if sent == 0:
        raise RuntimeError("socket connection broken")
    totalsent = totalsent + sent

# Receive the response!

chunks = ""
bytes_recd = 0
print("starting socket read")
print("reading header / message length")

response = None
while True:
    chunk = s.recv(2048)
    if chunk == '':
        print("socket connection broken")
        break

    chunks += chunk

    bytes_recd = bytes_recd + len(chunk)

    if bytes_recd >= 4:
        (total_message_size,) = struct.unpack("!I", chunks[0:4])

        if bytes_recd >= 4 + total_message_size:
            response = pickle.loads(chunks[4:])
            break

if response != None:  # no error
    print("Here's what we got from the client:")
    print(response)
