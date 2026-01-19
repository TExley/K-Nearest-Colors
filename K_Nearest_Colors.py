# importing tkinter module
import tkinter as tk
import csv
import os
# importing the choosecolor package
from tkinter import colorchooser
from tkinter.filedialog import askopenfilename
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk
import matplotlib.colors as colors
import colorsys

scale = 10
conversion = cv.COLOR_BGR2RGB

def updatefile():
    # empty the listbox
    listBox.delete(0,'end')

    file = open(f'data/save.csv', 'r')
    csv_reader = csv.reader(file, delimiter=',')
    if csv_reader:
        for row in csv_reader:
            listBox.insert(tk.END, row[0])
    file.close()

    return csv_reader != None

def choose_color():
    # variable to store hexadecimal code of color
    color_code = colorchooser.askcolor(title ="Choose color")
    print(color_code)
    return color_code

def removebox():
    selection = listBox.curselection()
    if selection:
        listBox.delete(selection[0])
        updatepicture()

def updatefilebox():
    updatefile()
    updatepicture()

def addbox():
    color_code = choose_color()
    if color_code:
        listBox.insert(tk.END, str(color_code[1]))
        updatepicture()

def closewindow():
    os.makedirs('data', exist_ok=True)
    file = open(f'data/save.csv', 'w')
    for i, entry in enumerate(listBox.get(0, tk.END)):
        file.write(f'{entry},\n');
    file.close()
    root.destroy()

def getlboxsize():
    size = 0
    for i, entry in enumerate(listBox.get(0, tk.END)):
        size += 1
    return size

def getkmatrix():
    size = getlboxsize()
    if size == 0:
        return None
    km = np.empty(shape=(size, 3), dtype=np.float16)
    km_rgb = np.empty(shape=(size, 3), dtype=np.uint8)
    for i, entry in enumerate(listBox.get(0, tk.END)):
        r, g, b = colors.hex2color(entry)
        km_rgb[i, 0] = r * 255
        km_rgb[i, 1] = g * 255
        km_rgb[i, 2] = b * 255

        one, two, three = r, g, b
        
        if conversion == cv.COLOR_BGR2HLS:
            one, two, three = colorsys.rgb_to_hls(r, g, b)
        elif conversion == cv.COLOR_BGR2HSV:
            one, two, three = colorsys.rgb_to_hsv(r, g, b)

        km[i, 0] = one
        km[i, 1] = two
        km[i, 2] = three
    return km, km_rgb

def getnearestimg():
    km, km_rgb = getkmatrix()
    convert_img = cv.cvtColor(cv_im, conversion)
    if km is not None:
        convert_img16 = (convert_img / 255).astype(np.float16)
        img_mess = np.empty(shape=(convert_img16.shape[0], convert_img16.shape[1], km.shape[0]), dtype=np.float16)
        for i in range(0, km.shape[0]):
            img_mess[:,:,i] = np.linalg.norm(convert_img16 - km[i], axis=2)
        indices = np.argpartition(img_mess, 0)[:,:,0]
        convert_img = km_rgb[indices,:]
    return convert_img

def updatepicture():
    u_img = getnearestimg()
    pil_img = Image.fromarray(u_img).resize((cv_im.shape[1] * scale, cv_im.shape[0] * scale), Image.Resampling.NEAREST)
    img = ImageTk.PhotoImage(image=pil_img)
    canvas.create_image(0, 0, image=img, anchor=tk.NW, state="normal")
    canvas.image_reference = img

root = tk.Tk()
tl = tk.Toplevel(root)

listBox = tk.Listbox(root)
listBox.pack()

os.makedirs('data', exist_ok=True)
should_update = updatefile()

AddBtn = tk.Button(root, text="Add Color", command = lambda: addbox())
AddBtn.pack()

RmBtn = tk.Button(root, text="Remove Selected", command = lambda: removebox())
RmBtn.pack()

RmBtn = tk.Button(root, text="Update From File", command = lambda: updatefilebox())
RmBtn.pack()

close_button = tk.Button(root, text="Save & Exit", command = lambda: closewindow())
close_button.pack()

cv_im = cv.imread(askopenfilename())

canvas = tk.Canvas(tl, width=cv_im.shape[1] * scale, height=cv_im.shape[0] * scale, bg="#ffffff")
canvas.pack()


rgb_img = cv.cvtColor(cv_im, cv.COLOR_BGR2RGB)
pil_img = Image.fromarray(rgb_img).resize((cv_im.shape[1] * scale, cv_im.shape[0] * scale), Image.Resampling.NEAREST)
img = ImageTk.PhotoImage(image=pil_img)
canvas.create_image(0, 0, image=img, anchor=tk.NW, state="normal")
canvas.image_reference = img

if should_update:
    updatepicture()

root.geometry("250x300")
root.mainloop()
