import os
import numpy as np
import PIL.Image
import PIL.ImageTk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import *

from Definitions import *

class Stego:

	def __init__(self, master):
		print("Setting up GUI")
		self.master = master
		self.master.title(TITLE)

		# Images Container
		imagesContainer = Frame(master=self.master, bg=self.master['bg'])
		self.canvasOrig = Canvas(bg='white')
		self.canvasOrig.pack(in_=imagesContainer, side='left')

		self.canvasNew = Canvas(bg='white')
		self.canvasNew.pack(in_=imagesContainer, side='left')
		imagesContainer.pack(side='top', fill='x')

		# File Opening/Saving Container
		fileSelectsContainer = Frame(master=self.master, bg=self.master['bg'])
		self.pickFileBtn = Button(text='Select an image', command=self.openFileHandle)
		self.pickFileBtn.pack(in_=fileSelectsContainer, side='left')

		self.saveNewBtn = Button(text='Save new image', command=self.saveImageHandle)
		self.saveNewBtn['state'] = DISABLED
		self.saveNewBtn.pack(in_=fileSelectsContainer, side='left')
		fileSelectsContainer.pack(side='top', fill='none', expand=True)

		# Text Input
		self.textInput = ScrolledText(master=self.master, width=TEXT_INPUT_W, height=TEXT_INPUT_H)
		self.textInput['state'] = DISABLED
		self.textInput.pack()

		# Step Input Container
		stepsContainer = Frame(master=self.master, bg=self.master['bg'])
		stepsLabel = Label(text='Step: ')
		stepsLabel.pack(in_=stepsContainer, side='left')

		self.stepsVar = StringVar()
		self.stepsVar.set(DEFAULT_STEP_COUNT)
		self.stepsInput = Entry(textvariable=self.stepsVar)
		self.stepsInput['state'] = DISABLED
		self.stepsInput.pack(in_=stepsContainer, side='left')

		self.maskSteps = IntVar()
		self.maskSteps.set(DEFAULT_MASK)
		self.maskStepsBtn = Checkbutton(text='Mask Steps', variable=self.maskSteps)
		self.maskStepsBtn['state'] = DISABLED
		self.maskStepsBtn.pack(in_=stepsContainer, side='left')
		stepsContainer.pack(side='top', fill='none', expand=True)

		# Message Buttons Container
		messageBtnsContainer = Frame(master=self.master, bg=self.master['bg'])
		self.hideMessageBtn = Button(text='Hide Message', command=self.hideMessageHandle)
		self.hideMessageBtn['state'] = DISABLED
		self.hideMessageBtn.pack(in_=messageBtnsContainer, side='left')

		self.showMessageBtn = Button(text='Recover Message', command=self.recoverMessageHandle)
		self.showMessageBtn['state'] = DISABLED
		self.showMessageBtn.pack(in_=messageBtnsContainer, side='left')
		messageBtnsContainer.pack(side='top', fill='none', expand=True)

		# Close Button
		self.closeBtn = Button(master=self.master, text='Close', command=master.quit)
		self.closeBtn.pack()

	def enableButtons(self):
		print("Enabling Buttons")
		self.saveNewBtn['state'] = NORMAL
		self.saveNewBtn.update()

		self.showMessageBtn['state'] = NORMAL
		self.showMessageBtn.update()

		self.hideMessageBtn['state'] = NORMAL
		self.hideMessageBtn.update()

		self.textInput['state'] = NORMAL
		self.textInput.update()

		self.stepsInput['state'] = NORMAL
		self.stepsInput.update()

		self.maskStepsBtn['state'] = NORMAL
		self.maskStepsBtn.update()

	# pickFileBtn callback
	def openFileHandle(self):
		print("Open File Handler Hit")
		
		filePath = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select a File', filetypes=(('png files', '*.png'),('all files', '*.*')))
		print("File Path Selected: {}".format(filePath))

		if filePath == "":
			return
		self.canvasOrig.filePath = filePath
		self.canvasOrig.img = PIL.Image.open(filePath)
		w, h = self.canvasOrig.img.size
		self.canvasOrig.config(width=w, height=h)
		self.canvasOrig.tkImg = PIL.ImageTk.PhotoImage(self.canvasOrig.img)
		self.canvasOrig.imgSprite = self.canvasOrig.create_image(w/2, h/2, anchor=CENTER, image=self.canvasOrig.tkImg)
		self.canvasOrig.update()

		self.enableButtons()

	# Convert a string to an array of bits
	def convertStringToBitsArray(self):
		print("Converting Message to Bit Array")
		bytes = bytearray()
		bytes.extend(self.textInput.get('1.0', END).encode('utf-8'))
		bytes.append(23) # End of Transmission Block utf-8 character
		bits = np.unpackbits(bytes)
		return bits

	def hideMessageHandle(self):
		print("Hide Message Handler Hit")
		
		self.canvasNew.filePath = self.canvasOrig.filePath
		self.canvasNew.img = PIL.Image.open(self.canvasNew.filePath)
		w, h = self.canvasNew.img.size
		self.canvasNew.config(width=w, height=h)
		self.canvasNew.tkImg = PIL.ImageTk.PhotoImage(self.canvasNew.img)
		self.canvasNew.imgSprite = self.canvasNew.create_image(w/2, h/2, anchor=CENTER, image=self.canvasNew.tkImg)
		self.canvasNew.update()
		
		
		bits = self.convertStringToBitsArray()
		size = self.canvasNew.img.size
		width, height = size

		newImg = PIL.Image.new('RGB', (width, height), 'white')
		pixels = newImg.load()

		# Use best fit steps if user did not enter a step count
		if self.stepsVar.get() == '':
			totalPixels = width * height - 4
			tempStep = max(totalPixels * 3 // len(bits), 1)
			# Biggest step we can hold in 12 bits is 4095
			step = min(tempStep, MAX_STEP)
			self.stepsVar.set(str(step))
		else: # Use User input step
			step = int(self.stepsVar.get())
			if step > MAX_STEP:
				step = MAX_STEP
				self.stepsVar.set(str(step))

		print("Step Count: {}".format(step))

		settingsBits = '{0:012b}'.format(step)

		bitsPtr = 0
		settingsPtr = 0
		for i in range(width):
			for j in range(height):
				pixel = self.canvasNew.img.getpixel((i, j))
				if settingsPtr < len(settingsBits) and self.maskSteps.get() == 0:
					r = (pixel[0] & ~1) | int(settingsBits[settingsPtr])
					settingsPtr += 1
					g = (pixel[1] & ~1) | int(settingsBits[settingsPtr])
					settingsPtr += 1
					b = (pixel[2] & ~1) | int(settingsBits[settingsPtr])
					settingsPtr += 1
					pixels[i, j] = (r, g, b)
				elif settingsPtr < len(settingsBits) and self.maskSteps.get() == 1:
					pixels[i, j] = pixel
					settingsPtr += 1
				else:
					if (i * width + j) % step == 0: # Change this pixel
						if bitsPtr + 3 < len(bits):
							r = (pixel[0] & ~1) | bits[bitsPtr]
							bitsPtr += 1
							g = (pixel[1] & ~1) | bits[bitsPtr]
							bitsPtr += 1
							b = (pixel[2] & ~1) | bits[bitsPtr]
							bitsPtr += 1
							pixels[i, j] = (r, g, b)
						else:
							pixels[i, j] = pixel
					else: # Use original pixel
						pixels[i, j] = pixel

		self.canvasNew.img = newImg
		self.canvasNew.tkImg = PIL.ImageTk.PhotoImage(self.canvasNew.img)
		self.canvasNew.imgSprite = self.canvasNew.create_image(width/2, height/2, anchor=CENTER, image=self.canvasNew.tkImg)
		self.canvasNew.update()
		print('Hide Message Handle Hit')

	def saveImageHandle(self):
		print('Save Message Handle Hit')
		filepath = filedialog.asksaveasfilename(initialdir=os.getcwd(), title='Save as', filetypes=(('png file', '*.png'), ('all files', '*.*')))
		if '.png' != filepath[-4:]:
			filepath += '.png'
		self.canvasNew.img.save(filepath, 'png')
		print("File saved as: {}".format(filepath))

	def recoverMessageHandle(self):
		print("Recover Message Handler Hit")
		
		self.canvasNew.filePath = self.canvasOrig.filePath
		self.canvasNew.img = PIL.Image.open(self.canvasNew.filePath)
		w, h = self.canvasNew.img.size
		self.canvasNew.config(width=w, height=h)
		self.canvasNew.tkImg = PIL.ImageTk.PhotoImage(self.canvasNew.img)
		self.canvasNew.imgSprite = self.canvasNew.create_image(w/2, h/2, anchor=CENTER, image=self.canvasNew.tkImg)
		self.canvasNew.update()

		newImg = PIL.Image.new('RGB', (w, h), 'white')
		pixels = newImg.load()

		allBitsArr = []

		if self.stepsVar.get() != '':
			print("Using User Input for Steps")
			step = max(int(self.stepsVar.get()), 1)
		else:
			print("Using Calculated Number for Steps")
			settingsBits = ""
			for x in range(4):
				pixel = self.canvasNew.img.getpixel((0, x))
				rBit = (pixel[0] & 1)
				gBit = (pixel[1] & 1)
				bBit = (pixel[2] & 1)
				settingsBits += (str(rBit))
				settingsBits += (str(gBit))
				settingsBits += (str(bBit))
				pixels[0, x] = (0, 0, 0)

			step = int(settingsBits, 2)
			self.stepsVar.set(step)

		for i in range(w):
			for j in range(h):
				# Ignore first 4 pixels (Message starts after the first 4 pixels)
				if i == 0 and j < 4:
					continue
				pixel = self.canvasNew.img.getpixel((i, j))
				if (i * w + j) % step == 0: # Get bits of msg and change this pixel to black
					rBit = (pixel[0] & 1)
					gBit = (pixel[1] & 1)
					bBit = (pixel[2] & 1)
					allBitsArr.append(rBit)
					allBitsArr.append(gBit)
					allBitsArr.append(bBit)
					pixels[i, j] = (0, 0, 0)
				else: # Use original pixel
					pixels[i, j] = pixel

		msgBytes = np.packbits(allBitsArr)
		msg = ""
		for ele in msgBytes:
			if ele == 23:
				break
			msg += str(chr(ele))
		self.textInput.delete('1.0', END)
		self.textInput.insert('1.0', msg)
		print("Message recovered: {}".format(msg))

		self.canvasNew.img = newImg
		self.canvasNew.tkImg = PIL.ImageTk.PhotoImage(self.canvasNew.img)
		self.canvasNew.imgSprite = self.canvasNew.create_image(w/2, h/2, anchor=CENTER, image=self.canvasNew.tkImg)
		self.canvasNew.update()

if __name__ == '__main__':
	print("Starting Stego")
	root = Tk()
	gui = Stego(root)
	root.mainloop()
	print("Closing Stego")
