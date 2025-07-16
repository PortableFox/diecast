from random import random
from bisect import bisect_left
from math import pi, e, sqrt
from collections import Counter
from statistics import stdev
import lark
import matplotlib.pyplot as plt


'''
Generalized dice roller that allows for custom values and non-uniform distributions
'''
class dice:
    '''
    Constructor
    -----------
    :param values (list[str] | list[int]): list of values representing the sides of the dice
    :param dist (list[float]): list representing distributions for each side where each value is mapped to for rolls within [prev
                               dist val, dist val). Uses 0 implicitly as the minimum for the first side. Distribution max can be 
                               any value, dice will automatically adjust for distributions that aren't between [0, 1).
    :param value_map (list[int]): optional mapping representing how to convert values to integers, useful when dice sides are 
                                  strings. Mapping is of the form values[idx] -> value_map[idx]
    '''
    def __init__(self, values: list[str] | list[int], dist: list[float], value_map: list[int] = None) -> None:
        if not sorted(dist):
            raise ValueError("distribution must be strictly increasing")
        if len(dist) != len(set(dist)):
            raise ValueError("distribution must not have duplicate elements")
        if len(values) != len(dist):
            raise ValueError("distribution must have exactly one element for each value")
        if value_map and len(value_map) != len(values):
            raise ValueError("values must be mapped one-to-one")
        self.values = values
        self.dist = dist
        if value_map:
            self.value_map = {v: m for v, m in zip(self.values, value_map)}
        elif type(self.values[0]) == int:
            self.value_map = {v: v for v in self.values}
        else:
            self.value_map = {v: 0 for v in self.values}
        self.is_numeric = set(self.value_map.values()) != {0}
        
    def __call__(self, ndice = 1):
        return self.rolls(ndice)

    def __contains__(self, val):
        return val in self.values
    
    def __eq__(self, other):
        return self.values == other.values and self.dist == other.dist and self.value_map == other.value_map
    
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.roll()
    
    def __repr__(self):
        return f'dice(values = {self.values}, dist = {self.dist})' 
    
    def __str__(self):
        res = f'die {{\n'
        for idx, val in enumerate(self.values):
            res += f'\t{val} [val: {self.value_map[val] if self.is_numeric else "N/A"}]: {(self.dist[idx]-(self.dist[idx-1] if idx > 0 else 0))/self.dist[-1]:.3f}%\n'
        res += f'}}'
        return res
    
    '''
    Roll die single time
    --------------------
    :returns: randomly rolled dice side
    '''
    def roll(self):
        rand = random() * self.dist[-1]
        idx = bisect_left(self.dist, rand)
        return self.values[idx]
    
    '''
    Roll die multiple times
    -----------------------
    :param num_dice (int): number of dice to roll
    :returns: list of rolled dice sides
    '''
    def rolls(self, num_dice: int = 2):
        rolls = []
        for i in range(num_dice):
            rand = random() * self.dist[-1]
            idx = bisect_left(self.dist, rand)
            rolls.append(self.values[idx])
        return rolls
        
    '''
    Sums dice rolls based on value map
    ----------------------------------
    :param (list): list of dice rolls to sum over
    :returns: if dice is numeric sum of all dice in list otherwise dictionary of counts for each side rolled
    '''
    def sum(self, rolls: list):
        if self.is_numeric:
            return sum([self.value_map[roll] for roll in rolls])
        else:
            return dict(sorted(Counter(rolls).items()))
    
    '''
    Generate distribution using monte carlo method
    ----------------------------------------------
    :param num_samples (int): number of samples to generate with
    :returns: dictionary of the form {side: times rolled for each side}
    '''
    def mc(self, num_samples: int = 100000, num_dice: int = 1):
        if not self.is_numeric and num_dice > 1:
            raise ValueError("Monte carlo distributions over composite rolls are undefined for non-numeric dice")
        counts = {}
        for i in range(num_samples):
            rolls = [self.roll() for i in range(num_dice)]
            key = self.sum(rolls) if self.is_numeric else rolls[0]
            counts[key] = 1 if key not in counts.keys() else counts[key]+1 
        return dict(sorted(counts.items()))
    
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
        plt.title('Distribution')
        plt.xlabel('Values')
        plt.ylabel('Frequency')
        plt.show()
    
    
    # Dice Presets
    # ------------
    
    '''
    Construct a die with a uniform distribution
    -------------------------------------------
    :param values (list[str] | list[int]): list of dice sides
    :param value_map: optional map for side values -> integer values (useful if sides are strings)
    :returns: dice with uniform distribution weighting for sides
    '''
    @staticmethod
    def uniform(values: list[str] | list[int], value_map = None):
        return dice(values, [i * 1.0/len(values) for i in range(1, len(values)+1)], value_map)
    
    '''
    Construct a die with a truncated normal distribution
    ----------------------------------------------------
    :param values (list[str] | list[int]): list of dice sides
    :param value_map: optional map for side values -> integer values (useful if sides are strings)
    :returns: dice with normal distribution weighting for sides
    '''
    @staticmethod
    def normal(values: list[str] | list[int], value_map = None):
        bins = [i for i in range(1, len(values)+1)]
        weights = [1/(stdev(bins) * sqrt(2*pi)) * e**(-(val - (sum(bins)/len(bins)))**2 / (2 * stdev(bins)**2)) for val in bins]
        dist = [sum(weights[:idx+1]) for idx in range(len(weights))]
        return dice(values, dist, value_map)
    
    '''
    Construct a 3-sided die
    '''
    @staticmethod
    def d3():
        return dice.uniform([i for i in range(1,4)])
    
    '''
    Construct a 4-sided die
    '''
    @staticmethod
    def d4():
        return dice.uniform([i for i in range(1,5)])
    
    '''
    Construct a 6-sided die
    '''
    @staticmethod
    def d6():
        return dice.uniform([i for i in range(1,7)])
    
    '''
    Construct a 10-sided die
    '''
    @staticmethod
    def d10():
        return dice.uniform([i for i in range(1,11)])
    
    '''
    Construct a 12-sided die
    '''
    @staticmethod
    def d12():
        return dice.uniform([i for i in range(1,13)])
    
    '''
    Construct a 20-sided die
    '''
    @staticmethod
    def d20():
        return dice.uniform([i for i in range(1,21)])
    
    '''
    Construct a 100-sided die
    '''
    @staticmethod
    def d100():
        return dice.uniform([i for i in range(1,101)])
    
    '''
    Construct a coin
    '''
    @staticmethod
    def coin():
        return dice.uniform(['heads', 'tails'])
    
    '''
    Construct a fudge die
    '''
    @staticmethod
    def fudge():
        return dice.uniform(values = ['+', '-', '0'], value_map = [1, -1, 0])


