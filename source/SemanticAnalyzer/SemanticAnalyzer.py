import sys
sys.path.append( '.' )
from source.core.symbol_table import Token, Identifiers
from source.core.error_handler import SemanticError as SemError
from source.core.error_types import Semantic_Errors as se
from source.core.AST import AST
# from source.CodeGeneration.CodeGen import CodeGeneration2



GBL="Global"
LOCAL="Local"
VAR="Variable"
FUNC="Function"
MOD="Module"
SEQ="Sequence"
IMP="Imported"
PARAM="Parameter"

CONST="Constant"


class SemanticAnalyzer:
    """  
    The semantic analyzer traverses the parse tree.
    The semantic analyzer will check the AST for any semantic errors.
    The SA must also assign identifiers to the symbol table.
    The SA will check:
        - Variable Declaration
        - Variable Use
        - Function Declaration
        - Function Use
        - Function Return Type
        - Function Arguments
        - Function Calls
        - Variable Assignment
        - Sequence Size
        - Sequence Access
        - Sequence Assignment


    Things to check:
        - Identifiers
        - Parameters/ Arguments
        - Return Types
        - Sequence Size
        - Sequence Access
        - Sequence Assignment/ Init

    """
    
    def __init__(self, parse_tree:AST) -> None:
        self.parse_tree:AST=parse_tree
        
        # self.matched=matched
        self.semantic_expected=[]

        self.semantic_errors: list[SemError]=[]
        self.id=Identifiers()
        self.parse_tree.symbol_table=self.id

        self.req_type=None

        self.current_node:AST=self.parse_tree
        self.previous_node:AST=None

        self.current_scope=GBL

        self.check=Check(self)
        self.create=Create(self)

        self.buffer=[]

        self.nearest_id=None
        
        self.routines={

#SECTION: ID TYPE ENFORCEMENT 

            "import_prog": self.import_prog,
            "import_tail": self.import_tail,
            "in_param": self.in_param,
            "allowed_in_loop": self.allowed_in_loop,
            "id_tail": self.id_tail,
            "var_or_seq_dec": self.var_or_seq_dec,
            "more_whl_var": self.more_whl_var,
            "more_dec_var": self.more_dec_var,
            "more_sus_var": self.more_sus_var, 
            "more_txt_var": self.more_txt_var, 
            "more_chr_var": self.more_chr_var, 
            "charr_value": self.charr_value, 
            "const_type": self.const_type, 
            "more_whl_const": self.more_whl_const, 
            "more_dec_const": self.more_dec_const, 
            "more_sus_const": self.more_sus_const, 
            "more_txt_const": self.more_txt_const,
            "more_chr_const": self.more_chr_const,
            "control_flow_statement": self.control_flow_statement,
            "looping_statement": self.looping_statement,
            "loop_body_statement": self.loop_body_statement,
            "func_def": self.func_def,
            "id_as_val": self.id_as_val,
            "id_val_tail": self.id_val_tail,
            "sheesh_declaration": self.sheesh_declaration,
            "math_op": self.math_op,
            "reg_body": self.reg_body,
            



            
            }
        
    def __repr__(self) -> str:
        return f"SemanticAnalyzer({self.parse_tree})"

    def analyze(self):
        while True:
            if self.current_node.root not in self.routines.keys():
                self.previous_node=self.current_node
                self.current_node = self.parse_tree.traverse(self.current_node)
            else:
                self.routines[self.current_node.root]()
                self.previous_node=self.current_node
                self.current_node = self.parse_tree.traverse(self.current_node)
            if self.current_node is None:
                # self.code_gen.generate_code()
                break  # Exit the loop if the tree has been fully traversed


    def import_prog(self):
        raise NotImplementedError

    def import_tail(self):
        raise NotImplementedError



    def in_param(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_param(type=self.current_node.children[0].children[0].value)

        elif self.current_node.children[2].type=="Identifier":
            self.nearest_id=self.current_node.children[2]
            self.create.new_param( type="charr")
        # raise NotImplementedError


    def allowed_in_loop(self):
        try:
            if self.current_node.children[0].type=="Identifier":
                self.nearest_id=self.current_node.children[0]
            else: 
                # raise ValueError("No Identifier Found")
                pass
        except AttributeError:
            print(f"Attribute Error in {self.current_node.root}, got {self.current_node.children}")
            pass

    def id_tail(self):
        tail_map={
            "(": self.check.func,
            "one_dim": self.check.seq,
            "assign_op": self.create.assign,
        }

        try:
            tail_map[self.current_node.children[0].root]()
        except AttributeError:
            tail_map[self.current_node.children[0].value]()

    
    def id_val_tail(self):
        tail_map={
            "(": self.check.func,
            "one_dim": self.check.seq,
        }

        try:
            tail_map[self.current_node.children[0].root]()
        except AttributeError:
            tail_map[self.current_node.children[0].value]()

    def var_or_seq_dec(self):
        try:
            if self.current_node.children[1].type=="Identifier":
                self.nearest_id=self.current_node.children[1]
                self.create.new_id(type=self.current_node.children[0].value, attribute=VAR)
                self.create.load_type(self.current_node.children[1])

                self.create.assign(self.current_node.children[1])
                print(self.nearest_id)
                

            elif self.current_node.children[2].type=="Identifier":
                self.nearest_id=self.current_node.children[2]
                self.create.new_id(type="charr", attribute=VAR)
                self.create.load_type(self.current_node.children[2])

                self.create.assign(self.current_node.children[2])
            else:
                raise ValueError("No Identifier Found")
        except AttributeError:
            # raise AttributeError("No Identifier Found")
            print(f"Attribute Error in {self.current_node.root}, got {self.current_node.children}")
            print("No Identifier Found")
            pass
    
    def more_whl_var(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="whole", attribute=VAR)
    def more_dec_var(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id(type="dec", attribute=VAR)
    def more_sus_var(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="sus", attribute=VAR)
    def more_txt_var(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="text", attribute=VAR)
    def more_chr_var(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="charr", attribute=VAR)
    

    def charr_value(self):
        if self.current_node.children[0].type=="Identifier":
            self.nearest_id=self.current_node.children[0]
            self.check.var()
            self.check.var_value()
            self.check.var_type() 
            self.check.scope() 
    

    def const_type(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type=self.current_node.children[0], attribute=CONST)
    

    def more_whl_const(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="whole", attribute=CONST)
    def more_dec_const(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id(type="dec", attribute=CONST)
    def more_sus_const(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id(type="sus", attribute=CONST)
    def more_txt_const(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="text", attribute=CONST)
    def more_chr_const(self):
        if self.current_node.children[1].type=="Identifier":
            self.nearest_id=self.current_node.children[1]
            self.create.new_id( type="charr", attribute=CONST)
    

    def control_flow_statement(self):
        try:
            if self.current_node.children[2].type=="Identifier" and self.current_node.children[0].value=="choose":
                self.nearest_id=self.current_node.children[2]
                self.check.var()
                self.check.var_value()
                self.check.scope() 
        except AttributeError:
            print(f"Attribute Error sa {self.current_node.root}, had {self.current_node.children}")
            pass

    def looping_statement(self):
        if self.current_node.children[2].type=="Identifier" and self.current_node.children[0].value=="for":
            self.nearest_id=self.current_node.children[2]
            self.check.var()
            self.check.var_value()
            self.check.scope() 

    def loop_body_statement(self):
        try:
            if self.current_node.children[2].type=="Identifier" and self.current_node.children[0].value=="choose":
                self.nearest_id=self.current_node.children[2]
                self.check.var()
                self.check.var_value()
                self.check.scope()
        except IndexError as e:
            print(f"Index Error sa {self.current_node.root}, had {self.current_node.children}")
            pass

    def func_def(self):

        self.current_scope=FUNC

        if self.current_node.children[2].type=="Identifier":
            self.nearest_id=self.current_node.children[2]
            self.create.new_func( type=self.current_node.children[1].children[0].value)
        elif self.current_node.children[3].type=="Identifier":
            self.nearest_id=self.current_node.children[3]
            self.create.new_func( type=self.current_node.children[1].children[0].value)
    

    def id_as_val(self):
        if self.current_node.children[0].type=="Identifier":
            self.nearest_id=self.current_node.children[0]
            self.check.var()
            print(self.nearest_id)
            self.check.var_value()
            self.check.var_type() 
            self.check.scope()
            self.create.load_type(self.nearest_id)


    def sheesh_declaration(self):
        if self.current_node.children[0].type=="sheesh":
            self.current_scope=LOCAL


    def math_op(self):
        if self.current_node.children[0].type=="/":
            operand=self.check.next_operand()
            if int(operand.numerical_value) == 0:
                self.semantic_error(se.ZERO_DIV, operand, "Non-zero value")

    def reg_body(self):
        if len(self.current_node.children)<=2:
            self.semantic_error(se.EMPTY_BODY, self.current_node.children[0], "Non-empty body")


    def semantic_error(self, error, token, expected):
        self.semantic_expected.append(expected)
        self.semantic_errors.append(SemError(error=error, line=token.line, toknum=token.position, value=token.value, expected=expected))
        
    



class Check:
        
        def __init__(self, semantic: SemanticAnalyzer) -> None:
            self.semantic=semantic


        def func(self):
            id=self.semantic.nearest_id
            if id.value not in self.semantic.id.accessible_ids():
                exp=f"Declared Function {id.value}"
                err=se.FUNC_UNDECL
                self.semantic.semantic_error(err, id, exp)
                return
            
        def seq(self):
            id=self.semantic.nearest_id
            if id.value not in self.semantic.id.accessible_ids():
                exp=f"Declared Sequence {id.value}"
                err=se.SEQ_UNDECL
                self.semantic.semantic_error(err, id, exp)
                return
            
        def var(self):
            id=self.semantic.nearest_id
            if id.value not in self.semantic.id.accessible_ids().keys():
                exp=f"Declared Variable {id.value}"
                err=se.VAR_UNDECL
                self.semantic.semantic_error(err, id, exp)
                return False
            else:
                self.semantic.create.load_var(id)
                return True
                
        

        def var_value(self):
            id=self.semantic.nearest_id
            if id.numerical_value==None:
                exp=f"Value for Variable {id.value}"
                err=se.VAR_UNDEF
                self.semantic.semantic_error(err, id, exp)
                return
            else: return True

        def var_type(self):
            id=self.semantic.nearest_id
            if id.dtype!=self.semantic.req_type:
                exp=f"Variable of Type {self.semantic.req_type}, Got {id.dtype}"
                err=se.VAR_OPERAND_INVALID
                self.semantic.semantic_error(err, id, exp)
                return
            
        def scope(self):
            id=self.semantic.nearest_id
            if id.scope!=self.semantic.current_scope:
                exp=f"In {self.semantic.current_scope} Scope"
                err=se.VAR_SCOPE_INVALID
                self.semantic.semantic_error(err, id, exp)
                print(id.scope, self.semantic.current_scope)
                return


        def next_operand(self):
            temp_node=self.semantic.previous_node
            try:
                if temp_node.children[1].children[0].type in ["Identifier", "Whole", "Dec"]:
                    return temp_node.children[1].children[0]

            except AttributeError:
                return temp_node.children[2]

            
        

class Create:

    def __init__(self, semantic:SemanticAnalyzer) -> None:
        self.semantic=semantic

    def assign(self, to_id=None)->None:
        if to_id==None:
            to_id=self.semantic.nearest_id
        expr=[]
        value=None
        if self.semantic.check.var():
            items=self.semantic.current_node.leaves()
            for children in items:
                try:
                    if children.type not in ["#", ",", "Newline", "whole", "dec", "sus", "text", "charr"]:
                        if children.type=="Identifier":
                            self.semantic.nearest_id=children
                            if self.semantic.check.var() and self.semantic.check.var_value():
                                expr.append(self.semantic.nearest_id)
                        else: expr.append(children)
                except AttributeError:
                    raise AttributeError("No Identifier Found")
                
            value=self.semantic.create.eval_arithm(expr)
            # while self.semantic.current_node.children:
            #     try:
            #         if self.semantic.current_node.children[0].type=="=":
            #             value=self.semantic.current_node.children[1]
            #             break
            #         expr.append(self.semantic.current_node.children)
            #         self.semantic.current_node=self.semantic.parse_tree.traverse(self.semantic.current_node)
            if value:
                self.semantic.parse_tree.symbol_table.accessible_ids()[to_id.value].numerical_value=value
                return True
        
    def get_var(self, id:Token):
        try:
            return self.semantic.id.vars[id.value]
        except KeyError:
            self.semantic.semantic_error(se.VAR_UNDECL, id, f"Variable {id.value}")

    def load_type(self, id:Token):
        self.semantic.req_type=id.dtype

    def load_var(self, id:Token):
        declared=self.semantic.id.vars[id.value]

        self.semantic.nearest_id.dtype=declared.dtype
        self.semantic.nearest_id.numerical_value=declared.numerical_value
        self.semantic.nearest_id.scope=declared.scope
        self.semantic.nearest_id.attribute=declared.attribute

        return True


    def new_id(self, type, scope=LOCAL,  attribute=None):
        id=self.semantic.nearest_id #NOTE - idk if this is the right way to do this
        if id.value not in self.semantic.id.accessible_ids():
            id.dtype=type
            id.attribute=attribute
            id.scope=self.semantic.current_scope

            self.semantic.id.vars.add(id)
            self.semantic.nearest_id=id
        else:
            self.semantic.semantic_error(se.VAR_REDECL, id, f"Variable {id.value}")


    def new_func(self,type, attribute=FUNC):
        id=self.semantic.nearest_id
        if id.value not in self.semantic.id.accessible_ids():
            id.dtype=type
            id.attribute=attribute
            id.scope=GBL

            self.semantic.id.funcs.add(id)
        else:
            self.semantic.semantic_error(se.FUNC_REDECL_INSCOPE, id, f"Function {id.value}")

    
    def new_param(self,  type, scope=FUNC, attribute=PARAM):
        id=self.semantic.nearest_id
        if id.value not in self.semantic.id.params.keys():
            id.dtype=type
            id.attribute=attribute
            id.scope=scope

            self.semantic.id.params.add(id)
        else:
            self.semantic.semantic_error(se.PARAM_REDECL, id, f"Parameter {id.value}")

    def evaluate(self, eval:list):
        precedence = {'+':1, '-':1, '*':2, '/':2, '%':2}
        operator_stack = []
        operand_stack = []

        for token in reversed(eval):
            if token.type == "Identifier":
                operand_stack.append(token.numerical_value)
            elif token.type not in ['+', '-', '*', '/', '^', '(', ')', "=", "%", "Newline"]:
                try:
                    operand_stack.append(int(token.value))
                except ValueError:
                    operand_stack.append(int(token.value[1:-1]))
            elif token.type == '(':
                operator_stack.append(token.value)
            elif token.type == ')':
                while operator_stack[-1].type != '(':
                    operator = operator_stack.pop().value
                    operand2 = operand_stack.pop()
                    operand1 = operand_stack.pop()
                    if operator == '+':
                        result = operand1 + operand2
                    elif operator == '-':
                        result = operand1 - operand2
                    elif operator == '*':
                        result = operand1 * operand2
                    elif operator == '/':
                        result = operand1 / operand2
                    elif operator=='%':
                        result = operand1 % operand2
                    operand_stack.append(result)
                operator_stack.pop()  # Remove the '(' from the stack
            else:
                while (operator_stack and operator_stack[-1].type != '(' and 
                    precedence[operator_stack[-1].type] >= precedence[token.type]):
                    operator = operator_stack.pop().value
                    operand2 = operand_stack.pop()
                    operand1 = operand_stack.pop()
                    if operator == '+':
                        result = operand1 + operand2
                    elif operator == '-':
                        result = operand1 - operand2
                    elif operator == '*':
                        result = operand1 * operand2
                    elif operator == '/':
                        result = operand1 / operand2
                    elif operator=='%':
                        result = operand1 % operand2
                    operand_stack.append(result)
                operator_stack.append(token)

        while operator_stack:
            operator = operator_stack.pop().value
            operand2 = operand_stack.pop()
            operand1 = operand_stack.pop()
            if operator == '+':
                result = operand1 + operand2
            elif operator == '-':
                result = operand1 - operand2
            elif operator == '*':
                result = operand1 * operand2
            elif operator == '/':
                result = operand1 / operand2
            elif operator=='%':
                result = operand1 % operand2
            operand_stack.append(result)

        print(operand_stack[0])
        return operand_stack[0]
    
    def eval_arithm(self, expr):

        eval=[]
        for match in reversed(expr):
            if match.type=="=":
                return self.evaluate(eval)
            elif match.type in ["#", "Newline"]:
                pass
            else:
                eval.append(match)


  