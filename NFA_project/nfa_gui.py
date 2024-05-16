import customtkinter as ctk
import pylab as plt
import pandas as pd
import graphviz
import pandastable
from pandastable import Table
from tkinter import filedialog,messagebox,ttk
import tkinter
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import tkinter as tk
from tkinter import Label
from tkinter import filedialog
from PIL import Image, ImageTk

import re

from prompt_toolkit.key_binding.bindings.named_commands import self_insert

input = " "


class PandasAPP():
    def __init__(self, frame) ->   None :
        try :
            self.frame = frame
            self.frame.place(relx=0.35, rely=0)
            df = pd.read_csv("transition_table.csv")
            self.table = Table(self.frame, dataframe=df)
            self.table.show()
        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None



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


# to positive closure
def check(st):
    v=0
    for i in range(len(st)):
       if st[i]=='+':
           v=1
           break
    if v==1:
        print('have')
        cv=convert(input)
        r=positive(cv)
        return r
    else:
        return st

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



def group_inner_list(item_list):
        grouped_items = []
        grouped_items = defaultdict(list)
        items = []
        items = item_list
        for sublist in items:
            state = sublist[0]
            symbol = sublist[1]
            next_state = int(sublist[2])
            grouped_items[state] = []
            grouped_items[state].append((symbol, next_state))


        updated_list = []
        for state, values in grouped_items.items():
            symbols = list(set([symbol for symbol, _ in values]))
            combined_values = [next_state for _, next_state in values]
            # print(type(combined_values[0]))
            updated_list.append([state, symbols] + [combined_values])

        return updated_list


def Intialize_dataframe_columns() :
    df = pd.DataFrame()
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
    state_list = state_list[1:]
    symbol_list = symbol_list[1:]
    next_state_list = next_state_list[1:]

    # Print the separate lists
    print("state_list", state_list)
    print("symbol_list", symbol_list)
    print("next_state_list", next_state_list)
    #
    # Find the unique values
    distinct_symbols = list(set(symbol_list))
    # Convert string numbers to integers and sort the list
    distinct_states = list(set(sorted(map(int, state_list))))

    # Print the sorted list
    print(distinct_states)

    # Remove 'epsilon' from the list
    distinct_symbols.remove('epsilon')

    # Sort the remaining letters alphabetically
    distinct_symbols.sort()

    # Create a new list with 'symbol' as the first element, the sorted letters in the middle, and 'epsilon' as the last element
    new_lst = ['state'] + distinct_symbols + ['epsilon']

    # Create a dataframe from the new list
    df = pd.DataFrame(columns=[new_lst])

    # Print the updated dataframe
    return df


def contrust_dataframe() :

    df = Intialize_dataframe_columns()
    print("dataframe columns" ,df.columns)
    items = []
    items = t[1:]
    print("items", items)
    updated_item_list = []
    updated_item_list = group_inner_list(items)
    print("updated_item_list",updated_item_list)

    # Iterate over the items and update the DataFrame
    for item in updated_item_list:
        current_state, symbol, next_state = item
        current_state = int(current_state)
        symbol = (symbol[0],)
        #
        for col in df.columns:
            # print(symbol, col[0])
            if symbol == col:
                if col[0] == "epsilon":
                    # print(True)
                    new_lst = []
                    new_lst.append(current_state)
                    new_lst.extend(element for element in next_state)
                    df.loc[current_state, col] = sorted(new_lst)
                    break
                else:

                    df.loc[current_state, col] = next_state

                    df.loc[current_state, "epsilon"] = current_state

                    break  # Exit the loop after finding a match

    df['state'] = [item[0] for item in updated_item_list]
    df.fillna('-', inplace=True)  # Fill null values with '-'
    # print(df)

    df.reset_index(drop=True, inplace=True)
    print(df)

    # Save the DataFrame as a CSV file
    df.to_csv('transition_table.csv', index=False)


