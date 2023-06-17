import sqlite3
from tables import Products
from components import DialogBoxes, Errors
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('static/kv_file/style.kv')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

class MDDialogContent(BoxLayout):
    pass


class AppManager(ScreenManager):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.home = Home(name = 'Home')
        self.point_of_sale = PointOfSale(name = 'PDV')
        self.form = Form(name = 'Form')
        self.list_products = ListProducts(name = 'ListProducts')
        
        self.add_widget(self.home)
        self.add_widget(self.point_of_sale)
        self.add_widget(self.form)
        self.add_widget(self.list_products)

    
    def change_screen(self, screen='Home'):
        self.current = screen


class Home(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog_to_confirm_aplication_exit = None
    

    def exit_alert_dialog(self):
        if not self.dialog_to_confirm_aplication_exit:
            self.dialog_to_confirm_aplication_exit = MDDialog(
                title = 'EXIT ALERT',
                text = 'Tem certeza que quer sair do aplicativo?',
                buttons = [
                    MDFlatButton(
                        text='Cancelar',
                        text_color = 'blue',
                        on_release = self.close_dialog
                    ),
                    MDRaisedButton(
                        text='Confirmar',
                        text_color = 'white',
                        md_bg_color = 'green',
                        on_release = MainApp().exit
                    )
                ]
            )
        self.dialog_to_confirm_aplication_exit.open()


    def close_dialog(self, obj):
        self.dialog_to_confirm_aplication_exit.dismiss()


class PointOfSale(Screen):
    
    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        self.total_of_purchase = 0
        self.keys = {'9': self.exit_point_of_sale, '285': self.reset_purchase, '286': self.make_the_purchase, '287': self.remove_product, '13': self.calculate_change}
        self.fields = (self.ids.field_description, self.ids.field_code_bar, self.ids.unitary_value, self.ids.money_change, self.ids.purchase_total, self.ids.total_received, self.ids.quantity_of_items)
        self.dialog_boxes = DialogBoxes()
        self.table = MDDataTable(
            size_hint = (None, None),
            width = 800,
            height = 555,
            rows_num = 100,
            padding = (80, 0, 0, 100),
            use_pagination = True,
            pagination_menu_height = '120dp',
            background_color = [1,0,0,1],
            column_data = [
                ("Código", dp(25)),
                ("Descrisão", dp(50)),
                ("preço", dp(20)),
                ("estoque", dp(20)),
                ("tipo", dp(25))
            ],
            row_data = []
        )
        self.ids.main_grid.add_widget(self.table)


    def exit_point_of_sale(self): 
        self.parent.change_screen()
    

    def reset_purchase(self):
        for field in self.fields:
            field.text = ''
        self.total_of_purchase = 0
        self.table.row_data = []


    def calculate_change(self):
        if self.ids.total_received.text.isdigit() == False:
            self.dialog_boxes.set_error_message("""Digite um valor válido no campo "Total Recebido" """)
            self.ids.total_received.text = ''
        self.ids.money_change.text = f'{float(self.ids.total_received.text) - float(self.ids.purchase_total.text)}'

    
    def remove_product(self):
        product = self.get_product()
        index_product = self.table.row_data.index(product)
        for _ in range(self.get_quantity_of_items()):
            del(self.table.row_data[index_product])
            self.reduce_the_total_price(product)

    
    def reduce_the_total_price(self, product):
        price_total = int(self.ids.purchase_total.text.replace('.', ''))
        self.ids.purchase_total.text = "{:.2f}".format((price_total - product[2])/100, 2)
        self.total_of_purchase -= product[2]


    def make_the_purchase(self):
        self.product = self.get_product()
        self.set_total_purchase()
        self.add_row_to_purchasing_table()
        self.ids.unitary_value.text = f'{self.product[2]/100}'
        self.ids.field_description.text = f'{self.product[1]}'
        self.ids.field_code_bar.text = ''
        self.ids.quantity_of_items.text = ''

    
    def get_product(self):
        try:
            product = MainApp.products.get(id = self.ids.field_code_bar.text)
        except TypeError:
            self.dialog_boxes.set_error_message('Não existe produto com esse código de barras')
            self.ids.field_code_bar.text = ''
        except sqlite3.OperationalError:
            self.dialog_boxes.set_error_message('Digite um código de barras válido!!!')
            self.ids.field_code_bar.text = ''
        return product

    
    def add_row_to_purchasing_table(self):
        list_containing_the_quantity_of_an_item = list()
        for _ in range(self.get_quantity_of_items()):
            list_containing_the_quantity_of_an_item.append(self.product)
        self.table.row_data.extend(list_containing_the_quantity_of_an_item)

    
    def set_total_purchase(self):
        self.total_of_purchase += self.product[2] * self.get_quantity_of_items()
        self.ids.purchase_total.text = "{:.2f}".format(self.total_of_purchase/100, 2)

    
    def get_quantity_of_items(self):
        if self.ids.quantity_of_items.text == '':
            return 1
        elif self.ids.quantity_of_items.text.isdigit() == False:
            self.dialog_boxes.set_error_message(""" Digite um valor válido para o campo "Quantidade de itens" """)
            self.ids.quantity_of_items.text = ''
        else:
            return int(self.ids.quantity_of_items.text)


class Form(Screen, Errors):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keys = {'9': self.exit_form, '13': self.save_form}
        self.dialog_boxes = DialogBoxes()

        for widget in self.ids.box_layout.children:
            widget.bind()


    def save_form(self, *args):

        if self.set_error(ids = self.ids) == False:
            try:
                MainApp.products.insert_values('(id, name, price, amount, type)', (self.ids.button_code_bar.text, self.ids.button_product.text, int(self.ids.button_price.text.replace(',', '')), int(self.ids.button_stock.text), self.ids.button_type_product.text))

                self.dialog_boxes.set_approved_message('Produto cadastrado com sucesso')
                self.parent.list_products.fill_table()
            except sqlite3.IntegrityError:
                self.dialog_boxes.set_error_message('Já tem um produto com esse código de barras cadastrado!')
    

    def exit_form(self):
        self.parent.change_screen()


class ListProducts(Screen, Errors):
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.keys = {'9': self.close_the_pending_windows, '49': self.remove_row_from_products_table, '50':  self.create_products_table_form}
        self.dialog_to_choose_an_action_to_edit_the_table = None
        self.form_to_update_data_from_the_products_table  = None
        self.table_containing_data_from_products = MDDataTable(
            size_hint = (0.95, 0.8),
            pos_hint = {'center_x': 0.5, 'center_y':0.5},
            rows_num = 20,
            use_pagination = True,
            pagination_menu_height = '120dp',
            background_color = [1,0,0,1],
            column_data = [
                ("Código", dp(50)),
                ("Descrisão", dp(50)),
                ("preço", dp(50)),
                ("estoque", dp(50)),
                ("tipo", dp(50))
            ],
            row_data = []
        )
        self.table_containing_data_from_products.bind(on_row_press = self.create_a_dialog_to_modify_the_table_products)
        self.add_widget(self.table_containing_data_from_products)
        self.fill_table()


    def convert_prices(self):
        list_contaning_products = []
        for product in MainApp.products.all():
            product = list(product)
            converted_price = "{:.2f}".format(product[2]/100, 2)
            product[2] = f'{converted_price}'.replace('.', ',')
            list_contaning_products.append(tuple(product))
        return list_contaning_products

    
    def fill_table(self):
        list_contaning_products = self.convert_prices()
        self.table_containing_data_from_products.row_data.extend(list_contaning_products)

    
    def create_a_dialog_to_modify_the_table_products(self, instance_table, instance_row):
        start_index, end_index = instance_row.table.recycle_data[instance_row.index]["range"]
        self.row = [instance_row.table.recycle_data[i]["text"] for i in range(start_index, end_index+1)]

        if self.dialog_to_choose_an_action_to_edit_the_table == None:
            self.dialog_to_choose_an_action_to_edit_the_table = MDDialog(
                title = f'Deseja editar ou remover o produto {self.row}',
                buttons = [
                    MDFlatButton(
                            text='Cancelar',
                            text_color = 'blue',
                            on_release = self.close_dialog
                        ),
                        MDRaisedButton(
                            text='Remover produto',
                            text_color = 'white',
                            md_bg_color = 'green',
                            on_release = self.remove_row_from_products_table
                        ),
                        MDRaisedButton(
                            text='Atualizar produto',
                            text_color = 'white',
                            md_bg_color = 'green',
                            on_release = self.create_products_table_form
                        )
                ]
            )
        self.dialog_to_choose_an_action_to_edit_the_table.open()

    
    def close_dialog(self, obj=None):
        self.dialog_to_choose_an_action_to_edit_the_table.dismiss()

    
    def remove_row_from_products_table(self,*args):
        MainApp.products.delete(id = self.row[0])
        self.close_dialog()
        self.fill_table()

    
    def create_products_table_form(self, *args):
        self.close_dialog()
        self.keys.setdefault('13', self.confirm_product_table_row_update)
        if self.form_to_update_data_from_the_products_table == None:
            self.form_to_update_data_from_the_products_table = MDDialog(
                title = 'Atualizar Produto',
                type='custom',
                content_cls = MDDialogContent(),
                size_hint = (None, None),
                buttons = [
                    MDFlatButton(
                        text='Cancelar',
                        text_color = 'blue',
                        on_release = self.close_dialog_form
                    ),
                    MDRaisedButton(
                        text='Confirmar',
                        text_color = 'white',
                        md_bg_color = 'green',
                        on_release = self.confirm_product_table_row_update
                    )
                ]
            )
        self.form_to_update_data_from_the_products_table.width = self.width/2
        self.open_dialog_form()
        for index, key in enumerate(self.form_to_update_data_from_the_products_table.content_cls.ids):
            self.form_to_update_data_from_the_products_table.content_cls.ids[key].text = self.row[index]
        self.row = None
            

    def open_dialog_form(self):
        if self.row:
            self.form_to_update_data_from_the_products_table.open()


    def close_dialog_form(self, obj=None):
        self.form_to_update_data_from_the_products_table.dismiss()

    
    def confirm_product_table_row_update(self, obj=None):
        if self.set_error(ids = self.form_to_update_data_from_the_products_table.content_cls.ids) == False:
            MainApp.products.update(
                fields = "name = ?, price = ?, amount = ?, type = ?", 

                values = (self.form_to_update_data_from_the_products_table.content_cls.ids['button_product'].text, int(self.form_to_update_data_from_the_products_table.content_cls.ids['button_price'].text.replace(',', '')), self.form_to_update_data_from_the_products_table.content_cls.ids['button_stock'].text, self.form_to_update_data_from_the_products_table.content_cls.ids['button_type_product'].text), 

                id = self.form_to_update_data_from_the_products_table.content_cls.ids['button_code_bar'].text)
            
            self.form_to_update_data_from_the_products_table.dismiss()
            self.fill_table()

    
    def close_the_pending_windows(self):
        try:
            self.close_dialog()
            self.close_dialog_form()
        except:
            pass
        finally:
            self.parent.change_screen()


class MainApp(MDApp):

    title = 'Sistema PDV'
    products = Products()
    connect = sqlite3.connect('database/register.db')


    def build(self):
        Window.maximize()
        self.icon = 'static/images/icon-app.png'
        Window.bind(on_key_down = self.on_key_press)
        self.sm = AppManager()
        return self.sm

    
    def on_key_press(self, keyboard, keycode, text, modifiers, *args):
        try:
            for screen in self.sm.children:
                if self.sm.current == screen.name:
                    function = screen.keys.setdefault(str(keycode), '')
                    function()
                    return True
        except:
            pass
        return False


    def exit(self, *args):
        self.get_running_app().stop()


if __name__ == '__main__':
    MainApp().run()