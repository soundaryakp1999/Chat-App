import wx
import socket
import pickle
from threading import Thread
import accessible_output2.outputs.auto

o = accessible_output2.outputs.auto.Auto()
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


class Frame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, "Chat Room", size=(500,500))
		panel = wx.Panel(self, wx.ID_ANY)

		self.Maximize()
		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onEnter, id=randomId)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_RETURN, randomId )])
		self.SetAcceleratorTable(accel_tbl)
		self.read = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(500, 500))
		self.write=wx.TextCtrl(panel, size=(500, 500))
		self.write.SetFocus()

	def onEnter(self, event):
		s=str(self.write.GetValue())
		s.replace("\n", " ")
		send_binary(client, ("MESS", username + " says: " + s))
		self.write.SetValue("")


	def receive(self):
		for message in get_binary(client):
			if message[0] == 1:
				self.read.AppendText(message[1]+"\r")
				o.speak(message[1])
				


def inputDLG(message):
	dlg = wx.TextEntryDialog(frame, message)
	if dlg.ShowModal() == wx.ID_OK:
		x=dlg.GetValue()
	dlg.Destroy()
	return(x)

app = wx.App(False)
frame = Frame()
frame.Show()

username=inputDLG("Username:")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1111))

send_binary(client, ('JOIN', username))

receive_thread = Thread(target=frame.receive)
receive_thread.start()
app.MainLoop()