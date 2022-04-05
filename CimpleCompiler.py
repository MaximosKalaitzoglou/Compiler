# KALAITZOGLOY MAXIMOS , AM : 2983 , username : cse52983
# LABROS GIANNAKOPOULOS , AM : 2955 , username : cse52955


import string
import sys
import os
import json
import re



cimpleWords = ['if', 'else', 'while', 'program', 'declare', 'switchcase',
               'forcase', 'incase', 'case', 'default', 'not', 'and', 'or',
               'function', 'procedure', 'call', 'return', 'in', 'inout',
               'input', 'print']


# special characters that are not used in cimple
special_characters = ['!', '@', '$', '%', '^',
    '&', '~', '`', '|', '?', '\\', '"', "'"]
# Characters with meaning in cimple
opened_brackets = ['[', '{', '(']
closed_brackets = [']', '}', ')']
delimiters = [',', ';', '.']
addOperators = ['+', '-']
mulOperators = ['*', '/']
relOperatos = ['>','<','<>','=','>=','<=']
commentIdentifier = '#'


class Token:
    # Properties: tokenType, tokenString, lineNo
    def __init__(self, tokenType='', tokenString='', lineNo=1):
        self.tokenType = tokenType
        self.tokenString = tokenString
        self.lineNo = lineNo


TOKEN_NUMBER = 'number'
TOKEN_KEYWORD = 'keyword'
TOKEN_IDENTIFIER = 'identifier'
TOKEN_ADD_OPERATOR = 'addOperator'
TOKEN_MUL_OPERATOR = 'mulOperator'
TOKEN_GROUP_SYMBOL = 'groupSymbol'
TOKEN_DELIMITER = 'delimiter'
TOKEN_ASSIGNMENT = 'assignment'
TOKEN_REL_OPERATOR = 'relOperator'


class Lex:
    # basically tried to implement lex as a state_machine instead of calling it all the time from the parser i store all the tokens <Object_type>
    # inside a list so basically a Object_list and then the parser just scrolls through the already made and thankfully error free list

    STATE_START = 'start'
    STATE_DIG = 'dig'
    STATE_IDK = 'idk'
    STATE_ASGN = 'asgn'
    STATE_REM = 'rem'
    STATE_SMALLER = 'smaller'
    STATE_LARGER = 'larger'

    def __init__(self, file):
        self.file = file
        self.lineNo = 1
        self.current_pos = 0
        self.current_char = ''
        self.lexState = 'start'
        self.tokenString = ''

    # seek position of char in file read char get its position close file
    def read_next_char(self):
        with open(self.file, 'r') as fr:
            fr.seek(self.current_pos)
            self.current_char = fr.read(1)
            self.current_pos = fr.tell()
            fr.close()
        return

    # check next char without reading it well theoretically at least
    def snick_pick_next_char(self):
        char = ''
        with open(self.file, 'r') as fr:
            fr.seek(self.current_pos)
            char = fr.read(1)
            fr.close()
        return char

    def is_new_line(self, char):
        return char == '\n'

    def is_eof(self, char):
        if char == '':
            return True

    def is_charets(self, char):
        return char == ' ' or char == '\t' or char == '\r' or char == '\n'

    def die_on_special_char(self, char):  # what the name says
        if char in special_characters:
            print("This character :", char, "is not used in cimple")
            exit()

    def start(self):

        self.read_next_char()

        if self.is_eof(self.current_char):  # if its eof
            if self.lexState == self.STATE_REM:  # if comments are open
                print("Comments opened but never closed...")
                exit()
            return None

        if self.lexState != self.STATE_REM:  # if special characters are found in comments don't die plz
            self.die_on_special_char(self.current_char)

        if self.is_charets(self.current_char):  # ignore tabs spaces etc
            # if its new line, next line count
            if self.is_new_line(self.current_char):
                self.lineNo += 1
            return self.start()

        if self.current_char == commentIdentifier:  # if its a comment
            if self.lexState == self.STATE_REM:  # if we are already in comments
                self.lexState = self.STATE_START  # end of comments set state to start
            else:
                self.lexState = self.STATE_REM  # else we begin a comment
            return self.start()  # return to start()

        if self.lexState == self.STATE_REM:  # basically keep reading and ignoring the comments
            return self.start()

        if self.current_char.isdigit():  # if its a number then set state to dig_state
            self.state = self.STATE_DIG
            return self.dig_state()  # call the dig_state

        if self.current_char.isalpha():  # if its ascii
            self.state = self.STATE_IDK  # set state to IDK_state
            return self.idk_state()

        if self.current_char in opened_brackets or self.current_char in closed_brackets:  # identify groupSymbols
            return Token(TOKEN_GROUP_SYMBOL, self.current_char, self.lineNo)

        if self.current_char in addOperators:
            return Token(TOKEN_ADD_OPERATOR, self.current_char, self.lineNo)

        if self.current_char in mulOperators:
            return Token(TOKEN_MUL_OPERATOR, self.current_char, self.lineNo)

        if self.current_char in delimiters:
            return Token(TOKEN_DELIMITER, self.current_char, self.lineNo)

        if self.current_char == '=':
            return Token(TOKEN_REL_OPERATOR, self.current_char, self.lineNo)

        if self.current_char == '>':
            self.state = self.STATE_LARGER
            return self.larger_state()

        if self.current_char == '<':
            self.state = self.STATE_SMALLER
            return self.smaller_state()

        if self.current_char == ':':
            self.state = self.STATE_ASGN
            return self.asgn_state()

    def idk_state(self):
        # fisrt alpha
        tokenString = self.current_char

        # look ahead
        nextChar = self.snick_pick_next_char()

        while nextChar.isalpha() or nextChar.isdigit():
            # next is valid, make it current
            self.read_next_char()
            tokenString += self.current_char
            nextChar = self.snick_pick_next_char()

        tokenType = TOKEN_KEYWORD if tokenString in cimpleWords else TOKEN_IDENTIFIER
        self.validate_idk_state_value(tokenType, tokenString)

        self.lexState = self.STATE_START
        return Token(tokenType, tokenString, self.lineNo)

    def validate_idk_state_value(self, tokenType, tokenString):
        if tokenType == TOKEN_IDENTIFIER and len(tokenString) > 30:
            print('error found in line:', self.lineNo,
                  TOKEN_IDENTIFIER + 'exceeds allowed length of 30 characters')
            exit()

    def dig_state(self):
        # fisrt digit
        tokenString = self.current_char

        # look ahead
        nextChar = self.snick_pick_next_char()
        self.validate_dig_state_next_char(nextChar)

        while nextChar.isdigit():
            # next is valid, make it current
            self.read_next_char()
            tokenString += self.current_char
            nextChar = self.snick_pick_next_char()
            self.validate_dig_state_next_char(nextChar)
        self.validate_dig_state_value(tokenString)

        self.state = self.STATE_START
        return Token(TOKEN_NUMBER, tokenString, self.lineNo)

    def validate_dig_state_next_char(self, char):
        if char.isalpha():
            print('error found in line:', self.lineNo,
                  'invalid expression\nif you want to write a variable dont start with a digiti')
            exit()

    def validate_dig_state_value(self, value):
        # if the full number is not in the valid range ->error
        if int(value) < -4294967295 or int(value) > 4294967295:
            print("error in line : ", self.lineNo,
                  "number used is too big,\n must be in the range of [-4294967295, 4294967295]")
            exit()

    def larger_state(self):
        tokenString = self.current_char
        nextChar = self.snick_pick_next_char()

        if nextChar == '=':
            self.read_next_char()
            tokenString += self.current_char

        self.lexState = self.STATE_START
        return Token(TOKEN_REL_OPERATOR, tokenString, self.lineNo)

    def smaller_state(self):
        tokenString = self.current_char
        nextChar = self.snick_pick_next_char()

        if nextChar == '=' or nextChar == '>':
            self.read_next_char()
            tokenString += self.current_char

        self.lexState = self.STATE_START
        return Token(TOKEN_REL_OPERATOR, tokenString, self.lineNo)

    def asgn_state(self):
        nextChar = self.snick_pick_next_char()
        if nextChar != '=':
            print('error found in line:', self.lineNo,
                  'Assignment operator \':=\' was expected')
            exit()
        self.read_next_char()
        self.lexState = self.STATE_START
        return Token(TOKEN_ASSIGNMENT, ':=', self.lineNo)


