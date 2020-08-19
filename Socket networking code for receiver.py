# Socket networking code for receiver
import settings
import random
import socket
import pickle

class segment:
	"""
	data: integer, 0 when segment is an ACK
	seq: Boolean, False (for seq 0) or True (for seq 1)
	ack: Boolean, sequence number ACK
	nack: Boolean, is this an ACK
	"""
	def __init__(self, data, seqSeg, seqAck, isAck):
		self.data = data
		self.seqSeg = seqSeg
		self.seqAck = seqAck
		self.isAck = isAck

BUFFER_SIZE = 1024
PORT = 12345

"""
seed_segment_corrupt: The seed for the random number generator used for determining if a segment has been corrupted
probability_segment_corrupt: The probability that a segment has been corrupted. Between [0 and 1) 
"""
input_list = [float(x) for x in input().split()]
seed_segment_corrupt = int(input_list[0])
probability_segment_corrupt = input_list[1]

segment_corrupt_rate_generator = random.Random(seed_segment_corrupt)

seqSeg = False

# Create socket connection
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.bind(('', settings.PORT))
my_socket.listen(1)
client, addr = my_socket.accept()

print("The receiver is moving to state WAIT FOR {} FROM BELOW".format
	(int(seqSeg)))

while True:

	received_pickled_segment = client.recv(BUFFER_SIZE)

	if (received_pickled_segment == b''):
		break;

	generated_corrupt_rate = segment_corrupt_rate_generator.random()
	
	if generated_corrupt_rate < probability_segment_corrupt:
		print("A corrupted segment has been received")
		print("The receiver is moving back to state WAIT FOR {} FROM BELOW".format(
			int(seqSeg)))

	else:
		unpickled_segment = pickle.loads(received_pickled_segment)

		print("A segment with sequence number {} has been received".format(
			int(unpickled_segment.seqSeg)))

		print("Segment received contains: data = {} seqSeg = {} seqAck = {} isAck = {}".format(
			unpickled_segment.data,
			int(unpickled_segment.seqSeg),
			int(unpickled_segment.seqAck),
			int(unpickled_segment.isAck)))

		# Create ack we want to send
		my_ack = segment(0, unpickled_segment.seqSeg, unpickled_segment.seqSeg, True)

		print("An ACK{} is about to be sent".format(int(my_ack.seqSeg)))
		print("ACK to send contains: data = {} seqSeg = {} seqAck = {} isAck = {}".format(
			my_ack.data,
			int(my_ack.seqSeg),
			int(my_ack.seqAck),
			int(my_ack.isAck)))

		# Pickle ack and send
		pickled_ack = pickle.dumps(my_ack)
		client.send(pickled_ack)

		seqSeg = not seqSeg


		print("The receiver is moving to state WAIT FOR {} FROM BELOW".format
			(int(seqSeg)))
      
print("\nClosing connection")
my_socket.close()