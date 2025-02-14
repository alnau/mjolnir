import customtkinter as ctk
import constants as const


class boolWrangler(ctk.CTkToplevel):
    def __init__(self, master, bool_values):
        super().__init__(master)
        self.master = master

        self.geometry(f"{400}x{400}")
        self.title('Действуй на свой страх и риск')
        self.deiconify()
        # print(bool_values)
        self.bool_values = bool_values
        self.check_boxes = {}
        self.check_vars = {}
        for name in bool_values:
            check_var = ctk.BooleanVar(value=bool_values[name])
            self.check_vars[name] = check_var
            self.check_vars[name].trace_add('write', lambda  *args, key = name: self.updateBool(key, *args))
            check_box = ctk.CTkCheckBox(self, text=name, onvalue=True, offvalue=False, variable=self.check_vars[name]) 
            check_box.pack(anchor = 'w',pady = 10, padx = 10)
            self.check_boxes[name] = check_box 


    def updateBool(self, key, *args):
        print('before:',self.bool_values[key] )
        self.bool_values[key] = self.check_vars[key].get()
        print('after:',self.bool_values[key])


    def closeWindow(self):
        self.destroy()
        self.update()



