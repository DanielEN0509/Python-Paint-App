import os
import random
from tkinter import *
from tkinter import DOTBOX, StringVar
from tkinter import Frame, NW, Label
from tkinter import Tk, Canvas, Button
from tkinter import colorchooser, OptionMenu, messagebox
from tkinter import filedialog
from tkinter import font
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk
from PIL import ImageGrab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image as RLImage
from reportlab.platypus import SimpleDocTemplate

root = Tk()
root.title("Daniel's PaintApp")
root.geometry("1100x600")

# ---------------------------variables---------------------------
# Variables for size
options = [i for i in range(1, 72, 3)]
stroke_size = IntVar()
stroke_size.set(8)

# Variables for color
stroke_color = StringVar()
stroke_color.set("black")
previousColor = StringVar()
previousColor.set("white")
previousColor2 = StringVar()
previousColor2.set("white")

# Variables for Pencil
current_tool = "Pencil"
prev_point = [0, 0]
currentPoint = [0, 0]

# Variable for text
textValue = StringVar()

# Variables for font
font_choice = StringVar()
font_choice.set("Arial")
font_list = font.families()
selected_font = font.Font(family=font_list[0], size=stroke_size.get())

# Variables for shape
shape_var = StringVar(root)
shape_var.set("Shapes")
current_shape = None
fill_color = StringVar()
fill_color.set("white")
outline_color = StringVar()
outline_color.set("black")

# Variables for functions
actions_stack = []
selected_items = []

start_x = 0
start_y = 0
initial_x = 0
initial_y = 0
line_points = 0
selected_item = None
line_id = 0
selected_items_positions = {}
line_ids = []
object_data = {}


# ------------------------functions-------------------

def update_cursor():
    """Set match cursor to the current tool"""
    global current_tool
    if current_tool == "Pencil":
        canvas["cursor"] = "arrow"
    elif current_tool == "Eraser":
        canvas["cursor"] = "dotbox"
    elif current_tool == "Spray":
        canvas["cursor"] = "sprayCan"
    else:
        canvas["cursor"] = "arrow"


def change_tool(tool):
    """Change the current drawing tool the specified tool"""
    global current_tool
    current_tool = tool
    update_cursor()


def select_move_items_tool():
    """Select the tool for moving items on the canvas"""
    global current_tool
    current_tool = "Move Items"


def select_pencil_tool():
    """Select the pencil tool for drawing freehand lines"""
    change_tool("Pencil")


def select_shape_tool():
    """Select the shape drawing tool for creating geometric shapes"""
    change_tool("Shape")


def select_eraser_tool():
    """Select the eraser tool for erasing drawn elements"""
    change_tool("Eraser")


def select_order_tool():
    """Select the tool for changing the order of objects on the canvas"""
    change_tool("Order")


def select_spray_tool():
    """Select the spray tool for creating a spray paint effect"""
    change_tool("Spray")


def select_delete_tool():
    """Select the tool for deleting items on the canvas"""
    global current_tool
    current_tool = "Erase"
    canvas.bind("<Button-1>", delete_item)


def use_pencil():
    """Set up the canvas for using the pencil tool"""
    global current_tool
    select_pencil_tool()
    stroke_color.set("black")
    stroke_size.set(8)
    canvas["cursor"] = "arrow"


def paint(event):
    """Draw on the canvas with the currently selected tool"""
    global prev_point, line_points

    x = event.x
    y = event.y
    current_point = [x, y]

    if prev_point != [0, 0]:
        canvas.create_line(prev_point[0], prev_point[1], current_point[0], current_point[1],
                           fill=stroke_color.get(),
                           width=stroke_size.get(), capstyle="round", smooth=True)
    prev_point = current_point

    if event.type == "5":
        prev_point = [0, 0]


def use_eraser():
    """Set up the canvas for using the eraser tool"""
    stroke_color.set("white")
    canvas["cursor"] = DOTBOX


def erase(event):
    """Erase parts of the drawing on the canvas"""
    global prev_point, currentPoint
    x = event.x
    y = event.y
    currentPoint = [x, y]

    if prev_point != [0, 0]:
        canvas.create_line(prev_point[0], prev_point[1], currentPoint[0], currentPoint[1],
                           fill="white",
                           width=stroke_size.get(), capstyle="round", smooth=True)

    prev_point = currentPoint

    if event.type == "5":
        prev_point = [0, 0]
    canvas["cursor"] = "dotbox"


