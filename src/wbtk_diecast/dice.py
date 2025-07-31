from bisect import bisect_left
from collections import Counter
from math import pi, e, sqrt
from random import random
from statistics import stdev

import json
import matplotlib.pyplot as plt


'''
Generalized dice roller that allows for custom values and non-uniform distributions
'''
class Dice:
    '''
    Constructor
    -----------
    :param values (list[str] | list[int]): list of values representing the sides of the dice
    :param weights (list[float]): list of weightings for each side 
    :param value_map (list[int]): optional mapping representing how to convert values to integers, useful when dice sides are 
                                  strings. Mapping is of the form values[idx] -> value_map[idx]
    '''
    def __init__(self, values: list[str] | list[int], weights: list[float], value_map: list[int] = None, name = None) -> None:
        if len(values) != len(weights):
            raise ValueError("weights must have exactly one element for each value")
        
        if value_map and len(value_map) != len(values):
            raise ValueError("values must be mapped one-to-one")
        
        self.name = name if name else f"d{len(values)}<custom>"
        self.values = values
        self.weights = weights
        
        # Convert from weights to different structure that allows binary search over our probability distribution
        self.dist = [round(sum(weights[:i+1]), 8) for i in range(len(weights))]
        
        if value_map:
            self.value_map = value_map
        elif type(self.values[0]) == int:
            self.value_map = {v: v for v in self.values}
        else:
            try:
                self.value_map = {v: int(v) for v in self.values}
            except:
                self.value_map = {v: 0 for v in self.values}
        self.is_numeric = set(self.value_map.values()) != {0}
        
    def __call__(self, ndice = 1):
        return self.roll(ndice)
    
    def __contains__(self, val):
        return val in self.values
    
    def __eq__(self, other):
        return self.values == other.values and self.dist == other.dist and self.value_map == other.value_map
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.roll()
    
    def __repr__(self):
        return f'Dice(name = "{self.name}", values = {self.values}, weights = {self.weights})' 
    
    def __str__(self):
        res = f'{self.name} dice {{\n'
        for idx, val in enumerate(self.values):
            res += f'\t{val} [val: {self.value_map[val] if self.is_numeric else "N/A"}]: {self.weights[idx]/sum(self.weights):.3f}%\n'
        res += f'}}'
        return res
    
    def is_numeric(self):
        return self.is_numeric
        
    '''
    Roll one or more dice
    ---------------------
    :param num_dice (int): number of dice to roll
    :returns: list of rolled dice sides
    '''
    def roll(self, num_dice: int = 1):
        sides = []
        for i in range(num_dice):
            rand = random() * self.dist[-1]
            idx = bisect_left(self.dist, rand)
            sides.append(self.values[idx])
        return Roll(num_dice, self, sides)
        
    '''
    Generate distribution using monte carlo method
    ----------------------------------------------
    :param num_samples (int): number of samples to generate with
    :param num_dice (int): number of dice to roll for each sample (numeric dice only)
    :param as_percent (bool): return values as percent of total instead of count
    :returns: dictionary of the form {side: times rolled for each side}
    '''
    def mc(self, num_samples: int = 100000, num_dice: int = 1, as_percent: bool = False):
        if not self.is_numeric and num_dice > 1:
            raise ValueError("Monte carlo distributions over composite rolls are undefined for non-numeric dice")
        counts = {}
        for i in range(num_samples):
            rolls = self.roll(num_dice)
            key = sum(rolls) if self.is_numeric else str(rolls)
            counts[key] = 1 if key not in counts.keys() else counts[key]+1 
        result = dict(sorted(counts.items()))
        if as_percent:
            return {k:f'{v/sum(result.values())*100.0:.2f}%' for k,v in result.items()}
        else:
            return result
    
    '''
    Display plot of monte carlo distribution
    ----------------------------------------
    :param num_samples (int): number of samples to generate with
    '''
    def mc_plot(self, num_samples: int = 100000, num_dice: int = 1):
        counts = self.mc(num_samples, num_dice)
        bins = [v for k,v in counts.items()]
        totals = [v/sum(bins) for v in bins]
        
        plt.bar(counts.keys(), totals, color='skyblue', edgecolor='black')
        plt.gca().set_xticks(list(counts.keys()))
        plt.title(f'{num_dice}{self.name.capitalize()} Dice Distribution ({num_samples:,} samples)')
        plt.xlabel('Values')
        plt.ylabel('Frequency')
        plt.show()
    
    
    # Dice Presets
    # ------------
    '''
    Construct a dice from JSON configuration
    ----------------------------------------
    :param config (json): JSON config describing a dice
    :returns: dice based on the provided config
    
    config layout:
    {
        "name": DICE_NAME
        "dist_type": "uniform" | "normal" | "saddle" | "custom",
        "sides": {
            SIDE_LABEL : {
                value: SIDE_VALUE, (optional numeric value of side primarily used for doing math on dice with non-numeric side labels)
                weight: SIDE_WEIGHT (only used when dist_type == "custom" determines probability of landing on side = SIDE_WEIGHT/sum([weight for side in sides]))
            }
        }
    }
    '''
    @staticmethod
    def from_json(config: json):
        try:
            name = config['name']
        except KeyError:
            name = None
        
        try:
            dist_type = config['dist_type']
        except KeyError:
            print("config must specify a dist_type")
            return Dice()
        
        try:
            sides = [k for k in config['sides']]
        except KeyError:
            print("provided config missing required field: 'sides'")
            return Dice()
        
        value_map = {}
        weights = []
        for side, side_config in config['sides'].items():
            if 'value' in side_config:
                value_map[side] = int(side_config['value'])
            else:
                try:
                    value_map[side] = int(side)
                except:
                    value_map[side] = 0
            
            if 'weight' in side_config:
                try:
                    weights.append(float(side_config['weight']))
                except ValueError:
                    print("weights must be numeric values")
                    return Dice()
        
        if dist_type == "uniform":
            return Dice.uniform(sides, value_map)
        elif dist_type == "normal":
            return Dice.normal(sides, value_map)
        elif dist_type == "saddle":
            return Dice.saddle(sides, value_map)
        else:
            return Dice(sides, weights, value_map, name)
    
    '''
    Construct a die with a uniform distribution
    -------------------------------------------
    :param values (list[str] | list[int]): list of dice sides
    :param value_map: optional map for side values -> integer values (useful if sides are strings)
    :returns: dice with uniform distribution weighting for sides
    '''
    @staticmethod
    def uniform(values: list[str] | list[int], value_map = None, name = None):
        return Dice(values, [1.0/len(values) for i in range(1, len(values)+1)], value_map, name if name else f"d{len(values)}<uniform>")
    
    '''
    Construct a die with a truncated normal distribution
    ----------------------------------------------------
    :param values (list[str] | list[int]): list of dice sides
    :param value_map: optional map for side values -> integer values (useful if sides are strings)
    :returns: dice with normal distribution weighting for sides
    '''
    @staticmethod
    def normal(values: list[str] | list[int], value_map = None, name = None):
        bins = [i for i in range(1, len(values)+1)]
        weights = [1/(stdev(bins) * sqrt(2*pi)) * e**(-(val - (sum(bins)/len(bins)))**2 / (2 * stdev(bins)**2)) for val in bins]
        return Dice(values, weights, value_map, name = name if name else f"d{len(values)}<normal>")
    
    '''
    Construct a die with a saddle (inverted normal) distribution
    ------------------------------------------------------------
    :param values (list[str] | list[int]): list of dice sides
    :param value_map: optional map for side values -> integer values (useful if sides are strings)
    :returns: dice with saddle distribution weighting for sides
    '''
    @staticmethod
    def saddle(values: list[str] | list[int], value_map = None, name = None):
        bins = [i for i in range(1, len(values)+1)]
        weights = [1/(stdev(bins) * sqrt(2*pi)) * e**(-(val - (sum(bins)/len(bins)))**2 / (2 * stdev(bins)**2)) for val in bins]
        return Dice(values, [max(weights)*1.1 - w for w in weights], value_map, name = name if name else f"d{len(values)}<saddle>")
    
    '''
    Construct a 3-sided die
    '''
    @staticmethod
    def d3():
        return Dice.uniform([i for i in range(1,4)], name = "d3")
    
    '''
    Construct a 4-sided die
    '''
    @staticmethod
    def d4():
        return Dice.uniform([i for i in range(1,5)], name = "d4")
    
    '''
    Construct a 6-sided die
    '''
    @staticmethod
    def d6():
        return Dice.uniform([i for i in range(1,7)], name = "d6")
    
    '''
    Construct a 8-sided die
    '''
    @staticmethod
    def d8():
        return Dice.uniform([i for i in range(1,9)], name = "d8")
    
    '''
    Construct a 10-sided die
    '''
    @staticmethod
    def d10():
        return Dice.uniform([i for i in range(1,11)], name = "d10")
    
    '''
    Construct a 12-sided die
    '''
    @staticmethod
    def d12():
        return Dice.uniform([i for i in range(1,13)], name = "d12")
    
    '''
    Construct a 20-sided die
    '''
    @staticmethod
    def d20():
        return Dice.uniform([i for i in range(1,21)], name = "d20")
    
    '''
    Construct a 100-sided die
    '''
    @staticmethod
    def d100():
        return Dice.uniform([i for i in range(1,101)], name = "d100")
    
    '''
    Construct a coin
    '''
    @staticmethod
    def coin():
        return Dice.uniform(['heads', 'tails'], name = "<coin>")
    
    '''
    Construct a fudge die
    '''
    @staticmethod
    def fudge():
        return Dice.uniform(values = ['+', '-', '0'], value_map = {'+': 1, '-': -1, '0': 0}, name = "dF")