# ALL the lists below are used for the parser to avoid too many or's
declarations = ['declare']
subprograms = ['function', 'procedure']
statements = ['if', 'while', 'switchcase', 'forcase', 'print',
    'call', 'return', 'input', 'incase', 'forcase', '{']
cases = ['forcase', 'switchcase']
in_out = ['in', 'inout']


class Parse_Error():  # just a class for printing errors

    def __init__(self, pos, *args):
        if args:
            self.msg = args[0]
            self.line = pos

    def __str__(self):

        return 'Error in Line : ' + str(self.line) + ' -> ' + self.msg


class Node:
    def __init__(self,data):
        self.data = data
        self.nextval = None



class ST:
    def __init__(self):
        self.entityList = {}
        self.scope = 0
        self.offset = {self.scope:8}
        self.headval = None
        self.tailval = None
        self.s = open('symbolTable.txt','w')

    def insertEntity(self,data):
        
        if self.tailval is None:
            self.headval = Node(data)
            self.tailval = self.headval
        else:
            self.tailval.nextval = Node(data)
            self.tailval = self.tailval.nextval
        
        try:
            self.entityList[self.scope] += [data]
        except KeyError:
            self.entityList[self.scope] = [data]

        
    def lookup(self,scope,name):
        #lookup needs scope and name scope because when you look for a parameter it makes sense to first look your scope then others scopes
        if scope in self.entityList:
            if scope == 0:
                
                for img in self.entityList[scope]:
                    if img['name'] == name and 'entype' in img:
                        
                        return img,0
            else:
                for i in range(scope,-1,-1):
                    for img in self.entityList[i]:
                        if img['name'] == name and 'entype' in img:
                            return img,i

            return False,-1
        else:
            scope -= 1
            if scope < 0:
                print('Error scope < 0 ')
                exit()
            self.lookup(scope,name)


    def deleteScope(self,scope):
        del self.entityList[scope]
        self.scope -= 1
        del self.offset[scope]
        return
        

    def modify_data(self,name,scope,off,start,frame):
        #used for functions because when we encounter and insert them to our scope we don't know their framelength offset or startQuad
        val = self.entityList[scope]
        for i in range(len(val)):
            if val[i]['name'] == name:
                val[i]['offset'] = off
                val[i]['startQuad'] = start
                val[i]['framelength'] = frame            
                break

    def print_s(self):
        
        for i in range(len(self.entityList)):
            x = self.entityList[i]
            sx = "Currently in scope : " + str(i)
            self.s.write(sx + '\n')
            for j in range(len(x)):
                self.s.write(json.dumps(x[j]))
                self.s.write('\n')

    def declarations(self):
        for img in self.entityList[0]:
            if 'entype' in img:
                if img['entype'] == 'declare' or img['entype'] == 'temp':
                    sa.declared_vars.append(img['name'])
        return 0

            
            

