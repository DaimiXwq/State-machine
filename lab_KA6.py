import itertools


class FiniteAutomaton:
    def __init__(self, states, alphabet, transition_table, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transition_table = transition_table
        self.start_state = start_state
        self.accept_states = accept_states
        self.count_state = start_state

    def transition(self, state, symbol):
        return self.transition_table[state][symbol]

    def is_accepting(self, state):
        return state in self.accept_states
    
    def next_step(self, symbol):
        self.count_state = self.transition_table[self.count_state][symbol]
        
    def get_state(self):
        return self.count_state
    
    def __getitem__(self, key):
        for i in str(key):
            self.next_step(i)
            print("state ",self.get_state())
            
        return self.count_state
    
    def __setitem__(self, key, value):
        if key in self.states:
            # Проверяем, является ли value словарем
            if isinstance(value, dict):
                for i, j in value.items():
                    if i in self.alphabet and j in self.states:
                        continue
                    else:
                        self.transition_table[key] = {}
                        break
                else:     
                    self.transition_table[key] = value
            else:
                # Если нет, присваиваем пустой словарь
                self.transition_table[key] = {}
        else:
            print("дал в штангу")
    
    # Функция для вычисления ε-замыкания (ε-closure) множества состояний
    # ε-замыкание - это все состояния, в которые можно попасть из текущего состояния, следуя только ε-переходам (переходам по пустому символу).
    def epsilon_closure(self, states=None):
        if states is None:
            states = set([self.start_state])
        stack = list(states)  # Стек для обработки состояний
        closure = set(states)  # Замыкание (начинаем с исходного множества состояний)
        
        # Обрабатываем все состояния в стеке
        while stack:
            state = stack.pop()  # Извлекаем состояние из стека
            # Переходы по ε (пустой строке) для текущего состояния
            for next_state in self.transition_table.get(state, {}).get('', []):  # Получаем все состояния, достижимые по ε
                if next_state not in closure:  # Если состояние ещё не в замыкании
                    closure.add(next_state)  # Добавляем его в замыкание
                    stack.append(next_state)  # Добавляем в стек для дальнейшей обработки
        
        return closure  # Возвращаем итоговое ε-замыкание

    # Функция для выполнения перехода по символу входного алфавита
    # Принимает множество состояний и символ, возвращает множество состояний, достижимых из исходных по этому символу.
    def move(self, states, symbol):
        next_states = set()  # Множество для хранения новых состояний
        for state in states:  # Проходим по каждому состоянию из исходного множества
            next_states.update(self.transition_table.get(state, {}).get(symbol, []))  # Добавляем состояния, достижимые по символу
        return next_states  # Возвращаем новое множество состояний

    # Основная функция для преобразования НКА в ДКА
    def nfa_to_dfa(self):
        dfa_transitions = {}  # Таблица переходов для ДКА
        unmarked_states = []  # Список непомеченных состояний ДКА (тех, которые ещё не обработаны)
        marked_states = []  # Список помеченных состояний ДКА (тех, которые уже обработаны)
        
        # Начальное состояние ДКА - это ε-замыкание начального состояния НКА
        start_closure = self.epsilon_closure()
        unmarked_states.append(start_closure)  # Добавляем его в список непомеченных состояний
        # dfa_states будет хранить все состояния ДКА (множества состояний НКА) и их индексы
        dfa_states = {frozenset(start_closure): 0}  # Замораживаем множество состояний и назначаем индекс 0
        dfa_state_count = 1  # Счетчик для уникальных индексов состояний ДКА
        
        # Пока есть непомеченные состояния
        while unmarked_states:
            current_states = unmarked_states.pop(0)  # Извлекаем текущее состояние (множество состояний НКА)
            marked_states.append(frozenset(current_states))  # Помечаем его как обработанное
            
            # Для каждого символа входного алфавита вычисляем новое состояние
            for symbol in self.alphabet:
                # Выполняем переход по символу и затем строим ε-замыкание для полученного множества состояний
                next_states = self.epsilon_closure( self.move( current_states, symbol))
                
                if not next_states:  # Если нет переходов по символу, пропускаем
                    continue
                
                frozen_next_states = frozenset(next_states)  # Замораживаем множество состояний, чтобы работать с ним как с одним состоянием ДКА
                
                # Если это новое множество состояний (ещё не встречалось в ДКА)
                if frozen_next_states not in dfa_states:
                    dfa_states[frozen_next_states] = dfa_state_count  # Назначаем новое состояние
                    dfa_state_count += 1  # Увеличиваем счетчик состояний ДКА
                    unmarked_states.append(next_states)  # Добавляем новое состояние в список непомеченных
                
                # Добавляем переход в таблицу переходов ДКА
                #dfa_transitions[(dfa_states[frozenset(current_states)], symbol)] = dfa_states[frozen_next_states]

                current_state_key = tuple(current_states) if len(current_states) > 1 else list(current_states)[0]
                
                if current_state_key not in dfa_transitions:
                    dfa_transitions[current_state_key] = {}
                
                dfa_transitions[current_state_key][symbol] = tuple(next_states) if len(next_states) > 1 else list(next_states)[0]
        
        
        # Определяем конечные состояния ДКА
        # Если хотя бы одно из состояний в множестве является конечным в НКА, то множество считается конечным в ДКА
        #dfa_accept_states = {dfa_states[states] for states in dfa_states if states & set(self.accept_states)}
        #dfa_accept_states = {dfa_states[states] for states in dfa_states if states & set(self.accept_states)}
        # Определяем конечные состояния ДКА
        dfa_accept_states = {tuple(states) for states in dfa_states if states & set(self.accept_states)}
        
        
        return FiniteAutomaton(self.states, self.alphabet, dfa_transitions, self.start_state, dfa_accept_states)  # Возвращаем ДКА
    
    
    


def union_automata(automaton1, automaton2):
    states1 = automaton1.states
    states2 = automaton2.states
    alphabet = automaton1.alphabet
    
    # Декартово произведение состояний
    combined_states = list(itertools.product(states1, states2))
    #print("дал в штангу ",combined_states)
    
    # Новое начальное состояние
    combined_start_state = (automaton1.start_state, automaton2.start_state)
    
    # Новые конечные состояния 
    combined_accept_states = [(s1, s2) for s1, s2 in combined_states
                                  if s1 in automaton1.accept_states or s2 in automaton2.accept_states]
    
    # Новая таблица переходов
    combined_transition_table = {}
    
    for (state1, state2) in combined_states:
        combined_transition_table[(state1, state2)] = {}
        for symbol in alphabet:
            next_state1 = automaton1.transition(state1, symbol)
            next_state2 = automaton2.transition(state2, symbol)
            combined_transition_table[(state1, state2)][symbol] = (next_state1, next_state2)
    
    return FiniteAutomaton(combined_states, alphabet, combined_transition_table, combined_start_state, combined_accept_states)

def intersection_automata(automaton1, automaton2):
    states1 = automaton1.states
    states2 = automaton2.states
    alphabet = automaton1.alphabet
    
    # Декартово произведение состояний
    combined_states = list(itertools.product(states1, states2))
    
    # Новое начальное состояние
    combined_start_state = (automaton1.start_state, automaton2.start_state)
    
    # Новые конечные состояния
    combined_accept_states = [(s1, s2) for s1, s2 in combined_states
                                  if s1 in automaton1.accept_states and s2 in automaton2.accept_states]
    
    # Новая таблица переходов
    combined_transition_table = {}
    
    for (state1, state2) in combined_states:
        combined_transition_table[(state1, state2)] = {}
        for symbol in alphabet:
            next_state1 = automaton1.transition(state1, symbol)
            next_state2 = automaton2.transition(state2, symbol)
            combined_transition_table[(state1, state2)][symbol] = (next_state1, next_state2)
    
    return FiniteAutomaton(combined_states, alphabet, combined_transition_table, combined_start_state, combined_accept_states)

# Пример автомата 1
states1 = ['q0', 'q1','q3']
alphabet = ['a', 'b']
transition_table1 = {
    'q0': {'a': 'q1', 'b': 'q0'},
    'q1': {'a': 'q0', 'b': 'q1'},
    'q3': {'a': 'q1', 'b': 'q3'}
}
start_state1 = 'q0'
accept_states1 = ['q1','q3']

automaton1 = FiniteAutomaton(states1, alphabet, transition_table1, start_state1, accept_states1)

# Пример автомата 2
states2 = ['p0', 'p1']
transition_table2 = {
    'p0': {'a': 'p0', 'b': 'p1'},
    'p1': {'a': 'p1', 'b': 'p0'}
}
start_state2 = 'p0'
accept_states2 = ['p0']

automaton2 = FiniteAutomaton(states2, alphabet, transition_table2, start_state2, accept_states2)

# Объединение автоматов
union_automaton = union_automata(automaton1, automaton2)

# Пересечение автоматов
intersection_automaton = intersection_automata(automaton1, automaton2)

# Вывод результатов
def print_automaton(automaton):
    print("Состояние:", automaton.states)
    print("Начальное состояние:", automaton.start_state)
    print("Конечное состояние:", automaton.accept_states)
    print("Таблица переходов:")
    for state, transitions in automaton.transition_table.items():
        print(f"  {state}: {transitions}")

print("Объединение КА:")
print_automaton(union_automaton)

print("\nПересечение КА:")
print_automaton(intersection_automaton)


in_str = input("Введите строку:")
print(automaton1.transition_table[automaton1.count_state])
for char in in_str:
    automaton1.next_step(char)
    automaton2.next_step(char)
    union_automaton.next_step(char)
    intersection_automaton.next_step(char)
    
    print("automaton1 ",automaton1.get_state(),'\t',"automaton2 ",automaton2.get_state(),'\t', "union_automaton ", union_automaton.get_state(),'\t',"intersection_automaton ",intersection_automaton.get_state(),'\t')

print(automaton1[in_str])
automaton1['0'] = {'a': '0', 'b': 'q1'}
print(automaton1.transition_table)
# Таблица переходов НКА (табличный вид):
states3 = ['q0', 'q1', 'q2', 'q3']
transition_table3 = {
    'q0': {'a': ['q1', 'q3'], 'b': ['q0','q1'], 'c': ['q0']}, 
    'q1': {'a': ['q3'], 'b': ['q0','q3'], 'c': ['q3']},
    'q2': {'a': ['q1', 'q3'], 'b': ['q3'], 'c': ['q0','q1']},
    'q3': {'a': ['q0'], 'b': ['q1'], 'c': ['q1','q2']}
}

start_state3 = 'q0'  # Начальное состояние НКА
accept_states3 = ['q2', 'q3']  # Конечные состояния НКА
alphabet3 = ['a', 'b', 'c']  # Входной алфавит

automaton3 = FiniteAutomaton(states3, alphabet3, transition_table3, start_state3, accept_states3)
# Преобразуем НКА в ДКА
dfa_automaton3 = automaton3.nfa_to_dfa()

# Вывод таблицы переходов для ДКА
print(" ДКА:")
print_automaton(dfa_automaton3)