'''
Representation of a dice roll
'''
class Roll:
    def __init__(self, num_dice, dice, values):
        self.num_dice = num_dice
        self.dice = dice
        self.sides = values
        self.values = [dice.value_map[side] for side in self.sides]
        self.is_numeric = self.dice.is_numeric
        
    def __float__(self):
        if self.is_numeric:
            return float(sum(self.values))
        else:
            return 0.0
    
    def __int__(self):
        if self.is_numeric:
            return int(sum(self.values))
        else:
            return 0
    
    def __str__(self):
        if self.is_numeric:
            return str(self.__int__())
        else:
            if len(self.sides) == 1:
                return str(self.sides[0])
            else:
                return str(self.sides)
    
    def __iter__(self):
        if self.is_numeric:
            yield from self.values
        else:
            yield from self.sides
    
    def __repr__(self):
        return f'''Roll({self.num_dice}, {self.dice.__repr__()}, {self.sides})'''
    
    def __add__(self, other):
        if self.is_numeric:
            return sum(self.values) + other
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __radd__(self, other):
        if self.is_numeric:
            return other + sum(self.values)
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")

    def __sub__(self, other):
        if self.is_numeric:
            return sum(self.values) - other
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __rsub__(self, other):
        if self.is_numeric:
            return other - sum(self.values)
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __mul__(self, other):
        if self.is_numeric:
            return sum(self.values) * other
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __rmul__(self, other):
        if self.is_numeric:
            return other * sum(self.values)    
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")

    def __truediv__(self, other):
        if self.is_numeric:
            return sum(self.values) // other
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __rtruediv__(self, other):
        if self.is_numeric:
            return other // sum(self.values) 
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
          
    def __truediv__(self, other):
        if self.is_numeric:
            return sum(self.values) / other
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __rtruediv__(self, other):
        if self.is_numeric:
            return other / sum(self.values) 
        else:
            raise TypeError("arithmetic operations unsupported on non-numeric roll")
    
    def __eq__(self, other):
        if self.is_numeric:
            return self.__int__() == other
        else:
            try:
                return sorted(list(self)) == sorted(list(other))
            except TypeError:
                raise TypeError("non-numeric dice not comparible with non-iterable type")
    
    def __lt__(self, other):
        if self.is_numeric:
            return self.__int__() < other
        else:
            raise TypeError("< operator unsupported on non-numeric roll")
    
    def __gt__(self, other):
        if self.is_numeric:
            return self.__int__() > other
            raise TypeError("> operator unsupported on non-numeric roll")
    
    def __le__(self, other):
        if self.is_numeric:
            return self.__int__() <= other
            raise TypeError("<= operator unsupported on non-numeric roll")
    
    def __ge__(self, other):
        if self.is_numeric:
            return self.__int__() >= other
            raise TypeError(">= operator unsupported on non-numeric roll")
    
    def __contains__(self, val):
        return val in self.values
    
    def is_numeric(self):
        return self.is_numeric


