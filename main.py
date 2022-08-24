"""This app allows you to perform a text search on multiple pdf files all at
once. At this time you can select multiple pdf files in different
folders or select one entire folder. Future versions will support OCR."""

import tkinter as tk
from tkinter import messagebox
import re
from os import scandir
import tkinter.filedialog as fd
import PyPDF2
import customtkinter as ctk

# Modes: "System" (standard), "Dark", "Light"
ctk.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
ctk.set_default_color_theme("blue")
# global variables that get updated dynamically
FILE_LIST = []  # Holds the pdf files to search
WIDGET_HEIGHTS = []  # For window resizing
WIDGET_WIDTHS = []  # For window resizing


# overwriting tkinter\'s callback exception method in order to display
# exceptions in message window
def report_callback_exception(val):
    messagebox.showerror("Error:", message=str(val))


tk.Tk.report_callback_exception = report_callback_exception


class App(ctk.CTk):
    """Main class for entire app"""
    def __init__(self):
        super().__init__()
        self.title("PDF Search")
        # self.configure(bg="#1B2829")
        #  Getting screen parameters in order to position the window better
        screen_size = self.wm_maxsize()
        offset = str(int(screen_size[0] // 4))
        self.update_idletasks()
        root_width = self.geometry()[0:3]
        root_height = str(int(root_width) // 2)
        self.geometry(f'{root_width}x{root_height}+{offset}+50')
        self.question_label = ctk.CTkLabel(master=self,
                                           text="What word/words are you "
                                                "looking for?",
                                           text_font=("Roboto", 25))
        self.question_label.pack(pady=10)
        self.entry_frame = ctk.CTkFrame(master=self)
        self.entry_frame.pack(pady=10)
        self.entry_box = ctk.CTkEntry(master=self.entry_frame,
                                      placeholder_text="Enter text here",
                                      text_font=("Roboto", 20),
                                      height=32, width=500)
        self.entry_box.pack(side=tk.LEFT)
        self.button_clear = ctk.CTkButton(master=self.entry_frame,
                                          text="Clear", bg_color='#00393D',
                                          height=32, width=20, bg='#00393D',
                                          command=lambda:
                                          self.entry_box.delete(
                                              0, "end"))
        self.button_clear.pack(side=tk.LEFT, padx=5)
        self.button_dir = ctk.CTkButton(master=self, bg_color='#00393D',
                                        text="Select an entire "
                                             "directory",
                                        height=32,
                                        text_font=("Roboto", 20),
                                        command=self.select_dir)
        self.button_dir.pack(pady=10)
        self.button_file = ctk.CTkButton(master=self, bg_color='#00393D',
                                         text="Select one or more "
                                              "files",
                                         height=32,
                                         text_font=("Roboto", 20),
                                         command=self.select_file)
        self.button_file.pack(pady=10, ipadx=9)
        self.selected_frame = ctk.CTkFrame(master=self, corner_radius=10)
        self.selected_textbox = tk.Text(master=self.selected_frame, bd=0,
                                        wrap=tk.NONE, height=1,
                                        bg="#292929", fg="white",
                                        highlightthickness=0,
                                        font=("Roboto", 20))
        self.selected_frame.pack_forget()
        self.selected_scrollbar = ctk.CTkScrollbar(
            master=self.selected_frame, bg="#292929",
            command=self.selected_textbox.yview)
        self.selected_scrollbar.pack(side=tk.RIGHT, fill='y', padx=5, pady=5)
        self.selected_textbox.configure(
            yscrollcommand=self.selected_scrollbar.set)
        self.search_image = tk.PhotoImage(file='search.png')
        self.button_search = ctk.CTkButton(master=self,
                                           image=self.search_image,
                                           text="Search",
                                           text_font=("Roboto", 20),
                                           height=35,
                                           compound="right",
                                           command=self.search)
        self.results_frame = ctk.CTkFrame(master=self, corner_radius=10)
        self.results_textbox = tk.Text(master=self.results_frame,
                                       wrap=tk.NONE, font=("Roboto", 20),
                                       bg="#292929", fg="white", bd=0,
                                       highlightthickness=0)
        self.results_frame.pack_forget()
        self.results_scrollbar = ctk.CTkScrollbar(
            master=self.results_frame, bg="#292929",
            corner_radius=10, command=self.results_textbox.yview)
        self.results_scrollbar.pack(side='right', fill='y', padx=5, pady=5)
        self.results_textbox.configure(
            yscrollcommand=self.results_scrollbar.set)
        for widget in (self.question_label, self.entry_frame,
                       self.button_dir, self.button_file,
                       self.selected_textbox, self.button_search,
                       self.results_textbox):
            WIDGET_HEIGHTS.append(widget)
        for widget in (self.selected_textbox,
                       self.results_textbox,
                       self.selected_scrollbar,
                       self.results_scrollbar):
            WIDGET_WIDTHS.append(widget)

    def window_resize(self) -> None:
        """Resizes window once file or folder has been selected and placed
        into the textbox to fit content"""
        height_required_list = []
        width_required_list = []
        for widget in WIDGET_HEIGHTS:
            height_required_list.append(int(widget.winfo_reqheight()))
        for widget in WIDGET_WIDTHS:
            width_required_list.append(int(widget.winfo_reqwidth()))
        # Add up all the widget heights
        minimum_height = 0
        for height in height_required_list:
            minimum_height += height
        # Get the longest width from the list
        minimum_width = max(width_required_list)
        # Make window correct size
        self.geometry(f"{minimum_width}x{minimum_height}")

    def select_dir(self) -> None:
        """Upon clicking the button to select an entire directory, we
        take what was selected, insert into the text box, and populate the
        global FILE_LIST"""
        self.selected_textbox.delete(1.0, tk.END)
        directory = fd.askdirectory(mustexist=True, title="Choose a "
                                                          "directory")
        with scandir(directory) as folder:
            for file in folder:
                if file.name.endswith('.pdf') and file.is_file():
                    FILE_LIST.append(f'{directory}/{file.name}')
        self.selected_textbox.insert(1.0, directory)
        self.selected_frame.pack(pady=10, padx=20, fill='x')
        self.selected_textbox.pack(padx=5, ipadx=10, side=tk.LEFT,
                                   fill='both')
        self.button_search.pack(pady=10)
        self.selected_textbox.configure(height=7)
        self.window_resize()

    def select_file(self) -> None:
        """Upon clicking the button to select multiple files, we
        take what was selected, insert into the text box, and populate the
        global FILE_LIST"""
        self.selected_textbox.delete(1.0, tk.END)
        files = fd.askopenfiles(mode='rb', title="Choose a file",
                                filetypes=[("Pdf file", "*.pdf")])
        if files:
            for file in files:
                self.selected_textbox.insert(1.0, f'{file.name}\n')
                FILE_LIST.append(f'{file.name}')
        self.selected_frame.pack(pady=10, padx=20, fill='x')
        self.selected_textbox.pack(ipadx=10, side=tk.LEFT, fill='both')
        self.button_search.pack(pady=10)
        self.selected_textbox.configure(height=7)
        self.window_resize()

    def search(self) -> None:
        """Extracts each page of each file from the global FILE_LIST that
        is populated by the select_dir and select_file methods and searches
        for the text entered in the entry_box. Places the hits in the
        results_textbox"""
        found_text = []
        for file in FILE_LIST:
            read_pdf = PyPDF2.PdfFileReader(file, strict=False)
            num_pages = read_pdf.getNumPages()
            search_text = self.entry_box.get()
            results_text = ''
            page_list = ''
            # Iterate over each page and do the search
            for page in range(num_pages):
                page_object = read_pdf.getPage(page)
                page_text = page_object.extractText()
                if re.search(search_text, page_text, re.I):
                    found_text.append(1)
                    page_list += str(page + 1) + ", "
                    results_text += f'\n\"{search_text}\" found on page(s) ' \
                                    f'{page_list} in file:\n{file}\n'
            self.results_textbox.insert(1.0, results_text)
        if not found_text:
            self.results_textbox.insert(1.0, "\nNot found\n")
        self.results_frame.pack(pady=10, padx=20, fill='x')
        self.results_textbox.pack(ipadx=10, side=tk.LEFT, fill='both')
        FILE_LIST.clear()
        self.window_resize()


if __name__ == "__main__":
    app = App()
    app.mainloop()
