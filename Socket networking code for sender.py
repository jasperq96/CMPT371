# Socket networking code for sender
import settings
import random
import socket
import pickle
import time as t

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
HOST = 'localhost'
PORT = 12345
DATA_RANGE = 1024

"""
seed_time: The seed for the random number generator used for timing
number_of_segments: The number of segments to send
seed_ack_corrupt: The seed for the random number generator used for determining if an ACK has been corrupted.
probability_ack_corrupt: The probability that an ACK has been corrupted. Between [0 and 1)
seed_data: The seed for the generation of the data field in each packet Between [0 and 1024]
round_trip: The round trip travel time used for timeout
"""
#seed_time, number_of_segments, seed_ack_corrupt, probability_ack_corrupt, seed_data, round_trip) = input().split()
input_list = [float(x) for x in input().split()]
seed_time = int(input_list[0])
number_of_segments = int(input_list[1])
seed_ack_corrupt = int(input_list[2])
probability_ack_corrupt = input_list[3]
seed_data = int(input_list[4])
round_trip = int(input_list[5])

elapsed = 5

data_generator = random.Random(seed_data)
wait_time = random.Random(seed_time)

# Create socket connection
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((HOST, PORT))
my_socket.settimeout(int(round_trip))

seqSeg = False

for x in range(number_of_segments):
	time = wait_time.uniform(0,5)
	diff_time = time - elapsed

	if diff_time > 0:
		t.sleep(diff_time)

	ack_received = False
	data = data_generator.randint(0, DATA_RANGE)

	print("The sender is moving to state WAIT FOR CALL {} FROM ABOVE".format(
		int(seqSeg)))

	# Create segment we want to send
	my_segment = segment(data, seqSeg, seqSeg, False)
	
	print("A data segment with sequence number {} is about to be sent".format(
		int(my_segment.seqSeg)))

	# Pickle segment and send
	pickled_segment = pickle.dumps(my_segment)
	start_time = t.time()
	my_socket.send(pickled_segment)

	print("Segment sent: data = {} seqSeg = {} seqAck = {} isAck = {}".format(
		my_segment.data,
		int(my_segment.seqSeg),
		int(my_segment.seqAck),
		int(my_segment.isAck)))

	print("The sender is moving to state WAIT FOR ACK {}".format(
		int(my_segment.seqAck)))

	while not ack_received:
		generated_corrupt_rate = random.random()

		if generated_corrupt_rate < probability_ack_corrupt:
			print("A corrupted ACK segment has just been received")
			print("The sender is moving back to state WAIT FOR ACK {}".format(
				int(my_segment.seqAck)))
		else:
			try:
		
				received_pickled_ack = my_socket.recv(BUFFER_SIZE)
				elapsed = t.time()-start_time
				unpickled_ack = pickle.loads(received_pickled_ack)
				print("An ACK{} has just been received".format(
					int(unpickled_ack.seqSeg)))

				seqSeg =  not seqSeg # Toggle boolean
				ack_received = True
			except socket.timeout:
				print("A data segment with sequence number {} is about to be resent".format(
					int(my_segment.seqSeg)))

				my_socket.send(pickled_segment)


print("\nClosing connection")
my_socket.close() 