def select_color():
    """Allow the user to select a color for drawing"""
    global current_tool
    if current_tool != "Spray":
        current_tool = "Pencil"
    selectedColor = colorchooser.askcolor("blue", title="Select Color")
    if selectedColor[1] is None:
        stroke_color.set("black")
    else:
        stroke_color.set(selectedColor[1])
        update_text_color()
        previousColor2.set(previousColor.get())
        previousColor.set(selectedColor[1])

        currentColorButton["bg"] = previousColor.get()
        previousColorButton["bg"] = previousColor2.get()


def set_previous_color(color):
    """Set the previously used color"""
    previousColor.set(color)


def set_color_and_previous(color):
    """Set the current color for drawing and update the previously used color"""
    global current_tool
    if current_tool != "Spray":
        current_tool = "Pencil"
    stroke_color.set(color)
    update_previous_color2(previousColor.get())
    set_previous_color(color)
    currentColorButton["bg"] = previousColor.get()
    previousColorButton["bg"] = previousColor2.get()


def update_previous_color2(color):
    """Update the secondary previous color"""
    if current_tool in ["Pencil", "Spray"]:
        if stroke_color.get() != color:
            previousColor2.set(color)


def save_image():
    """Save the current canvas content as an image file"""
    try:
        filetypes = [("JPEG files", "*.jpg"),
                     ("PDF files", "*.pdf"),
                     ("SVG files", "*.svg"),
                     ("All files", "*.*")]
        fileLocation = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".jpg")
        if fileLocation:
            if fileLocation.endswith(".pdf"):
                # Save as PDF
                x = root.winfo_rootx()
                y = root.winfo_rooty() + 100
                img = ImageGrab.grab(bbox=(x, y, x + 1100, y + 500))
                # Save temporary JPEG image
                img.save("temp_image.jpg")

                pdf_path = fileLocation
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                img_path = "temp_image.jpg"
                rl_img = RLImage(img_path)
                rl_img.drawHeight = 300
                rl_img.drawWidth = 500
                doc.build([rl_img])
                # Remove the temporary image file
                os.remove("temp_image.jpg")
            elif fileLocation.endswith(".svg"):
                # Save as SVG
                x = root.winfo_rootx()
                y = root.winfo_rooty() + 100
                img = ImageGrab.grab(bbox=(x, y, x + 1100, y + 500))
                # Save temporary JPEG image
                img.save("temp_image.jpg")
                img = Image.open("temp_image.jpg")
                # Convert to SVG and save
                img.save(fileLocation[:-3] + "jpg")
                # Remove the temporary image file
                os.remove("temp_image.jpg")
            else:
                # Save as JPG
                x = root.winfo_rootx()
                y = root.winfo_rooty() + 100
                img = ImageGrab.grab(bbox=(x, y, x + 1100, y + 500))
                img.save(fileLocation)

    except Exception as e:
        messagebox.showinfo("Error", "An error occurred: " + str(e))


def clear_canvas():
    """Clear all elements from the canvas"""
    if messagebox.askokcancel("Daniel's PaintApp", "Do you want to clear all? "):
        canvas.delete('all')


def create_new():
    """Create a new canvas, optionally prompting the user to save the current one"""
    response = messagebox.askyesnocancel("Daniel's PaintApp",
                                         "Do you want to save your work before clearing all?")
    if response is None:
        return
    elif response:
        save_image()
        canvas.delete('all')
    else:
        canvas.delete('all')


def helper():
    """Display a help message describing how to use the application"""
    helpText = ("1. Draw by holding the right mouse button to create lines.\n\n"
                "2. Click the scroll button to put text on the canvas.\n\n"
                "3. Click on 'Select Color' to choose a specific color.\n\n"
                "4. Click on 'Clear' to erase the entire canvas.\n\n"
                "5. Move object by holding down the left mouse button and dragging it around the canvas.\n\n"
                "6. Move items by selecting them with a left-click and then move them by holding down the left mouse "
                "button.\n\n"
                "7. Change Order by clicking the right mouse button on the upper object.\n\n"
                "8. Choose shape fill and outline, and create it by long-pressing the left mouse button and dragging "
                "the mouse.")

    messagebox.showinfo("Help", helpText)


def write_text(event):
    """Write text on the canvas at the specified location"""
    global selected_font
    canvas.create_text(event.x, event.y, text=textValue.get(), fill=stroke_color.get(),
                       font=(selected_font, stroke_size.get()))


def update_text_color():
    """Update the text color"""
    stroke_color.get()


def update_font(font_name):
    """Update the selected font for text drawing"""
    global selected_font
    selected_font = font_name


