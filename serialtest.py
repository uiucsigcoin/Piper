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
import sys
import locale

from settings import *
from coinbase import *

locale.setlocale( locale.LC_ALL, '' )

coinbase = CoinbaseAPI(key=COINBASE_KEY, secret=COINBASE_SECRET)

port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

STOP_THREAD = False
def stop_thread():
	global STOP_THREAD
	STOP_THREAD = True

def update_exchange_rates(ui):
	rates = coinbase.exchange_rates()
	global btc_to_usd
	global usd_to_btc
	btc_to_usd = float(rates["btc_to_usd"])
	usd_to_btc = float(rates["usd_to_btc"])
	ui.display_exchange_rate(locale.currency(btc_to_usd))

btc_to_usd = None
usd_to_btc = None

totals = {'penny':0, 'dime':0,'quarter':0, 'nickel':0, 'all':0}
with open('totals.json', 'r') as total_file:
	total_dict = total_file.read()
	if total_dict:
		totals = json.loads(total_dict)

def send_coins(pubkey, amount, snum):
	if amount < COINBASE_MIN_TX_FEE * btc_to_usd:
		return None
	elif amount < COINBASE_NO_FEE_AMOUNT * btc_to_usd:
		fee = COINBASE_MIN_TX_FEE
		amount -= fee * btc_to_usd
		if float(amount) * usd_to_btc < COINBASE_MIN_AMOUNT:
			return None
	else:
		fee = 0
	print "amount: {0}, fee: {1}BTC".format(locale.currency(amount), fee)
	response = coinbase.send_coins(pubkey, amount,
                                      currency="USD",
                                      message="Serial Number: {0}".format(snum),
                                      tx_fee=fee)
	return response

def waitForButton(ui, transaction):
	minimum = btc_to_usd * (0.00005460 + COINBASE_MIN_TX_FEE)
	ui.display_message("Please enter some coins\n(Minimum is {0})!".format(locale.currency(minimum)))
	print "All systems are go! Waiting for money"
	while (GPIO.input(17)):
		if (transaction['total'] > 0):
			ui.display_message("{0} USD = {1} BTC".format(locale.currency(transaction['total']), transaction['total']*usd_to_btc))
		if STOP_THREAD:
			sys.exit(0)
		coinval = port.read(1)
		if (len(coinval) is 0):
                  continue
		else:
                  coinval = ord(coinval)
		if   coinval == 1:
			print "You got a penny!"
			transaction['penny'] += 1
			transaction['total'] += .01
		elif coinval ==  5:
			print "You got a nickel!"
			transaction['nickel'] += 1
			transaction['total'] += .05
		elif coinval == 10:
			print "You got a dime!"
			transaction['dime'] += 1
			transaction['total'] += .10
		elif coinval == 25:
			print "That was a quarter!"
			transaction['quarter'] += 1
			transaction['total'] += .25

		ui.display_message("{0} USD = {1} BTC".format(locale.currency(transaction['total']), transaction['total']*usd_to_btc))
	print "Button was pushed."
	return transaction

def main_loop(ui):
	transaction = {'penny':0, 'dime':0,'quarter':0, 'nickel':0, 'total':0}
	while True:
		update_exchange_rates(ui)
		transaction = waitForButton(ui, transaction);
		totals['all'] += transaction['total']
		totals['penny'] += transaction['penny']
		totals['nickel'] += transaction['nickel']
		totals['dime'] += transaction['dime']
		totals['quarter'] += transaction['quarter']
		print "Total amount inserted: {0}USD".format(locale.currency(transaction['total']))

		with open('totals.json', 'w') as total_file:
			total_file.write(json.dumps(totals))
		# get a keypair
		pubkey, privkey, snum = piper.genKeys()
		text = "Public Key: {0}\nPrivate Key: {1}\nSerial Number: {2}\n".format(pubkey, privkey, snum) + "-"*20 + "\n"
		print text
		with open('keys.txt', 'a+') as key_file:
			key_file.write(text)
		leftMarkText = "Serial Number: {0}".format(snum)
		ui.display_message("Sending transaction!")
		if (DEBUGGING):
			print "JK we're not actually sending it"
			transaction = {'penny':0, 'dime':0,'quarter':0, 'nickel':0, 'total':0}
			continue
		response = send_coins(pubkey, transaction['total'], snum)
		if response == None:
			print "Not enough money! Send refund of {0:}".format(locale.currency(transaction['total']))
			minimum = btc_to_usd * (0.00005460 + COINBASE_MIN_TX_FEE)
			ui.display_message("Not enough money!\nMinimum is {0}USD\nPlease try again!".format(locale.currency(minimum)))
			time.sleep(2)
			continue
		elif response['success']:
			# do the actual printing
			coinbase_tx = response['transaction']
			ui.display_message("Transaction Successful!\nPrinting Receipt.")
			print "Successful transaction: {0}".format(coinbase_tx['id'])
			print "Printing receipt"
			piper.print_keypair(pubkey, privkey, leftMarkText)
			print "resetting values"
			transaction = {'penny':0, 'dime':0,'quarter':0, 'nickel':0, 'total':0}
			
		else:
			print "Something is very wrong!"
			print "You should probably refund", transaction['total']
			ui.display_message("Transaction Failure. :-(")
			print response
