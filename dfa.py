#!/usr/bin/env python
try:
    from graphviz import Digraph
except ImportError:
    pass

import queue as Queue

import nfa


class DFA(object):
    """Model a Nondeterministic Finite Automaton

    The automaton contains the following:

        - "alphabet": a set of symbols
        - "states": set of non-negative integers
        - "start_state": a member of "states"
        - "final_states": a subset of "states"
        - "delta": a dictionary from configurations to states
                {(state, symbol): state}
                where "state" is a member of "states" and "symbol" is a member
                of "alphabet"

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
        self.sink_state = None

    def to_graphviz(self):
        def get_edges(delta):
            edges = {}
            for (prev_state, symbol), next_state in delta.items():
                edge = (prev_state, next_state)
                if edge not in edges:
                    edges[edge] = set()

                edges[edge].add(symbol)

            return edges

        def collate_symbols(edge_symbols):
            collated = []
            i = 0
            edge_symbols = sorted(edge_symbols)
            while i < len(edge_symbols):
                range_start = i
                while i + 1 < len(edge_symbols) and \
                      ord(edge_symbols[i + 1]) == ord(edge_symbols[i]) + 1:
                    i += 1

                dist = i - range_start
                if dist >= 2:
                    label = "{}-{}".format(edge_symbols[range_start],
                                           edge_symbols[i])
                    collated.append(label)
                else:
                    collated.append(str(edge_symbols[range_start]))
                    if dist == 1:
                        collated.append(str(edge_symbols[range_start + 1]))
                        i += 1

                i += 1

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


def get_epsilon_closure(nfa, state):
    epsilon_closure = set()
    queue = Queue.Queue(maxsize=0)
    next_states = nfa.delta.get((state, '&'))
    if next_states == None:
        epsilon_closure.add(state)
        return epsilon_closure
    for x in next_states:
        queue.put(x)
    while not queue.empty():
        crt_state = queue.get()
        if crt_state in epsilon_closure:
            continue
        epsilon_closure.add(crt_state)
        if nfa.delta.get((crt_state, '&')) == None:
            continue
        for x in nfa.delta.get((crt_state, '&')):
            if x not in epsilon_closure:
                queue.put(x)
    epsilon_closure.add(state)
    return epsilon_closure


def nfa_to_dfa(nfa):

    """print(nfa.alphabet)
    print(nfa.start_state)
    print(nfa.states)
    print(nfa.final_states)
    print(nfa.delta)"""

    dfa_alphabet = ""
    for c in nfa.alphabet:
        if c != '&':
            dfa_alphabet = dfa_alphabet + c

    dfa_states = set()
    dfa_start_state = frozenset(get_epsilon_closure(nfa, nfa.start_state))
    dfa_states.add(dfa_start_state)
    dfa_final_states = set()
    dfa_delta = {}
    queue = Queue.Queue(maxsize=0)
    queue.put(get_epsilon_closure(nfa, nfa.start_state))
    while not queue.empty():
        crt = queue.get()
        for symbol in dfa_alphabet:
            next_state = set()
            for state in crt:
                if (state, symbol) in nfa.delta:
                    new_states = nfa.delta.get((state, symbol))
                    for x in new_states:
                        next_state.update(get_epsilon_closure(nfa, x))
            if not next_state == set():
                dfa_delta.update({(frozenset(crt), symbol): frozenset(next_state)})
                if not next_state in dfa_states:
                    queue.put(next_state)
                dfa_states.add(frozenset(next_state))
    for f_state in nfa.final_states:
        for state in dfa_states:
            if f_state in state:
                dfa_final_states.add(state)
    return DFA(dfa_alphabet, dfa_states, dfa_start_state, dfa_final_states, dfa_delta)