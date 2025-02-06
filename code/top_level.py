import customtkinter as ctk
import constants as const


class TopLevel(ctk.CTkToplevel):
    def __init__(self, master, data_container):
        super().__init__(master)
        self.main = self.master.main
        self.data_container = data_container
        self.geometry(f"{300}x{400}")
        self.title('Выберете кадры для анализа')
        self.deiconify()
        self.focus()
        self.names = []
        self.check_boxes = []
        self.checkVals = []

        self.data_container_for_analysis = []
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill = 'both', expand = True)
        for i in range(len(self.data_container)):
            self.names.append(self.data_container[i].image_name)
            tmp_checkVal = ctk.IntVar(value=1)
            self.checkVals.append(tmp_checkVal)
            tmp_checkbox = ctk.CTkCheckBox(self.scroll_frame, onvalue=1,  offvalue=0, variable=self.checkVals[i], text = self.names[i])
            self.check_boxes.append(tmp_checkbox)
            
        for i in range(len(self.data_container)):
            self.check_boxes[i].pack(anchor = 'w', pady = const.DEFAULT_PADY)

        self.button_frame = ctk.CTkFrame(self.scroll_frame, fg_color='transparent')
        self.button_frame.pack()
        self.continue_button = ctk.CTkButton(self.button_frame, text = 'Начать Анализ', command = self.sendDataToAnalyze)
        self.cancel_button = ctk.CTkButton(self.button_frame, text = 'Отмена', command = self.closeWindow)

        self.continue_button.pack(side = 'left', fill = 'x', expand = True)
        self.cancel_button.pack(side = 'left', fill = 'x', expand = True)

    def closeWindow(self):
        self.destroy()
        self.update()
        self.main.toplevel_window = None


    def sendDataToAnalyze(self):
        for i in range(len(self.data_container)):
            if self.checkVals[i].get():
                print(self.data_container[i].plotname)
                self.data_container_for_analysis.append(self.data_container[i])

        self.withdraw()
        self.master.analyzeAll(self.data_container_for_analysis)