def start_move(event):
    """Start moving an item on the canvas"""
    global selected_item, initial_x, initial_y
    selected_item = canvas.find_closest(event.x, event.y)
    initial_x = event.x
    initial_y = event.y


def move_item(event):
    """Move an item on the canvas"""
    global initial_x, initial_y
    if selected_item:
        delta_x = event.x - initial_x
        delta_y = event.y - initial_y
        canvas.move(selected_item, delta_x, delta_y)
        initial_x = event.x
        initial_y = event.y


def stop_move(event):
    """Stop moving an item on the canvas"""
    global selected_item
    selected_item = None
    selected_items.clear()


def start_shape(event):
    """Start drawing a shape on the canvas"""
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas["cursor"] = "arrow"


def end_shape(event):
    """End drawing a shape on the canvas"""
    global start_x, start_y
    end_x, end_y = event.x, event.y
    shape_type = shape_var.get()
    if shape_type == "Rectangle":
        canvas.create_rectangle(start_x, start_y, end_x, end_y, outline=outline_color.get(), fill=fill_color.get())
    elif shape_type == "Circle":
        canvas.create_oval(start_x, start_y, end_x, end_y, outline=outline_color.get(), fill=fill_color.get())
    elif shape_type == "Ellipse":
        canvas.create_oval(start_x, start_y, end_x, end_y, outline=outline_color.get(), fill=fill_color.get())
    elif shape_type == "Triangle":
        points = [start_x, end_y, end_x, end_y, (start_x + end_x) / 2, start_y]
        canvas.create_polygon(points, outline=outline_color.get(), fill=fill_color.get())
    elif shape_type == "Line":
        canvas.create_line(start_x, start_y, end_x, end_y, fill=outline_color.get())
    elif shape_type == "Semi Circle":
        canvas.create_arc(start_x, start_y, end_x, end_y, start=0, extent=180, outline=outline_color.get(),
                          fill=fill_color.get())


def select_fill_color():
    """Allow the user to select a fill color for shapes"""
    selected_color = askcolor(title="Select Fill Color")
    if selected_color[1] is not None:
        fill_color.set(selected_color[1])
        fillColorButton.configure(bg=selected_color[1])


def select_outline_color():
    """Allow the user to select an outline color for shapes"""
    selected_color = colorchooser.askcolor(title="Select Outline Color")
    if selected_color[1] is not None:
        outline_color.set(selected_color[1])
        outlineColorButton.configure(bg=selected_color[1])


def open_image():
    """Open an image file and display it on the canvas"""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    if file_path:
        img = Image.open(file_path)
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=NW, image=canvas.image)


def handle_left_click(event):
    """Handle left mouse clicks on the canvas"""
    if current_tool == "Pencil":
        paint(event)
    elif current_tool == "Shape":
        start_shape(event)
    elif current_tool == "Eraser":
        erase(event)
    elif current_tool == "Spray":
        spray(event)
    elif current_tool == "Order":
        swap_objects()
    elif current_tool == "Move Items":
        add_to_selected_items(event)


def handle_left_motion(event):
    """Handle left mouse motion on the canvas"""
    if current_tool == "Pencil":
        paint(event)
    elif current_tool == "Eraser":
        erase(event)
    elif current_tool == "Spray":
        spray(event)
    elif current_tool == "Order":
        pass
    elif current_tool == "Move Items":
        pass


def handle_left_release(event):
    """Handle left mouse button release on the canvas"""
    global current_tool
    if current_tool == "Pencil":
        paint(event)
    elif current_tool == "Shape":
        end_shape(event)
    elif current_tool == "Eraser":
        erase(event)
    elif current_tool == "Spray":
        spray(event)
    elif current_tool == "Order":
        pass
    elif current_tool == "Move Items":
        pass


def handle_right_release():
    """Handle right mouse button release on the canvas"""
    global current_tool
    if current_tool == "Move Items":
        clear_selected_items()
        stop_move()
    else:
        stop_move()


def handle_right_motion(event):
    """Handle right mouse motion on the canvas"""
    global current_tool
    if current_tool == "Move Items":
        move_selected_items(event)
    else:
        move_item(event)


def add_to_selected_items(event):
    """Add an item to the list of selected items on the canvas"""
    item = canvas.find_closest(event.x, event.y)
    if item not in selected_items:
        selected_items.append(item)


def save_selected_items(event):
    """Save selected items on the canvas"""
    global selected_items_positions
    item = canvas.find_closest(event.x, event.y)[0]
    selected_items.append(item)
    selected_items_positions[item] = [canvas.coords(item)]


