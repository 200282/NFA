import numpy as np

inp = '(a|b)*.a.b.b'    #input("")
print ('input regular expression : ' , inp)
#'(a|b)*.a.b.b' // my regular expression
"""
Give your input in the above variable
    a and b are the only terminals accepted by this script
    e denotes epsilon 
    . is used for "and" operation Eg. ab = a.b //concatenation
    | is used for "or" operation Eg. a|b = a|b  //oring
    * is the Kleene's Closure operator. You can give star operator after any closing brackets and terminals 
"""


_="-"

start = 1 # denotes start of e-nfa table
end = 1   # denotes end of our table which is initially same as start
cur = 1   # denotes current position of our pointer
# this is intitial e-nfa table with only one state which is start and end both
table = [["state","epsilon","a","b"],
          [1,_,_,_]]

def print_t(table):
    """
    This function prints the e-nfa table
    """
    i = table[0]
    print(f'{i[0]: <10}'+f'| {i[1]: <10}'+f'| {i[2]: <10}'+f'| {i[3]: <10}')
    print("-"*46)
    for i in table[1:]:
        try:
            x = " ".join([str(j) for j in i[1]])
        except:
            x = ""
        try:
            y = " ".join([str(j) for j in i[2]])
        except:
            y = ""
        try:
            z = " ".join([str(j) for j in i[3]])
        except:
            z = ""
        print(f'{i[0]: <10}'+f'| {x: <10}'+f'| {y: <10}'+f'| {z: <10}')

def e_(cur,ed=end):
    """
    this fuction adds epsilon to the table
    """
    temp = table[cur]
    
    try:
        table[cur] = [cur,temp[1].append(cur+1),temp[2],temp[3]]
    except:
        table[cur] = [cur,[cur,cur+1],temp[2],temp[3]]
    try:
        nv = table([cur+1])
    except:
        table.append([ed+1,_,_,_])
        ed+=1
    return ed


def a_(cur,ed=end):
    temp = table[cur]
   
    try:
        table[cur] = [cur,temp[1],temp[2].append(cur+1),temp[3]]
    except:
        table[cur] = [cur,temp[1],[cur+1],temp[3]]
    try:
        nv = table([cur+1])
    except:
        table.append([ed+1,_,_,_])
        ed+=1
    return ed

def b_(cur,ed=end):
    temp = table[cur]
    try:
        table[cur] = [cur,temp[1],temp[2],temp[3].append(cur+1)]
    except:
        table[cur] = [cur,temp[1],temp[2],[cur+1]]
    try:
        nv = table([cur+1])
    except:
        table.append([ed+1,_,_,_])
        ed+=1
    return ed

def or_b(cur,ed=end):
    temp = table[cur]
    try:
        table[cur] = [cur,temp[1],temp[2],temp[3].append(cur+1)]
    except:
        table[cur] = [cur,temp[1],temp[2],[cur+1]]


def or_a(cur,ed=end):
    temp = table[cur]
    try:
        table[cur] = [cur,temp[1],temp[2].append(cur+1),temp[3]]
    except:
        table[cur] = [cur,temp[1],[cur+1],temp[3]]

def and_a(cur,ed=end):
    cur+=1
    temp = table[cur]
    try:
        table[cur] = [cur,temp[1],temp[2].append(cur+1),temp[3]]
    except:
        table[cur] = [cur,temp[1],[cur+1],temp[3]]
    try:
        nv = table([cur+1])
    except:
        table.append([cur+1,_,_,_])
        ed+=1
    return cur,ed

def and_b(cur,ed=end):
    cur+=1
    temp = table[cur]
    try:
        table[cur] = [cur,temp[1],temp[2],temp[3].append(cur+1)]
    except:
        table[cur] = [cur,temp[1],temp[2],[cur+1]]
    try:
        nv = table([cur+1])
    except:
        table.append([cur+1,_,_,_])
        ed+=1
    return cur,ed

def star(cur,ed=end):
    table.append([ed+1,_,_,_])
    table.append([ed+2,_,_,_])
    ed+=2
    for i in range(cur,ed):
        temp = [table[ed-i+cur][0]]+table[ed-i+cur-1][1:4]
        for j in [1,2,3]:
            try:
                temp[j] = [x+1 for x in table[ed-i+cur-1][j]]
            except:
                pass
        table[ed-i+cur] = temp
    table[cur]=[cur,_,_,_]

    temp = table[cur]
    try:
        table[cur] = [temp[0],temp[1]+[cur+1,ed],temp[2],temp[3]]
    except:
        table[cur] = [temp[0],[cur+1,ed],temp[2],temp[3]]
    
    temp = table[ed-1]
    try:
        table[ed-1] = [temp[0],temp[1]+[cur+1,ed],temp[2],temp[3]]
    except:
        table[ed-1] = [temp[0],[cur+1,ed],temp[2],temp[3]]

    return ed-1,ed


