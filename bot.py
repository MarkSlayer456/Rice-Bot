import os
import pyautogui
import webbrowser
import socket
import time

from PIL import Image
from pytesseract import pytesseract
from pynput.keyboard import Listener, KeyCode

url = 'https://freerice.com/categories/multiplication-table'

webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
webbrowser.get('chrome').open(url)

rice_before_reset = 1000

start_stop_key = KeyCode(char='s')
exit_key = KeyCode(char='q')
running = True
attempts_before_guess = 5

host = "10.0.0.20"
port = 14456

path_to_tess = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
user = os.getlogin()
dir_start = r'C:\Users'
dir_end = r'Desktop\Rice-Bot-Temp'
dir_temp = os.path.join(dir_start, user)
dir = os.path.join(dir_temp, dir_end)
rice_csv = os.path.join(dir, "rice.csv")

BUFFER_SIZE = 1024

# get the mouse out of the way
pyautogui.moveTo(5,5)

pytesseract.tesseract_cmd = path_to_tess

filename = "temp.png"

try:
	os.mkdir(dir)
except FileExistsError as error:
	pass
except OSError as error2:
	print(error2)

	
prev_question = ""
attempt = 0
tries = 0
current_rice = 0
max_tries = 10 # close tab and restart after this many failed attempts (not sure if correct)
try:
	while running:
		correct = False
		#pyautogui.moveTo(5,5)
		myScreenshot = pyautogui.screenshot()
		path = os.path.join(dir, filename)
		myScreenshot.save(path)

		im = Image.open(path);

		width, height = im.size

		scaleH = height/1080
		scaleW = width/1920

		left = width/2 - (200*scaleW)
		top = height/2 - (350*scaleH)
		right = width/2 + (250*scaleW)
		bottom = height / 2 + (75*scaleH)

		im1 = im.crop((left, top, right, bottom))
		try:
			im1.save(path)
		except:
			continue
		img = Image.open(path)
		# make attempt counter and after three failed attempts just click option one!
		if(attempt == attempts_before_guess):
			print("Something went wrong! :(. I'll guess the first answer!")
		
			pyautogui.moveTo(width/2, height/2 - 250*scaleH)
			pyautogui.click()
		
			correct = False
			tries += 1
			attempt = 0
			prev_question = ""
		else:
			try:
				text = pytesseract.image_to_string(img, config ='--psm 6 --oem 3 -c 	tessedit_char_whitelist=01234567890x')
				
				choices = text.split("\n")
				
				question = choices.pop(0)
				if(question == prev_question):
					sleep(1)
					continue
				prev_question = question
				print("Question: ", question)
				print("Choice 1:", choices[0])
				print("Choice 2:", choices[1])
				print("Choice 3:", choices[2])
				print("Choice 4:", choices[3])
				if(len(choices) != 5):
					print("Something went wrong! :(. I'll guess the first answer!")
						
					pyautogui.moveTo(width/2, height/2 - 250*scaleH)
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
						pyautogui.moveTo(width/2, height/2 - 250*scaleH)
					elif(i == 1):
						pyautogui.moveTo(width/2, height/2 - 190*scaleH)
					elif(i == 2):
						pyautogui.moveTo(width/2, height/2 - 130*scaleH)
					elif(i == 3):
						pyautogui.moveTo(width/2, height/2 - 70*scaleH)
					else:
						print("Something went wrong! :(. I'll guess the first answer!")
						correct = False
						pyautogui.moveTo(width/2, height/2 - 250*scaleH)
						tries+=1

					pyautogui.click()
			except:
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
			webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
			pyautogui.hotkey('ctrl', 'w')
			webbrowser.get('chrome').open(url)
			try:
				sock = socket.socket()
				sock.connect((host, port))
				grains = str(current_rice)
				read = grains.encode('utf-8')
				sock.sendall(read)
				sock.close()
				print("Grains sent to server:", grains)
			except:
				print("WARNING: Data is not being sent to the server... is it up?")
			finally:
				tries = 0
				current_rice = 0
		time.sleep(3)
except KeyboardInterrupt as error:
	print("let me try to upload to the server real quick!")
	try:
		sock = socket.socket()
		sock.connect((host, port))
		grains = str(current_rice)
		read = grains.encode('utf-8')
		sock.sendall(read)
		sock.close()
		print("Grains sent to server:", grains)
	except Error as e:
		print("WARNING: Data is not being sent to the server... is it up?")
		print(e)
	
def on_press(key):
    if key == start_stop_key:
        running = False
    elif key == exit_key:
        quit()
