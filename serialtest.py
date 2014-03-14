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
from settings import *
from coinbase import *

coinbase = CoinbaseAPI(key=COINBASE_KEY, secret=COINBASE_SECRET)

port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)


runningtotal = Decimal('0.00').quantize(Decimal('.01'))
totalpennies = 0
totalnickels = 0
totaldimes = 0
totalquarters = 0

def send_coins(pubkey, amount):
	rates = coinbase.exchange_rates()
	btc_to_usd = float(rates["btc_to_usd"])
	usd_to_btc = float(rates["usd_to_btc"])
	if amount < COINBASE_MIN_TX_FEE * btc_to_usd:
		return None
	elif amount < COINBASE_NO_FEE_AMOUNT * btc_to_usd:
		fee = COINBASE_MIN_TX_FEE
	else:
		fee = 0
	print "fee: {0}".format(fee)
	response = coinbase.send_coins(pubkey, amount,
                                      currency="USD",
                                      message="Testing for EOH",
                                      tx_fee=fee)
	return response


def waitForButton():
	pennies = 0
	nickels = 0
	dimes = 0
	quarters = 0
	getcontext().prec = 2
	transactiontotal = Decimal('0.00')
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
	text = "Public Key: {0}\nPrivate Key: {1}\nSerial Number: {2}\n".format(pubkey, privkey, snum) + "-"*20 + "\n"
	print text
	with open('keys.txt', 'a+') as key_file:
		key_file.write(text)
        leftMarkText = "Serial Number: {0}".format(snum)
	response = send_coins(pubkey, transaction[0])
	if response == None:
		print "Not enough money! Send refund of {0}".format(transaction[0])
		continue
	elif response['success']:
		# do the actual printing
		coinbase_tx = response['transaction']
		print "Successful transaction: {0}".format(coinbase_tx['id'])
		print "Printing receipt"
		piper.print_keypair(pubkey, privkey, leftMarkText)
	else:
		print "Something is very wrong!"
		print response












