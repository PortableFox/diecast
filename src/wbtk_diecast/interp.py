from lark import Lark, Transformer, Tree, v_args, Token
import rich


#@v_args(tree=True)
#class ASTTransformer(Transformer):
#    def __init__(self, visit_tokens=False):
#        self.diceRolls = []
#        self.diceTotal = 0
#
#    def dice(self, tree):
#        nodes = tree.children
#        numDice = int(nodes[0])
#        if nodes[1] == "f" or nodes[1] == "F":
#            rolls = [randint(-1, 1) for i in range(numDice)]
#            self.diceRolls.append(rolls)
#        else:
#            numSides = int(nodes[1])
#            rolls = [randint(1, numSides) for i in range(numDice)]
#            self.diceRolls.append(rolls)
#        return Token('DICE', rolls)
#
#    def selectdice(self, tree):
#        nodes = tree.children
#        numDice = int(nodes[0])
#        numSides = int(nodes[1])
#        selectType = nodes[2]
#        select = int(nodes[3])
#        rolls = [randint(1, numSides) for i in range(numDice)]
#        if selectType.type == "LOW":
#            rolls = sorted(rolls)[:select]
#        elif selectType.type == "HIGH":
#            select *= -1
#            rolls = sorted(rolls)[select:]
#        self.diceRolls.append(rolls)
#        return Token('DICE',  rolls)
#
#    def stmt(self, tree):
#        nodes = tree.children
#        if len(nodes) == 1:
#            nodeVal = nodes[0].children[0]
#            self.diceTotal = sumup(nodeVal.value)
#            return nodeVal
#        elif len(nodes) > 1:
#            if nodes[1].children[0].type == "PLUS":
#                nodeVal = sumup(nodes[2].children[0].value)
#                self.diceTotal = self.diceTotal + nodeVal
#                return Token("INT", self.diceTotal)
#            if nodes[1].children[0].type == "MINUS":
#                nodeVal = sumup(nodes[2].children[0].value)
#                self.diceTotal = self.diceTotal - nodeVal
#                return Token("INT", self.diceTotal)


class AST_Transformer(Transformer):
    def standard_dice(self, args):
        print(f"standard dice: {args}")
        return Token('DICE', 0)
    
    def custom_dice(self, args):
        print(f"custom dice: {args}")
        return Token('cdice', 0)
    
    def stored_dice(self, args):
        print(f"stored dice: {args}")
        return Token('stdice', 0)
    
    def uniform(self, args):
        print(f"uniform dice: {args}")
        return Token('uniform', 0)
    
    def normal(self, args):
        print(f"normal dice: {args}")
        return Token('normal', 0)
    
    def var(self, args):
        print(f"var: {args}")
        return Token('VAR', args[0])


class Interpreter():
    def __init__(self):
        self.transform = AST_Transformer()
        self.parser = Lark(self.grammar(), parser='lalr', transformer=self.transform)
        self.env = {}
    
    def parse(self, stmt):
        print(self.parser.parse(stmt))
    
    def grammar(self):
        grammar = r"""
            ?start: dice_roll
            
            dice_roll: INT "d" INT           -> standard_dice
                     | INT "<" dice_type ">" -> custom_dice
                     | INT "{" dice_var "}"  -> stored_dice
            
            dice_type: "uniform(" side_list ")" -> uniform
                     | "normal(" side_list ")"  -> normal
            
            dice_var: WORD -> var
            
            side_list: INT "," side_list
                     | INT
            
            %import common.INT
            %import common.WORD
            %import common.WS
            
            %ignore WS
        """
        return grammar

#        grammar = Lark(r"""
#            stmt: expr
#                | stmt op expr
#        
#            expr: selectdice
#                | dice
#                | INT
#        
#            selectdice: INT "d"i INT LOW INT
#                      | INT "d"i INT HIGH INT
#        
#            dice: INT "d"i INT
#                | INT "d"i FATE
#        
#            op: PLUS
#              | MINUS
#        
#            PLUS: "+"
#            MINUS: "-"
#            INT: /[1-9][0-9]*/
#            LOW: "lowest"i | "low"i | "l"i
#            HIGH: "highest"i | "high"i | "h"i
#            FATE: "f"i | "F"i
#            
#            %import common.WS
#            %ignore WS
#        """, start='stmt', parser='lalr')
#        return grammar
