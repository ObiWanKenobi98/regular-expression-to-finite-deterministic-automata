#!/usr/bin/env python
import sys
import pickle

import dfa
import regular_expression
import nfa as Nfa
import parse


if __name__ == "__main__":
    valid = (len(sys.argv) == 4 and sys.argv[1] in ["RAW", "TDA"]) or \
            (len(sys.argv) == 3 and sys.argv[1] == "PARSE")
    if not valid:
        sys.stderr.write(
            "Usage:\n"
            "\tpython3 main.py RAW <regex-str> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py TDA <tda-file> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py PARSE <regex-str>\n"
        )
        sys.exit(1)

    if sys.argv[1] == "TDA":
        tda_file = sys.argv[2]
        with open(tda_file, "rb") as fin:
            parsed_regex = pickle.loads(fin.read())
    else:
        regex_string = sys.argv[2]
        parsed_regex = parse.parse(regex_string)
        if sys.argv[1] == "PARSE":
            print(str(parsed_regex))
            sys.exit(0)
    regular_expression = regular_expression.regex_to_regular_expression(parsed_regex)
    nfa = Nfa.re_to_nfa(regular_expression)
    dfa = dfa.nfa_to_dfa(nfa)

    """print(dfa.alphabet)
    print(dfa.start_state)
    print(dfa.states)
    print(dfa.final_states)
    print(dfa.delta)"""

    with open(sys.argv[3], "r") as fin:
        content = fin.readlines()

    for word in content:
        newword = list(word)
        crt = dfa.start_state
        ok = False
        for c in newword:
            if c != '\n':
                crt = dfa.delta.get((crt, c))
                if crt == None:
                    print("False")
                    ok = True
                    break
        if ok == False:
            if crt in dfa.final_states:
                print("True")
            else:
                print("False")