def move_selected_items(event):
    """Move selected items on the canvas"""
    global selected_items_positions, selected_items
    global start_x, start_y

    if start_x is None or start_y is None:
        start_x = event.x
        start_y = event.y
    else:
        delta_x = event.x - start_x
        delta_y = event.y - start_y

        for item in selected_items:
            if canvas.find_withtag(item):
                canvas.move(item, delta_x, delta_y)
                if item in selected_items_positions:
                    selected_items_positions[item].append(canvas.coords(item))
                else:
                    selected_items_positions[item] = [canvas.coords(item)]

        start_x = event.x
        start_y = event.y


def clear_selected_items():
    """Clear selected items from the canvas"""
    global selected_items
    for item in selected_items:
        canvas.delete(item)


def delete_item(event):
    """Delete an item from the canvas"""
    global current_tool
    if current_tool == "Erase":
        item, = canvas.find_closest(event.x, event.y)
        canvas.delete(item)
        canvas.unbind("<Button-1>")
        canvas.bind("<Button-1>", handle_left_click)


def use_spray():
    """Set up the canvas for using the spray paint tool"""
    global current_tool
    current_tool = "Spray"
    canvas["cursor"] = "sprayCan"


def spray(event):
    """Use the spray paint tool on the canvas"""
    x = event.x
    y = event.y
    spray_size = stroke_size.get()
    density = 5
    for i in range(density):
        rx = random.randint(x - spray_size, x + spray_size)
        ry = random.randint(y - spray_size, y + spray_size)
        canvas.create_rectangle(rx, ry, rx, ry, fill=stroke_color.get(), width=0)


def undo():
    """Undo the last action on the canvas"""
    global actions_stack
    if canvas.find_all():
        item = canvas.find_all()[-1]
        actions_stack.append(item)
        canvas.delete(item)


def swap_objects():
    """Swap the order of overlapping objects on the canvas"""
    global current_tool
    if current_tool == "Order":
        clicked_object = canvas.find_withtag("current")
        if clicked_object:
            overlapping_objects = canvas.find_overlapping(*canvas.bbox(clicked_object))
            if overlapping_objects:
                top_object = overlapping_objects[-1]
                if top_object != clicked_object:
                    canvas.tag_raise(top_object)
                    canvas.tag_lower(clicked_object)


# ------------------user Interface---------------


# Frame 1 : Buttons

frame1 = Frame(root, height=100, width=1100)
frame1.grid(row=0, column=0, sticky=NW)

# Tools Frame

toolsFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
toolsFrame.grid(row=0, column=0)

pencilButton = Button(toolsFrame, text="Pencil", width=10, command=select_pencil_tool)
pencilButton.grid(row=0, column=0)
eraserButton = Button(toolsFrame, text="Eraser", width=10, command=select_eraser_tool)
eraserButton.grid(row=1, column=0)
sprayButton = Button(toolsFrame, text="Spray", width=10, command=use_spray)
sprayButton.grid(row=2, column=0)

# Size Frame

sizeFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
sizeFrame.grid(row=0, column=1)

defaultButton = Button(sizeFrame, text="Default", width=10, command=use_pencil)
defaultButton.grid(row=0, column=0)
sizeLabel = Label(sizeFrame, text="Size", width=10)
sizeLabel.grid(row=1, column=0)
sizeList = OptionMenu(sizeFrame, stroke_size, *options)
sizeList.grid(row=2, column=0)

# ColorBox Frame

colorBoxFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
colorBoxFrame.grid(row=0, column=2)

colorBoxButton = Button(colorBoxFrame, text="Select Color", width=10, command=select_color)
colorBoxButton.grid(row=0, column=0)
currentColorButton = Button(colorBoxFrame, text="Current Color", width=10,
                            command=lambda: set_color_and_previous(previousColor.get()))
currentColorButton.grid(row=1, column=0)
previousColorButton = Button(colorBoxFrame, text="Previous Color", width=10,
                             command=lambda: set_color_and_previous(previousColor2.get()))
previousColorButton.grid(row=2, column=0)

# Colors Frame

colorsFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
colorsFrame.grid(row=0, column=3)

redButton = Button(colorsFrame, text="Red", bg="red", width=10, command=lambda: set_color_and_previous("red"))
redButton.grid(row=0, column=0)
GreenButton = Button(colorsFrame, text="Green", bg="green", width=10, command=lambda: set_color_and_previous("green"))
GreenButton.grid(row=1, column=0)
BlueButton = Button(colorsFrame, text="Blue", bg="blue", width=10, command=lambda: set_color_and_previous("blue"))
BlueButton.grid(row=2, column=0)
yellowButton = Button(colorsFrame, text="Yellow", bg="yellow", width=10,
                      command=lambda: set_color_and_previous("yellow"))
