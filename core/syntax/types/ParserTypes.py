from syntax.tokens.ParserTokens import ParserToken as PToken

class ParserTypes:
    
    def Command(self, cmd_name, params):
        return PToken("COMMAND", cmd_name, params)
    
    def GlobalFlagAssignment(self, global_flag_name, params):
        return PToken("GF_ASSIGN", global_flag_name, params)

    def GlobalFlagLookup(self, global_flag_name):
        return PToken("GF_LOOKUP", global_flag_name)
    
    def VariableAssignment(self, variable_name, params):
        return PToken("VAR_ASSIGN", variable_name, params)

    def VariableLookup(self, variable_name):
        return PToken("VAR_LOOKUP", variable_name)
    
    def MacroAssignment(self, macro_name, params):
        return PToken("MAC_ASSIGN", macro_name, params)
        
    def MacroLookup(self, macro_name):
        return PToken("MAC_LOOKUP", macro_name)
    
    def funcCall(self, func_name, params):
        return PToken("FUN_CALL", func_name, params)
    
    

