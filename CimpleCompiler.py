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

    PROGRAM = 'program
