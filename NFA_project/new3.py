import pandas as pd
import matplotlib.pyplot as plt
class Type:
    SYMBOL = 1
    CONCAT = 2
    UNION = 3
    KLEENE = 4


class ExpressionTree:

    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
        self.left = None
        self.right = None


def constructTree(regexp):
    stack = []
    for c in regexp:
        if c.isalpha():
            stack.append(ExpressionTree(Type.SYMBOL, c))
        else:
            if c == "|":
                z = ExpressionTree(Type.UNION)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == ".":
                z = ExpressionTree(Type.CONCAT)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == "*":
                z = ExpressionTree(Type.KLEENE)
                z.left = stack.pop()
            stack.append(z)

    return stack[0]


def inorder(et):
    if et._type == Type.SYMBOL:
        print(et.value)
    elif et._type == Type.CONCAT:
        inorder(et.left)
        print(".")
        inorder(et.right)
    elif et._type == Type.UNION:
        inorder(et.left)
        print("+")
        inorder(et.right)
    elif et._type == Type.KLEENE:
        inorder(et.left)
        print("*")


def higherPrecedence(a, b):
    p = ["|", ".", "*"]
    return p.index(a) > p.index(b)


def postfix(regexp):
    # adding dot "." between consecutive symbols
    temp = []
    for i in range(len(regexp)):
        if i != 0 \
                and (regexp[i - 1].isalpha() or regexp[i - 1] == ")" or regexp[i - 1] == "*") \
                and (regexp[i].isalpha() or regexp[i] == "("):
            temp.append(".")
        temp.append(regexp[i])
    regexp = temp

    stack = []
    output = ""

    for c in regexp:
        if c.isalpha():
            output = output + c
            continue

        if c == ")":
            while len(stack) != 0 and stack[-1] != "(":
                output = output + stack.pop()
            stack.pop()
        elif c == "(":
            stack.append(c)
        elif c == "*":
            output = output + c
        elif len(stack) == 0 or stack[-1] == "(" or higherPrecedence(c, stack[-1]):
            stack.append(c)
        else:
            while len(stack) != 0 and stack[-1] != "(" and not higherPrecedence(c, stack[-1]):
                output = output + stack.pop()
            stack.append(c)

    while len(stack) != 0:
        output = output + stack.pop()

    return output


class FiniteAutomataState:
    def __init__(self):
        self.next_state = {}


def evalRegex(et):
    # returns equivalent E-NFA for given expression tree (representing a Regular
    # Expression)
    if et._type == Type.SYMBOL:
        return evalRegexSymbol(et)
    elif et._type == Type.CONCAT:
        return evalRegexConcat(et)
    elif et._type == Type.UNION:
        return evalRegexUnion(et)
    elif et._type == Type.KLEENE:
        return evalRegexKleene(et)


def evalRegexSymbol(et):
    start_state = FiniteAutomataState()
    end_state = FiniteAutomataState()

    start_state.next_state[et.value] = [end_state]
    return start_state, end_state


def evalRegexConcat(et):
    left_nfa = evalRegex(et.left)
    right_nfa = evalRegex(et.right)

    left_nfa[1].next_state['epsilon'] = [right_nfa[0]]

    return left_nfa[0], right_nfa[1]


def evalRegexUnion(et):
    start_state = FiniteAutomataState()
    end_state = FiniteAutomataState()

    up_nfa = evalRegex(et.left)
    down_nfa = evalRegex(et.right)

    start_state.next_state['epsilon'] = [up_nfa[0], down_nfa[0]]
    up_nfa[1].next_state['epsilon'] = [end_state]
    down_nfa[1].next_state['epsilon'] = [end_state]

    return start_state, end_state


def evalRegexKleene(et):
    start_state = FiniteAutomataState()
    end_state = FiniteAutomataState()

    sub_nfa = evalRegex(et.left)

    start_state.next_state['epsilon'] = [sub_nfa[0], end_state]
    sub_nfa[1].next_state['epsilon'] = [sub_nfa[0], end_state]

    return start_state, end_state


t = [["state", 'symbol', 'next state']]


def printStateTransitions(state, states_done, symbol_table):
    if state in states_done:
        return

    states_done.append(state)

    for symbol in list(state.next_state):
        line_output = "s" + str(symbol_table[state]) + "\t\t" + symbol + "\t\t\t"

        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
            line_output = line_output + "s" + str(symbol_table[ns]) + " "
            t.append([str(symbol_table[state]), symbol, str(symbol_table[ns])])
        print(line_output)

        for ns in state.next_state[symbol]:
            printStateTransitions(ns, states_done, symbol_table)


def printTransitionTable(finite_automata):
    print("State\t\tSymbol\t\t\tNext state")
    printStateTransitions(finite_automata[0], [], {finite_automata[0]: 0})


