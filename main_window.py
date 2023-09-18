import time
import datetime
import threading
import tkinter as tk
from opcua import ua
from tkinter import ttk
from opcua_c import OPCUA_Client
from tkinter import scrolledtext





class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure()
        self.title("OPC_UA")
        self.geometry("800x600")
        self.resizable(False, False)

        self.client: OPCUA_Client

        self.img_folder = tk.PhotoImage(file="img/icon1.png")
        self.img_var = tk.PhotoImage(file="img/icon2.png")
        self.img_method = tk.PhotoImage(file="img/icon3.png")
        self.img_other = tk.PhotoImage(file="img/icon4.png")
        self.pad = 10

        self.parent_width = 800
        self.parent_height = 600
        self.nodes = {}
        self.frame_tree = tk.Frame(self, width=self.parent_width*0.3 - self.pad, height=self.parent_height*0.7 - self.pad)
        self.frame_table = tk.Frame(self, width=self.parent_width*0.7 - self.pad, height=self.parent_height*0.7 - self.pad)
        self.frame_log = tk.Frame(self, width=self.parent_width - self.pad*2, height=self.parent_height * 0.3 - self.pad)
        self.treeview = ttk.Treeview(self.frame_tree, show='tree')

        self.tree_menu = tk.Menu(self.frame_tree, tearoff=False)
        self.tree_menu_item_id = 0
        self.tree_menu_var_name = 0

        self.table_var = ttk.Treeview(self.frame_table, columns=("Name", "Value"), show="headings")
        self.table_var.heading('Name', text='Name')
        self.table_var.heading('Value', text='Value')

        self.log = tk.Text(self.frame_log)

        # self.text_var = scrolledtext.ScrolledText(self.frame_text)
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.__background_task, args=(self.event,))
        self.table_menu = tk.Menu(self.frame_table, tearoff=False)
        self.table_menu_item_id = ''

    def create_start_windows(self):
        print(self.img_var)
        self.grid_window()
        self.create_tree_menu()
        self.create_table_menu()
        self.create_main_menu()

    def clk_btn_start(self):
        self.server_ip = self.entr_start.get()
        if self.server_ip:
            try:
                self.client = OPCUA_Client(self.server_ip)
                self.client.connect()
                self.client.get_all_nodes()
                self.create_tree_nodes(self.client.all_nodes)
                self.log.insert(tk.END, "{} connection to server {} \n".format(datetime.datetime.now(), self.server_ip))

            except Exception as error:
                self.log.insert(tk.END, "{} {} \n".format(datetime.datetime.now(), error))
        else:
            self.log.insert(tk.END, "{} The IP field must not be empty \n".format(datetime.datetime.now()))

    def create_main_menu(self):
        def new_connect():
            connect_window = tk.Toplevel(self)
            connect_window.title('Connect')
            connect_window.geometry("280x50")

            self.lbl_start = tk.Label(connect_window, text='IP PLC: ')
            self.entr_start = tk.Entry(connect_window, width=20)
            self.btn_start = tk.Button(connect_window, text="Connect", command=self.clk_btn_start)

            self.lbl_start.pack(side=tk.LEFT, anchor=tk.W, padx=10)
            self.entr_start.pack(side=tk.LEFT, anchor=tk.W)
            self.btn_start.pack(side=tk.LEFT, anchor=tk.W, padx=10)

        def new_disconnect():
            try:
                self.client.get_root_node() #Проверка активен ли сервер
                self.client.disconnect()
                self.treeview.delete(*self.treeview.get_children()) #Удаление элементов дерева
                self.log.insert(tk.END, "{} connection to the server {} is lost \n".format(datetime.datetime.now(), self.server_ip))
            except:
                self.log.insert(tk.END, "{} no active connections \n".format(datetime.datetime.now()))
        main_menu = tk.Menu(self)
        self.config(menu=main_menu)

        new_menu = tk.Menu(main_menu)
        main_menu.add_cascade(label="New", menu=new_menu)
        new_menu.add_command(label="Connect", command=new_connect)
        new_menu.add_command(label="Disconnect", command=new_disconnect)

    def grid_window(self):
        """
        Функция создает дерево связей.

        node_image - Присваивает каждому элементу дерева свою иконку,  в зависимости от типа элемента
        """
        # Добавление виджета скроллинга
        # scrollbar_tr_x = ttk.Scrollbar(master=self.frame_tree, orient=tk.HORIZONTAL, command=self.treeview.xview)
        # scrollbar_tr_x.pack(side=tk.BOTTOM, fill=tk.X)
        # scrollbar_tr_x = ttk.Scrollbar(master=self.frame_table, orient=tk.HORIZONTAL, command=self.treeview.xview)
        # scrollbar_tr_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_tr_y = ttk.Scrollbar(master=self.frame_tree, orient=tk.VERTICAL, command=self.treeview.yview)
        scrollbar_tr_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_tree.grid(column=0, row=0, padx=(self.pad, 0), pady=(self.pad, 0))
        self.frame_table.grid(column=1, row=0, padx=(0, self.pad), pady=(self.pad, 0))
        self.frame_log.grid(column=0, row=1, columnspan=2, padx=self.pad, pady=(0, self.pad))

        self.frame_tree.propagate(False)
        self.frame_table.propagate(False)
        self.frame_log.propagate(False)

        self.treeview.pack(expand=True, fill="both")
        self.table_var.pack(expand=True, fill="both")
        tk.Label(self.frame_log, text='Log:').pack(anchor=tk.NW)
        self.log.pack(expand=True, fill="both")

        # self.treeview.configure(yscrollcommand=scrollbar_tr_y.set, xscrollcommand=scrollbar_tr_x.set)
        self.treeview.configure(yscrollcommand=scrollbar_tr_y.set)

    def create_tree_nodes(self, nodes):
        """
        Функция создает дерево связей.

        node_image - Присваивает каждому элементу дерева свою иконку,  в зависимости от типа элемента
        """
        self.nodes = nodes
        def node_image(node):
            try:
                nodeclass = node.get_node_class()
                if nodeclass == ua.NodeClass.Object:
                    return self.img_folder
                elif nodeclass == ua.NodeClass.Variable:
                    return self.img_var
                elif nodeclass == ua.NodeClass.Method:
                    return self.img_method
                elif nodeclass == ua.NodeClass.ObjectType:
                    return self.img_other
                elif nodeclass == ua.NodeClass.VariableType:
                    return self.img_other
                elif nodeclass == ua.NodeClass.ReferenceType:
                    return self.img_other
                elif nodeclass == ua.NodeClass.DataType:
                    return self.img_other
                else:
                    return self.img_other
            except:
                pass

        all_items = []
        #Извлечение ключей из словаря
        for item in nodes.items():
            all_items.append(item[0])
        #Добавление элементов в дерево
        for item in all_items:
            if len(item.split('_')) == 2:
                self.treeview.insert("", "end", item, text=nodes[item][0].get_display_name().Text,
                                     image=node_image(nodes[item][0]))

            else:
                split_item = item.split('_')
                parent_item = 'item'
                for i in range(1, len(split_item) - 1):
                    parent_item = parent_item + "_" + split_item[i]
                self.treeview.insert(parent_item, "end", item, text=nodes[item][0].get_display_name().Text,
                                     image=node_image(nodes[item][0]))

    def create_tree_menu(self):
        """
        Функция инициализирует контекстное меню для дерева связей.

        show_context_menu - Реагирует на ПКМ, показывает меню, и скохраняет идентификатор и текст нажатой строки;

        handle_menu_command - Вызывается по выбору "Add to list" из контекстного меню. Добавляет  выбранную переменную из списка
        в список client.nodes_screen и отображает таблице. При добавлении первого элемента запускает выполнение паралельного потока
        """
        def show_context_menu(event):
            item_id = self.treeview.identify_row(event.y)
            self.tree_menu_item_id = item_id
            self.tree_menu_var_name = self.treeview.item(item_id, 'text')
            try:
                if self.nodes[item_id][0].get_node_class() == ua.NodeClass.Variable:
                    self.tree_menu.post(event.x_root, event.y_root)
            except Exception as error:
                print(error)
                self.treeview.delete(*self.treeview.get_children()) #Удаление элементов дерева
                self.log.insert(tk.END, "{} connection to the server {} is lost \n".format(datetime.datetime.now(), self.server_ip))

        def handle_menu_command():
            if self.client.add_to_list_screen(self.tree_menu_item_id, self.tree_menu_var_name):
                try:
                    self.table_var.insert("", "end",
                                          values=(self.client.nodes_screen[-1][0],
                                                  self.client.nodes_screen[-1][1].get_value()))
                    self.log.insert(tk.END, "{} Variable {} added to the list \n".format(datetime.datetime.now(),
                                                                         self.client.nodes_screen[-1][0] ))
                except:
                    self.log.insert(tk.END, "{} Failed to add variable \n".format(datetime.datetime.now()))

            if not self.thread.is_alive():
                self.thread.daemon = True
                self.thread.start()


        self.treeview.bind("<Button-3>", show_context_menu)
        self.tree_menu.add_command(label="Add to list", command=lambda: handle_menu_command())

    def create_table_menu(self):
        """
        Функция инициализирует контекстное меню для таблицы с переменными.

        show_context_menu - Реагирует на ПКМ, показывает меню, и скохраняет идентификатор нажатой строки;

        delete_row - Вызывается по выбору "Delete" из контекстного меню. Удаляет  выбранную переменную из списка
        добавленных переменных добавленных  к обработке client.nodes_screen и из отображения в таблице.
        """

        def show_context_menu(event):
            self.table_menu_item_id = self.table_var.identify_row(event.y)
            self.table_menu.post(event.x_root, event.y_root)

        def delete_row():

            if self.table_var:
                count = 0
                for var in self.client.nodes_screen:
                    if self.table_var.item(self.table_menu_item_id)['values'][0] in var:
                        self.log.insert(tk.END, "{} Variable {} removed from list \n".format(datetime.datetime.now(),
                                                                                             self.client.nodes_screen[
                                                                                                 count][0]))
                        self.client.nodes_screen.pop(count)
                        break
                    else:
                        count += 1
                self.table_var.delete(self.table_menu_item_id)

        self.table_var.bind("<Button-3>", show_context_menu)
        self.table_menu.add_command(label="Delete", command=delete_row)
    def update_text(self):
        """
        Функция используется паралельным процессом для обновления данных перменных
        """
        if len(self.client.nodes_screen) != 0:
            for i in range(0, len(self.client.nodes_screen)):
                try:
                    item = self.table_var.get_children()[i]
                    self.table_var.set(item, column="Value", value=self.client.nodes_screen[i][1].get_value())
                except IndexError:
                    self.client.nodes_screen.pop()
                except Exception as error:
                    print(error)
                    self.treeview.delete(*self.treeview.get_children())  # Удаление элементов дерева
                    self.log.insert(tk.END, "{} connection to the server {} is lost \n".format(datetime.datetime.now(),
                                                                                                   self.server_ip))

    def __background_task(self,event):
        while True:
            while not event.is_set():
                time.sleep(0.2)
                self.update_text()






