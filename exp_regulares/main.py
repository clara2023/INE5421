
class RexEx:
    def __init__(self, regex):
        self.regex = regex
        self.operators = ['*', '|', '(', ')', '.']
        #self.add_concat_op()    

    def get_regex(self):
        print(self.regex) 

class SyntaxTree:
    def __init__(self, regex):
        self.root = None
        self.alphabet = []
        self.leaves = []
        self.operators = ['|', '*', '(', ')']
        self.build_tree(regex)
        self.followpos_map = {}

    def build_tree(self, regex):

        new_regex, stack = self.tokenize(regex)
        self.leaves = stack
        t = self.parse_regex(new_regex)

        final = Node('#')
        self.leaves.append(final)
        concat = Node('.')
        concat.right = final
        final.root = concat
        final.leaf = len(self.leaves)
        final.firstpos.add(final.leaf)
        final.lastpos.add(final.leaf)
        concat.left = self.parse_regex(new_regex)

        self.root = concat

    def print_positions(self, root):
        if root is None:
            return
        print("Node:", root.value)
        print("FirstPos:", root.firstpos)
        print("LastPos:", root.lastpos)
        self.print_positions(root.left)
        self.print_positions(root.right)

    def tokenize(self, regex):
        non_concat_r = ['|', '(']
        non_concat_l = ['|', '*', ')']
        new_regex = []
        prev_char = '|'
        stack = []

        for char in regex:
            c1 = char in self.operators
            c2 = char in self.alphabet
            c3 = char in non_concat_l
            c4 = prev_char in non_concat_r
            if not c3 and not c4:
                new_regex.append('.')
            new_regex.append(char)
            if not c1:
                leaf = Node(char)
                stack.append(leaf)
                leaf.leaf = len(stack)
                leaf.firstpos.add(leaf.leaf)
                leaf.lastpos.add(leaf.leaf)
                if char == '&':
                    leaf.nullable = True
                    leaf.firstpos = set()
                    leaf.lastpos = set()
                    stack.pop()
                elif not c2:
                    self.alphabet.append(char)
                new_regex[-1] = leaf
            prev_char = char
        return new_regex, stack


    def calculate_positions(self, root):
        
        # calculate firstpos, lastpos, followpos
        self.calculate_firstpos(root)
        self.calculate_lastpos(root)
        followpos_map = {position: set() for position in range(1, 100)} 
        self.calculate_followpos(root, followpos_map)
        self.format_followpos(followpos_map)

        self.followpos_map = followpos_map

    def format_followpos(self, followpos_map):
        # sets size of followpos_map to the number of leaves
        followpos_map = {position: followpos_map[position] for position in range(1, len(self.leaves) + 1)}
        #print(followpos_map)

    def calculate_firstpos(self, root):
        if root is None:
            return

        if root.leaf:
            root.firstpos.add(root.leaf)

        self.calculate_firstpos(root.left)
        self.calculate_firstpos(root.right)

        if root.value == '|':
            root.firstpos = root.left.firstpos.copy().union(root.right.firstpos.copy())
        elif root.value == '*':
            root.firstpos = root.left.firstpos.copy()
        elif root.value == '.':
            if root.left.nullable:
                root.firstpos = root.left.firstpos.copy().union(root.right.firstpos.copy())
            else:
                root.firstpos = root.left.firstpos.copy()

    def calculate_lastpos(self, root):
        if root is None:
            return

        if root.leaf:
            root.lastpos.add(root.leaf)

        self.calculate_lastpos(root.left)
        self.calculate_lastpos(root.right)

        if root.value == '|':
            root.lastpos = root.left.lastpos.union(root.right.lastpos.copy())
        elif root.value == '*':
            root.lastpos = root.left.lastpos.copy()
        elif root.value == '.':
            if root.right.nullable:
                root.lastpos = root.left.lastpos.union(root.right.lastpos.copy())
            else:
                root.lastpos = root.right.lastpos.copy()

    def calculate_followpos(self, root, followpos_map):
        if root is None:
            return

        # if root is a concatenation operator (root = c1 . c2)
        # for each position in lastpos(c1), add firstpos(c2) to followpos_map[position]
        if root.value == '.':
            for position in root.left.lastpos:
                followpos_map[position].update(root.right.firstpos)
        
        # if root is a kleene star operator (root = c*)
        # for each position in lastpos(c), add firstpos(c) to followpos_map[position]
        elif root.value == '*':
            for position in root.lastpos:
                followpos_map[position].update(root.firstpos)

        self.calculate_followpos(root.left, followpos_map)
        self.calculate_followpos(root.right, followpos_map)

    def parse_regex(self, regex):
        nodes = []
        i = 0
        while i < len(regex):
            new_node = regex[i]
            if type(new_node) == Node:
                nodes.append(new_node)
            elif new_node == '(':
                j = i + 1
                count = 1
                while count > 0:
                    if regex[j] == '(':
                        count += 1
                    elif regex[j] == ')':
                        count -= 1
                    j += 1
                sub_regex = regex[i+1:j-1]
                sub_nodes = self.parse_regex(sub_regex)
                nodes.append(sub_nodes)
                i = j - 1
            elif new_node == '*':
                prev = nodes[-1]
                node = Node(new_node)
                node.left = prev
                node.nullable = True
                prev.pai = node
                nodes[-1] = node
            else:
                nodes.append(Node(new_node))
            i += 1
        i = 1
        while i + 1 < len(nodes):
            node = nodes[i]
            if node.value == '.':
                node.left = nodes[i-1]
                node.right = nodes[i+1]
                nodes[i-1] = node
                node.left.pai = node
                node.right.pai = node
                node.nullable = node.left.nullable and node.right.nullable
                nodes.pop(i)
                nodes.pop(i)
            else:
                i += 1
        i = 1
        while i + 1 < len(nodes):
            node = nodes[i]
            if node.value == '|':
                node.left = nodes[i-1]
                node.right = nodes[i+1]
                nodes[i-1] = node
                node.left.pai = node
                node.right.pai = node
                node.nullable = node.left.nullable or node.right.nullable
                nodes.pop(i)
                nodes.pop(i)
            else:
                i += 1

        return nodes[-1]

    def build_dfa(self):
        # initial state is the firstpos of the root node
        dfa = DFA()
        dfa.initial_state = self.root.firstpos

        # add initial state to the list of states
        dfa.states.append(self.root.firstpos)

        dfa.alphabet = self.alphabet

        # finds the correspondance between the followpos map keys and the values for the nodes
        # in the syntax tree
        symbol_map = {}
        for i, node in enumerate(self.leaves):
            symbol_map[node.leaf] = node.value        
        state_pile = [self.root.firstpos]
        while state_pile:
            state = state_pile.pop()
            for symbol in self.alphabet:
                new_state = set()
                for position in state:
                    if symbol_map[position] == symbol:
                        new_state.update(self.followpos_map[position])
                if new_state not in dfa.states:
                    dfa.states.append(new_state)
                    state_pile.append(new_state)
                if len(new_state) != 0:
                    dfa.transitions.append((state, symbol, new_state))
                # if new state contains the last index in dictionary, it is a final state
                if len(new_state.intersection(self.leaves[-1].lastpos)) > 0:
                    dfa.final_states.append(new_state)

                # also for state
                if len(state.intersection(self.leaves[-1].lastpos)) > 0:
                    dfa.final_states.append(state)

        # removes duplicates from transitions
        new_transitions = []
        for transition in dfa.transitions:
            if transition not in new_transitions:
                new_transitions.append(transition)
        dfa.transitions = new_transitions

        # removes duplicates from states
        new_states = []
        for state in dfa.states:
            if state not in new_states and len(state) != 0:
                new_states.append(state)
        dfa.states = new_states

        dfa.n_states = len(dfa.states)

        # removes duplicates from final states
        new_final_states = []
        for final_state in dfa.final_states:
            if final_state not in new_final_states and len(final_state) != 0:
                new_final_states.append(final_state)
        dfa.final_states = new_final_states

        dfa.get_output()

    def print_tree(self, node, indent=0):
        if node is None:
            return
        self.print_tree(node.right, indent + 1)
        print('    ' * indent + str(node.value))
        self.print_tree(node.left, indent + 1)   

