assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    global rows
    rows = 'ABCDEFGHI'
    global cols
    cols = '123456789'
    global dan
    dan = cross(rows,cols)
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    diagonal_units = [['A1','B2','C3','D4','E5','F6','G7','H8','I9'],['A9','B8','C7','D6','E5','F4','G3','H2','I1']]
    global unitlist
    da = []
    w = 0
    for i in range(9):
        if grid[w] != '.':
            da.append(grid[w])
        else:
            da = da
        w = w + 10



    e = 0
    for i in da:
        e = 0
        for p in da:
            if p == i:
                e = e +1
            else:
                e = e
        if e == 1:
            unitlist = row_units + column_units + square_units + diagonal_units
           
        else:
            unitlist = row_units + column_units + square_units
            break

    db = []
    v = 8
    for i in range(9):
        if grid[v] != '.':
            db.append(grid[v])
        else:
            db = db
        v = v + 8


    g = 0
    for i in db:
        g = 0
        for p in db:
            
            if p == i:
                g = g +1
            else:
                g = g
        if g == 1:
            unitlist = row_units + column_units + square_units + diagonal_units

        else:
            unitlist = row_units + column_units + square_units
            break

    global units
    units= dict((s, [u for u in unitlist if s in u]) for s in dan)
    global peers
    peers= dict((s, set(sum(units[s],[]))-set([s])) for s in dan)

        
    values = grid_values(dan, grid)
    values = search(values)
    #return values
    print (display(values))

def cross(A, B):
    return [s+t for s in A for t in B]
    "Cross product of elements in A and elements in B."

    
def grid_values(dan , grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    a = []
    for i in grid:
        if i == '.':
            a.append( '123456789')
        else:
            a.append(i)
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    return dict(zip(dan, a))
    return values

    pass


def eliminate(values):
    '''eliminates digits from other boxes in a box's peers once the digit have been assigned to a box'''

    p = []
    for i in values:
        if len(values[i]) == 1:
            p.append(i)
    o = ''
    for i in p:
        o = values[i]
        for e in peers[i]:
            #assign_value(values, e, values[e].replace(o,''))
            values[e] = values[e].replace(o,'')
    return values
def only_choice(values):
    '''Assigns a digit to a particular box once it's determined it belongs to that box'''
    for unit in unitlist:
        for i in '123456789':
            s = [e for e in unit if i in values[e]]
            
            if len(s) == 1:
                assign_value(values, s[0], i)
                values[s[0]] = i
    return values
    pass

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    big =[] #set of all keys with length 2
    k = []
    g = values.keys()
    p = values.values()
    j = len(values)
    for i in g:
        if len (values[i]) == 2:
            big.append(i)
        else:
            big = big
            
            
    for i in big:
        d = units[i]
        for e in d:
            if counter(values, i, e) == 'yes':
                remove(values, i, e)
            else:
                big == big
    return values
    

def remove(values, i, e):
    s = []
    for a in values[i]:
        s.append(a)
    for o in e:
        k = []
        for h in values[o]:
            k.append(h)
        if len(values[o])>1 and s != k :
            t = []
            for y in values[o]:
                t.append(y)
            for r in s:
                if r in t:
                    t.remove(r)
                else:
                    t = t
            p = ''
            for i in t:
                p =  p+i
            values[o] = p
            #assign_value(values, o, p)
        
   
        else:
            values[o] = values[o]
    return values

            

def counter(values,i,e):
    u = 0
    for f in e:
        if values[i] == values[f]:
            u = u + 1
        else:
            u = u
    if u == 2:
        return 'yes'
    else:
        return 'no'




def reduce_puzzle(values):
    '''uses all the functions in loops to reduce the puzzle'''
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        #Your code here: Use the naked twins strategy
        values = (naked_twins(values))
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

    pass


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = (reduce_puzzle(values))
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in dan): 
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in dan if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt
    pass



def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in dan)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

    #pass




solve('8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..')


#print(assignments)