'''
Extended dice roller that supports statefulness 
'''
class stateful_dice:
    def __init__(self, nodes = []):
        self.node = 0
        self.start_node = 0
        self.node_list = {
            0: {
                'dice':  dice.uniform([None]),
                'edges': {
                    None: 0
                }
            }
        }
        if len(nodes) > 0:
            self.node = 1
            self.start_node = 1
            for node in nodes:
                self.add_node(node)
    
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
        return f'stateful_dice'
    
    def __str__(self):
        res = f'stateful_dice{{\n'
        for node in self.node_list:
            res += f'\tnode id: {node}{" (terminal node)" if node == 0 else ""}\n'
            res += f'\t\t dice: {self.node_list[node]["dice"].__repr__()}\n'
            res += f'\t\tlinks: {self.node_list[node]["edges"]}\n'
        res += f'\tstart node: {self.start_node}\n'
        res += f'\tcurrent node: {self.node}\n'
        res += f'}}'
        return res
    
    def add_node(self, dice):
        node_id = len(self.node_list)
        self.node_list[node_id] = {
            'dice': dice,
            'edges': {side: node_id for side in dice.values}
        }
        if node_id == 1:
            self.start_node = 1
            self.node = 1
    
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
    
    def set_start_node(self, node_id):
        if node_id in self.node_list:
            self.start_node = node_id
    
    def reset(self):
        self.node = self.start_node
     
    def roll(self):
        result = self.node_list[self.node]['dice']()
        self.node = self.node_list[self.node]['edges'][result[0]]
        return result[0]
    
    def terminated(self):
        return self.node_list[self.node]['dice'] == self.node_list[0]['dice']


'''
Parser for expressing dice rolls in mathematical notation
'''
class interpreter():
    def __init__(self):
        #will use Lark
        #define a grammar that captures, as much as possible, the full scope of normal dice roll operations
        #e.g.: dice including custom dice (reduce by rolling, non-numerics treated special), integers, single die 
        #      operators (+, -, *, /, ^, %), multi-die operators (advantage/highest x, disadvantage/lowest x, sum, 
        #      average), branch-conditionals (if dice roll = side value, do this, else that) possibly include a way 
        #      to run mc and plot results for when people are creating crazy dice
        self.grammar = """
        """
        
        #'''
        #examples:
        #    abilities = roll 6 {4d6 high 3} # [roll(2, 4, 4 = 10), roll(3, 5, 6 = 14), roll(2, 3, 4 = 9), roll(5, 5, 6 = 16), roll(3, 6, 6 = 15), roll(4, 5, 5 = 14)]
        #    abilities[0]      # roll(2, 4, 4 = 10)
        #    sum{abilities[0]} # 10
        #    
        #    roll1 = 1d4 * 2d3     # 2 * 2,3 = 10
        #    roll2 = (1d4)d6       # (3)d6 -> 1, 4, 5 = 10
        #    roll3 = roll1 + roll2 # 20
        #    
        #    roll = high{4dF, 3} # roll(-, 0, +, + = 1) -> roll(0, +, + = 2)
        #    
        #    dice{uniform, element, [earth, fire, wind, water]}
        #    roll = 2d<element> # [roll(earth, water) = [earth: 1, fire: 0, wind: 0, water: 1]]
        #    
        #    dice{normal, 20, [1, ..., 20]}
        #    roll = 3d<20> # [roll(7, 9, 9 = 25), roll(6, 10, 12 = 28), roll(4, 12, 13 = 29)]
        #    
        #    roll = if{1d4, 
        #        1 | 1d4,
        #        2 | 2d3,
        #        _ | 1d20
        #    }
        #    # 3 -> 1d20 -> roll(17 = 17)
        #    
        #    disadv{2d20} # roll(16, 17 = 33) roll(8, 14 = 22) -> roll(8, 14 = 22)
        #    
        #    dice{[0.01, 0.03, 0.05, 0.08, 0.12, 0.17, 0.23, 0.3, 0.38, 0.47], skew10, [1, ..., 10]}
        #    roll = 3d<skew10> # roll(2, 8, 9 = 19)
        #    
        #    dice{[0.01, 0.5, 1.5], odd, [foo:1, bar:4, baz:6]}
        #    roll = 2d<odd> # roll(bar, baz = 10)
        #'''