class SyntaxAnalyzer:

    PROGRAM = 'program_state'
    CASE = 'case_state'
    FUNC = 'function_state'
    PROC = 'procedure_state'
    # bracket symbols
    L_PARENTHESIS = '('
    R_PARENTHESIS = ')'
    L_CURLY_BRACKET = '{'
    R_CURLY_BRACKET = '}'
    L_BRACKET = '['
    R_BRACKET = ']'

    declared_vars = []
    function_vars = []
    functions_id = {}  # stores in a dict functions and their parameters with the key being the name and the value being the parameters
    # previous state is empty used for mainly functions different error checking
    previous_state = ''
    produce_C_bool = True  # if we have a program with function they don;t generate C_code so its a bool to determine if a .int file or a .c file will be created

    value = '' #stores current function name
    

    LABEL = 0
    TEMP = -1
    main_start = 0
    returnFlag = False #used for checking if a function has at least one return in it
    exp = [] #used for parameter check see more at def factor 



    def __init__(self, tokens=[]):
        self.tokens = tokens  # tokens from lexer
        self.current_token = None  # initialize
        self.next_token = None
        self.pos = -1
        self.parse_state = 'program'

    def invalid_program(self):
        if len(tokens) < 2:  # if only 2 tokens we now we have an invalid program
            print("Not a valid program")
            exit()

        return

    def index_out_of_range(self):  # is used for avoiding out of bounds
        if self.pos == len(self.tokens):

            return None
        return 4  # just used it for if check == None, kinda bad ik ;x

    def succesfully_reached_eof(self):
        # simple stuff if we have . we reached the end of the program
        if self.current_token.tokenString == '.':
            print('End of program reached and no errors encountered\nnow exiting ......')
            exit()

    def move_to_next_token(self):
        # advance to next token in the list
        self.pos += 1
        self.current_token = self.tokens[self.pos]
        return

    def look_next_token(self):
        # if is not out of range peek next token
        check = self.index_out_of_range()
        if check == None:
            self.succesfully_reached_eof()

        self.next_token = self.tokens[self.pos + 1]
        return

    def move_token_idx(self):
        self.move_to_next_token()
        self.look_next_token()

    def parse(self):

        self.invalid_program()

        w = self.program_sym()

        self.move_token_idx()

        x = self.block_sym()
        if x.tokenString != '.':

            print(Parse_Error(
                x.lineNo, 'Error that is not a statement : ' + x.tokenString))
            exit()
        self.genquad('halt', '_', '_', '_')
        self.genquad('end_program', expressions[1][1], '_', '_')
        
        name = sys.argv[1].split('.')
        print('functions : ', self.functions_id)
        if self.functions_id:
            self.produce_C_bool = False
        if self.produce_C_bool == True:
           
            print("\nProducing C code file named %s............" %
                  (name[0] + '.c'))
            self.produce_C_code(name[0])
        print('\nproducing %s...............\n' %(name[0] + '.int'))
        self.produce_intermediate(name[0])
        print('Finished parsing ...........\n')
        print('Producing assembly file called %s.asm\n'%name[0])
        f.produce_final_code(self.main_start,self.LABEL)
        return

    # ================================= INTERMEDIATE FUNCTIONS======================================================

    def newTemp(self):  # Returns a new iterative temporary variable
        self.TEMP += 1
        x = 'T_'+str(self.TEMP)
        self.make_data('temp',x)
        return x

    # generates quad of expressions-conditions-blocks
    def genquad(self, operand, left, right, tmp):

        self.LABEL += 1
        if tmp == None:
            tmp = self.newTemp()
        temp = [operand, left, right, tmp]

        expressions[self.LABEL] = temp

        return

    def makelist(self, x):  # makes an empty list and appends value x in it
        new_list = []
        new_list.append(x)
        return new_list

    def empty_list(self):  # creates an empty list and returns it
        empty = []
        return empty

    def backpatch(self, list1, z):  # gets as parameters a list of LABELS pointing to the quads of expression list and completes the _ expressions with value z
        for i in range(len(list1)):
            x = expressions[list1[i]]
            if x[3] == '_':
                x[3] = z

        return

    def get_key(self,value):
        for key,val in expressions.items():
            if value == val:
                return key
        

    def write_exp_to_C(self, c, s1):  # writes to .c file the quads as comments
        c.write('\t//%s' % s1)
        c.write('\n')

        return

    # begin .c transformation of expressions  declaring the variables /int main(){}
    def begin_C_transition(self, c):
        key = self.get_key(['begin_main_block', expressions[1][1], '_', '_'])
        s1 = ','.join(expressions[key])
        c.write('#include <stdio.h>\n#include <stdlib.h>\n\n')
        c.write('int main ()')
        self.write_exp_to_C(c, s1)
        c.write('{\n')
        c.write('int ')
        st.declarations()
        for i in range(0, len(self.declared_vars)):
            if i != len(self.declared_vars) - 1:
                c.write(self.declared_vars[i] + ', ')

            else:

                c.write(self.declared_vars[i] + ';')
        c.write('\t//declared vars : %s' % self.declared_vars)
        c.write('\n')
        c.write('L_1: ')
        c.write('\n')
        return
            

    # transform expressions into their counterparts  in c (creates and opens file with name from .ci program)
    def produce_C_code(self,name):
    
        ops = ['+', '-', '*', '/']
        relops = ['>', '<', '>=', '<=', '<>', '=']
        with open(name + '.c', 'w') as c:

            self.begin_C_transition(c)

            for i in range(2, len(expressions) + 1):
                x = expressions[i]
                joined = ','.join(expressions[i])

                if x[0] == ':=':
                    s1 = x[3] + ' = ' + x[1] + ';'
                    c.write('L_' + str(i) + ': %s' % s1)
                    self.write_exp_to_C(c, joined)

                elif x[0] in ops:
                    s1 = x[3] + ' = ' + x[1] + ' ' + x[0] + ' ' + x[2] + ';'
                    c.write('L_' + str(i) + ': %s' % s1)
                    self.write_exp_to_C(c, joined)

                elif x[0] in relops:
                    tmp = x[0]
                    if x[0] == '=':
                        tmp = '=='
                    if x[0] == '<>':
                        tmp = '!='
                    s2 = x[1] + ' ' + tmp + ' ' + x[2]
                    s1 = 'if (%s) ' % s2
                    c.write('L_' + str(i) + ': %s' % s1)
                    c.write('goto L_%s;' % x[3])
                    self.write_exp_to_C(c, joined)

                elif x[0] == 'jump':
                    c.write('L_' + str(i) + ': goto L_%s;' % x[3])
                    self.write_exp_to_C(c, joined)

                elif x[0] == 'halt':
                    c.write('L_' + str(i) + ': {}')
                    self.write_exp_to_C(c, joined)

                    break

                elif x[0] == 'out':
                    tmp = '{} = '.format(x[1]) + '%' + 'd'
                    s1 = 'printf("{0}\\n",{1});'.format(tmp,x[1])
                    c.write('L_' + str(i) + ': %s' % s1)
                    self.write_exp_to_C(c, joined)

                elif x[0] == 'inp':
                    tmp = '%' + 'd'
                    
                    s1 = 'scanf("{0}",&{1});'.format(tmp,x[1])
                    c.write('L_' + str(i) + ': %s' % s1)
                    self.write_exp_to_C(c, joined)

                elif x[0] == 'retv':
                    s1 = 'return(%s);' % x[1]
                    c.write('L_' + str(i) + ': %s' % s1)
                    self.write_exp_to_C(c, joined)
                else:
                    self.write_exp_to_C(c, joined)
            c.write('\n}')

    # produces an intermediate file .int with all the expressions (quads)
    def produce_intermediate(self,name):
        
        with open(name + '.int', 'w') as inter:
            for i in range(1, len(expressions)):
                x = expressions[i]
                s1 = ','.join(x)
                inter.write(s1 + '\n')

    # ============================================================================================================

    # ================================VALIDATIONS FOR METHODS ====================================================

    def valid_var(self):  # checks if variable is valid meaning its declared or its a function
        # if we are in a function and the identifier is not known to the function (declared,parameter) then error
        # self.value is basically the current functions name i use it so i can acces the parameters of the current function and check errors
        w = self.next_token.tokenString
        valid = st.lookup(st.scope,w)
        if valid == False:
            
                
            print(Parse_Error(self.next_token.lineNo,"Variable %s is not declared nor a function or in the same nesting level" % self.next_token.tokenString))
            exit()
        

        return

    # checks if there is opening of curly_brackets after function declaration
    def brackets_after_func(self):

        if self.next_token.tokenString != self.L_CURLY_BRACKET:
            print(Parse_Error(self.current_token.lineNo,
                  'Expected right curly bracket after func declaration'))
            exit()
        return

    # uses flag and func_id to validate function blocks and method statements
    def move_look_and_validate(self, flag, func_id,*args):

        self.move_to_next_token()
        self.look_next_token()
        x = None
        if flag == 1:  # if its a method then check for statements

            x = self.statement_sym()
            self.invalid_statement(x)
        else:  # else its a function so check brackets and validate block of function until end of brackets
            self.brackets_after_func()
            self.move_token_idx()
            x = self.functionBlock(func_id,args[0])
            self.move_token_idx()

        if self.next_token.tokenString == '.':  # if after brackets its . then we have end of file check it
            print('reached end of file succesfully......')
            return x

        return x

    # i use this to check if function parameters from calls of function are valid
    def parameter_check(self, w,exp):
        
        if exp:
            j = 0
            func,s = st.lookup(st.scope,w)
            temp = []
            functionPars = func['arguments']
            for i in range(0,len(functionPars),2):
                temp.append(functionPars[i])

            if len(exp) > len(functionPars)/2:
                print(Parse_Error(self.next_token.lineNo,'Parameters given are more than the function %s can carry -> (max) %d\nGiven -> %d' % (w,len(functionPars)/2,len(exp))))
                exit()

            for i in exp:
                try:
                    x = temp[j]
                except IndexError:
                    break
                if x == 'in' and i[0] == 'in':
                    self.genquad('par',i[1],'cv','_')
                elif x == 'inout' and i[0] == 'inout':
                    self.genquad('par',i[1],'ref','_')
                else:
                    print(Parse_Error(self.next_token.lineNo,"Parameters of %s don't match\nActual parameters ->" % w))
                    print(func['arguments'])
                    print("Given Parameters ->")
                    print(*exp)
                    exit()
                j += 1
                
        else:
            return

        return        



    def end_of_statement(self):
        # each statement ends with ; check it
        if self.next_token.tokenString != ';':
                print(Parse_Error(self.current_token.lineNo,
                      ' expected ; after statement'))
                exit()
        self.move_token_idx()
        return

    # checks if the statement is valid if its a } it will just be returned to the 1st caller and he will determine if its valid or not
    def invalid_statement(self, token):
        if token != None:
            if token.tokenString != self.R_CURLY_BRACKET:
               print(Parse_Error(token.lineNo,
                     "Not a valid statement %s" % token.tokenString))
               exit()
        return

    def functionBlock(self, w,mode):  # function block
        # call block basiccaly
        #i use this because main has the def block function -> seperate main from functions
        self.declare_sym()
        self.subprogram_sym()
        self.genquad('begin_func_block', w, '_', '_')
        self.value = w
        startQuad = self.LABEL + 1
        if mode == 'proc':
            self.parse_state = self.PROC
        else:
            self.parse_state = self.FUNC
    
        self.statement_sym()
        while self.next_token.tokenString != self.R_CURLY_BRACKET:  # w8 for end of function meaning } bracket
            if self.next_token.tokenString == self.L_CURLY_BRACKET:
                print(Parse_Error(self.next_token.lineNo,'Opening of new bracket before closing previous\nin function body -> %s' %w))
                exit()
            a = self.statement_sym()
            self.invalid_statement(a)
        # self.valid_statements(self.current_token.lineNo)
        if self.returnFlag != 1 and mode == 'func':
            print(Parse_Error(self.next_token.lineNo,'Expected at least one return in function body -> %s\n' % w))
            exit()

        self.genquad('end_func_block_', w, '_', '_')

        if self.next_token.tokenString == '.':
            print('Error reached end of program and bracket "{" still open')
            exit()
        
        offset = st.offset[st.scope]
        framelength = st.offset[st.scope] + 4
        st.modify_data(w,(st.scope-1),offset,startQuad,framelength)
        #set current scope for final code production to this functions scope
        f.current_scope = st.scope 
        f.produce_final_code(startQuad-1,self.LABEL) #set the block start and end to be produced
        st.print_s() #print symbol table
        if st.scope != 0:
            st.deleteScope(st.scope) #delete symbol table
            f.current_scope = st.scope
        self.returnFlag = 0 #reset retunflag for next function
        
        return 

    def valid_statements(self, pos):
            # keep pos of first bracket opening if its not closed and u eventually reach eof error pops in that original pos
        while self.next_token.tokenString != self.R_CURLY_BRACKET and self.next_token.tokenString != '.':
            if self.next_token.tokenString == self.L_CURLY_BRACKET:
                print(Parse_Error(self.next_token.lineNo,
                      "Cannot open another statement bracket { "))
                exit()
            a = self.statement_sym()  # gets a return from statements
            # f its none nothing happens if its a token then check if its } or invalid
            self.invalid_statement(a)
        if self.next_token.tokenString == '.':
            print(Parse_Error(pos, 'curly brackets were never closed'))
            exit()

        # basically get multiple statements inside {} brackets
        self.move_token_idx()

        return

    # ===================================================================================================================

    # ====================PROGRAM- BLOCK - DECLARE - SUBPROGRAM AND STATEMENTS===========================================

    def program_sym(self):

        self.move_token_idx()

        if self.tokens[0].tokenString != 'program':

            print(Parse_Error(self.current_token.lineNo,
                  'Each file needs to start with program'))
            exit()

        if self.tokens[-1].tokenString != '.':
            # i decide to snick peek here to see if we have a program error
            print(Parse_Error(self.current_token.lineNo,
                  'Program needs to end with a . '))
            exit()

        if self.current_token.tokenString == 'program' and self.next_token.tokenType != TOKEN_IDENTIFIER:
            print(Parse_Error(self.current_token.lineNo,
                  'program declaration expected identifier but got ' + self.next_token.tokenType))
            exit()
        self.genquad('begin_program', self.next_token.tokenString, '_', '_')

        return self.next_token.tokenString

    def block_sym(self):

        # if next token in list statements its a statement

        self.declare_sym()

        self.subprogram_sym()
        self.parse_state = 'main'
        self.value = ''
        # only the main program statements are gonna be called from block since its an explicit declaration from parse
        # nowhere else is it called
        # we are now going into main statements set parse_state to ''
        self.statement_sym()
        
        if self.next_token.tokenString == '.':
            print('End of program exiting succesfully.....\n')
            return self.next_token
        return self.next_token

        # if its . end of program exit

    def declare_sym(self):
        # recursive descent every method is based on this principle

        if self.next_token.tokenString in declarations:

            self.move_token_idx()

            if self.next_token.tokenType == TOKEN_IDENTIFIER:  # check
                # if its func state then you can declare the same named variable locally
                
                # append into declared list the current variable
                
                self.make_data('var')
                self.move_token_idx()
                self.declare_varlist()  # call varlist maybe we have more identifiers etc

                if self.next_token.tokenString != ';':
                    print(Parse_Error(self.current_token.lineNo,
                          'expected ; at the end of declaration'))
                    exit()
                self.move_token_idx()

                if self.next_token.tokenString in declarations:
                    
                    self.declare_sym()
                
                return

            else:
                print(Parse_Error(self.current_token.lineNo,
                      'was expecting identifier after declare'))
                exit()

        else:
            return

    def declare_varlist(self):

        if self.next_token.tokenString == ',':
            self.move_token_idx()
            if self.next_token.tokenType == TOKEN_IDENTIFIER:
                var = self.next_token.tokenString
                if st.lookup(st.scope,self.next_token.tokenString) == True:

                    print(Parse_Error(self.current_token.lineNo,
                          "Variable is already declared : " + self.next_token.tokenString))
                    exit()

                
                self.make_data('var')
                self.move_token_idx()
                return self.declare_varlist()
            else:
                print(Parse_Error(self.current_token.lineNo,
                      ' expected identifier after ,'))
                exit()

        else:
            return

    def subprogram_sym(self):
        if self.next_token.tokenString in subprograms:
            if self.next_token.tokenString == 'procedure':
                mode = 'proc'
            else:
                mode = 'func'
            
            self.move_token_idx()
            if self.next_token.tokenType == TOKEN_IDENTIFIER:
                # if another function is declared and it has the same name its an error
                valid,s = st.lookup(st.scope,self.next_token.tokenString)
                if valid != False and valid['entype'] != 'parameter':
                    print(Parse_Error(self.current_token.lineNo,
                          'The name of the function/procedure needs to be unique:\nfound symbol with the same :\nname -> %s\nwith type -> %s'%(self.next_token.tokenString,valid)))
                    exit()
                w = self.next_token.tokenString  # keep function name stored
                
                
                self.move_token_idx()
                # checks correct syntax of function declaration
                if self.next_token.tokenString == self.L_PARENTHESIS:

                    self.move_token_idx()
                    function_parameters = []
                    function_parameters = self.subprogram_validate(
                        function_parameters)

                    # functions_id is a dict with a key of the function name and the value of the parameters of the same function
                    self.functions_id[w] = function_parameters
                    # append the parameters as a value of function and clear the list for next fucntion
                    
                    if self.next_token.tokenString != self.R_PARENTHESIS:
                        print(Parse_Error(self.current_token.lineNo,
                              'brackets were not closed in subprogram declaration'))
                        exit()
                   
                    if mode == 'proc':
                        self.make_data('proc',w)
                    else:
                        self.make_data('func',w)
                    
                    st.headval = st.tailval
                    st.scope+=1
                    st.offset[st.scope] = 8
                    tmp = self.functions_id[w]
                    for i in range(0,len(tmp),2):
                        if tmp[i] == 'in':
                            self.make_data('par',tmp[i+1],'cv')
                        elif tmp[i] == 'inout':
                            self.make_data('par',tmp[i+1],'ref')
                        
                    
                    

                    self.move_look_and_validate(0, w,mode)
                    
                    
                    
                    
                    if self.next_token.tokenString in subprograms:
                        self.subprogram_sym()
                    
                    return
                else:
                    print(Parse_Error(self.current_token.lineNo,
                          'was expecting ( after identifier'))
                    exit()

            else:
                print(Parse_Error(self.current_token.lineNo,
                      'was expecting identifier after : ' + self.current_token.tokenString))
                exit()
        else:
            return

    def subprogram_validate(self, function_parameters):
        self.look_next_token()
        if self.next_token.tokenString in in_out:
            self.move_to_next_token()
            function_parameters.append(self.current_token.tokenString)
            f = self.subprogram_formalparlist(function_parameters)
            return f

        else:
            return function_parameters

    def subprogram_formalparlist(self, function_parameters):
        self.look_next_token()
        flag = False
        if self.next_token.tokenType == TOKEN_IDENTIFIER:
            self.move_token_idx()
            function_parameters.append(self.current_token.tokenString)
            if self.next_token.tokenString == ',':
                self.move_to_next_token()
                f = self.subprogram_validate(function_parameters)
                return f
            else:
                return function_parameters
        else:
            print(Parse_Error(self.current_token.lineNo,
                  'expected identifier after : ', self.current_token.tokenString))
            exit()

    # check statements and call their respective def_stats

    def statement_sym(self):

        if self.next_token.tokenType == TOKEN_IDENTIFIER:
            self.assign_stat()
            return None

        elif self.next_token.tokenString == 'if':
            self.if_stat()
            return None

        elif self.next_token.tokenString == 'while':
            self.while_stat()
            return None

        elif self.next_token.tokenString in cases:
            exitlist = self.empty_list()
            # make exitlist and pass it to for_switch-case
            if self.next_token.tokenString == 'forcase':
                case = 'for'
                # different statements for forcase and switchcase so we need to know which one it is
            else:
                case = 'switch'
            self.previous_state = self.parse_state
            w = self.LABEL
            self.for_switch_case_stat(exitlist, case, w)
            self.parse_state = self.previous_state
            # reset parse_state if we are in func state things change so we need to know reset the state
            return None

        elif self.next_token.tokenString == 'incase':

            exitlist = self.empty_list()
            self.previous_state = self.parse_state
            w = str(self.LABEL + 1)
            self.incase_stat(exitlist, w)
            # set flag for incase due to its unique rules
            self.genquad('=', 'flag', '1', w)
            # if flag = 1 loop incase
            self.parse_state = self.previous_state
            return None

        elif self.next_token.tokenString == 'return':
            if self.parse_state != self.FUNC:
                print(Parse_Error(self.next_token.lineNo,"Return can only be used inside a function body you are currently in %s body"%self.parse_state))
                exit()
            self.return_stat()
            self.end_of_statement()
            self.returnFlag = 1
            return None

        elif self.next_token.tokenString == 'call':
            self.call_stat()

            self.end_of_statement()
            return None

        elif self.next_token.tokenString == 'input':
            self.input_stat()
            self.end_of_statement()
            return None

        elif self.next_token.tokenString == 'print':
            self.print_stat()
            self.end_of_statement()
            return None

        elif self.next_token.tokenString == self.L_CURLY_BRACKET:
            
            # this is techincally true but i put state as nested so that if i encounter a subprogram here then at the end i can return here and not at block_sym()
            self.move_to_next_token()
            self.look_next_token()

            # if we are in main state then make a begin_main_block quad and set state to main_end
            # so that we don;t keep printing begin_main_block quads
            # how is that possible u say ? well since while,if and other methods are just calling statement_sym()
            # if they have only one statement then its fine
            # but if the have multiple meaning {} brackets are opened and we are already in main well its gonna be printed
            # this dodges that undesirable outcome
            if self.parse_state == 'main':

                self.genquad('begin_main_block', expressions[1][1], '_', '_')
                self.parse_state = 'main_end'
                self.main_start = self.LABEL

            self.valid_statements(self.current_token.lineNo)
            if self.next_token.tokenString != '.':

                self.end_of_statement()
                if self.next_token.tokenString == '.':
                    print(Parse_Error(self.current_token.lineNo,"Main statement block ends with . not ; "))
                    exit()
            
            

        elif self.next_token.tokenString in declarations:
            print(Parse_Error(self.current_token.lineNo,
                  'cannot declare variable inside { statements } '))
            exit()

        elif self.next_token.tokenString in subprograms:
            print(Parse_Error(self.next_token.lineNo,
                  "Was not expecting function declaration to be passed as if its a statement"))
            exit()

        # if its none of the above return the token and let it be determined if its valid or not
        # every other return in statements is None so we can differentiate them from an unexpected token and check it afterwards
        else:
            return self.next_token

    # ===================================================================================================================
    # =====================================Symbol Table =================================================================

    def make_data(self,mode,*args): #makes a data (dict) depending on the mode its called (variable,functions ,procedure,temp,const)
                                    #then depending on the mode checks if the value already exists in the same scope with def data_check() 
        if mode == 'var':
            st.offset[st.scope] += 4
            data = {'name':self.next_token.tokenString,'entype':'declare','offset':st.offset[st.scope]}
            self.data_check(data,st.scope)
            st.insertEntity(data)
            
        if mode == 'func':
            data = {'name':args[0],'entype':'function','offset':None,'arguments':self.functions_id[args[0]],'framelength':None,'startQuad':None,'scope':st.scope + 1}
            self.data_check(data,st.scope)
            st.insertEntity(data)
        if mode == 'proc':
            data = {'name':args[0],'entype':'procedure','offset':None,'arguments':self.functions_id[args[0]],'framelength':None,'startQuad':None,'scope':st.scope + 1}
            self.data_check(data,st.scope)
            st.insertEntity(data)
        if mode == 'temp':
            st.offset[st.scope] += 4
            data = {'name':args[0],'entype':'temp','offset':st.offset[st.scope]}
            st.insertEntity(data)
            
        if mode == 'par':
            st.offset[st.scope] += 4
            data = {'name':args[0],'entype':'parameter','parMode':args[1],'offset':st.offset[st.scope]}
            st.insertEntity(data)


        if mode == 'const':
            data = {'name':args[0],'value':args[1]}
            st.insertEntity(data)
        return


    
    def data_check(self,data,scope): #is used by make_data to check if an entity already exists in the same scope but parameters are an exception
        if st.scope in st.entityList:

            for i in st.entityList[scope]:
                if i['name'] == data['name'] and i['entype'] != 'parameter':
                    if scope == 0:
                        state = 'main'
                    else:
                        state = 'function'
                    print('Error in line -> %d\nVariable : %s is already declared with the type -> %s\nin the same scope->%s' %(self.current_token.lineNo,i['name'],i['entype'],state))
                    exit()
        return
    #====================================================================================================================



    

    # ================================ STATMENT STATS ====================================================================

    def print_stat(self):
        # print grammar
        self.move_token_idx()
        w = self.current_token.tokenString
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
            y = self.expression()
            if self.next_token.tokenString != self.R_PARENTHESIS:
                print(Parse_Error(self.current_token.lineNo,
                      'Expected right parenthesis "(" after expression in print function but got : ' + self.next_token.tokenString))
                exit()

            self.move_token_idx()
            self.genquad("out", y, '_', '_')
            return

        else:
            print(Parse_Error(self.current_token.lineNo,
                  'in print function expected right parenthesis "(" after print but got : ' + self.next_token.tokenString))
            exit()

    def input_stat(self):
        # input func grammar
        self.move_token_idx()
        w = self.current_token.tokenString
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
            if self.next_token.tokenType == TOKEN_IDENTIFIER:
                y = self.next_token.tokenString
                if st.lookup(st.scope,y) == False:  # if its not declared we have an error first declare then input value to it
                    print(Parse_Error(self.current_token.lineNo,
                          'Variable is not declared : ' + y))
                    exit()

                x = self.next_token.tokenString
                self.move_token_idx()
                if self.next_token.tokenString != self.R_PARENTHESIS:
                    print(Parse_Error(self.current_token.lineNo,
                          'in input function expected only right parenthesis ")" after identifier but got : ' + self.next_token.tokenString))
                    exit()

                
                self.move_token_idx()
                self.genquad("inp", y, '_', '_')

                return
            else:
                print(Parse_Error(self.current_token.lineNo,
                      'in input function expected identifier but got : ' + self.next_token.tokenType))
                exit()
        else:
            print(Parse_Error(self.current_token.lineNo,
                  'expected opening parenthesis after input function but got : ' + self.next_token.tokenString))
            exit()

    def return_stat(self):
        self.move_token_idx()
        w = self.current_token.tokenString
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
            x = self.expression()

            if self.next_token.tokenString != self.R_PARENTHESIS:
                print(Parse_Error(self.current_token.lineNo,
                      'expected closing of bracket after return expression'))
                exit()

            self.genquad("retv", x, '_', '_')
            self.move_token_idx()
        else:
            print(Parse_Error(self.next_token.lineNo,'Expected parenthesis after return keyword'))
            exit()

            

    def call_stat(self):
        # call func grammar
        self.move_token_idx()
        y = self.current_token.tokenString

        if self.next_token.tokenType == TOKEN_IDENTIFIER:
            valid,s = st.lookup(st.scope,self.next_token.tokenString)
            if valid == False:
                print(Parse_Error(self.next_token.lineNo, 'Function with the name : ' +
                      self.next_token.tokenString + " doesn't exist or isn't seen"))
                exit()
            elif valid['entype'] == 'function':
                print(Parse_Error(self.next_token.lineNo,'Functions cannot be called\nonly be used in expressions\nexample -> var := %s(parameters)'%valid['name']))
                exit()
            elif 'scope' not in valid:
                print(Parse_Error(self.next_token.lineNo,'call identifier exists but is not a procedure/function you cannot call it\nvariable -> %s' %valid['name']))
                exit()
            self.valid_var()
            self.move_token_idx()
            w = self.current_token.tokenString
            if self.next_token.tokenString == self.L_PARENTHESIS:
                self.move_token_idx()
                p,exp = self.actual_par_list(w)
                # get parameter list of function call
                # check the parameters so they are valid
                self.parameter_check(w,exp)
               
                # reset temp list
                if self.next_token.tokenString != self.R_PARENTHESIS:
                    print(Parse_Error(self.current_token.lineNo,
                          'brackets were never closed in call function'))
                    exit() 
                self.move_token_idx()
                self.genquad(y, w, '_', '_')
                return
            else:
                print(Parse_Error(self.current_token.lineNo,
                      'expected opening of brackets after call-ID'))
                exit()

        else:
            print(Parse_Error(self.current_token.lineNo,
                  'expected identifier after call function'))
            exit()

    def for_switch_case_stat(self, exitlist, case, w):
        # forcase and switchcase have basically the same gramamr rule
        # because we need to call this function again set parse_state to CASE if its case state don;t move the tokens
        if self.parse_state != self.CASE:
            self.move_token_idx()

        self.parse_state = self.previous_state

        if self.next_token.tokenString == 'case':

            exitlist = self.case_extension(exitlist, case)
            if case == 'for':
                # differnt backpatch for forcase
                self.backpatch(exitlist, str(w + 1))


            if self.next_token.tokenString == 'case':
               # we know we have another case 
                self.parse_state = self.CASE #set parse_State to case 
                self.for_switch_case_stat(exitlist,case,w) #call function again for the next case
            if self.next_token.tokenString == 'default': 
                self.move_token_idx()
                self.statement_sym()
               
                self.backpatch(exitlist,str(self.LABEL + 1))
            
           
                        
        else:
           print(Parse_Error(self.current_token.lineNo,'expected case after for/switch case declaration ' +  str(self.current_token.lineNo)))
           exit()


    def incase_stat(self, exitlist, w):
        if self.parse_state != self.CASE:
            # same as for_switch_case_stat used for recursion purposes
            self.move_token_idx()
        self.parse_state = self.previous_state
        
        if self.next_token.tokenString == 'case':
            exitlist = self.case_extension(exitlist, 'incase')
            if self.next_token.tokenString == 'case':
                # we know we have another case coming so set state to case and recursion
                self.parse_state = self.CASE
                self.incase_stat(exitlist, w)
            
            if self.next_token.tokenString == 'default':
                
                print(Parse_Error(self.current_token.lineNo,'incase has no default keyword\n'))
                exit()
            self.declared_vars.append('flag')    

        else:
            print(Parse_Error(self.current_token.lineNo,'expected ( , case after incase declaration '))
            exit()


    def case_extension(self, exitlist, method):

        # check case grammar
        self.check_case()
        self.move_token_idx()
        # statement after case condition
        self.statement_sym()
        
        if method != 'incase':
            # because case_extension function is used by incase as well and the below statements are invalid for incase
            e = self.makelist(self.LABEL + 1)
            self.genquad('jump', '_', '_', '_')
            exitlist = exitlist + e
            self.backpatch(self.b_false, str(self.LABEL + 1))
        else: #incase quads
            self.genquad(':=', "1", '_', 'flag')
            self.backpatch(self.b_false, str(self.LABEL + 1))
        #self.move_token_idx()

        # if after case grammar another case pops then check again

        return exitlist


    def check_case(self):
        # case grammar case(condition)
        
        self.move_token_idx()
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
            x = self.condition()
            
            self.backpatch(self.b_true,str(self.LABEL + 1))
            if self.next_token.tokenString != self.R_PARENTHESIS:
                    print(Parse_Error(self.current_token.lineNo,'expected closing of brackets after case - condition'))
                    exit()    
            return         
        else:
            print(Parse_Error(self.current_token.lineNo,'expected case after opening brackets before case'))
            exit()
        return                



    def assign_stat(self):
        self.valid_var()
        self.move_token_idx()
        w = self.current_token.tokenString
        
        if self.next_token.tokenString == ':=':
            y = self.next_token.tokenString 
           
            # --------------------------------------
           
            # --------------------------------------
            self.move_token_idx()
            valid = self.expression()
            x = self.genquad(y,valid,'_',w)
            # expressions.append(x)
            self.make_data('const',w,valid)
            self.end_of_statement()    

            return
     
        else:
            print(Parse_Error(self.current_token.lineNo,'expected assignment := after ' + self.current_token.tokenType + ' -> ' + self.current_token.tokenString))
            exit()


    def if_stat(self):
        self.move_token_idx()
        w = self.current_token.tokenString
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
            b_true,b_false = self.condition()
            # i get the condition lists and then reset their "global" versions 
            self.reset_b_list()
            self.backpatch(b_true,str(self.LABEL + 1))
           
            if self.next_token.tokenString != self.R_PARENTHESIS:
                print(Parse_Error(self.current_token.lineNo,'if declaration expected closing of brackets'))
                exit()
            
            
            valid = self.move_look_and_validate(1,self.value)
            iflist = self.makelist(self.LABEL + 1)
            
            self.genquad('jump','_','_','_')
            if valid == 1:
                if self.next_token.tokenString != 'else':
                    print(Parse_Error(self.next_token.lineNo,'Invalid statement '))
                    exit()
           
            
            self.backpatch(b_false,str(self.LABEL + 1))
            bol = self.elsepart(iflist)
            if bol == -1 :
                self.backpatch(iflist,str(self.LABEL + 1))
                return
                
            return 
        else:
            print(Parse_Error(self.current_token.lineNo,'Expected left parenthesis "(" after if'))
            exit()

    def elsepart(self, iflist):

        if self.next_token.tokenString == 'else':
            w = self.next_token.tokenString

            self.move_token_idx()
            self.statement_sym()
            self.backpatch(iflist, str(self.LABEL + 1))
            return
        else:
            # no else method after if 
            return -1



    def while_stat(self):
        self.move_to_next_token()
        self.look_next_token()
       
        w = self.current_token.tokenString
        
        st = self.LABEL
        if self.next_token.tokenString == self.L_PARENTHESIS:
             self.move_to_next_token()
             self.look_next_token()
             b_true,b_false = self.condition()
             self.reset_b_list()
             
             
             # --------------------------------------------------------------
             self.backpatch(b_true,str(self.LABEL + 1))
             
             if self.next_token.tokenString != self.R_PARENTHESIS:
                 print(Parse_Error(self.current_token.lineNo,'in while declaration expected closing brackets'))
                 exit()
             
             self.move_look_and_validate(1,self.value)
             
             self.genquad('jump',"_",'_',str(st + 1))
             
             self.backpatch(b_false,str(self.LABEL + 1))
            
             
             return
        else:
            print(Parse_Error(self.next_token.lineNo,'Expected brackets after while '))
            exit()



    # ==============================================================================================================================

    # =================================EXPRESSIONS AND CONDITIONS ==================================================================

    

    def expression(self):
        # self.look_next_token()
        x = self.optional_sign()
        t1 = self.term()
        while self.next_token.tokenType == TOKEN_ADD_OPERATOR:
            self.move_token_idx()
            w = self.newTemp()
            self.genquad(self.current_token.tokenString,t1,self.term(),w)
            t1 = w
           

        
        if x != None :
            return x+t1
        else:
            return t1

    def optional_sign(self):
        if self.next_token.tokenType == TOKEN_ADD_OPERATOR:
            # --------------------------------------
            # --------------------------------------
            self.move_token_idx()
            x = self.current_token.tokenString
            return x
        else:
            return    


    def term(self):

       t1 = self.factor()
       self.look_next_token()
       while self.next_token.tokenType == TOKEN_MUL_OPERATOR:
          
           self.move_token_idx()
           w = self.newTemp()
           self.genquad(self.current_token.tokenString,t1, self.term(),w)
           check = expressions[self.LABEL]
           if check[0] == '/':
               if check[2] == '0':
                   print(Parse_Error(self.next_token.lineNo,"You can't divide by 0 simple math !!"))
                   exit()
              
              
           t1 = w

       return t1

        
    
    def factor(self):
        # self.look_next_token()
        if self.next_token.tokenType == TOKEN_NUMBER:
            
            self.move_to_next_token()       
            return self.current_token.tokenString


        elif  self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_token_idx()
         
            y = self.expression()
            if self.next_token.tokenString != self.R_PARENTHESIS:
                print(Parse_Error(self.current_token.lineNo,' expected ) to end expression'))
                exit()
             
            self.move_to_next_token()
            return y
            

        elif self.next_token.tokenType == TOKEN_IDENTIFIER:
            self.valid_var()
            self.move_to_next_token()
            
            w = self.current_token.tokenString
            y,exp = self.idtail(w)                               
            if y == -1: #if its not a function and if u are in main and the variable has no value u can;t use it
                flagy = -1
                for i in range(st.scope,-1,-1):
                    valid = st.lookup(i,w)
                    if valid != False:
                        flagy = 0
                        break
                if flagy == -1:
                    print(Parse_Error(self.next_token.lineNo,'Variable does not exist %s ' % w))
                    exit()
                
                return w
            
            y = self.newTemp()
            # if it is a function then call parameter check 
            #self.parameter_check(w)
            #parameter check works like this : 
            # first every function has its own exp list that every expression is appended with its given parMode
            # so let's say we have max(in max(in a,in b),in b) then the following will happend
            # we encounter the 1st max check next and see in then we see the next and its max (a function) so we call the expression which is max(in a,in b)
            # the new expression has its own exp and appends in a , in b then parameter check is called if its valid we return T_0 to the first max
            #remember par T_0,ret -> call max -> in T_0 then we check the parameter after which is in b we append it to exp and finally we have in T_0,in b
            self.parameter_check(w,exp)
            self.genquad('par',y,'ret','_')
            self.genquad('call',w,'_','_')
            
            return y
        else:
            print(Parse_Error(self.current_token.lineNo,'Invalid expression'))
            exit()  


    def idtail(self,w):
        self.look_next_token()
        if self.next_token.tokenString == self.L_PARENTHESIS:
            self.move_to_next_token()
            valid,i = st.lookup(st.scope,w)
            if valid == False:
                print(Parse_Error(self.next_token.lineNo,'Symbol -> "%s" is not found' %w))
                exit()
            if valid['entype'] != 'function':
                if valid['entype'] == 'procedure':
                    print(Parse_Error(self.next_token.lineNo,"You can't use procedures in expressions they have no return value"))
                    exit()
                elif valid['entype'] == 'declare':
                    print(Parse_Error(self.next_token.lineNo,'You are using symbol -> "%s" as a function\n but it has type -> variable'%valid['name']))
                    exit()
                else:
                    print(Parse_Error(self.next_token.lineNo,'You are using symbol -> "%s" as a function\n but it is of type %s'% (valid['name'],valid['entype'])))
                    exit()
            x,exp= self.actual_par_list(w)
            

            if self.next_token.tokenString != self.R_PARENTHESIS:
                print(Parse_Error(self.current_token.lineNo,' expected ) to end expression '))
                exit()
              
            self.move_to_next_token()
            return x,exp  

        else:
            return -1,[]
                 

    def actual_par_item(self,w,exp):

        self.look_next_token()
        if self.next_token.tokenType == TOKEN_IDENTIFIER:
            self.valid_var()
            if st.lookup(st.scope,self.next_token.tokenString) == False:
                print(Parse_Error(self.current_token.lineNo,"Variable is not in scope : " + self.next_token.tokenString))
                exit()
            self.move_token_idx()
            x = self.current_token.tokenString
            exp.append(['inout',x])
            #self.genquad('par',x,'ref','_')
            if self.next_token.tokenString == ',':
                self.move_to_next_token()
                a,e = self.actual_par_list(w)
                exp += e
                return a,exp
            elif self.next_token.tokenString == self.L_PARENTHESIS and x in self.functions_id:
                print(Parse_Error(self.next_token.lineNo,"Inout syntax is : inout ID(variable), instead you have used a function -> %s" % x))
                exit()
            else:                  
                return x,exp

        else:
            print(Parse_Error(self.current_token.lineNo,'expected identifier after inout '))
            exit()


    
    def actual_par_list(self,w):
        exp = []
        
        self.look_next_token()
        if self.next_token.tokenString == 'in':
            self.move_token_idx()
            

            
                # if after in we have a function then we need to get temp ready for parameter check(nested)
            
               
            
            y = self.expression()
            
            
            exp.append(['in',y])


            if self.next_token.tokenString == ',':
                
                self.move_to_next_token()
                
                y,x = self.actual_par_list(w)
                exp += x
                return y,exp
            else:
                
                return  y,exp  

        elif self.next_token.tokenString == 'inout':
            self.move_to_next_token()
        
           
            y,exp = self.actual_par_item(w,exp)
            
            
            return y,exp

        else:
            
            return 1,[]


    # made b_true for true expressions list and b_false respectively 
    # i made them to be basically "global"
    
    b_true = []
    b_false = []
    not_flag = 0
    def reset_b_list(self):
        # i reset the lists to be empty so the next conditions and backpatches don;t have to parse through extra items
        self.b_true = []
        self.b_false = []
        return

    def condition(self):

        x = self.boolterm()      
     
        while self.next_token.tokenString == 'or':
            
            self.backpatch(self.b_false,str(self.LABEL + 1))
          
            self.move_token_idx()
            x = self.condition()        
        
        b_true = self.b_true
        b_false = self.b_false
        # i return copies of self.b_true/b_false so i can immediately reset them after
        return b_true,b_false


    def boolterm(self):
        x = self.boolfactor()
        if x != -1:

            self.b_true.append(self.LABEL)
            self.genquad('jump','_','_','_')
            self.b_false.append(self.LABEL) 
        self.look_next_token()
       
        while self.next_token.tokenString == 'and':

            
            self.backpatch(self.b_true,str(self.LABEL + 1))
            
            self.move_token_idx()
            x = self.boolterm()
                 
        return x

    def boolfactor(self):
        
        if self.next_token.tokenString == 'not':
            

            self.move_to_next_token()
            self.look_next_token()
            if self.next_token.tokenString == self.L_BRACKET:
                self.move_to_next_token()
                self.look_next_token()
                self.not_flag = 1
                x = self.condition()
                self.not_flag = 0
                if self.next_token.tokenString != self.R_BRACKET:
                    print(Parse_Error(self.current_token.lineNo,'expecting left bracket "]" after condition'))
                    exit()
                
                tmp1 = self.b_true[-1]
                tmp2 = self.b_false[-1]
                
                self.b_true[-1] = tmp2
                self.b_false[-1] = tmp1   
                self.move_to_next_token()
               
                return -1
                
        elif self.next_token.tokenString == self.L_BRACKET:
             self.move_token_idx()
             self.not_flag = 1
             x = self.condition()
             self.not_flag = 0
             if self.next_token.tokenString != self.R_BRACKET:
                    print(Parse_Error(self.current_token.lineNo,'expecting left bracket "]" after condition'))
                    exit()
             self.move_to_next_token()
             return x


        w = self.expression()              
            
        if self.next_token.tokenType == TOKEN_REL_OPERATOR:
            rel = self.next_token.tokenString
               
            self.move_token_idx()
            x = self.expression()

            self.genquad(rel,w,x,'_')
            return x
                    
        else:
            print(Parse_Error(self.current_token.lineNo,'was expecting rel operator after expression' + self.current_token.tokenString))
            exit()        

    # ===================================================================================================
    # ===================================================================================================       

  



