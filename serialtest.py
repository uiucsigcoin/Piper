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

getcontext().prec = 2
runningtotal = Decimal('0.00')
totalpennies = 0
totalnickels = 0
totaldimes = 0
totalquarters = 0

totals = {'penny':0, 'dime':0,'quarter':0, 'nickel':0, 'all':0}

rates = coinbase.exchange_rates()
btc_to_usd = float(rates["btc_to_usd"])
usd_to_btc = float(rates["usd_to_btc"])

def send_coins(pubkey, amount):
	if amount < COINBASE_MIN_TX_FEE * btc_to_usd:
		return None
	elif amount < COINBASE_NO_FEE_AMOUNT * btc_to_usd:
		fee = COINBASE_MIN_TX_FEE
		amount -= Decimal(fee * btc_to_usd)
		if float(amount) * usd_to_btc < 0.00005:
			return None
	else:
		fee = 0
	print "amount: {0}, fee: {1}".format(amount, fee)
	response = coinbase.send_coins(pubkey, amount,
                                      currency="USD",
                                      message="Testing for EOH",
                                      tx_fee=fee)
	return response

def waitForButton(ui):
	pennies = 0
	nickels = 0
	dimes = 0
	quarters = 0
	getcontext().prec = 2
	transactiontotal = Decimal('0.00')
	ui.display_message("Please enter some coins\n(Minimum ~${0})!".format(btc_to_usd * (0.00005460 + COINBASE_MIN_TX_FEE)))
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
		ui.display_message("${0} USD = {1} BTC".format(transactiontotal, float(transactiontotal)*usd_to_btc))
	print "Button was pushed."
	return (transactiontotal, pennies, nickels, dimes, quarters)

def main_loop(ui):
	while True:
		print "Put some money in!"
		transaction = waitForButton(ui);
		totals['all'] += transaction[0]
		totals['penny'] += transaction[1]
		totals['nickel'] += transaction[2]
		totals['dime'] += transaction[3]
		totals['quarter'] += transaction[4]
		#with open('totals.json', 'w') as total_file:
		#	total_file.write(json.dumps(totals))

		print "Total amount inserted: {0}USD".format(transaction[0])
		# get a keypair
		pubkey, privkey, snum = piper.genKeys()
		text = "Public Key: {0}\nPrivate Key: {1}\nSerial Number: {2}\n".format(pubkey, privkey, snum) + "-"*20 + "\n"
		print text
		with open('keys.txt', 'a+') as key_file:
			key_file.write(text)
		leftMarkText = "Serial Number: {0}".format(snum)
		ui.display_message("Sending transaction!")
		response = send_coins(pubkey, transaction[0])
		if response == None:
			print "Not enough money! Send refund of {0}".format(transaction[0])
			ui.display_message("Not enough money!\nMinimum is {0}USD".format(COINBASE_MIN_TX_FEE * btc_to_usd))
			continue
		elif response['success']:
			# do the actual printing
			coinbase_tx = response['transaction']
			ui.display_message("Transaction Successful!\nPrinting Receipt.")
			print "Successful transaction: {0}".format(coinbase_tx['id'])
			print "Printing receipt"
			piper.print_keypair(pubkey, privkey, leftMarkText)
		else:
			print "Something is very wrong!"
			ui.display_message("Transaction Failure. :-(")
			print response



