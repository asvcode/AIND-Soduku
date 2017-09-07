assignments = []

def cross(rows, cols):
    """We'll start by writing a helper function, cross(a, b), which, given two strings a and b.
    It will return the list formed by all the possible concatenations of a letter s in string a
    with a letter t in string b.
    """
    return [s+t for s in rows for t in cols]
    
#definitions
rows = 'ABCDEFGHI' #rows
cols = '123456789' #columns
#b = boxes ie A1
#d = digit ie 1
#u = unit ie [A1, B1, C1, D1, E1, F1, G1, H1, I1]
#define boxes
boxes = cross(rows, cols)
#define rows
row_units = [cross(r, cols) for r in rows]
#define columns
column_units = [cross(rows, c) for c in cols]
#define squares
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
cols_rev = cols[::-1]
#define 2 additional diagonal units for diagonal soduku
d1_units = [[rows[i]+cols[i] for i in range(len(rows))]]
d2_units = [[rows[i]+cols_rev[i] for i in range(len(rows))]]
#set up diagonal soduku
do_diagonal = 1 #this can be set to 0 for non-diagonal soduku
if do_diagonal == 1:
    unitlist = row_units + column_units + square_units + d1_units + d2_units
else:
    unitlist = row_units + column_units + square_units
#define units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
#define peers
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    pot_twins = [box for box in values.keys() if len(values[box]) == 2]
    naked_twins = [[box1,box2] for box1 in pot_twins \
                    for box2 in peers[box1] \
                    if set(values[box1])==set(values[box2]) ]
    #for each twin get peers
    for i in range(len(naked_twins)):
        box1 = naked_twins[i][0]
        box2 = naked_twins[i][1]
        peers1 = set(peers[box1])
        peers2 = set(peers[box2])
        peers_int = peers1 & peers2
    # Eliminate the naked twins as possibilities for their peers
        for peer_val in peers_int:
            if len(values[peer_val])>1:
                for rm_val in values[box1]:
                    values = assign_value(values, peer_val, values[peer_val].replace(rm_val,''))
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            values.append(c)
        if c == '.':
            values.append(digits)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[k]) == 1 for k in boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    new, key = min((len(values[k]), k) for k in boxes if len(values[k]) > 1)
    # unsolved_values = {k: len(v) for k, v in values.items() if len(values[k]) > 1}

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for num in values[key]:
        potential_values = values.copy()
        # potential_values[key] = num
        assign_value(potential_values, key, num)
        success = search(potential_values)
        if success:
            return success

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use Eliminate strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Use Search Strategy
        #values = search(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
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
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
