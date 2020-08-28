#!/usr/bin/env python

import regex as Regex

EMPTY_SET = 0
EMPTY_STRING = 1
SYMBOL = 2
STAR = 3
CONCATENATION = 4
ALTERNATION = 5

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

_SIMPLE_TYPES = {EMPTY_SET, EMPTY_STRING, SYMBOL}


def str_paranthesize(parent_type, re):
    if parent_type > re.type or parent_type == re.type and parent_type != STAR:
        return str(re)
    else:
        return "({!s})".format(str(re))


class RegularExpression(object):
    """Model a Regular Expression TDA

    The member "type" is always available, indicating the type of the
    RegularExpression. Its value dictates which other members (if any) are
    defined:

        - EMPTY_SET:
        - EMPTY_STRING:
        - SYMBOL: "symbol" is the symbol
        - STAR: "lhs" is the RegularExpression
        - CONCATENATION: "lhs" and "rhs" are the RegularExpressions
        - ALTERNATION: "lhs" and "rhs" are the RegularExpressions

    """
    def __init__(self, type, obj1=None, obj2=None):
        """Create a Regular Expression

        The value of the "type" parameter influences the interpretation of the
        other two paramters:

            - EMPTY_SET: obj1 and obj2 are unused
            - EMPTY_STRING: obj1 and obj2 are unused
            - SYMBOL: obj1 should be a symbol; obj2 is unused
            - STAR: obj1 should be a RegularExpression; obj2 is unused
            - CONCATENATION: obj1 and obj2 should be RegularExpressions
            - ALTERNATION: obj1 and obj2 should be RegularExpressions

        """
        self.type = type
        if type in _SIMPLE_TYPES:
            if type == SYMBOL:
                assert obj1 is not None
                self.symbol = obj1
        else:
            assert isinstance(obj1, RegularExpression)
            self.lhs = obj1
            if type == CONCATENATION or type == ALTERNATION:
                assert isinstance(obj2, RegularExpression)
                self.rhs = obj2

    def __str__(self):
        if self.type == EMPTY_SET:
            return ""
        elif self.type == EMPTY_STRING:
            return "&"
        elif self.type == SYMBOL:
            return str(self.symbol)
        elif self.type == CONCATENATION:
            slhs = str_paranthesize(self.type, self.lhs)
            srhs = str_paranthesize(self.type, self.rhs)
            return slhs + srhs
        elif self.type == ALTERNATION:
            slhs = str_paranthesize(self.type, self.lhs)
            srhs = str_paranthesize(self.type, self.rhs)
            return slhs + "|" + srhs
        elif self.type == STAR:
            slhs = str_paranthesize(self.type, self.lhs)
            return slhs + "*"
        else:
            return ""

    def __mul__(self, rhs):
        """Concatenation"""
        if isinstance(rhs, str) and len(rhs) == 1:
            rhs = RegularExpression(SYMBOL, rhs)

        assert isinstance(rhs, RegularExpression)
        return RegularExpression(CONCATENATION, self, rhs)

    __rmul__ = __mul__

    def __or__(self, rhs):
        """Alteration"""
        if isinstance(rhs, str) and len(rhs) == 1:
            rhs = RegularExpression(SYMBOL, rhs)

        assert isinstance(rhs, RegularExpression)
        return RegularExpression(ALTERNATION, self, rhs)

    __ror__ = __or__

    def star(self):
        return RegularExpression(STAR, self)


def regex_to_regular_expression(regex):
    if(regex.type == Regex.EMPTY_STRING):
        regular_expression = RegularExpression(EMPTY_STRING)
        return regular_expression
    if(regex.type == Regex.SYMBOL_SIMPLE):
        regular_expression = RegularExpression(SYMBOL, regex.symbol)
        return regular_expression
    if(regex.type == Regex.SYMBOL_ANY):
        #empty??
        regular_expression = RegularExpression(EMPTY_STRING)
        for c in ALPHABET:
            regular_expression = RegularExpression(ALTERNATION, regular_expression, RegularExpression(SYMBOL, c))
        return regular_expression
    if(regex.type == Regex.SYMBOL_SET):
        # empty??
        regular_expression = RegularExpression(EMPTY_STRING)
        for x in regex.symbol_set:
            if isinstance(x, tuple):
                a, b = x
                a = ord(a)
                b = ord(b)
                while a <= b:
                    regular_expression = RegularExpression(ALTERNATION, regular_expression, RegularExpression(SYMBOL, str(chr(a))))
                    a = a + 1
            else:
                regular_expression = RegularExpression(ALTERNATION, regular_expression, RegularExpression(SYMBOL, x))
        return  regular_expression
    if(regex.type == Regex.MAYBE):
        regular_expression = RegularExpression(EMPTY_STRING)
        regular_expression = RegularExpression(ALTERNATION, regular_expression, regex_to_regular_expression(regex.lhs))
        return regular_expression
    if(regex.type == Regex.STAR):
        regular_expression = RegularExpression(STAR, regex_to_regular_expression(regex.lhs))
        return regular_expression
    if(regex.type == Regex.PLUS):
        regular_expression = regex_to_regular_expression(regex.lhs)
        regular_expression = RegularExpression(CONCATENATION, regular_expression, RegularExpression(STAR, regex_to_regular_expression(regex.lhs)))
        return regular_expression
    if(regex.type == Regex.RANGE):
        x, y = regex.range
        if x == -1:
            regular_expression = RegularExpression(EMPTY_STRING)
            temp = RegularExpression(EMPTY_STRING)
            for i in range(1, y + 1):
                temp = RegularExpression(CONCATENATION, temp, regex_to_regular_expression(regex.lhs))
                regular_expression = RegularExpression(ALTERNATION, regular_expression, temp)
            return regular_expression
        if y == -1:
            temp = RegularExpression(EMPTY_STRING)
            for i in range(1, x + 1):
                temp = RegularExpression(CONCATENATION, temp, regex_to_regular_expression(regex.lhs))
            regular_expression = RegularExpression(CONCATENATION, temp, RegularExpression(STAR, regex_to_regular_expression(regex.lhs)))
            return regular_expression
        temp = RegularExpression(EMPTY_STRING)
        for i in range(1, x + 1):
            temp = RegularExpression(CONCATENATION, temp, regex_to_regular_expression(regex.lhs))
        regular_expression = temp
        for i in range(x + 1, y + 1):
            temp = RegularExpression(CONCATENATION, temp, regex_to_regular_expression(regex.lhs))
            regular_expression = RegularExpression(ALTERNATION, regular_expression, temp)
        return regular_expression
    if(regex.type == Regex.CONCATENATION):
        regular_expression = RegularExpression(CONCATENATION, regex_to_regular_expression(regex.lhs), regex_to_regular_expression(regex.rhs))
        return regular_expression
    if(regex.type == Regex.ALTERNATION):
        regular_expression = RegularExpression(ALTERNATION, regex_to_regular_expression(regex.lhs), regex_to_regular_expression(regex.rhs))
        return regular_expression