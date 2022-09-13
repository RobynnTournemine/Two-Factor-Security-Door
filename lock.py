#!/usr/bin/env python3
from calendar import isleap
import MySQLdb
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
from select import select
from twilio.rest import Client
from mfrc522 import SimpleMFRC522

channel = 33
CardRead = SimpleMFRC522()
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(channel, GPIO.OUT)

try:
	# python 2
	import Tkinter as tk
	import ttk
except ImportError:
	# python 3
	import tkinter as tk
	from tkinter import ttk


class Fullscreen_Window:
	global dbHost
	global dbName
	global dbUser
	global dbPass

	dbHost = 'localhost'
	dbName = 'door_lock'
	#Change to your phpMyAdmin username/password
	dbUser = 'USERNAME'
	dbPass = 'PASSWORD'

	def __init__(self):
		GPIO.output(channel, True)
		self.tk = tk.Tk()
		self.tk.title("Two-Factor-Security-Door")
		self.tk.columnconfigure(0, weight=1)

		self.tk.attributes('-zoomed', True)
		self.tk.attributes('-fullscreen', True)
		self.state = True
		self.tk.bind("<F11>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		self.tk.config(cursor="none")
		

		self.show_idle()

		t = Thread(target=self.listen_rfid)
		t.daemon = True
		t.start()

	def show_idle(self):
		self.welcomeLabel = ttk.Label(self.tk, text="Please Present\nYour Token")
		self.welcomeLabel.config(font='size, 20', justify='center', anchor='center')
		self.welcomeLabel.grid(sticky=tk.W+tk.E, pady=210)

	def pin_entry_forget(self):
		self.validUser.grid_forget()
		self.photoLabel.grid_forget()
		self.enterPINlabel.grid_forget()
		count = 0
		while (count < 12):
			self.btn[count].grid_forget()
			count += 1

	def returnToIdle_fromPINentry(self):
		global isLoggedIn
		isLoggedIn = False
		self.pin_entry_forget()
		self.show_idle()

	def returnToIdle_fromValidation(self):
		GPIO.output(channel, True)
		self.PINresultLabel.grid_forget()
		self.show_idle()

	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"

	def listen_rfid(self):
		global pinInput
		global accessLogId
		global pinInput
		global userPin
		global isLoggedIn
		while True:
			id = CardRead.read_id()
			rfid_presented = id
			isLoggedIn = False
			dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
			cur = dbConnection.cursor(MySQLdb.cursors.DictCursor)
			cur.execute("SELECT * FROM access_list WHERE rfid_code = '%s'" %(rfid_presented))
			if cur.rowcount == 1:
				user_info = cur.fetchone()
				userPin = user_info['pin']
				isLoggedIn = True
			if isLoggedIn == False:
				self.welcomeLabel.config(text="ACCESS DENIED")
                
				cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 0" % (rfid_presented))
				dbConnection.commit()
                
				time.sleep(3)
				self.welcomeLabel.grid_forget()
				self.show_idle()
			if isLoggedIn:
				cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 1" % (rfid_presented))
				dbConnection.commit()
				accessLogId = cur.lastrowid
				self.welcomeLabel.grid_forget()
				self.validUser = ttk.Label(self.tk, text="Welcome\n %s!" % (user_info['name']), font='size, 15', justify='center', anchor='center')
				self.validUser.grid(columnspan=3, sticky=tk.W+tk.E)
				
				self.image = tk.PhotoImage(file=user_info['image'] + ".gif")
				self.photoLabel = ttk.Label(self.tk, image=self.image)
				self.photoLabel.grid(columnspan=3)
				
				self.enterPINlabel = ttk.Label(self.tk, text="\nPlease enter your PIN:\n\n", font='size, 18', justify='center', anchor='center')
				self.enterPINlabel.grid(columnspan=3, sticky=tk.W+tk.E)
				keypad = [
					'1', '2', '3',
					'4', '5', '6',
					'7', '8', '9',
					'*', '0', '#',
				]
				r = 10
				c = 0
				n = 0
				pinInput = ''
				self.btn = list(range(len(keypad)))
				
				for label in keypad:
					self.btn[n] = tk.Button(self.tk, text=label, font='size, 18', width=4, height=1, command=lambda digitPressed=label:self.combinePinInput(digitPressed))
					self.btn[n].grid(row=r, column=c, ipadx=36, ipady=20)
					n += 1
					c += 1
					
					if c > 2:
						c = 0
						r += 1
				
				self.PINentrytimeout = threading.Timer(10, self.returnToIdle_fromPINentry)
				self.PINentrytimeout.start()

				while isLoggedIn:
					if len(pinInput) == 6:
						self.validate()
						isLoggedIn = False
						pinInput = ''
			
			rfid_presented = ""
			dbConnection.close()

	def combinePinInput(self, value):
		global pinInput
		pinInput += value

	def validate(self):
		global accessLogId
		global pinInput
		global isLoggedIn
		global userPin
		
		self.PINentrytimeout.cancel()
		self.pin_entry_forget()
		
		if pinInput == userPin:
			pin_granted = 1
		else:
			pin_granted = 0
		
		# Log access attempt
		dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
		cur = dbConnection.cursor()
		cur.execute("UPDATE access_log SET pin_entered = '%s', pin_entered_datetime = NOW(), pin_granted = %s WHERE access_id = %s" %(pinInput, pin_granted, accessLogId))
		dbConnection.commit()
		
		if pinInput == userPin:
			self.PINresultLabel = ttk.Label(self.tk, text="Thank You,\nAccess Granted")
			self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
			self.PINresultLabel.grid(columnspan=3, sticky=tk.W+tk.E, pady=210)
			GPIO.output(channel, False)
			self.doorOpenTimeout = threading.Timer(12, self.returnToIdle_fromValidation)
			self.doorOpenTimeout.start()
		else:
			self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN !\n")
			self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
			self.PINresultLabel.grid(sticky=tk.W+tk.E, pady=210)
			time.sleep(3)
			self.returnToIdle_fromValidation()			

if __name__ == '__main__':
	w = Fullscreen_Window()
	w.tk.mainloop()

