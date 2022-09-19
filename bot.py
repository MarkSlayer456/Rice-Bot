import os
import pyautogui
import webbrowser
import socket
import time

from PIL import Image
from pytesseract import pytesseract
from pynput.keyboard import Listener, KeyCode
from sys import platform


url = 'https://freerice.com/categories/multiplication-table'

rice_before_reset = 1000

start_stop_key = KeyCode(char='s')
exit_key = KeyCode(char='q')
running = True
attempts_before_guess = 5

host = "10.0.0.20"
port = 14456

windows_cords = [250, 190, 130, 70]
linux_cords = [190, 130, 70, 10]

cords = []

path_to_tess = ""
directory = ""
pic_path = ""
crop_path = ""

BUFFER_SIZE = 1024

scaleH = 0
scaleW = 0

# get the mouse out of the way
pyautogui.moveTo(5,5)

pytesseract.tesseract_cmd = ""

filename = "temp.png"
crop_filename = "crop.png"

"""
Checks OS, username, etc
"""
def setup():
	if platform == "linux" or platform == "linux2":
		#path_to_tess = r'/usr/bin/tesseract'
		path_to_tess = r'/usr/bin/tesseract'
		pytesseract.tesseract_cmd = path_to_tess
		user = os.getlogin()
		dir_start = r'/home'
		dir_end = r'Documents/rice-bot-temp'
		dir_temp = os.path.join(dir_start, user)
		directory = os.path.join(dir_temp, dir_end)
		pic_path = os.path.join(directory, filename)
		webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("firefox"))
		webbrowser.get('firefox').open(url)
	elif platform == "darwin":
		# OS X
		pass
	elif platform == "win32":
		path_to_tess = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
		user = os.getlogin()
		dir_start = r'C:\Users'
		dir_end = r'Desktop\Rice-Bot-Temp'
		dir_temp = os.path.join(dir_start, user)
		directory = os.path.join(dir_temp, dir_end)
		pic_path = os.path.join(directory, filename)
		webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
		webbrowser.get('chrome').open(url)
	try:
		os.mkdir(directory)
	except FileExistsError as error:
		pass
	except OSError as error2:
		print(error2)
	except:
		print("UH OH...")
	return directory

"""
attempts to connect to the server and send the grains given to it
"""
def send_grains_to_server(grains):
	try:
		sock = socket.socket()
		sock.connect((host, port))
		grains = str(current_rice)
		read = grains.encode('utf-8')
		sock.sendall(read)
		sock.close()
		print("Grains sent to server:", grains)
	except socket.error as error:
		print("WARNING: Data is not being sent to the server... is it up?")


"""
Takes a picture of the screen and saves it. Then
opens the picture and returns it
"""
def screenshot():
	myScreenshot = pyautogui.screenshot()
	myScreenshot.save(pic_path)
	return Image.open(pic_path)

"""
Crops a picture of the screen and saves it. Then
opens the picture and returns it
"""
def crop_image(image, width, height):
	left = width/2 - (200*scaleW)
	top = height/2 - (350*scaleH)
	right = width/2 + (250*scaleW)
	bottom = height / 2 + (75*scaleH)
	
	crop = image.crop((left, top, right, bottom))
	try:
		crop.save(crop_path)
	except:
		print("ERROR: file not cropped, I'm not sure what happened!")	
	image.close()
	crop_img = Image.open(crop_path)
	return crop_img
	
prev_question = ""
attempt = 0
tries = 0
current_rice = 0
max_tries = 10 # close tab and restart after this many failed attempts (not sure if correct)
pic_path = os.path.join(setup(), filename) # why this has to be here is beyond me
crop_path = os.path.join(setup(), crop_filename)
if platform == "linux" or platform == "linux2":
	cords = linux_cords
elif platform == "win32":
	cords = windows_cords

print(cords)
try:
	while running:
		correct = False
		#pyautogui.moveTo(5,5)
		img = screenshot()

		width, height = img.size
		
		scaleW = width/1920
		scaleH = height/1080
		
		crop = crop_image(img, width, height)
		# make attempt counter and after three failed attempts just click option one!
		if(attempt == attempts_before_guess):
			print("Something went wrong! :(. I'll guess the first answer!")
		
			pyautogui.moveTo(width/2, height/2 - cords[0]*scaleH)
			pyautogui.click()
		
			correct = False
			tries += 1
			attempt = 0
			prev_question = ""
		else:
			try:
				#os.chmod(crop_path, 0o777)
				text = pytesseract.image_to_string(crop, config ='--psm 6 --oem 3 -c tessedit_char_whitelist=01234567890x')
				#crop.close()
				choices = text.split("\n")
				
				question = choices.pop(0)
				if(question == prev_question):
					time.sleep(1)
					continue
				prev_question = question
				print("Question: ", question)
				print("Choice 1:", choices[0])
				print("Choice 2:", choices[1])
				print("Choice 3:", choices[2])
				print("Choice 4:", choices[3])
				if(len(choices) != 5):
					print("Something went wrong! :(. I'll guess the first answer!")
						
					pyautogui.moveTo(width/2, height/2 - cords[0])
					pyautogui.click()
				
					correct = False
					attempt = 0
					prev_question = ""
					tries += 1
				else:
					numbs = question.split("x")

					ans = int(numbs[0]) * int(numbs[1])

					i = 0
					for choice in choices:
						try:
							if(ans == int(choice)):
								correct = True
								break
							else:
								i += 1
						except ValueError as error:
							print(error)
					
					print("My Answer: ", ans, " (", i+1, ")")
				
					# determine mouse pos
					if(i == 0):
						pyautogui.moveTo(width/2, height/2 - cords[0])
					elif(i == 1):
						pyautogui.moveTo(width/2, height/2 - cords[1])
					elif(i == 2):
						pyautogui.moveTo(width/2, height/2 - cords[2])
					elif(i == 3):
						pyautogui.moveTo(width/2, height/2 - cords[3])
					else:
						print("Something went wrong! :(. I'll guess the first answer!")
						correct = False
						pyautogui.moveTo(width/2, height/2 - cords[0])
						tries+=1

					pyautogui.click()
			except Exception as e:
				print(e)
				attempt += 1
				continue
	
		if(correct):
			print("I'm assuming I was correct, +10!")
			current_rice += 10
			tries = 0
		else:
			print("I'm assuming I was wrong! I'll guess the first answer!")
		
		if(((current_rice != 0) and (current_rice % rice_before_reset == 0)) or max_tries == tries):
			print("--- Closing Tab and Starting Over ---")
			if platform == "linux" or platform == "linux2":
				webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("firefox"))
				pyautogui.hotkey('ctrl', 'w')
				webbrowser.get('firefox').open(url)
			elif platform == "win32":
				webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
				pyautogui.hotkey('ctrl', 'w')
				webbrowser.get('chrome').open(url)
			send_grains_to_server(str(current_rice))
			tries = 0
			current_rice = 0
		time.sleep(3)
except KeyboardInterrupt as error:
	print("let me try to upload to the server real quick!")
	send_grains_to_server(str(current_rice))
	
def on_press(key):
    if key == start_stop_key:
        running = False
    elif key == exit_key:
        quit()
