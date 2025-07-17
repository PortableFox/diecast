
'''
Parser for expressing dice rolls in mathematical notation
'''
class Interpreter():
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