yellowButton.grid(row=0, column=1)
orangeButton = Button(colorsFrame, text="Orange", bg="orange", width=10,
                      command=lambda: set_color_and_previous("orange"))
orangeButton.grid(row=1, column=1)
purpleButton = Button(colorsFrame, text="Purple", bg="purple", width=10,
                      command=lambda: set_color_and_previous("purple"))
purpleButton.grid(row=2, column=1)

# Open Save New Frame
saveImageFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
saveImageFrame.grid(row=0, column=4)

openButton = Button(saveImageFrame, text="Open", bg="white", width=10, command=open_image)
openButton.grid(row=0, column=0)
saveImageButton = Button(saveImageFrame, text="Save", bg="white", width=10, command=save_image)
saveImageButton.grid(row=1, column=0)
newImageButton = Button(saveImageFrame, text="New", bg="white", width=10, command=create_new)
newImageButton.grid(row=2, column=0)

# Undo Delete Clear Frame

copyPasteFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
copyPasteFrame.grid(row=0, column=5)

undoButton = Button(copyPasteFrame, text="Undo", bg="white", width=10, command=undo)
undoButton.grid(row=0, column=0)
deleteItemButton = Button(copyPasteFrame, text="Delete Item", bg="white", width=10, command=select_delete_tool)
deleteItemButton.grid(row=1, column=0)
clearButton = Button(copyPasteFrame, text="Clear", bg="white", width=10, command=clear_canvas)
clearButton.grid(row=2, column=0)

# Text Frame

textFrame = Frame(frame1, height=100, width=200, relief=SUNKEN, borderwidth=4)
textFrame.grid(row=0, column=6)

textTitleButton = Label(textFrame, text="Write your text here:", width=20)
textTitleButton.grid(row=0, column=0, columnspan=1)
settingButton = Entry(textFrame, textvariable=textValue, bg="white", width=20, justify="right")
settingButton.grid(row=1, column=0)
clearButton = Button(textFrame, text="Clear", bg="white", width=10, command=lambda: textValue.set(""))
clearButton.grid(row=2, column=0)
fontMenu = OptionMenu(textFrame, font_choice, *font_list, command=lambda font_name: update_font(font_name))
fontMenu.grid(row=3, column=0)

# Shape Frame

noteFrame = Frame(frame1, height=100, width=400, relief=SUNKEN, borderwidth=4)
noteFrame.grid(row=0, column=7)

shapes_title = Label(noteFrame, text="SHAPES")
shapes_title.grid(row=0, column=0, columnspan=2)
shape_menu = OptionMenu(noteFrame, shape_var, "Rectangle", "Circle", "Ellipse",
                        "Triangle", "Line", "Semi Circle", command=lambda shape: select_shape_tool())
shape_menu.grid(row=1, column=0, columnspan=2)
fillColorButton = Button(noteFrame, text="Fill", width=10, command=select_fill_color)
fillColorButton.grid(row=2, column=0, padx=5)
outlineColorButton = Button(noteFrame, text="Outline", width=10, command=select_outline_color)
outlineColorButton.grid(row=3, column=0, padx=5)

# Move Change order Move items Frame

othersFrame = Frame(frame1, height=100, width=100, relief=SUNKEN, borderwidth=3)
othersFrame.grid(row=0, column=8)

moveItemsButton = Button(othersFrame, text="Move Items", bg="white", width=10, command=select_move_items_tool)
moveItemsButton.grid(row=1, column=0)
orderButton = Button(othersFrame, text="Change Order", bg="white", width=10, command=select_order_tool)
orderButton.grid(row=2, column=0)
helperButton = Button(othersFrame, text="Help", bg="white", width=10, command=helper)
helperButton.grid(row=3, column=0)

# Frame 2 : Canvas

frame2 = Frame(root, height=600, width=1100, bg="yellow")
frame2.grid(row=1, column=0)

canvas = Canvas(frame2, height=600, width=1100, bg="white")
canvas.grid(row=0, column=0)

# Mouse Operations

canvas.bind("<Button-1>", handle_left_click)
canvas.bind("<B1-Motion>", handle_left_motion)
canvas.bind("<ButtonRelease-1>", handle_left_release)
canvas.bind("<B3-Motion>", handle_right_motion)
canvas.bind("<Button-2>", write_text)
canvas.bind("<Button-3>", start_move)
canvas.bind("<ButtonRelease-3>", stop_move)

# Running the program

root.resizable(False, False)
root.mainloop()
