# This file is part of Piper.
#
#    Piper is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Piper is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Piper.  If not, see <http://www.gnu.org/licenses/>.
#
# Piper Copyright (C) 2013  Christopher Cassano

import Image
import ImageDraw
import ImageFont
import qrcode
import sys
from Adafruit_Thermal import *

printer = None
def get_printer(heat=200):
	global printer
	if printer:
		return printer
	else:
		# open the printer itself
		printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
		printer.begin(200)
		

def print_keypair(pubkey, privkey, leftBorderText):
	# check the cointype to decide which background to use
	finalImgName = "btc"
	coinName = "btc"
	printCoinName = (finalImgName == "blank")

	finalImgName += "-wallet"
	# load a blank image of the paper wallet with no QR codes or keys on it which we will draw on
	if(len(privkey) > 51):
		finalImgName += "-enc"
	else:
		finalImgName += "-blank"
	finalImgName += ".bmp"
	
	finalImgFolder = "/home/pi/Printer/Images/"
	finalImg = Image.open(finalImgFolder+finalImgName)



	# ---begin the public key qr code generation and drawing section---

	# we begin the QR code creation process
	# feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=0,
	)

	qr.add_data(pubkey)
	qr.make(fit=True)

	pubkeyImg = qr.make_image()

	# resize the qr code to match our design
	pubkeyImg = pubkeyImg.resize((175,175), Image.NEAREST)


	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 60)
	draw = ImageDraw.Draw(finalImg)

	if(printCoinName):
		draw.text((45, 400), coinName, font=font, fill=(0,0,0))
	font = ImageFont.truetype("/usr/share/fonts/truetype/droid/DroidSansMono.ttf", 20)
	startPos=(110,38)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(pubkey)

	while(keyLength % 17 != 0):
		pubkey += " "
		keyLength = len(pubkey)

	# draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		#print a line
		for y in range(0, 17):
			theChar = pubkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			
			# if y is 0 then this is the first run of this loop, and we should use startPos[0] for the x coordinate instead of the lastCharPos
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])



	# draw the QR code on the final image
	finalImg.paste(pubkeyImg, (150, 106))

	# ---end the public key qr code generation and drawing section---

	# ---begin the private key qr code generation and drawing section---

	# we begin the QR code creation process
	# feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=0,
	)
	qr.add_data(privkey)
	qr.make(fit=True)

	privkeyImg = qr.make_image()

	# resize the qr code to match our design
	privkeyImg = privkeyImg.resize((220,220), Image.NEAREST)

	# draw the QR code on the final image
	finalImg.paste(privkeyImg, (125, 560))


	startPos=(110,807)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(privkey)

	while(keyLength % 17 != 0):
		privkey += " "
		keyLength = len(privkey)


	# draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		# print a line
		for y in range(0, 17):
			theChar = privkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])

	# ---end the private key qr code generation and drawing section---



	# create the divider
	rightMarkText = "ACM@UIUC SIGCoin"


	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 20)

	rightMarkSize = draw.textsize(rightMarkText, font=font)

	leftMarkOrigin = (10, 15)
	rightMarkOrigin = (384-rightMarkSize[0]-10, 15)

	draw.text(leftMarkOrigin, leftBorderText, font=font, fill=(0,0,0))
	draw.text(rightMarkOrigin,rightMarkText, font=font, fill=(0,0,0))

	# do the actual printing

	printer.printImage(finalImg, True)
	if(len(privkey) <= 51):
		printer.println(privkey[:17])
		printer.println(privkey[17:34])
		printer.println(privkey[34:])
	else:
		printer.println(privkey)

	# print some blank space so we can get a clean tear of the paper
	printer.feed(3)
	printer.sleep()      # Tell printer to sleep
	printer.wake()       # Call wake() before printing again, even if reset
	printer.setDefault() # Restore printer to defaults

def genAndPrintKeys():
	# open serial number file which tracks the serial number
	snumfile = open('serialnumber.txt', 'r+')
	snum = snumfile.read()

	# this actually generates the keys.  see the file genkeys.py or genkeys_forget.py
	import genkeys as btckeys
	btckeys.genKeys()
	privkey = btckeys.privkey
	
	strToWrite = ""

	leftMarkText = "Serial Number: "+snum

	# do the actual printing
	print_keypair(btckeys.pubkey, privkey, leftMarkText)

	# update serial number
	snumfile.seek(0,0)
	snumfile.write(str(int(snum)+1))
	snumfile.close()
	return btckeys.pubkey, privkey, snum
