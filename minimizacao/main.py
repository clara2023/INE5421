import sys

class NDFA:
    def __init__ (self, input):
        self.n_states = int(input[0])
        self.initial_state = input[1]
        self.final_states = input[2]
        self.alphabeth = input[3]
        self.transitions = self.create_transitions(input[4:])
        self.states = self.create_states()
    
    def create_transitions(self, input):
        transitions = []
        for transition in input:
            new_transition = transition.split(',')
            transitions.append(new_transition)
        return transitions

    def create_states(self):
        states = []
        for transition in self.transitions:
            if transition[0] not in states:
                states.append(transition[0])
            if transition[2] not in states:
                states.append(transition[2])
        return states

    def get_automata(self):
        print('Number of states: ', self.n_states)
        print('Initial state: ', self.initial_state)
        print('Final states: ', self.final_states)
        print('Alphabeth: ', self.alphabeth)
        print('Transitions: ', self.transitions)
        print('States: ', self.states)
    
    def minimization(self):

        reachable_states = self.reachable_states()
        reachable_from_dead = self.dead_states(reachable_states)
        self.equivalent_states(reachable_from_dead)
    
    def reachable_states(self):

        reachable_states = []

        # from initial state, find all reachable states
        transitions_copy = self.transitions.copy()
        state_pile = [self.initial_state]
        
        while state_pile:
            current_state = state_pile.pop()
            reachable_states.append(current_state)
            for transition in transitions_copy:
                if transition[0] == current_state:
                    if transition[2] not in reachable_states:
                        state_pile = [transition[2]] + state_pile
                        reachable_states.append(transition[2])
                        
        # removes duplicate states
        reachable_states = list(set(reachable_states))
        return reachable_states

    def dead_states(self, reachable_states):
        # from final states, find states that are not reachable
        
        reachable_from_dead_states = []
        
        #creates state list with final states
        for symbol in self.final_states:
            if symbol not in reachable_from_dead_states and symbol != ',' and symbol != '{' and symbol != '}':
                reachable_from_dead_states.append(symbol)

                
        state_pile = reachable_from_dead_states.copy()

        # goes through the transitions and finds states that are reachable from final states
        while state_pile:
            current_state = state_pile.pop()
            for transition in self.transitions:
                if transition[2] == current_state:
                    if transition[0] not in state_pile:
                        if transition[0] not in reachable_from_dead_states:
                            state_pile.append(transition[0])   
                            reachable_from_dead_states.append(transition[0]) 

        final_reachable_states = list(set(reachable_states).intersection(set(reachable_from_dead_states)))

        # removes not reachable states from the list of states

        self.states = final_reachable_states

        # removes transitions that leave from dead states
        new_transitions = []
        for transition in self.transitions:
            if transition[0] in final_reachable_states and transition[2] in final_reachable_states:
                new_transitions.append(transition)

        self.transitions = new_transitions
        
        return final_reachable_states

    def equivalent_states(self, reachable_states):
        # creates a list of states that are equivalent

        finals_class = []
        non_finals_class = []

        for state in self.final_states:
            if state not in finals_class and state != ',' and state != '{' and state != '}':
                finals_class.append(state)

        for state in self.states:
            if state not in finals_class:
                non_finals_class.append(state)

        output = []

        alphabeth = []
        for state in self.alphabeth:
            if state not in alphabeth and state != ',' and state != '{' and state != '}':
                alphabeth.append(state)

        P = [finals_class, non_finals_class]
        W = [finals_class]

        while W:
            A = W.pop()
            for symbol in self.alphabeth:
                X = []
                for transition in self.transitions:
                    if transition[1] == symbol and transition[2] in A:
                        X.append(transition[0])
                for Y in P:
                    Y1 = []
                    Y2 = []
                    for state in Y:
                        if state in X:
                            Y1.append(state)
                        else:
                            Y2.append(state)
                    if Y1 and Y2:
                        P.remove(Y)
                        P.append(Y1)
                        P.append(Y2)
                        if Y in W:
                            W.remove(Y)
                            W.append(Y1)
                            W.append(Y2)
                        else:
                            if len(Y1) <= len(Y2):
                                W.append(Y1)
                            else:
                                W.append(Y2)

        self.format_automata(P)

    def format_automata(self, P):

        new_states = []
        new_transitions = []
        new_final_states = []
        new_initial_state = ''
        composite_states = []

        # creates new transitions    
        for state in P:
            if len(state) > 1:
                new_state = sorted(state)[0]
                composite_states.append(state)
                
                for transition in self.transitions:
                    if transition[0] in state:
                        # Update transitions to point to the representative state
                        if transition[2] in state:
                            new_transitions.append([new_state, transition[1], new_state])
                        else:
                            new_transitions.append([new_state, transition[1], transition[2]])
                    elif transition[2] in state:
                        # Update transitions coming into the composite state
                        new_transitions.append([transition[0], transition[1], new_state])
        
        for state in P:
            if len(state) == 1:
                
                for transition in self.transitions:
                    if transition[0] in state:

                        # goes through the composite states and checks if the transition is pointing to a composite state
                        for composite_state in composite_states:
                            if transition[2] in composite_state:
                                new_transitions.append([transition[0], transition[1], sorted(composite_state)[0]])
                            else:
                                new_transitions.append(transition)     

        # removes duplicate transitions
        unique_list = []
        [unique_list.append(x) for x in new_transitions if x not in unique_list]
        new_transitions = unique_list

        # creates new states
        for state in P:
            if len(state) > 1:
                # gets the new state name, by choosing the letter 
                # # that appears first in alphabetical order
                new_state = sorted(state)[0]
                new_states.append(str(new_state))

                # checks if new final states are needed
                for final_state in self.final_states:
                    if final_state in state:
                        new_final_states.append(new_state)

            else:
                if type(state) == list:
                    new_states.append(''.join(state))
                else:
                    new_states.append(state)

        # removes duplicate states  
        unique_list = []
        [unique_list.append(''.join(x)) for x in new_states if x not in unique_list]
        new_states = unique_list
        
        transitions_to_remove = []
        
        # checks if transitions are needed              
        for transition in new_transitions:
            if transition[0] not in new_states and transition in new_transitions:
                transitions_to_remove.append(transition)
            if transition[2] not in new_states and transition in new_transitions:   
                transitions_to_remove.append(transition)

        # removes transitions that are not needed
        for transition in transitions_to_remove:
            new_transitions.remove(transition)
        
        # removes duplicate final states
        unique_list = []
        [unique_list.append(x) for x in new_final_states if x not in unique_list]
        new_final_states = unique_list
        
        # order new final states in alphabetical order
        new_final_states = sorted(new_final_states)
        
        # order new states in alphabetical order
        new_states = sorted(new_states)
        
        # order new transitions in alphabetical order
        new_transitions = sorted(new_transitions)

        self.n_states = len(new_states)
        self.final_states = ''.join(new_final_states)
        self.states = new_states
        self.transitions = new_transitions

    
    def get_output(self):
        
        output = str(self.n_states) + ';' + self.initial_state + ';{' + ','.join(self.final_states) + '};' + self.alphabeth + ';' + ';'.join([','.join(transition) for transition in self.transitions])        
        print(output)    

n_input = input().split(';')

automata = NDFA(n_input)
automata.minimization()
automata.get_output()


# input_1 = '8;P;{S,U,V,X};{0,1};P,0,Q;P,1,P;Q,0,T;Q,1,R;R,0,U;R,1,P;S,0,U;S,1,S;T,0,X;T,1,R;U,0,X;U,1,V;V,0,U;V,1,S;X,0,X;X,1,V'
# input_1 = input_1.split(';')

# input_2 = ' 17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R'
# input_2 = input_2.split(';')

# test_1 = '9;A;{C,E};{a,b};A,a,F;A,b,B;B,a,D;B,b,A;C,a,A;C,b,B;D,a,E;D,b,D;E,a,B;E,b,C;F,a,G;F,b,A;G,a,I;G,b,G;H,a,F;H,a,G;H,b,G;I,a,G;I,b,I'
# test_1 = test_1.split(';')