class Node:
    def __init__(self, value):
        self.value = value
        self.root = None
        self.left = None
        self.right = None
        self.leaf = None
        self.firstpos = set()
        self.lastpos = set()
        self.nullable = False
        
class DFA:
    def __init__ (self):
        self.n_states = 0
        self.initial_state = ''
        self.final_states = []
        self.alphabet = []
        self.transitions = []
        self.states = []

    def get_automata(self):
        print('Number of states: ', self.n_states)
        print('Initial state: ', self.initial_state)
        print('Final states: ', self.final_states)
        print('Alphabeth: ', self.alphabet)
        print('Transitions: ', self.transitions)
        print('States: ', self.states)

    def format_for_output(self):
        # format transitions to match output format 
        for i, transition in enumerate(self.transitions):
            self.transitions[i] = '{' + ','.join(str(state) for state in transition[0]) + '},' + transition[1] + ',{' + ','.join(str(state) for state in transition[2]) + '}'

        #self.get_automata()
        # order alphabetically


        for i, state in enumerate(self.states):
            self.states[i] = sorted(state)
        self.states = sorted(self.states)
        

        for i, final_state in enumerate(self.final_states):
            self.final_states[i] = sorted(final_state)

        self.final_states = sorted(self.final_states)
        self.final_states = str(self.final_states).replace('[', '{').replace(']', '}').replace('\'', '')

        # removes unnecessary spaces in final states
        self.final_states = self.final_states.replace(' ', '')

        # remove unnecessary spaces in initial state
        self.initial_state = str(self.initial_state).replace(' ', '')

        # order alphabet
        self.alphabet = sorted(self.alphabet)

    def get_output(self):
        
        self.format_for_output()
        
        output = str(self.n_states) + ';' + str(self.initial_state) + ';' + self.final_states + ';{' + ','.join(self.alphabet) + '};'  + ';'.join(transition for transition in self.transitions)
        print(output)


def main():
    regex = input().strip()
    rex = RexEx(regex)
    tree = SyntaxTree(rex.regex)
    tree.calculate_positions(tree.root)
    tree.build_dfa()

if __name__ == "__main__":
    main()