'''
Extended dice roller that supports statefulness 
'''
class StatefulDice:
    TERMINAL = -1
    
    '''
    Constructor
    -----------
    :param name (str): label for stateful dice
    :param verbose (bool): whether or not to print verbose dice state details (primarily for debugging purposes)
    '''
    def __init__(self, name = None, verbose = False):
        self.name = name if name else f"sdice<custom>"
        self.verbose = verbose
        self.node = StatefulDice.TERMINAL
        self.start_node = StatefulDice.TERMINAL
        self.node_list = {
            StatefulDice.TERMINAL: {
                'name': 'Terminal Node',
                'dice':  Dice.uniform([None]),
                'edges': {
                    None: StatefulDice.TERMINAL
                }
            }
        }
    
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
        fmt_nid = lambda node_id: "StatefulDice.TERMINAL" if node_id == StatefulDice.TERMINAL else node_id
        fmt_nid_info = lambda node_id, data: "n/a" if node_id == StatefulDice.TERMINAL else str(data)
        
        res = f'{self.name} stateful dice {{\n'
        for node in self.node_list:
            res += f'\tnode id: {fmt_nid(node)}\n'
            res += f'\t\t name: {self.node_list[node]["name"]}\n'
            if node == StatefulDice.TERMINAL:
                continue
            res += f'\t\t dice: {fmt_nid_info(node, self.node_list[node]["dice"].__repr__())}\n'
            res += f'\t\tlinks: {fmt_nid_info(node, {(val, fmt_nid(nid)) for val, nid in self.node_list[node]["edges"].items()})}\n'
        res += f'\tstart node: {fmt_nid(self.start_node)}\n'
        res += f'\tcurrent node: {fmt_nid(self.node)}\n'
        res += f'}}'
        return res
    
    def current_dice(self):
        return self.node_list[self.node]['dice']
    
    def loop_node_link(self, node_id, link_val):
        if node_id not in self.node_list:
            raise ValueError(f"node {node_id} not in node list")
        if link_val not in self.node_list[node_id]['dice']:
            raise ValueError(f"{link_val} is not a valid side for node {node_id}")
        self.node_list[node_id]['edges'][link_val] = node_id
    
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
    
    def set_node(self, node_id, dice, name = None, default_link = None):
        self.node_list[node_id] = {
            'name': name if name else dice.name,
            'dice': dice,
            'edges': {side: default_link if default_link else self.TERMINAL for side in dice.values}
        }
     
    def set_node_link(self, node_id, link_val, link_id):
        if node_id not in self.node_list:
            raise ValueError(f"node {node_id} not in node list")
        if link_id not in self.node_list:
            raise ValueError(f"link node {link_id} not in node list")
        if link_val not in self.node_list[node_id]['dice']:
            raise ValueError(f"{link_val} is not a valid side for node {node_id}")
        self.node_list[node_id]['edges'][link_val] = link_id

    def set_start_node(self, node_id):
        if node_id in self.node_list:
            self.start_node = node_id
    
    def terminate_node_link(self, node_id, link_val):
        if node_id not in self.node_list:
            raise ValueError(f"node {node_id} not in node list")
        if link_val not in self.node_list[node_id]['dice']:
            raise ValueError(f"{link_val} is not a valid side for node {node_id}")
        self.node_list[node_id]['edges'][link_val] = StatefulDice.TERMINAL
        
    def terminated(self):
        return self.node_list[self.node]['dice'] == self.node_list[StatefulDice.TERMINAL]['dice']
    
    def update_state(self, value):
        try:
            new_node = self.node_list[self.node]['edges'][value]
            if self.verbose:
                print(f"dice state update: {self.node} -> {new_node}")
            self.node = new_node
        except KeyError:
            print(f"Unable to update state as value {value} is not a valid side for current dice {self.node_list[self.node]['dice']}")