class Final:

    def __init__(self):
        self.assembly = []
        self.current_scope = 0
        self.counter = 2


    def labels(self):
        #just appends to the list the label and its counter , then increments said counter
        self.assembly.append('L%d:\n'%self.counter)   
        return 

    def beginFuncBlock(self):
        #if the program has a function then do jump to main once only
        if expressions[2][0] == 'begin_func_block':
            self.assembly.append('L1: b Lmain\n')
            
            
        return 

    def produce_final_code(self,start,end):
        
        w = 0
        if start <= 3:
            self.beginFuncBlock()
    
        #basically producing final code for each block 
        parcount = 0
        for i in range(start,end+1):
            #by the book stuff(literally)
            self.counter = i
            value = expressions[i]
            if value[0] == 'begin_main_block':
                self.assembly.append('Lmain:\n')
                self.labels()
                self.assembly.append('\taddi $sp,$sp,%d\n'%(st.offset[0] + 4))
                self.assembly.append('\tmove $s0,$sp\n')
                self.current_scope = 0

              
            if value[0] == 'begin_func_block':
                
                self.labels()
                self.assembly.append('\tsw $ra,-0($sp)\n')

            if value[0] == 'end_func_block_':
                self.labels()
                self.assembly.append('\tlw $ra,-0($sp)\n')
                self.assembly.append('\tjr $ra\n')


            if value[0] == ':=':
                self.labels()
                self.loadvr(value[1],'$t1')
                self.storerv(value[3],'$t1')

            if value[0] in addOperators + mulOperators:
                self.labels()
                self.loadvr(value[1],'$t1')
                self.loadvr(value[2],'$t2')
                if value[0] == '+':
                    self.assembly.append('\tadd $t1,$t1,$t2\n')
                elif value[0] == '-':
                    self.assembly.append('\tsub $t1,$t1,$t2\n')
                elif value[0] == '*':
                    self.assembly.append('\tmul $t1,$t1,$t2\n')
                elif value[0] == '/':
                    self.assembly.append('\tdiv $t1,$t1,$t2\n')
                self.storerv(value[3],'$t1')

            if value[0] == 'halt':
                self.labels()
                self.assembly.append('\n')
                self.counter += 1
                self.labels()
                self.print_final()

                break

            if value[0] == 'jump':
                self.labels()
                self.assembly.append('\tb L%d\n'%int(value[3]))
            
            if value[0] == 'out':
                self.labels()
                self.assembly.append('\tli $v0,1\n')
                self.loadvr(value[1],'$a0')
                self.assembly.append('\tsyscall\n')

            if value[0] == 'inp':
                self.labels()
                self.assembly.append('\tli $v0,5\n')
                self.assembly.append('\tsyscall\n')
                self.storerv(value[1],'$v0')
    
            if value[0] == 'retv':
                self.labels()
                self.loadvr(value[1],'$t1')
                self.assembly.append('\tlw $t0,-8($sp)\n')
                self.assembly.append('\tsw $t1,($t0)\n')
                self.assembly.append('\tb L%d\n' % end)
                
            
            if value[0] in relOperatos:
                self.labels()
                self.loadvr(value[1],'$t1')
                self.loadvr(value[2],'$t2')
                if value[0] == '=':
                    self.assembly.append('\tbeq $t1,$t2,L%d\n' % int(value[3]))
                elif value[0] == '>':
                    self.assembly.append('\tbgt $t1,$t2,L%d\n' % int(value[3]))
                elif value[0] == '>=':
                    self.assembly.append('\tbge $t1,$t2,L%d\n' % int(value[3]))
                elif value[0] == '<':
                    self.assembly.append('\tblt $t1,$t2,L%d\n' % int(value[3]))
                elif value[0] == '<=':
                    self.assembly.append('\tble $t1,$t2,L%d\n' % int(value[3]))
                elif value[0] == '<>':
                    self.assembly.append('\tbne $t1,$t2,L%d\n' % int(value[3]))
            
            if value[0] == 'par':
                if parcount == 0:

                    for j in range(i + 1,end):
                        func = expressions[j]
                        if func[0] == 'call':
                            name = func[1]
                            func,funscope = st.lookup(self.current_scope,name)
                            frame = func['framelength']
                            break
                    
                    self.labels()
                    self.assembly.append('\taddi $fp,$sp,%d\n' %frame)
                if value[2] == 'cv':
                    self.loadvr(value[1],'$t0')
                    
                    self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                    parcount+= 1
                if value[2] == 'ref':
                    s,scope = st.lookup(self.current_scope,value[1])
                    if scope == self.current_scope:
                        if s['entype'] == 'parameter' and s['parMode'] == 'cv':
                            if parcount != 0:
                                self.labels()
                            self.assembly.append('\taddi $t0,$sp,-%d\n'%s['offset'])
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount += 1
                        elif s['entype'] == 'declare':
                            if parcount != 0:
                                self.labels()
                            self.assembly.append('\taddi $t0,$sp,-%d\n'%s['offset'])
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount+=1

                        elif s['entype'] == 'parameter' and s['parMode'] == 'ref':
                            if parcount != 0:
                                self.labels()
                            self.assembly.append('\tlw $t0,-%d($sp)\n'%s['offset'])
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount+=1
                    else:
                        if s['entype'] == 'parameter' and s['parMode'] == 'cv':
                            if parcount != 0:
                                self.labels()
                            self.gnvlcode(value[1])
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount += 1
                        elif s['entype'] == 'declare':
                            if parcount != 0:
                                self.labels()
                            self.gnvlcode(value[1])
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount += 1 
                        else:
                            if parcount != 0:
                                self.labels()
                            self.gnvlcode(value[1])
                            self.assembly.append('\tlw $t0,($t0)\n')
                            self.assembly.append('\tsw $t0,-%d($fp)\n'%(12 + 4*parcount))
                            parcount += 1
                if value[2] == 'ret':
                    temp,s = st.lookup(self.current_scope,value[1])
                    
                    if parcount != 0:
                            self.labels()
                    self.assembly.append('\taddi $t0,$sp,-%d\n'%temp['offset'])
                    self.assembly.append('\tsw $t0,-8($fp)\n')
                    

            if value[0] == 'call':
                fp = -1
                if parcount == 0:
                    fp = 1 #means function has no parameters p(); but is called
                parcount = 0
                func,scope = st.lookup(self.current_scope,value[1])
                
                if func['scope'] == self.current_scope:
                    self.labels()
                    #if fp == 1:
                        #self.assembly.append('\taddi $fp,$sp,%d\n' %func['framelength'])
                    self.assembly.append('\tlw $t0,-4($sp)\n')
                    self.assembly.append('\tsw $t0,-4($fp)\n')
                else:
                    self.labels()
                    #if fp == 1:
                        #self.assembly.append('\taddi $fp,$sp,%d\n' %func['framelength'])
                    self.assembly.append('\tsw $sp,-4($fp)\n')
                
                self.assembly.append('\taddi $sp,$sp,%d\n'%func['framelength'])
                self.assembly.append('\tjal L%d\n'%(func['startQuad'] - 1))
                self.assembly.append('\taddi $sp,$sp,-%d\n'%func['framelength'])


                
        return 

    def gnvlcode(self,v):
        #given help function from pdf
        scope = 0
        self.assembly.append('\tlw $t0,-4($sp)\n')
        for i in st.entityList:
            if i == self.current_scope:
                break
            valid,s = st.lookup(i,v)
            if valid != False:
                scope = i
                break
        
        for j in range(self.current_scope,scope):
            self.assembly.append('\tlw $t0,-4($t0)\n')
            
        self.assembly.append('\taddi $t0,$t0,-%d\n' % valid['offset'])


    def loadvr(self,v,r):
        scope = 0
        try:
            const = int(v)
            self.assembly.append('\tli %s,%d\n'%(r,const))
            return
        except ValueError:
            local,scope = st.lookup(self.current_scope,v)
            #from here on we have a different command for each situation e.x - > scope == self.current_scope meaning local variable
            # if its a parameter and its parMode is reference do this else do smth else...
            if scope == self.current_scope: 
                #local variable
                if local['entype'] == 'parameter' and local['parMode'] == 'ref':
                    self.assembly.append('\tlw $t0,-%d($sp)\n'% local['offset'])
                    self.assembly.append('\tlw %s,($t0)\n'%r)
                else:
                    self.assembly.append('\tlw %s,-%d($sp)\n'%(r,local['offset']))
                return
            if scope == 0:
                #global variable in main
                self.assembly.append('\tlw %s,-%d($s0)\n'%(r,local['offset']))
                return           
            
            if scope > 0 and scope < self.current_scope:
                if local['entype'] == 'parameter' and local['parMode'] == 'ref':
                    self.gnvlcode(v)
                    self.assembly.append('\tlw $t0,($t0)\n')
                    self.assembly.append('\tlw %s,($t0)\n'%r)
                else:
                    self.gnvlcode(v)
                    self.assembly.append('\tlw %s,($t0)\n'%r)

                return
        
    def storerv(self,v,r):
        local,scope = st.lookup(self.current_scope,v)


        if scope == self.current_scope:
            #local variable
            if local['entype'] == 'parameter' and local['parMode'] == 'ref':
                self.assembly.append('\tlw $t0,-%d($sp)\n'%local['offset'])
                self.assembly.append('\tsw %s,($t0)\n'%r)
            else:
                self.assembly.append('\tsw %s,-%d($sp)\n'%(r,local['offset']))
            return
        if scope == 0:
            self.assembly.append('\tsw %s,-%d($s0)\n'%(r,local['offset']))
            return
        

        if scope > 0 and scope < self.current_scope:
            if local['entype'] == 'parameter' and local['parMode'] == 'ref':
                self.gnvlcode(v)
                self.assembly.append('\tlw $t0,($t0)\n')
                self.assembly.append('\tsw %s,($t0)\n'%r)
            else:
                self.gnvlcode(v)
                self.assembly.append('\tsw %s,($t0)\n'%r)
            return

    
    def print_final(self):
        with open(checkFileExtention[0] + '.asm','w') as f:
            for i in self.assembly:
                f.write(i)
# ----------------------------------------------------------------------

lex = Lex(os.getcwd() + os.sep + sys.argv[1])
tokens = []
expressions = {}
checkFileExtention = sys.argv[1].split('.')
if checkFileExtention[1] != 'ci':
    print("Wrong file extension expected file.ci but got file.%s"%checkFileExtention[1])
    exit()


while True:
    token = lex.start()
    if token is not None:
        tokens.append(token)
        #print(json.dumps(token.__dict__))
    else:
        print("Succesfully finished lexing file...\n")
        print("Starting parsing............")
        # syntax analyzing can start now
        sa = SyntaxAnalyzer(tokens)
        st = ST()
        f = Final()
        sa.parse()              
        st.print_s()
        st.s = st.s.close()
        print('Mips assembly code succesfully generated\nYou can see the symbolTable of the code at the generated file symbolTable.txt\nexiting......')
        
        
        #f.produce_final_code()
        break
 