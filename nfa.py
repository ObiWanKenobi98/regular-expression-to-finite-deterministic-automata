#!/usr/bin/env python
try:
    from graphviz import Digraph
except ImportError:
    pass

import regular_expression


class NFA(object):
    """Model a Nondeterministic Finite Automaton

    The automaton contains the following:

        - "alphabet": a set of symbols
        - "states": set of non-negative integers
        - "start_state": a member of "states"
        - "final_states": a subset of "states"
        - "delta": a dictionary from configurations to a set of states
                {(state, word): next_states}
            where a "configuration" is a tuple consisting of a member of
            "states" and a list of 0 or more symbols from "alphabet" and
            "next_states" is a subset of "states"

    """
    def __init__(self, alphabet, states, start_state, final_states, delta):
        """See class docstring"""
        assert start_state in states
        assert final_states.issubset(states)
        for symbol in "()*|":
            assert symbol not in alphabet

        self.alphabet = alphabet
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.delta = delta

    def to_graphviz(self):
        def get_edges(delta):
            edges = {}
            for (prev_state, word), next_states in delta.items():
                for next_state in next_states:
                    edge = (prev_state, next_state)
                    if edge not in edges:
                        edges[edge] = set()

                    edges[edge].add(word)

            return edges

        def collate_symbols(edge_words):
            collated = []
            i = 0
            edge_words = sorted(edge_words)
            if len(edge_words[0]) == 0:  # contains empty string
                collated.insert(0, "&")
                edge_words = edge_words[1:]

            while i < len(edge_words) and len(edge_words[i]) == 1:
                range_start = i
                while i + 1 < len(edge_words) and \
                      len(edge_words[i + 1]) == 1 and \
                      ord(edge_words[i + 1]) == ord(edge_words[i]) + 1:
                    i += 1

                dist = i - range_start
                if dist >= 2:
                    label = "{}-{}".format(edge_words[range_start],
                                           edge_words[i])
                    collated.append(label)
                else:
                    collated.append(str(edge_words[range_start]))
                    if dist == 1:
                        collated.append(str(edge_words[range_start + 1]))
                        i += 1

                i += 1

            collated += [word for word in edge_words if len(word) > 1]
            return ",".join(collated)

        dot = Digraph()
        dot.graph_attr["rankdir"] = "LR"

        # This is here to nicely mark the starting state.
        dot.node("_", shape="point")
        dot.edge("_", str(self.start_state))

        for state in self.states:
            shape = "doublecircle" if state in self.final_states else "circle"
            dot.node(str(state), shape=shape)

        edges = get_edges(self.delta)

        edges = {k: collate_symbols(v) for k, v in edges.items()}
        for (prev_state, next_state), label in edges.items():
            dot.edge(str(prev_state), str(next_state), label=label)

        return dot


def rename_states(target, reference):
    off = max(reference.states) + 1
    target.start_state += off
    target.states = set(map(lambda s: s + off, target.states))
    target.final_states = set(map(lambda s: s + off, target.final_states))
    new_delta = {}
    for (state, symbol), next_states in target.delta.items():
        new_next_states = set(map(lambda s: s + off, next_states))
        new_delta[(state + off, symbol)] = new_next_states

    target.delta = new_delta

def new_states(*nfas):
    state = 0
    for nfa in nfas:
        m = max(nfa.states)
        if m >= state:
            state = m + 1

    return state, state + 1

def re_to_nfa(re):
    if (re.type == regular_expression.EMPTY_SET):
        alphabet = ""
        states = {0, 1}
        start_state = 0
        final_states = {1}
        delta = {}
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
    if (re.type == regular_expression.EMPTY_STRING):
        alphabet = "&"
        states = {0, 1}
        start_state = 0
        final_states = {1}
        delta = {(0, "&"): {1}}
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
    if (re.type == regular_expression.SYMBOL):
        alphabet = re.symbol + ""
        states = {0, 1}
        start_state = 0
        final_states = {1}
        delta = {(0, re.symbol): {1}}
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
    if (re.type == regular_expression.STAR):
        nfa = re_to_nfa(re.lhs)
        alphabet = "&"
        new = set(alphabet)
        new = new.union(set(nfa.alphabet))
        alphabet = ''.join(new)
        newstate1, newstate2 = new_states(nfa)
        states = {newstate1, newstate2}
        states = states.union(nfa.states)
        start_state = newstate1
        final_states = {newstate2}
        delta = nfa.delta
        delta.update({(newstate1, "&"): {nfa.start_state, newstate2}})
        for final_state in nfa.final_states:
            delta.update({(final_state, "&"): {newstate2, nfa.start_state}})
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
    if (re.type == regular_expression.CONCATENATION):
        nfa1 = re_to_nfa(re.lhs)
        nfa2 = re_to_nfa(re.rhs)
        rename_states(nfa1, nfa2)
        alphabet = "&"
        new = set(alphabet)
        new = new.union(set(nfa1.alphabet))
        new = new.union(set(nfa2.alphabet))
        alphabet = ''.join(new)
        newstate1, newstate2 = new_states(nfa1, nfa2)
        states = {newstate1, newstate2}
        states = states.union(nfa1.states)
        states = states.union(nfa2.states)
        start_state = newstate1
        final_states = {newstate2}
        delta = nfa1.delta
        delta.update(nfa2.delta)
        delta.update({(newstate1, "&"): {nfa1.start_state}})
        for final_state in nfa1.final_states:
            delta.update({(final_state, "&"): {nfa2.start_state}})
        for final_state in nfa2.final_states:
            delta.update({(final_state, "&"): {newstate2}})
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
    if (re.type == regular_expression.ALTERNATION):
        nfa1 = re_to_nfa(re.lhs)
        nfa2 = re_to_nfa(re.rhs)
        rename_states(nfa1, nfa2)
        alphabet = "&"
        new = set(alphabet)
        new = new.union(set(nfa1.alphabet))
        new = new.union(set(nfa2.alphabet))
        alphabet = ''.join(new)
        newstate1, newstate2 = new_states(nfa1, nfa2)
        states = {newstate1, newstate2}
        states = states.union(nfa1.states)
        states = states.union(nfa2.states)
        start_state = newstate1
        final_states = {newstate2}
        delta = nfa1.delta
        delta.update(nfa2.delta)
        delta.update({(newstate1, "&"): {nfa1.start_state, nfa2.start_state}})
        for final_state in nfa1.final_states:
            delta.update({(final_state, "&"): {newstate2}})
        for final_state in nfa2.final_states:
            delta.update({(final_state, "&"): {newstate2}})
        nfa = NFA(alphabet, states, start_state, final_states, delta)
        return nfa
