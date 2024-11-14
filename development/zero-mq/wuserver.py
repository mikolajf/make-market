#
#   Weather update server
#   Binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#

from random import randrange

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

while True:
    zipcode = 10001
    temperature = randrange(-80, 135)
    relhumidity = randrange(10, 60)

    socket.send_string(f"{zipcode} {temperature} {relhumidity}")
