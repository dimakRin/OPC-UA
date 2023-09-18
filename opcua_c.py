from opcua import Client

class OPCUA_Client(Client):
    def __init__(self, ip: str):
        super().__init__("opc.tcp://{}:4840".format(ip))
        self.all_nodes = {}
        self.nodes_screen = []

    def get_all_nodes(self, len_dict = 0):
        if len(self.all_nodes) == 0:
            count = 0
            roots = self.get_root_node().get_children()   #Извлечение дочерних элементов начальной директории
            for root in roots:
                if root.get_children():                   #Проверка на наличие дочерних директорий
                    self.all_nodes['item_{}'.format(count)] = [root, True]
                else:
                    self.all_nodes['item_{}'.format(count)] = [root, False]
                count += 1
            self.get_all_nodes()

        else:
            all_items = []
            #Извлечение ключей словаря all_nodes
            for item in self.all_nodes.items():
                all_items.append(item[0])
            len_cut = len(all_items)
            #Обрезка обработанных ключей
            if len_dict != 0:
                if len(all_items) == 1:
                    all_items = []
                else:
                    all_items = all_items[len_dict:]
            nonstop_recurse = False
            for item_tree in all_items:
                if self.all_nodes[item_tree][1]:  # Проверяем, что у элемента есть дочерние
                    nonstop_recurse = True
                    count = 0
                    for nude in self.all_nodes[item_tree][0].get_children():
                        if nude.get_children() != []:
                            self.all_nodes[item_tree + '_{}'.format(count)] = [nude, True]
                        else:
                            self.all_nodes[item_tree + '_{}'.format(count)] = [nude, False]
                        count += 1
            if nonstop_recurse:
                self.get_all_nodes(len_cut)

    def add_to_list_screen(self, item, name_var):
        """
        Если переменная уже есть в списке на отображение в таблице функция вернет False,
        иначе добавить переменную в список и вернет True
        """
        if len(self.nodes_screen) != 0:
            for var in self.nodes_screen:
                if name_var in var:
                    return False
        self.nodes_screen.append([name_var, self.all_nodes[item][0]])
        return True

    def get_text_screen(self):
        text = ''
        if len(self.nodes_screen) != 0:
            for var in self.nodes_screen:
                text = text + '{}: {} \n'.format(var[0], var[1].get_value())
        return text