# def to_transition_table(t):


# to positive closure


def convert(s):
    ms = []
    f = 0
    for i in range(len(s)):
        if s[i] == "(":
            x = i
            f = 1

        if s[i] == ")":
            y = i
            ms.append(s[x:y + 1])
            f = 0

        if f == 0:
            ms.append(s[i])
    ms = list(filter(lambda x: x != ')', ms))
    return ms


def positive(t):
    for i in range(len(t)):

        if t[i] == '+':

            ele = t.pop(i - 1)
            ele = ele + ele + '*'
            t.insert(i - 1, ele)

        else:
            pass

    out = ''
    t = list(filter(lambda x: x != '+', t))
    print('t', t)
    for i in range(len(t)):
        out = out + t[i]

    print('output', out)
    return out


input = "xy(ab)+"
cv = convert(input)
r = positive(cv)

print(r)

pr = postfix(r)
et = constructTree(pr)

# inorder(et)

fa = evalRegex(et)
print('regular expression :', input)
printTransitionTable(fa)
print(t)
# to_transition_table(t)

# Initialize separate lists for each position
state_list = []
symbol_list = []
next_state_list = []

# Extract elements at the same position
for item in t:
    print(item)
    state_list.append(item[0])
    symbol_list.append(item[1])
    next_state_list.append(item[2])


# slice needed values
state_list =  state_list[1:]
symbol_list = symbol_list[1:]
next_state_list = next_state_list[1:]

# Print the separate lists
print("state_list",state_list)
print("symbol_list",symbol_list)
print("next_state_list",next_state_list)


# Find the unique values
distinct_symbols = list(set(symbol_list))
# Convert string numbers to integers and sort the list
distinct_states = list(set(sorted(map(int, state_list))))

# Print the sorted list
print(distinct_states)

# Print the distinct symbols
# print(distinct_symbols)


# Remove 'epsilon' from the list
distinct_symbols.remove('epsilon')

# Sort the remaining letters alphabetically
distinct_symbols.sort()

# Create a new list with 'symbol' as the first element, the sorted letters in the middle, and 'epsilon' as the last element
new_lst = ['state'] + distinct_symbols + ['epsilon']

# Create a dataframe from the new list
df = pd.DataFrame(columns=[new_lst])



# Print the updated dataframe
print(df.columns)



items = t[1:]
print("items",items)

from collections import defaultdict

def group_inner_list(item_list):
    grouped_items = defaultdict(list)

    for sublist in item_list:
        state = sublist[0]
        symbol = sublist[1]
        next_state = int(sublist[2])
        # print(type(next_state))
        grouped_items[state].append((symbol, next_state))
        # print(grouped_items)

    updated_list = []
    for state, values in grouped_items.items():
        symbols = list(set([symbol for symbol, _ in values]))
        combined_values = [next_state for _, next_state in values]
        # print(type(combined_values[0]))
        updated_list.append([state, symbols] + [combined_values])

    return updated_list


updated_item_list = group_inner_list(items)
print(updated_item_list)

# df = pd.DataFrame()
# print(df)
# print(df.columns)
# Iterate over the items and update the DataFrame
for item in updated_item_list:
    current_state, symbol, next_state = item
    current_state = int(current_state)
    symbol = (symbol[0],)
    #
    for col in df.columns:
        print(symbol, col)
        if symbol == col:
            df.loc[current_state, col] = next_state
            break  # Exit the loop after finding a match


df['state'] = [item[0] for item in updated_item_list]
df.fillna('-', inplace=True)  # Fill null values with '-'
# print(df)

df.reset_index(drop=True, inplace=True)
print(df)

# Save the DataFrame as a CSV file
df.to_csv('transition_table.csv', index=False)

#Read Transtion Table
# df = pd.read_csv("transition_table.csv")


import graphviz

# Create a new Graphviz graph
graph = graphviz.Digraph()

# Initialize a set to keep track of states that appear as first elements in any transition
first_states = set()

# Add nodes and edges
for start, label, end in items:
    graph.edge(start, end, label=" "+label)
    first_states.add(start)

# Identify the first state as the first element of the first transition
first_state = items[0][0]

# Identify the last state as the last element of any transition that doesn't appear as the first element in any other transition
last_states = {items[-1] for items in items if items[-1] not in first_states}
if len(last_states) == 1:

    print("not common state")
else:
    raise ValueError("Ambiguous last state")

# Add styling for nodes
for state in first_states:
    if state == first_state:
        graph.node(state,shape='circle')  # Make first state a double circle

for state in last_states:
    graph.node(state, shape='doublecircle')  # Make last state(s) a double circle

# Render the graph
graph.render('output', format='png', cleanup=True)
# Display the dot graph using matplotlib
img = plt.imread('output.png')
plt.imshow(img)
plt.axis('off')
plt.show()


