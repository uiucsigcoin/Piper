#!/usr/bin/env python

import serial
import RPi.GPIO as GPIO
import time
from decimal import *
import hashlib
import hmac
import requests
import time
import json
import piper

port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)


runningtotal = Decimal('0.00').quantize(Decimal('.01'))
totalpennies = 0
totalnickels = 0
totaldimes = 0
totalquarters = 0

def waitForButton():
	pennies = 0
	nickels = 0
	dimes = 0
	quarters = 0
	transactiontotal = Decimal('0.00').quantize(Decimal('.01'))
	while (GPIO.input(17)):
		coinval = port.read(1)
		if (len(coinval) is 0):
                  continue
		else:
                  coinval = ord(coinval)
		if   coinval == 1:
			print "You got a penny!"
			pennies += 1
			transactiontotal += Decimal(.01)
		elif coinval ==  5:
			print "You got a nickel!"
			nickels+= 1
			transactiontotal += Decimal(.05)
		elif coinval == 10:
			print "You got a dime!"
			dimes+= 1
			transactiontotal += Decimal(.10)
		elif coinval == 25:
			print "That was a quarter!"
			quarters+= 25
			transactiontotal += Decimal(.25)
	print "button was pushed"
	return (transactiontotal, pennies, nickels, dimes, quarters)

while True:
	print "put some money in"
	transaction = waitForButton();
	runningtotal += transaction[0]
	totalpennies += transaction[1]
	totalnickels += transaction[2]
	totaldimes += transaction[3]
	totalquarters += transaction[4]

	print "Total amount inserted: {0}".format(transaction[0])

	# get a keypair
        pubkey, privkey, snum = piper.genKeys()
        leftMarkText = "Serial Number: {0}".format(snum)
        # do the actual printing
        piper.print_keypair(pubkey, privkey, leftMarkText)

	transaction = coinbase.send(to_address=pubkey,
		      amount=transaction[0],
		      notes='Coinverter Transaction {0}'.format(num))
