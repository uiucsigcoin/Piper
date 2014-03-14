CoinMachine
===========

A USD Coin to BTC converter.

Hardware Components
===================

* Coin Acceptor: http://www.adafruit.com/products/787
* Thermal Printer: http://www.adafruit.com/products/597

Code Components:
================

* GUI: Used to display current price and confirm transaction with user.
* Coin Acceptor: Serial connection to coin accepter to recognize pennies, nickels, and quarters.
* Receipt Rendering: Print out a QR code, public key, private key, and the balance.
* BTC Transfer code: Send money to wallet from local wallet or Coinbase API.