def uniqe_list(input_list) :
    unique_set = set(map(tuple, input_list))

    # Convert the tuples back to lists
    unique_list = [list(item) for item in unique_set]

    # Print the unique list
    return (unique_list)



def Draw_nfa_graph() :
    # Create a new Graphviz graph
    items = []
    graph = graphviz.Digraph()
    # Initialize a set to keep track of states that appear as first elements in any transition
    first_states = set()
    last_states = set()
    items = t[1:]
    # items=uniqe_list(items)


    # Add nodes and edges
    for start, label, end in items:
        graph.edge(start, end, label=" " + label)
        first_states.add(start)

    # Identify the first state as the first element of the first transition
    first_state = items[0][0]

    # Identify the last state as the last element of any transition that doesn't appear as the first element in any other transition
    last_states = {items[-1] for items in items if items[-1] not in first_states}
    if len(last_states) == 1:

        print("not common state")
    else:
        tkinter.messagebox.showerror("Information", "Ambiguous last state")
        return None
        # raise ValueError("Ambiguous last state")

    # Add styling for nodes
    for state in first_states:
        if state == first_state:
            graph.node(state, shape='circle')  # Make first state a  circle

    for state in last_states:
        graph.node(state, shape='doublecircle')  # Make last state(s) a double circle

    # Render the graph
    graph.render('output', format='png', cleanup=True)




def validate_regex(pattern):
    try:
        re.compile(pattern)
        print("Regular expression is valid.")
        return True
    except re.error:
        print("Invalid regular expression.")
        check_validation_label.configure(text="your RE is not VALID", font=('Times', 12), fg_color="red",bg_color="black")
        tkinter.messagebox.showerror("Information", "your RE is not VALID")
        return False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


app = ctk.CTk()
app.title("NFA Graph Design")
# app.iconphoto("NFAofaclosure.jpg")
app.geometry("500x450")




def read_exp() :
    # take t as input
    global t
    t = [["state", 'symbol', 'next state']]
    df = pd.DataFrame()
    updated_list = []
    input = ""
    input = entry_box.get()
    check_validation_label.configure(text="")
    value_of_validation = validate_regex(input)
    if(value_of_validation) :
        check_validation_label.configure(text="your RE is VALID", font=('Times', 12),bg_color="black",fg_color="green")
        pass

    if(value_of_validation != True) :
        exit(1)

    r = check(input)
    print(r)
    pr = postfix(r)
    et = constructTree(pr)
    # inorder(et)
    fa = evalRegex(et)
    print('regular expression :', input)
    printTransitionTable(fa)
    print(t)


    read_file_label.configure(text='')
    read_exp_label.configure(text="read from your entry RE", font=('Times', 14))

    new_window = ctk.CTkToplevel(app)
    new_window.title("NFA Graph Design")
    new_window.geometry("600x500")
    new_window.grid()

    # def clear_frame_content(frame):
    #     for widget in frame.winfo_children():
    #         widget.destroy()

    # new_frame for choise
    new_frame1 = ctk.CTkFrame(new_window,width=200, height=500)
    new_frame1.place(relx=0,rely=0)

    nfa_label = ctk.CTkLabel(new_frame1, text="Choose From:", font=('Times', 24))
    nfa_label.place(relx=0.13, rely=0.2)



    def load_dataframe() :

        try :
            # clear_frame_content(new_frame2)
            updated_list = group_inner_list(t[1:])
            # print("updated_list", updated_list)
            contrust_dataframe()
            df = pd.read_csv("transition_table.csv")
            root = PandasAPP(new_frame2)

        except ValueError :
            tkinter.messagebox.showerror("Information","dataframe is invalid")
            return None
        except FileNotFoundError :
            tkinter.messagebox.showerror("Information","No such file as transition_table.csv")
            return None

        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None

    def show_graph() :
        try :
            # clear_frame_content(new_frame2)
            Draw_nfa_graph()
            img_name = "output.png"
            size = Image.open(img_name).size

            # Image.resize()
            image = ctk.CTkImage(light_image=Image.open(img_name), size=(400, 500))
            nfa_graph_image_label = ctk.CTkLabel(new_window, text="", image=image)
            nfa_graph_image_label.place(relx=0.35, rely=0)
        except Exception as e:
            tkinter.messagebox.showerror("Information", f"{str(e)}")
            return None




    transtion_table_button = ctk.CTkButton(new_frame1,text="display Transion Table",font=('Times', 16),height=30,width=150,command=load_dataframe)
    transtion_table_button.place(relx=0.13,rely=0.4)





    Nfa_graph_button = ctk.CTkButton(new_frame1, text="display NFA Graph", font=('Times', 16),height=30,width=150,command=show_graph)
    Nfa_graph_button.place(relx=0.13, rely=0.55)

    Matching_tree_button = ctk.CTkButton(new_frame1, text="display Matching Tree", font=('Times', 16),height=30,width=150)
    Matching_tree_button.place(relx=0.13, rely=0.70)

    new_frame2 = ctk.CTkFrame(new_window,width=400,height=500)
    new_frame2.place(relx=0.35,rely=0)







    # updated_list=group_inner_list(t[1:])
    # print("updated_list",updated_list)
    # contrust_dataframe()
    # Draw_nfa_graph()




