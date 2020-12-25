import pickle
import time
import socketserver

HEADER_SIZE = 4

def send_binary(sending_socket, data):
	pickled_data=pickle.dumps(data)
	size=len(pickled_data)
	sending_socket.send(size.to_bytes(HEADER_SIZE, byteorder="big") + pickled_data)

def get_binary(receiving_socket):
	messages=[]
	buffer=b""
	socket_open=True
	while socket_open:
		for message in messages:
			yield message
		messages = []
		data = receiving_socket.recv(1024)
		if not data:
			socket_open = False
		buffer += data
		processing_buffer = True
		while processing_buffer:
			if len(buffer) >= HEADER_SIZE:
				size = int.from_bytes(buffer[0:HEADER_SIZE], byteorder="big")
				if len(buffer) >= HEADER_SIZE + size:
					unpickled_message=pickle.loads(buffer[HEADER_SIZE:HEADER_SIZE+size])
					messages.append(unpickled_message)
					buffer=buffer[HEADER_SIZE+size:]
				else:
					processing_buffer = False
			else:
				processing_buffer = False

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass
clients = []

class Server(socketserver.BaseRequestHandler):
	def handle(self):
		global clients
		clients.append(self.request)

		print(self.client_address)
		send_binary(self.request, (1, "Hello and welcome"))
		for recvd in get_binary(self.request):
			if recvd[0] == "MESS":
				print(recvd[1])
				for client in clients:
					send_binary(client, (1, recvd[1]))

chat_server = ThreadedTCPServer(("127.0.0.1", 1111), Server)
chat_server.serve_forever()