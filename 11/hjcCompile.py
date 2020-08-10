"""
hjcCompile.py -- CompileEngine class for Hack computer Jack compiler
Solution provided by Nand2Tetris authors, licensed for educational purposes
Refactored and skeleton-ized by Janet Davis, April 18, 2016
Refactored by John Stratton, April 2019
"""

from hjcTokens import *
from hjcTokenizer import *
from hjcOutputFile import *
from hjcSymbolTable import *
from hjcVMWriter import *

xml = True  # Enable _WriteXml...() functions


class CompileEngine(object):
    def __init__(self, inputFileName, outputFileName, xmlOutputFileName, source=True):
        """
        Initializes the compilation of 'inputFileName' to 'outputFileName'.
        If 'source' is True, source code will be included as comments in the
            output.
        """
        self.className = None
        self.inputFileName = inputFileName
        self.source = source
        self.xmlIndent = 0
        self.labelCounters = {}
        self.xmlOutputFile = OutputFile(xmlOutputFileName)
        self.vmWriter = VmWriter(outputFileName)
        self.symbolTable = SymbolTable()
        self.tokenizer = Tokenizer(inputFileName, self.xmlOutputFile, source)
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')


    def Close(self):
        """
        Finalize the compilation and close the output file.
        """
        self.xmlOutputFile.Close()
        
    def _GetNextLabel(self, label_prefix):
        """
        Gets a label that is unique within this subroutine.
        """

        if label_prefix not in self.labelCounters:
            self.labelCounters[label_prefix] = -1
        self.labelCounters[label_prefix] += 1
        return label_prefix + str(self.labelCounters[label_prefix])


    def CompileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final '}'
        """
        self._WriteXmlTag('<class>\n')
        self._ExpectKeyword(KW_CLASS)
        self._NextToken()

        self.className = self._ExpectIdentifier()
        self._NextToken()

        self._ExpectSymbol('{')
        self._NextToken()

        while True:
            if not self._MatchKeyword((KW_STATIC, KW_FIELD)):
                break
            self._CompileClassVarDec();

        while True:
            if not self._MatchKeyword((KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD)):
                break
            self._CompileSubroutine();

        self._ExpectSymbol('}')
        self._WriteTokenXML()
        self._WriteXmlTag('</class>\n')
        if self.tokenizer.Advance():
            self._RaiseError('Junk after end of class definition')

    def _CompileClassVarDec(self):
        """
        Compiles <class-var-dec> :=
            ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<classVarDec>\n')

        storageClass = self._ExpectKeyword((KW_STATIC, KW_FIELD))
        self._NextToken()

        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
        else:
            variableType = self._ExpectIdentifier()
        self._NextToken()
        
        
        while True:
            
            variableName = self._ExpectIdentifier()
            self._NextToken()
            if storageClass == KW_STATIC:
                self._DefineSymbol(variableName, variableType, SYMK_STATIC)
            else:
                self._DefineSymbol(variableName, variableType, SYMK_FIELD)

            if not self._MatchSymbol(','):
                break
            self._NextToken()
        def _countVar(self):
            return count1
       
        self._ExpectSymbol(';')
        self._NextToken()
        self._WriteXmlTag('</classVarDec>\n')

    def _CompileSubroutine(self):
        """
        Compiles <subroutine-dec> :=
            ('constructor' | 'function' | 'method') ('void' | <type>)
            <subroutine-name> '(' <parameter-list> ')' <subroutine-body>
            
        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<subroutineDec>\n')

        self.symbolTable.StartSubroutine()
        self.labelCounters = {}

        subroutineType = self._ExpectKeyword((KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD))
        self._NextToken()
        #TODO-11C: For a method in particular, we need to declare an implicit 
        #          first argument in the symbol table before we add the others.
        
        if subroutineType  == KW_METHOD:
            self.symbolTable.Define('this', self.className, SEG_ARG)

        if self.tokenizer.TokenType() == TK_KEYWORD:
            returnType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN, KW_VOID))
        else:
            returnType = self._ExpectIdentifier()
        self._NextToken()

        subroutineName = self._ExpectIdentifier()
        self._NextToken()


        self._ExpectSymbol('(')
        self._NextToken()

        self._CompileParameterList()
        
        self._ExpectSymbol(')')
        self._NextToken()
        
        self._CompileSubroutineBody(subroutineType, subroutineName)

        self._WriteXmlTag('</subroutineDec>\n')


    def _CompileParameterList(self):
        """
        Compiles <parameter-list> :=
            ( <type> <var-name> (',' <type> <var-name>)* )?

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<parameterList>\n')
        
        while True:
            if self._MatchSymbol(')'):
                break;
            
            if self.tokenizer.TokenType() == TK_KEYWORD:
                parameterType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            else:
                parameterType = self._ExpectIdentifier()
            self._NextToken()

            parameterName = self._ExpectIdentifier();
            self._NextToken();

            #TODO-11B: Define this parameter in the symbol table.
            #          Uncomment the next two lines and fill in a value 
            #          for parameterKind.
            parameterKind = SYMK_ARG
            self._DefineSymbol(parameterName, parameterType, parameterKind)

            if not self._MatchSymbol(','):
                break
            self._NextToken()
            
        # Write close tag
        self._WriteXmlTag('</parameterList>\n')
                

    def _CompileSubroutineBody(self, subroutineType, subroutineName):
        """
        Compiles <subroutine-body> :=
            '{' <var-dec>* <statements> '}'

        The tokenizer is expected to be positioned before the {
        ENTRY: Tokenizer positioned on the initial '{'.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<subroutineBody>\n')
        
        self._ExpectSymbol('{')
        self._NextToken()
        countVar = 0
        while self._MatchKeyword(KW_VAR):
            self._CompileVarDec()
            countVar = self.symbolTable.VarCount(SYMK_VAR)

        #TODO-11A: Write the VM function command below.
        #          The function name is given as a parameter above; 
        #          you will also need self.className.
        function_name = self.className + '.' + subroutineName
        self.vmWriter.WriteFunction(function_name, countVar)
        #need number of locals

        if subroutineType == KW_CONSTRUCTOR:
            #In a constructor, the first operations must allocate memory for 
            # the current object.
            self.vmWriter.WritePush(SEG_CONST, self.symbolTable.VarCount(SYMK_FIELD))
            self.vmWriter.WriteCall("Memory.alloc", 1)
            self.vmWriter.WritePop(SEG_POINTER, 0)
        elif subroutineType == KW_METHOD:
            #TODO-11C: Replace "pass" with code to move the current object pointer
            #          from its spot as the first argument to the THIS pointer location
            self.vmWriter.WritePush(SEG_ARG, 0)
            self.vmWriter.WritePop(SEG_POINTER, 0)

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._NextToken()
        
        self._WriteXmlTag('</subroutineBody>\n')


    def _CompileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial 'var'.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<varDec>\n')
        
        storageClass = self._ExpectKeyword(KW_VAR)
        self._NextToken()
        
        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
        else:
            variableType = self._ExpectIdentifier()
        self._NextToken()
        variableName = self._ExpectIdentifier()
        #self._DefineSymbol(variableName, variableType, SYMK_VAR)
        #might need to add to symbol table before while loop
        while True:
            variableName = self._ExpectIdentifier()
            self._NextToken()
            self._DefineSymbol(variableName, variableType, SYMK_VAR)
            #TODO-11B: Define the declared variable (above) in the symbol table.
            if not self._MatchSymbol(','):
                break
            self._NextToken()

        self._ExpectSymbol(';')
        self._NextToken()
    
        self._WriteXmlTag('</varDec>\n')


    def _CompileStatements(self):
        """
        Compiles <statements> := (<let-statement> | <if-statement> |
            <while-statement> | <do-statement> | <return-statement>)*

        The tokenizer is expected to be positioned on the first statement
        ENTRY: Tokenizer positioned on the first statement.
        EXIT:  Tokenizer positioned after final statement.
        """
        self._WriteXmlTag('<statements>\n')

        kw = self._ExpectKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))
        while kw:
            if kw == KW_DO:
                self._CompileDo()
            elif kw == KW_IF:
                self._CompileIf()
            elif kw == KW_LET:
                self._CompileLet()
            elif kw == KW_RETURN:
                self._CompileReturn()
            elif kw == KW_WHILE:
                self._CompileWhile()
            kw = self._MatchKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))
            
        self._WriteXmlTag('</statements>\n')


    def _CompileLet(self):
        """
        Compiles <let-statement> :=
            'let' <var-name> ('[' <expression> ']')? '=' <expression> ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<letStatement>\n')

        # TODO-10A: Extend the code below to parse a let statement without array indexing.
        # TODO-10F: Account for array indexing.
        self._ExpectKeyword(KW_LET)
        self._NextToken()
        self._ExpectIdentifier()
        var_name = self._ExpectIdentifier()
        self._NextToken()
        var_kind = self._KindToSegment(self.symbolTable.KindOf(var_name))
        var_index = self.symbolTable.IndexOf(var_name)


        isArrayAssign = False
        if self._MatchSymbol('[') == '[':
            isArrayAssign = True
       
        if isArrayAssign:
            self._ExpectSymbol('[')
            self._NextToken()
            self._CompileExpression()
            self._NextToken()  
            self._ExpectSymbol('=')
            self._NextToken() 
            self.vmWriter.WritePush(var_kind, var_index)
            
            self.vmWriter.WriteArithmetic(OP_ADD)
            self._CompileExpression()
            self.vmWriter.WritePop(SEG_TEMP, 0)
            self.vmWriter.WritePop(SEG_POINTER, 0)           
            self.vmWriter.WritePush(SEG_TEMP, 0)
            self.vmWriter.WritePop(SEG_THAT, 0)
       
        else:
            self._ExpectSymbol('=')
            self._NextToken()
            self._CompileExpression()
            self.vmWriter.WritePop(var_kind, var_index)
            


        self._ExpectSymbol(';')
        self._NextToken()
        

        #self._SkipStatement(';')    # TODO-10A Delete this line.

        #HINT: You will find this snippet of code helpful to handle assigning to arrays
        #
        #isArrayAssign = False
        #if self._MatchSymbol('['):
        #    isArrayAssign = True
            #TODO-11D: After computing the index, add that index to the base
            #             pointer.  Leave the result on the stack for now.
        
        #TODO-11B: After the expression is compiled above, write a pop to assign 
        #   the computed expression to given variable. Don't worry about arrays yet.
        #TODO-11D: Write VM commands to pop value into desired array location.
        #   The top value of the stack should be the value, and the value 
        #   underneath it should be a pointer to the location the value should 
        #   be stored. (See HINT above.)


        #self.vmWriter.WritePush(var_kind, var_index)
        self._WriteXmlTag('</letStatement>\n')


    def _CompileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'
        
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<doStatement>\n')

        self._ExpectKeyword(KW_DO)
        self._NextToken()

        self._CompileCall()

        #TODO-11A: Discard the return value from a void function 
        #          by popping it into temp 0.
        self.vmWriter.WritePop(SEG_TEMP, 0)
        #self.vmWriter.WriteReturn()
        self._ExpectSymbol(';')
        self._NextToken()

        self._WriteXmlTag('</doStatement>\n')


    def _CompileCall(self, firstIdentifier=None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first identifier.
            If 'firstIdentifier' is supplied, tokenizer is on the '.'
        EXIT:  Tokenizer positioned after final ';'.
        """
       
        scopeName = None
        if firstIdentifier == None:
            firstIdentifier = self._ExpectIdentifier()
            self._NextToken()
        
        sym = self._ExpectSymbol('.(')
        self._NextToken()

        if sym == '.':
            scopeName = firstIdentifier
            subroutineName = self._ExpectIdentifier()
            self._NextToken()
            
            sym = self._ExpectSymbol('(')
            self._NextToken()
        else:
            
            subroutineName = firstIdentifier

        #function_name = scopeName  + '.' + subroutineName
        argcount = 0
        callClass = scopeName
        if scopeName != None:
            
            inst_kind = self._KindToSegment(self.symbolTable.KindOfStr(firstIdentifier))
            inst_index = self.symbolTable.IndexOf(scopeName)
            self.vmWriter.WritePush(inst_kind, inst_index)
            function_name = (self.symbolTable.TypeOf(scopeName)) + '.' + scopeName
            argcount = 1
            
            
            #TODO-11C: Set callClass based on the scopeName, whether it is an
            #    object name or class name.  If object, push it for the first 
            #    implicit argument of the method, as the new "current object"
            
        else:
            #TODO-11C: we are implicitly calling a method on the current 
            #    object, so push the current object on the stack as the first argument
            function_name = firstIdentifier + '.' + subroutineName
            
        argcount += self._CompileExpressionList()

        #TODO-11A: Write the call to the function using scopeName and functionName.
        #function_name = scopeName  + '.' + subroutineName
        self.vmWriter.WriteCall(function_name, argcount)   

        self._ExpectSymbol(')')
        self._NextToken()
        

    def _CompileReturn(self):
        """
        Compiles <return-statement> :=
            'return' <expression>? ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<returnStatement>\n')

        # TODO-10A: Replace the following line with code to parse a return statement.
        self._ExpectKeyword(KW_RETURN)
        self._NextToken()
        if self._MatchSymbol(';') != ';':
            self._CompileExpression()
        # TODO-10B: Account for return values.
        else:
            self.vmWriter.WritePush(SEG_CONST, 0)
        self._NextToken()
        self.vmWriter.WriteReturn()
        # TODO-11A: In the case that no return expression was given, write the VM 
        #   command to return value 0 for void functions.
        
        # TODO-11A: Write the VM return command.

        self._WriteXmlTag('</returnStatement>\n')


    def _CompileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<ifStatement>\n')

        self._ExpectKeyword(KW_IF)
        self._NextToken()

        self._ExpectSymbol('(')
        self._NextToken()

        self._CompileExpression()

        truecase = self._GetNextLabel("IF_TRUE")
        falsecase = self._GetNextLabel("IF_FALSE")
        endif = self._GetNextLabel("IF_END")

        self.vmWriter.WriteIf(truecase)
        self.vmWriter.WriteGoto(falsecase)
        self.vmWriter.WriteLabel(truecase)

        self._ExpectSymbol(')')
        self._NextToken()

        self._ExpectSymbol('{')
        self._NextToken()

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._NextToken()


        if self._MatchKeyword(KW_ELSE):
            self.vmWriter.WriteGoto(endif)
            self.vmWriter.WriteLabel(falsecase)
            self._NextToken()

            self._ExpectSymbol('{')
            self._NextToken()

            self._CompileStatements()

            self._ExpectSymbol('}')
            self._NextToken()
            self.vmWriter.WriteLabel(endif)
        else:
            self.vmWriter.WriteLabel(falsecase)
        
        self._WriteXmlTag('</ifStatement>\n')


    def _CompileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'

        ENTRY: Tokenizer positioned on the first keyword
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<whileStatement>\n')

        condition = self._GetNextLabel("WHILE_EXP")
        end = self._GetNextLabel("WHILE_END")

        # TODO-10C: Replace the skip below with code to parse a while statement.
        # TODO-11B: Extend the function to emit VM code for a while statement.
        #self._SkipStatement('}')
        self.vmWriter.WriteLabel(condition)        
        self._ExpectKeyword(KW_WHILE)
        self._NextToken()
        self._ExpectSymbol('(')
        self._NextToken()
        self._CompileExpression()
        self._ExpectSymbol(')')
        self._NextToken()
        self.vmWriter.WriteArithmetic(OP_NOT)
        self.vmWriter.WriteIf(end)
        self._ExpectSymbol('{')
        self._NextToken()
        self._CompileStatements()
        self._ExpectSymbol('}')
        self._NextToken()     

        self.vmWriter.WriteGoto(condition)
        self.vmWriter.WriteLabel(end)
        self._WriteXmlTag('</whileStatement>\n')


    def _CompileExpression(self):
        """
        Compiles <expression> :=
            <term> (op <term>)*

        The tokenizer is expected to be positioned on the expression.
        ENTRY: Tokenizer positioned on the expression.
        EXIT:  Tokenizer positioned after the expression.
        """
        #In project 11, you may find this dictionary of VM opcodes helpful
        vm_opcodes = {'+':OP_ADD, '-':OP_SUB, '|':OP_OR, "<":OP_LT, ">":OP_GT, "=":OP_EQ, "&":OP_AND}

        self._WriteXmlTag('<expression>\n')

        # TODO-10E: Extend the following code.
        # TODO-11A: Write the operation for the VM.  Keep in mind that 
        #     multiply and divide need to be handled by calls to the 
        #     standard library, as the VM does not have those operators
        #     built-in. Use the dictionary of opcodes above.
        self._CompileTerm()
        signif = 0
        command1 = ''
        if self._MatchSymbol('+-*/&|<>='):
            if self._MatchSymbol('+'):
                command1 = OP_ADD
            elif self._MatchSymbol('-'):
                command1 = OP_SUB
            elif self._MatchSymbol('&'):
                command1 = OP_AND
            elif self._MatchSymbol('|'):
                command1 = OP_OR
            elif self._MatchSymbol('<'):
                command1 = OP_LT
            elif self._MatchSymbol('>'):
                command1 = OP_GT
            elif self._MatchSymbol('='):
                command1 = OP_EQ
            elif self._MatchSymbol('*'):
                signif = 1
            elif self._MatchSymbol('/'):
                signif = 2

            self._NextToken()
            self._CompileTerm()

            if signif == 0:
                self.vmWriter.WriteArithmetic(command1)
            elif signif == 1:
                self.vmWriter.WriteCall("Math.multiply", 2)
            elif signif ==2:
                self.vmWriter.WriteCall("Math.divide", 2)

        self._WriteXmlTag('</expression>\n')

    def _EmitStringConstantVMCode(self, stringConstant):
        """Emits VM code for the given string constant"""
        self.vmWriter.WritePush(SEG_CONST, len(stringConstant))
        self.vmWriter.WriteCall("String.new", 1)
        for char in stringConstant:
            self.vmWriter.WritePush(SEG_CONST, ord(char))
            self.vmWriter.WriteCall("String.appendChar", 2)
        return

    def _CompileTerm(self):
        """
        Compiles a <term> :=
            <int-const> | <string-const> | <keyword-const> | <var-name> |
            (<var-name> '[' <expression> ']') | <subroutine-call> |
            ( '(' <expression> ')' ) | (<unary-op> <term>)

        ENTRY: Tokenizer positioned on the term.
        EXIT:  Tokenizer positioned after the term.
        """
        self._WriteXmlTag('<term>\n')
        # TODO-10D: Extend the following to account for subroutine calls.
        # TODO-10F: Extend the following to account for array indexing.
        # TODO-10E: Extend the following to account for all other terms.
        # TODO-11A: Write the VM command below to push an integer constant onto the stack.
        # TODO-11B: Write VM commands below for the unary operations, 
        #           keyword constants, and string constants.
        #           Note the helper function _EmitStringConstantVMCode above.
        # TODO-11B: If the expression is a variable, push it onto the stack.
        #           Don't worry about array accesses yet.
        # TODO-11C: Perform an array access on the variable if needed. See pp 227-228.
        if self._MatchSymbol('-~') is not None:
            if self._MatchSymbol('~') is not None:
                self._NextToken()
                self._CompileTerm()
                self.vmWriter.WriteArithmetic(OP_NOT)
            elif self._MatchSymbol('-') is not None:
                self._NextToken()
                self._CompileTerm()
                self.vmWriter.WriteArithmetic(OP_NEG)
        elif self._MatchIntConstant() is not None:
            self.vmWriter.WritePush(SEG_CONST, self._MatchIntConstant())
            self._NextToken()
        elif self._MatchStringConstant() is not None:
            self._EmitStringConstantVMCode()
            self._NextToken()
        
        elif self._MatchKeyword(KW_TRUE) is not None:
             self.vmWriter.WritePush(SEG_CONST, 0)
             self.vmWriter.WriteArithmetic(OP_NOT)
             self._NextToken()
        elif self._MatchKeyword((KW_FALSE, KW_NULL)) is not None:
             self.vmWriter.WritePush(SEG_CONST, 0)
             self._NextToken()
        elif self._MatchKeyword(KW_THIS) is not None:
             self.vmWriter.WritePush(SEG_POINTER, 0)
             self._NextToken()

            
        elif self._MatchSymbol('(') is not None:
            self._NextToken()
            self._CompileExpression()
            self._NextToken() #deal with )
        else:
            self._ExpectIdentifier() #must be an identifier
            idenName = self._ExpectIdentifier()
            self._NextToken()
            if self._MatchSymbol('[') == '[': # is an array tbd
                self._NextToken()
                self.vmWriter.WritePush(self._KindToSegment(self.symbolTable.KindOfStr(idenName)),self.symbolTable.IndexOf(idenName));
                self._CompileExpression()
                self._NextToken() # deals with ]
                self.vmWriter.WriteArithmetic(OP_ADD)
                self.vmWriter.WritePop(SEG_POINTER, 1)
                self.vmWriter.WritePush(SEG_THAT, 0)
            elif self._MatchSymbol('.') == '.': # us a subroutine call
                self._CompileCall(idenName)
            else:
                self.vmWriter.WritePush(self._KindToSegment(self.symbolTable.KindOf(idenName)),self.symbolTable.IndexOf(idenName))   
         
                
        self._WriteXmlTag('</term>\n')

    def _CompileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        Returns number of expressions compiled.

        ENTRY: Tokenizer positioned on the first expression.
        EXIT:  Tokenizer positioned after the last expression.
        """
        self._WriteXmlTag('<expressionList>\n')

        count = 0
        while True:
            if self._MatchSymbol(')'):
                break
            self._CompileExpression()
            count += 1

            if not self._MatchSymbol(','):
                break
            self._NextToken()
        
        self._WriteXmlTag('</expressionList>\n')
        return count

    def _MatchKeyword(self, keywords):
        """
        Check whether the next token matches one of 'keywords'.
        'keywords' may be a keywordID or a list or tuple of keywordIDs.
        If one of the keywords is matched, returns the matched keyword.
        If next token is not a keyword matching one of the requested keywords, returns None.
        """
        if type(keywords) == list:
            keywords = tuple(keywords)
        elif type(keywords) != tuple:
            keywords = (keywords,)
        if not self.tokenizer.TokenType() == TK_KEYWORD:
            return None
        if self.tokenizer.Keyword() in keywords:
            return self.tokenizer.Keyword()
        return None


    def _ExpectKeyword(self, keywords):
        """
        Parse the next token.  It is expected to be one of 'keywords'.
        'keywords' may be a keywordID or a list or tuple of keywordIDs.

        If an expected keyword is parsed, returns the keyword.
        Otherwise raises an error.
        """
        match = self._MatchKeyword(keywords)
        if not match:
            self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                             self.tokenizer.TokenTypeStr())
        else:
            return match

    def _ExpectIdentifier(self):
        """
        Parse the next token.  It is expected to be an identifier.

        Returns the identifier parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_IDENTIFIER:
            self._RaiseError('Expected <identifier>, got '+
                             self.tokenizer.TokenTypeStr())
        return self.tokenizer.Identifier()
        
    def _MatchSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        If an expected symbol is parsed, returns the symbol.
        If no such symbol is parsed, returns None.
        """
        if not self.tokenizer.TokenType() == TK_SYMBOL or self.tokenizer.Symbol() not in symbols:
            return None
        else:
            return self.tokenizer.Symbol()

    def _ExpectSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        If an expected symbol is parsed, returns the symbol.
        Otherwise raises an error.
        """
        sym = self._MatchSymbol(symbols)
        if not sym:
            if not self.tokenizer.TokenType() == TK_SYMBOL:
                self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                                 self.tokenizer.TokenTypeStr())
            else:
                self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                                 self._SymbolStr(self.tokenizer.Symbol()))
        return sym

    def _MatchIntConstant(self):
        """
        Parse the next token.  It is expected to be of type TK_INT_CONST

        If an expected token is matched, returns the integer constant.
        If no such token is parsed, returns None.
        """
        if self.tokenizer.TokenType() == TK_INT_CONST:
            return self.tokenizer.IntVal()
        return None

    def _MatchStringConstant(self):
        """
        Parse the next token.  It is expected to be TK_STRING_CONST.

        If the string constant if present, or None.
        """
        if self.tokenizer.TokenType() == TK_STRING_CONST:
            return self.tokenizer.StringVal()
        return None

    def _RaiseError(self, error):
        message = '%s line %d:\n  %s\n  %s' % (
                  self.inputFileName, self.tokenizer.LineNumber(),
                  self.tokenizer.LineStr(), error)
        raise HjcError(message)
        

    def _KeywordStr(self, keywords):
        if type(keywords) != tuple:
            return '"' + self.tokenizer.KeywordStr(keywords) + '"'
        ret = ''
        for kw in keywords:
            if len(ret):
                ret += ', '
            ret += '"' + self.tokenizer.KeywordStr(kw) + '"'
        if len(keywords) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _SymbolStr(self, symbols):
        if type(symbols) != tuple:
            return '"' + symbols + '"'
        ret = ''
        for symbol in symbols:
            if len(ret):
                ret += ', '
            ret += '"' + symbol + '"'
        if len(symbols) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _NextToken(self, emitXML=True):
        if emitXML:
            self._WriteTokenXML()
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')

    def _ConsumeToken(self):
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')

    def _WriteXmlTag(self, tag):
        if xml:
            if tag[1] == '/':
                self.xmlIndent -= 1
            self.xmlOutputFile.Write('  ' * self.xmlIndent)
            self.xmlOutputFile.Write(tag)
            if '/' not in tag:
                self.xmlIndent += 1
    
    def _WriteXml(self, tag, value):
        if xml:
            self.xmlOutputFile.Write('  ' * self.xmlIndent)
            self.xmlOutputFile.WriteXml(tag, value)

    def _SkipStatement(self, end_symbol):
         """
         Consumes tokens unparsed until the specified end symbol is seen.
         Used as a placeholder for actually parsing the statements.
         """
         while not self._ExpectSymbol(end_symbol):
             self._NextToken();
         self._NextToken();

    def _WriteTokenXML(self):
         """
         Writes out whatever the next token is to the output file, regardless of type or content.
         """
         tokenType = self.tokenizer.TokenType()
         if tokenType == TK_SYMBOL:
             self._WriteXml('symbol', self.tokenizer.Symbol())
         elif tokenType == TK_KEYWORD:
             self._WriteXml('keyword', self.tokenizer.KeywordStr())
         elif tokenType == TK_IDENTIFIER:
             self._WriteXml('identifier', self.tokenizer.Identifier())
         elif tokenType == TK_INT_CONST:
             self._WriteXml('integerConstant', str(self.tokenizer.IntVal()))
         elif tokenType == TK_STRING_CONST:
             self._WriteXml('stringConstant', self.tokenizer.StringVal())

    def _DefineSymbol(self, name, type, kind):
        """
        Adds a new symbol to the symbol table.
        """
        self.symbolTable.Define(name, type, kind)

    def _KindToSegment(self, kind):
        """
        Converts symbol table "kinds" to segment numbers for the VmWriter.
        """
        return (SEG_STATIC, SEG_THIS, SEG_ARG, SEG_LOCAL)[kind]

    def _WriteSymbolTableEntry(self, name, assign=False):
        """
        Writes an XML tag for a symbol table entry.
        """
        type = self.symbolTable.TypeOf(name)
        kind = self.symbolTable.KindOfStr(name)
        index = self.symbolTable.IndexOf(name)
        self._WriteXmlTag('<tableEntry type="%s" kind="%s" index="%s" assign="%s">\n' % (type, kind, index, assign))