def read_file():
    read_exp_label.configure(text='')
    read_file_label.configure(text="read from your entry File", font=('Times', 14))
    filename = filedialog.askopenfilename(initialdir="/",title="Select A File",filetype=(("txt files","*.txt"),("All Files",("*.*"))))
    entry_box.configure(font=("Times", 16))
    entry_box.delete(0, tk.END)  # Clear existing text
    entry_box.insert(0, filename)
    words = load_data()

    def next_re() :
        try :
            entry_box.delete(0, tk.END)  # Clear existing text
            entry_box.insert(0, words.pop(0))
        except IndexError :
            tkinter.messagebox.showerror("Information", "You have drawn all RE in File")

    read_next_RE = ctk.CTkButton(master=app, text="NEXT RE", font=('Times', 16),command=next_re)  #TODO :, command=read_exp
    read_next_RE.place(relx=0.65,rely=0.9)




def load_data() :
    file_path = entry_box.get()
    try :
        stop_word = '#'
        txt_filename=r"{}".format(file_path)
        with open(txt_filename, 'r') as file:
            content = file.read()
            words = re.split("#|\n",content)
            print(words)
            return words
    except ValueError :
        tkinter.messagebox.showerror("Information", "the file you have choosen is invalid ")
        return None
    except FileNotFoundError :
        tkinter.messagebox.showerror("Information", f"No such file as{file_path}")
        return None
    except Exception as e:
        tkinter.messagebox.showerror("Information", f"{str(e)}")
        return None



# NFA Graph Design
nfa_label = ctk.CTkLabel(app,text="NFA Graph Design",font=('Times', 24))
nfa_label.place(relx=0.36,rely=0.2)


# read_exp_button
read_exp_button = ctk.CTkButton(master=app,text="get your RE",font=('Times', 16),command=read_exp)
read_exp_button.place(relx=0.1,rely=0.75)

# read_exp_label
read_exp_label = ctk.CTkLabel(app,text="")
read_exp_label.place(relx=0.1,rely=0.82)

# read_file_button
read_file_button = ctk.CTkButton(master=app,text="read From File",font=('Times', 16),command=read_file)
read_file_button.place(relx=0.65,rely=0.75)

# read_file_label
read_file_label = ctk.CTkLabel(app,text="")
read_file_label.place(relx=0.65,rely=0.82)


# check_validation_label
check_validation_label = ctk.CTkLabel(app, text="")
check_validation_label.place(relx=0.2,rely=0.55)

# entry_box
entry_box =ctk.CTkEntry(app,placeholder_text="Drop File/Write RE",font=("Times", 20),width= 300,height=35)
entry_box.place(relx=0.2,rely=0.45)
app.mainloop()





