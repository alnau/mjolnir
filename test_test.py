

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk



ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=10, padx = 2, side = 'top')
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=3)
        
        self.button1 = ctk.CTkButton(self.button_frame, text="Button 3")
        self.button1.grid(row = 0, column = 0, sticky = 'e', padx = 10, pady = 5)
        # self.button1.pack(side="left", padx=10, pady=5)

        self.button2 = ctk.CTkButton(self.button_frame, text="Button 4")
        self.button2.grid(row = 0, column = 1, padx = 10, pady = 5)
        # self.button2.pack(side="left", padx=10, pady=5)

        self.button3 = ctk.CTkButton(self.button_frame, text="Button 5")
        self.button3.grid(row = 0, column = 2, sticky = 'w', padx = 10, pady = 5)
        # self.button2.pack(side="right", padx=10, pady=5)

class LeftFrame(ctk.CTkFrame):
    def __init__(self, master, image_path, **kwargs):
        super().__init__(master, **kwargs)

        self.image_path = image_path
        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack(fill="both", padx = (5,0), pady = 5, expand=True)
        self.image = Image.open(self.image_path)

        # Bind the <Configure> event to resize the image
        
        self.bind("<Configure>", self.resize_image)

        # Load and display the initial image
        self.resize_image(None)



    
    def resize_image(self, event):
        # Get the current size of the frame
        # image = Image.open(self.image_path)
        width = self.winfo_width()
        height = self.winfo_height()

        # Load and resize the image to fit the frame
        image = self.image
        image_resized = image.resize((width, height))
        self.photo = ImageTk.PhotoImage(image_resized)

        # Update the label with the resized image
        self.image_label.configure(self, image=self.photo)

class RightFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create a matplotlib figure with a 2:1 aspect ratio
        fig, ax = plt.subplots(figsize=(5, 3))  # 4:2 aspect ratio
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.set_aspect('auto', adjustable='box')

        # Create a canvas to embed the plot
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx = 5, pady = (5,0), side = "top")

        # Add an entry field just under the plot
        self.entry_frame = ctk.CTkFrame(self, )
        self.entry_frame.pack(fill="x", pady=(10, 5), side = 'top')
        
        self.entry = ctk.CTkEntry(self.entry_frame)
        self.entry.pack(fill="x", side = 'left', padx=2, pady=2, expand = True)
        
        self.continue_button = ctk.CTkButton(self.entry_frame, text = 'Продолжить')
        self.continue_button.pack(side = 'left', pady = 2, padx = (2,2))


        # Add a thin frame just under the entry field
        self.thin_frame = ctk.CTkFrame(self, height=2, bg_color="gray")
        self.thin_frame.pack(fill="x", padx =10, pady=5,)

        self.empty_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.empty_frame.pack(fill="x", expand = True)

        # Add two buttons side by side at the bottom of the frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", pady=10, padx = 2,  side = 'top')

        self.button1 = ctk.CTkButton(self.button_frame, text="Button 1")
        self.button1.pack(side="left", padx=10, pady=5, expand = 'true')

        self.button2 = ctk.CTkButton(self.button_frame, text="Button 2")
        self.button2.pack(side="right", padx=10, pady=5,expand = 'true')


class App(ctk.CTk):    
    def __init__(self):
        super().__init__()
        self.title("mjolnir")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        height = int(0.8*screen_height)
        width = int(0.8*screen_width)
        self.geometry(f"{width}x{height}")

        self.image_path="D:\Photonics\KGW МУР\!18_d.tif"
        

        # Configure the grid for the main application window
        self.grid_columnconfigure(0, weight=2)  # Left frame is 2 times wider
        self.grid_columnconfigure(1, weight=1)  # Right frame is 1 time wider
        self.grid_rowconfigure(0, weight=1)     # Single row for the frames
        self.grid_rowconfigure(1, weight = 0)

        # Create the left frame
        # self.left_frame = LeftFrame(self, image_path="D:\Photonics\KGW МУР\!18_d.tif")
        self.left_frame = LeftFrame(self, image_path=self.image_path)
        self.left_frame.grid(row=0, column=0, rowspan = 1, sticky="nsew")

        # Create the right frame
        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=1, rowspan = 2, sticky="nsew")

        self.navigation_frame = NavigationFrame(self)
        self.navigation_frame.grid(row=1, column=0, rowspan = 1, sticky="nsew")
        # Ensure the frames resize correctly
        self.update_idletasks()  # Force an update to ensure the grid configuration is applied immediately

        # Debugging: Print frame sizes after 1 second

        self.after(1000, self.print_frame_sizes)

        # self.left_frame.resize_image(None)
        # self.bind("<Configure>", self.left_frame.resize_image)

        self.mainloop()

    def print_frame_sizes(self):
        print(f"Left frame width: {self.left_frame.winfo_width()}")
        print(f"Right frame width: {self.right_frame.winfo_width()}")

# Example usage
if __name__ == "__main__":
    app = App()

    # # Configure the grid for the main application window
    # self.grid_columnconfigure(0, weight=2)  # Left frame is 2 times wider
    # self.grid_columnconfigure(1, weight=1)  # Right frame is 1 time wider
    # self.grid_rowconfigure(0, weight=1)     # Single row for the frames

    # # Create the left frame
    # left_frame = LeftFrame(app, image_path="D:\Photonics\KGW МУР\!18_d.tif")
    # left_frame.grid(row=0, column=0, sticky="nsew")

    # # Create the right frame
    # right_frame = RightFrame(app)
    # right_frame.grid(row=0, column=1, sticky="nsew")

    # # Ensure the frames resize correctly
    # self.update_idletasks()  # Force an update to ensure the grid configuration is applied immediately

    # # Debugging: Print frame sizes after 1 second
    # def print_frame_sizes():
    #     print(f"Left frame width: {left_frame.winfo_width()}")
    #     print(f"Right frame width: {right_frame.winfo_width()}")

    # self.after(1000, print_frame_sizes)

    # self.mainloop()