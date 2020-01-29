### Using Stego

#### Installing Dependencies
Run the following lines in a command shell to install the proper dependencies:
- `pip install Pillow`
- `pip install NumPy`

#### Running the Program
- Execute `python stego.py` in a command shell to open the Steganography GUI.

#### Hiding a Message:
- Click `Select an Image`. A file select dialog will open, pointing at the directory the program is in.
- Select an image. By default, `*.png` files are shown. You can select any image file supported by PIL by 
changing the filetype the selector displays. Upon selecting an image, it will be displayed within the Steganography
window.
- Enter a message you'd like to hide inside of the image.
- Specify Step Count or leave blank. If left blank, the program will find the best Step Count to fit the message into the
pixel count.
- Check `Mask Steps` if you'd like the program to not place the step settings into the image.
- With a message entered and the wanted Step settings entered/selected, click `Hide Message` to hide the message in the selected
picture.
- Click `Save New Image` to save the newly created image to the local filesystem.

#### Recovering a Message:
- Click `Select an Image`. A file select dialog will open, pointing at the directory the program is in.
- Select an image that contains a hidden message. By default, `*.png` files are shown. You can select any image file supported by PIL by 
changing the filetype the selector displays. Upon selecting an image, it will be displayed within the Steganography
window.
- Click `Recover Message` to retrieve the hidden message within the image. If the 'Mask Steps' option was selected during message hiding, 
you will need to know and enter the correct Steps Count to retrieve the hidden message. If the 'Mask Steps' option was NOT selected during
message hiding, the program will read the first 4 pixels to determine the Step Count.
- The output image will display black pixels for any pixels it attempted to retrieve bits of the message from.


abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