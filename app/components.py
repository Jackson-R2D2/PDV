from kivymd.uix.dialog import MDDialog
from time import sleep
from kivymd.uix.button import MDFlatButton, MDRaisedButton


class DialogBoxes(MDDialog):

    def __init__(self):
        self.generic_error_message_dialog = None
        self.dialog_approved  = None


    def set_error_message(self, text):
        if self.generic_error_message_dialog == None:
            self.generic_error_message_dialog = MDDialog(
                title = 'Error',
                text = text,
                auto_dismiss = False,
                buttons = [
                    MDRaisedButton(
                        text = 'Ok',
                        text_color = 'white',
                        md_bg_color = 'red',
                        on_release = self.close_dialog_error
                    )
                ]
            )
        self.generic_error_message_dialog.open()


    def close_dialog_error(self, *args):
        self.generic_error_message_dialog.dismiss()

    
    def set_approved_message(self, text):
        if self.dialog_approved == None:
            self.dialog_approved = MDDialog(
                title = 'Ok',
                text = text,
                auto_dismiss = False,
                buttons = [
                    MDRaisedButton(
                        text = 'Ok',
                        text_color = 'white',
                        md_bg_color = 'green',
                        on_release = self.close_dialog_approved
                    )
                ]
            )
        self.dialog_approved.open()

    
    def close_dialog_approved(self, *args):
        self.dialog_approved.dismiss()



    def custom_dialog(self, obj, buttons, text, content = None):
        DialogBoxes.dialog = MDDialog(
                title = 'EXIT ALERT',
                text = text,
                type = 'custom',
                content_cls = content,
                buttons = buttons
            )
        DialogBoxes.dialog.open()


    @classmethod
    def close_dialog(cls, obj):
        cls.dialog.dismiss()


class Errors():

    def set_error(self,ids):
        self.errors = {'Apenas números': [[ids.button_code_bar, ids.button_code_bar.text.isdigit],[ids.button_stock, ids.button_stock.text.isdigit]], 
        'Digite um preço válido': [[ids.button_price, ids.button_price.text.replace(',', '').isdigit]]}
        self.error = False 
    
        for message_error in self.errors:
            for widget in self.errors[message_error]:
                    if widget[1]() == False:
                        widget[0].helper_text = message_error
                        widget[0].error = True
                        self.error = True
        if self.error == False: return False