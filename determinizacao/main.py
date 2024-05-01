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
            new_transition[2] = list(new_transition[2])
            transitions.append(new_transition)
        return transitions
    
    def get_automata(self):
        print('Number of states: ', self.n_states)
        print('Initial state: ', self.initial_state)
        print('Final states: ', self.final_states)
        print('Alphabeth: ', self.alphabeth)
        print('Transitions: ', self.transitions)
        print('States: ', self.states)
    
    def create_states(self):
        states = []
        for transition in self.transitions:
            if transition[0] not in states:
                states.append(transition[0])
            if transition[2][0] not in states:
                states.append(transition[2][0])
        return states
    
    def determinize(self):
        symbols = []
        E_closure_dict = {} 
        for transition in self.transitions:
            symbols.append(transition[1])
        if '&' in symbols:
            self.determinize_with_e()
        else:
            self.determinize_no_e(E_closure_dict) 
    
    def determinize_with_e(self):
        
        # calculate epsilon closure, then determinize_no_e
        
        E_closure_dict = {}
        for state in self.states:
            E_closure_dict[state] = state
        E_closure = [[state] for state in self.states]
        new_initial_state_index = E_closure.index([self.initial_state])
        
        for closure in E_closure:
            for element in closure:
                for transition in self.transitions:
                    if transition[0] == element and transition[1] == '&':
                        closure.append(transition[2][0])
                        E_closure_dict[element] = closure
        self.states = self.states + E_closure
        
        # remove duplicates

        self.n_states = len(self.states)
        self.initial_state = E_closure[new_initial_state_index]
        
        # remove epsilon transitions
        self.remove_epsilon_transitions()
        self.determinize_no_e(E_closure_dict)

    
    def remove_epsilon_transitions(self):
        for transition in self.transitions:
            if transition[1] == '&':
                self.transitions.remove(transition)
        for symbol in self.alphabeth:
            if symbol == '&':
                self.alphabeth = self.alphabeth.replace(symbol, '')     
            
    def determinize_no_e(self, e_closure_dict):

        # adds the new composite states to the list of states
        state_pile = []
        state_pile.append(self.initial_state)
        
        new_transitions = []
        new_states = set()

        new_final_states = []
                
        already_visited = []
        
        self.initial_state = ''.join(self.initial_state)
        
        while state_pile:
            current_state = state_pile.pop()
            if current_state in already_visited:
                continue
            already_visited.append(current_state)
            for symbol in self.alphabeth:
                next_states = self.calculate_transitions(current_state, symbol, e_closure_dict)
                
                # remove duplicates
                unique_list = []
                [unique_list.append(item) for item in next_states if item not in unique_list]
                next_states = unique_list

                
                if len(next_states) > 0:
                    new_state = ''.join(next_states)
                    self.states.append(new_state)
                    
                    if new_state not in already_visited:
                        state_pile.append(next_states)
                    new_states.add(new_state)
                                        
                    # remove duplicates from pile (not necessary anymore)
                    unique_tuples = set(tuple(i) for i in state_pile)
                    state_pile = [list(i) for i in unique_tuples]
                    
            
                    state_label = ''.join(current_state)
                    
                    new_transitions.append((state_label, symbol, new_state))  
                    
                    # go through the new states and check if they contain a final state
                    # then add the new state to self.final_states
                    
                    for state in next_states:
                        if state in self.final_states:
                            new_final_states.append(new_state)
        

        self.update_automata(new_states, new_transitions, new_final_states)

    def update_automata(self, states, transitions, new_final_states):
        
        # order transitions by alphabetical order
        transitions.sort(key=lambda x: x[0])  
        
        # surrounds each state in the trasitions (transition[0] and transition[2]) in {}
        new_transitions = []
        for transition in transitions:
            # replace tuple
            transition = list(transition)
            transition[0] = '{' + transition[0] + '}'
            transition[2] = '{' + transition[2] + '}'
            transition = tuple(transition)
            new_transitions.append(transition)
            
        # surrounds each state in {}
        for state in states:
            state = '{' + state + '}'
                        
        # formats new transitions
        for transition in new_transitions:
            for state in transition:
                if type(state) == list:
                    transition[transition.index(state)] = str(state)
                    
        # removes unnecessary commas from the alphabeth
        self.alphabeth = self.alphabeth.replace(',', '')
        self.alphabeth = self.alphabeth.replace('{', '')
        self.alphabeth = self.alphabeth.replace('}', '')
        
        # separates symbols in the alphabeth again
        self.alphabeth = ','.join(self.alphabeth)
        
        #updates the final states:
        
        old_final_states = self.final_states.split(',')
        old_final_states = [state.replace('{', '') for state in old_final_states]
        old_final_states = [state.replace('}', '') for state in old_final_states]        

        # removes duplicates from new_final_states
        unique_list = []
        [unique_list.append(item) for item in new_final_states if item not in unique_list]

        new_final_states = unique_list

        # surrounds each state in {}
        final_states_result = new_final_states + old_final_states

        # goes through the states and eliminate from final states the unreacheable states
        for state in final_states_result:
            if state not in states:
                final_states_result.remove(state)
        
        # orders the final states alphabetically
        final_states_result.sort()

        # removes duplicate final states
        unique_list = []
        [unique_list.append(x) for x in final_states_result if x not in unique_list]
        final_states_result = unique_list        
        
        fresult = ['{' + element + '}' for element in final_states_result]

        self.final_states = ','.join(fresult)

        self.states = states
        self.transitions = new_transitions
        self.n_states = len(states)

        
    def calculate_transitions(self, states, symbol, e_closure_dict):
        result = []
        if len(e_closure_dict) != 0:
            for state in states:
                for transition in self.transitions:
                    if transition[0] == state and transition[1] == symbol:
                        result.append(transition[2][0])
                        new_closure = list(e_closure_dict[transition[2][0]]) if type(e_closure_dict[transition[2][0]]) != list else e_closure_dict[transition[2][0]] 
                        result = result + new_closure
        else:
            for state in states:
                for transition in self.transitions:
                    if transition[0] == state and transition[1] == symbol:
                        result.append(transition[2][0])            
        return result

    def get_output(self):
        
        output = str(self.n_states) + ';{' + self.initial_state + '};{' + self.final_states + '};{' + self.alphabeth + '};' + ';'.join([','.join(transition) for transition in self.transitions])        
        print(output)

n_input = input().split(';')

automata = NDFA(n_input)
automata.determinize()
automata.get_output()


# test = '4;A;{D};{a,b};A,a,B;A,a,C;B,a,D;B,b,D;C,a,D;C,b,D;D,a,D;D,b,D;C,a,B'
# test = test.split(';')

# input_1 =  '3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C'
# input_1 = input_1.split(';')

# input_2 = '4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S'
# input_2 = input_2.split(';')

# input_3 =  '4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D'
# input_3 = input_3.split(';')


