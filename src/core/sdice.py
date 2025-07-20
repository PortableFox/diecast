from .dice import *

'''
Extended dice roller that supports statefulness 
'''
class StatefulDice:
    TERMINAL = -1
    
    '''
    Constructor
    -----------
    :param nodes (list[dice]): list of dice representing the dice rolled for each state
    :param links (dict{int:{int:int}}): dictionary that maps node ids to a map from node dice roll values to linked node ids.
                                        node ids are determined by the index of their dice in the nodes list argument.
    :param verbose (bool): whether or not to print verbose dice state details (primarily for debugging purposes)
    '''
    def __init__(self, nodes = [], links = [], verbose = False):
        self.verbose = verbose
        self.node = self.TERMINAL
        self.start_node = self.TERMINAL
        self.node_list = {
            self.TERMINAL: {
                'dice':  Dice.uniform([None]),
                'edges': {
                    None: self.TERMINAL
                }
            }
        }
        if len(nodes) > 0:
            self.node = 0
            self.start_node = 0
            for node in nodes:
                self.add_node(node)
        for link in links:
            for roll in links[link]:
                self.set_node_link(link, roll, links[link][roll])
    
    def __call__(self):
        return self.roll()
    
    def __eq__(self, other):
        return self.start_node == other.start_node and self.node_list == other.node_list
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while not self.terminated():
            yield self.roll()
    
    def __repr__(self):
        return f'StatefulDice'
    
    def __str__(self):
        fmt_nid = lambda node_id: "TERMINAL_NODE" if node_id == self.TERMINAL else node_id
        fmt_nid_info = lambda node_id, data: "n/a" if node_id == self.TERMINAL else str(data)
        
        res = f'StatefulDice{{\n'
        for node in self.node_list:
            res += f'\tnode id: {fmt_nid(node)}\n'
            res += f'\t\t dice: {fmt_nid_info(node, self.node_list[node]["dice"].__repr__())}\n'
            res += f'\t\tlinks: {fmt_nid_info(node, {(val, fmt_nid(nid)) for val, nid in self.node_list[node]["edges"].items()})}\n'
        res += f'\tstart node: {fmt_nid(self.start_node)}\n'
        res += f'\tcurrent node: {fmt_nid(self.node)}\n'
        res += f'}}'
        return res
    
    def add_node(self, dice):
        node_id = len(self.node_list)-1
        self.node_list[node_id] = {
            'dice': dice,
            'edges': {side: node_id for side in dice.values}
        }
        if node_id == 0:
            self.start_node = 0
            self.node = 0
    
    def current_dice(self):
        return self.node_list[self.node]['dice']
    
    def set_node_link(self, node_id, link_val, link_id):
        if node_id not in self.node_list:
            raise ValueError(f"node {node_id} not in node list")
        if link_id not in self.node_list:
            raise ValueError(f"link node {link_id} not in node list")
        if link_val not in self.node_list[node_id]['dice']:
            raise ValueError(f"{link_val} is not a valid side for node {node_id}")
        self.node_list[node_id]['edges'][link_val] = link_id
    
    def set_node_links(self, node_id, links):
        for val, link in links:
            self.set_node_link(node_id, val, link)
    
    def set_node_terminator(self, node_id, value):
        if node_id in self.node_list and value in self.node_list[node_id]['dice'].values:
            self.node_list[node_id][value] = self.self.TERMINAL
    
    def set_start_node(self, node_id):
        if node_id in self.node_list:
            self.start_node = node_id
    
    def reset(self):
        if self.verbose:
            print(f"dice state reset: {self.node} -> {self.start_node}")
        self.node = self.start_node
     
    def roll(self):
        result = self.node_list[self.node]['dice']()
        self.update_state(sum(result) if result.is_numeric else str(result))
        return result
    
    def roll_until(self, node_id, max_iter = 100):
        rolls = []
        if node_id in self.node_list:
            roll_count = 0
            while self.node != node_id and roll_count <= max_iter:
                roll_count += 1
                rolls.append(self.roll())
        return rolls
    
    def terminated(self):
        return self.node_list[self.node]['dice'] == self.node_list[self.TERMINAL]['dice']
    
    def update_state(self, value):
        try:
            new_node = self.node_list[self.node]['edges'][value]
            if self.verbose:
                print(f"dice state update: {self.node} -> {new_node}")
            self.node = new_node
        except KeyError:
            print(f"Unable to update state as value {value} is not a valid side for current dice {self.node_list[self.node]['dice']}")