def mod_table(inp,start,cur,end,table):
    #print(inp)
    k = 0
    while k<len(inp):
        
        if inp[k]=="a":
            end = a_(cur,end)
           
        elif inp[k]=="b":
            end = b_(cur,end)
            
        elif inp[k]=="e":
            end = e_(cur,end)
        elif inp[k]==".":
            k+=1
            if inp[k]=="a":
                
                cur,end = and_a(cur,end)
            elif inp[k]=="b":
                cur,end = and_b(cur,end)
                
            elif inp[k]=="(":
                li = ["("]
                l = k
                for i in inp[k+1:]:
                    if i == "(":
                        li.append("(")
                    if i == ")":
                        try:
                            del li[-1]
                        except:
                            break
                    if len(li)==0:
                        break
                    l+=1
                m = k
                k=l+1
                cur+=1
                start,cur,end,table = mod_table(inp[m+1:l+1],start,cur,end,table)

        elif inp[k]=="|":
            k+=1
            if inp[k]=="a":
                or_a(cur,end)
                
            elif inp[k]=="b":
                or_b(cur,end)
                
            else:
                print(f"ERROR at{k }Done:{inp[:k+1]}Rem{inp[k+1:]}")
        
        elif inp[k]=="*":
            #print("in star")
            cur,end = star(cur,end)
        elif inp[k]=="(":
            li = ["("]
            l = k
            for i in inp[k+1:]:
                if i == "(":
                    li.append("(")
                if i == ")":
                    try:
                        del li[-1]
                    except:
                        break
                if len(li)==0:
                    break

                l+=1
            m = k
            k=l+1
            try:
                if inp[k+1]=="*":
                    cur_ = cur
            except:
                pass
            #print(inp[m+1:l+1])
            start,cur,end,table = mod_table(inp[m+1:l+1],start,cur,end,table)
            try:
                if inp[k+1]=="*":
                    cur = cur_
            except:
                pass
        else:
            print(f'error{k}{inp[k]}')
        k+=1
    return start,cur,end,table

def add(c,e):
    for i in range(e+1):
        
          try: 
            c[i][1].insert(0,c[i][0])
          except:
             pass 
          if c[i][1]=='-':
             c[i][1]=str(c[i][0])
          else:
             pass
   # print(c)

start,cur,end,table = mod_table(inp,start,cur,end,table)
ttograph=table

# take a copy of the table for the drawing of the graph
table_x = table


add(table,end)
print_t(table)
print()
print()









## the nfa diagram will be drawn here

# create a 2d numpy array of dtype = object with the dimensions (states x states) and initialize it by "-"
str_array = np.full((len(table_x)-1, len(table_x)-1), "-", dtype=object)

for i in range(1,len(table_x)-1):
    epsilon = table_x[i][1]
    # if the epsilon is a number stored as string then we convert that string to a int
    if len(epsilon) == 1:
        epsilon = int(epsilon)
        str_array[i-1][epsilon-1] = "e"
    else:
        for k in range (len(epsilon)):
            if epsilon != "-":
                str_array[i-1][epsilon[k]-1] = "e"
    
    a = table_x[i][2]
    for k in range (len(a)):
        if a != '-':
            # append tha value of a to the str_array at the position i-1 and a[k]-1 and seperate the values by comma
            if str_array[i-1][a[k]-1] == "-":
                str_array[i-1][a[k]-1] = "a"
            else:
                str_array[i-1][a[k]-1] = str_array[i-1][a[k]-1] + ",a"
    b = table_x[i][3]
    for k in range (len(b)):
        if b != '-':
            # append tha value of b to the str_array at the position i-1 and b[k]-1 and seperate the values by comma
            if str_array[i-1][b[k]-1] == "-":
                str_array[i-1][b[k]-1] = "b"
            else:
                str_array[i-1][b[k]-1] = str_array[i-1][b[k]-1] + ",b"
    
print (str_array)
print()

# let's draw the graph
# import MarkovChain
from markovchain import MarkovChain
# create an array of strings with the states from 1 to the number of states in the table
states = [str(i) for i in range(1, len(table_x))]

# create a copy of the str_array but replace each unique element with a number from 0 to the number of unique elements
# make it a generic code
str_array = np.where(str_array == "-", 0, str_array)
str_array = np.where(str_array == "e", 1, str_array)
str_array = np.where(str_array == "a", 0.1, str_array)
str_array = np.where(str_array == "b", 0.2, str_array)
str_array = np.where(str_array == "a,b", 0.3, str_array)
str_array = np.where(str_array == "b,a", 0.3, str_array)
str_array = np.where(str_array == "a,e", 0.4, str_array)
str_array = np.where(str_array == "e,a", 0.4, str_array)
str_array = np.where(str_array == "b,e", 0.5, str_array)
str_array = np.where(str_array == "e,b", 0.5, str_array)
print (str_array)
print()
mc = MarkovChain(str_array, states)


# draw the graph
mc.draw()