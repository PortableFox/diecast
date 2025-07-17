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
class Dice:
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
        return f'Dice(values = {self.values}, dist = {self.dist})' 
    
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
        return Dice(values, [i * 1.0/len(values) for i in range(1, len(values)+1)], value_map)
    
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
        return Dice(values, dist, value_map)
    
    '''
    Construct a 3-sided die
    '''
    @staticmethod
    def d3():
        return Dice.uniform([i for i in range(1,4)])
    
    '''
    Construct a 4-sided die
    '''
    @staticmethod
    def d4():
        return Dice.uniform([i for i in range(1,5)])
    
    '''
    Construct a 6-sided die
    '''
    @staticmethod
    def d6():
        return Dice.uniform([i for i in range(1,7)])
    
    '''
    Construct a 10-sided die
    '''
    @staticmethod
    def d10():
        return Dice.uniform([i for i in range(1,11)])
    
    '''
    Construct a 12-sided die
    '''
    @staticmethod
    def d12():
        return Dice.uniform([i for i in range(1,13)])
    
    '''
    Construct a 20-sided die
    '''
    @staticmethod
    def d20():
        return Dice.uniform([i for i in range(1,21)])
    
    '''
    Construct a 100-sided die
    '''
    @staticmethod
    def d100():
        return Dice.uniform([i for i in range(1,101)])
    
    '''
    Construct a coin
    '''
    @staticmethod
    def coin():
        return Dice.uniform(['heads', 'tails'])
    
    '''
    Construct a fudge die
    '''
    @staticmethod
    def fudge():
        return Dice.uniform(values = ['+', '-', '0'], value_map = [1, -1, 0])
