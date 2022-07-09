"""Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def get_phrases(level_description):
    '''
    Helper function for parse_rules. Given level_description (2D array), return
    a list of unique possible phrases satisfying the following conditions:
        - contains at least 3 words
        - contains "IS"
    '''
    all_phrases = []
    
    # parse horizontally
    for row in level_description:
        temp_phrase = []
        for obj in row:
            if len(obj) == 1 and obj[0] in WORDS:
                temp_phrase.append(obj[0])
            elif len(obj) == 0:
                if (len(temp_phrase) >= 3) and (temp_phrase not in all_phrases) and ("IS" in temp_phrase):
                    all_phrases.append(temp_phrase)
                temp_phrase = []
        
        # append if reached the end of a row
        if (len(temp_phrase) >= 3) and (temp_phrase not in all_phrases) and ("IS" in temp_phrase):
            all_phrases.append(temp_phrase)
        
        
    return all_phrases

def strip_AND(phrase, word_type):
    '''
    Helper function for parse_rules. Returns a list of filtered words in
    phrase (a list of words), given that they are of word_type (NOUNS or PROPERTIES)
    Also checks the validity of the syntax. Returns an empty list if not valid.
    '''
    stripped = []
    
    # iterate through each word in phrase (list)
    for i in range(len(phrase)):
        
        # first word must be of word_type
        if i%2 == 0:
            if phrase[i] in word_type:    # word_type refers to NOUNS or PROPERTIES
                stripped.append(phrase[i])
        
        # following word must be 'AND' conjunction
        if i%2 == 1:
            # return empty list if syntax is not met
            if phrase[i] != 'AND':
                return []
    
    return stripped
    

def parse_rules(game):
    '''
    Given game (an instance of Board), return property_rules and noun_rules dict.
    property_rules maps an object to a set of properties.
    noun_rules maps a graphical object (lowercase) to another graphical object
    (lowercase) it will change to.
    '''
    property_rules = {}
    noun_rules = {}
    
    
    # Text objects all have a default property of PUSH
    for word in WORDS:
        property_rules[word] = set()
        property_rules[word].add("PUSH")
    
    
    # Get potential phrases
        # first get horizontal phrases
    phrases = get_phrases(game.level_description)
        
        # get vertical phrases by transposing the 2D list
    columns = []
    for i in range(game.cols):
        columns.append([row[i] for row in game.level_description])
        
        # add the vertical and horizontal possible phrases
    phrases += get_phrases(columns)
    print("phrases", phrases, "\n")
    
    
    # Match rule patterns
    for phrase in phrases:
        
        # IS rules
        # slice through every 3 consecutive words to see if it matches the IS pattern
        for i in range(len(phrase)-2):
            word1 = phrase[i]
            word2 = phrase[i+1]
            word3 = phrase[i+2]
            
            # NOUN RULES
            # Ex. NOUN IS NOUN IS NOUN
            if (word1 in NOUNS) and (word2 == "IS") and (word3 in NOUNS):
                original = word1.lower()
                change_to = word3.lower()
                
                noun_rules[original] = change_to
    
            # PROPERTY RULES
            # Ex. NOUN IS PROPERTY
            if (word1 in NOUNS) and (word2 == "IS") and (word3 in PROPERTIES):
                noun = word1.lower()
                property_ = word3
                
                if noun not in property_rules:
                    property_rules[noun] = set()
                property_rules[noun].add(property_)
        
        
        # Complex cases:
            # AND rules
        if "AND" in phrase:
            
            # split on "IS": divides between phrase_1 and phrase_2 object mapping
            IS_index = phrase.index("IS")
            phrase_1 = phrase[:IS_index]
            phrase_2 = phrase[IS_index+1:]
            
            # check valid syntax in noun_phrase and property_phrase
            nouns_1 = strip_AND(phrase_1, NOUNS)
            nouns_2 = strip_AND(phrase_2, NOUNS)
            properties_2 = strip_AND(phrase_2, PROPERTIES)
            
            # Ex. NOUN AND NOUN IS NOUN AND NOUN
            # valid syntax if nouns_1 and nouns_2 are not empty lists
            if nouns_1 and nouns_2:
                # map each noun to the other noun
                for noun in nouns_1:
                    noun_rules[noun.lower()] = nouns_2[0].lower()
            
            # Ex. NOUN AND NOUN IS PROPERTY
            # valid syntax if nouns_1 and properties_2 are not empty lists
            if nouns_1 and properties_2:
                # map each noun to the property
                for noun in nouns_1:
                    property_rules[noun.lower()] = set(property_ for property_ in properties_2)
    
    print("property_rules", property_rules, "\n")
    print("noun_rules", noun_rules, "\n")
    return property_rules, noun_rules


class Board:
    def __init__(self, level_description):
        '''
        Initializer for Board instance. Contains level_description, number of rows, and cols.
        '''
        self.level_description = level_description
        self.rows = len(level_description)
        self.cols = len(level_description[0])
    
    
    def get_locations(self, obj):
        '''
        Return a list of tuple locations (x,y) for given (str) obj
        '''
        locations = []
        for i in range(self.rows):
            for j in range(self.cols):
                # check that there's more than one of the same obj in a given location
                for index in range(len(self.level_description[i][j])):
                    if self.level_description[i][j][index] == obj:
                        locations.append((i,j))
        return locations
    
    
    def is_within_boundaries(self, new_location):
        '''
        Returns boolean if the (new_x, new_y) location is:
            - within x boundaries
            - within y boundaries
        '''
        new_x, new_y = new_location
        return (0 <= new_x < self.rows) and (0 <= new_y < self.cols)
    
    
    def is_not_stop(self, property_rules, new_location):
        '''
        Returns boolean if the (new_x, new_y) location does not contain an
        object with a 'STOP' property
        '''
        new_x, new_y = new_location
        
        for obj in self.level_description[new_x][new_y]:
            if obj in property_rules:
                # If "ROCK" has both the "PUSH" and "STOP" properties,
                # then the "PUSH" behavior takes priority
                if "PUSH" in property_rules[obj]:
                    continue
                if "STOP" in property_rules[obj]:
                    return False
        return True     # defaults to True after exiting loop
    
    
    def move_obj(self, obj, current, direction):
        '''
        Move a given obj (str) from location current (tuple (x,y)) in
        the given direction (tuple (dx,dy))
        '''
        # unpack x and y components
        x, y = current
        dx, dy = direction
    
        # remove the object from its current location
        self.level_description[x][y].remove(obj) 
        
        # add the object to its new location
        self.level_description[x+dx][y+dy].append(obj)
    
    
    def get_push_chain(self, property_rules, current, direction):
        '''
        PUSH SCENARIO:
            Returns a dictionary obj_sequence (mapping an obj (str) to a set of tuple locations)
            of all the objects that will be pushed by you object (str) in current (tuple) location
        '''
        x, y = current
        dx, dy = direction
        
        # get all the objects who are in the chain line, excluding the YOU object
        obj_sequence = {}   # maps object (str) to a list of locations (tuple)
        
        
        # loop to find the chain of items to be pushed
        while (self.is_within_boundaries((x+dx, y+dy)) and
               self.is_not_stop(property_rules, (x+dx, y+dy)) and
               self.level_description[x+dx][y+dy] != []):
            
            # position where the object might be pushed
            next_obj = self.level_description[x+dx][y+dy]
            
            # iterate through each object in the next position
            for elt in next_obj:
                
                exists_push = False
                
                # add object to obj_sequence if it has PUSH property
                if (elt in property_rules) and ("PUSH" in property_rules[elt]):
                    
                    exists_push = True  # change to True if there exists a push chain
                    
                    if elt not in obj_sequence:
                        obj_sequence[elt] = []
                    obj_sequence[elt].append((x+dx, y+dy))
                    print("generic obj_sequence", obj_sequence)
                    
                    # also check that the pushed object can pull another object
                    current_obj = self.level_description[x][y]
                    print("current_obj", current_obj)
                    for elt in current_obj:
                        
                        # add object to obj_sequence if it has PULL property
                        if (elt in property_rules) and ("PULL" in property_rules[elt]):
                            if elt not in obj_sequence:
                                obj_sequence[elt] = []
                            obj_sequence[elt].append((x,y))
                
             # stop checking for more push objects if the chain breaks
            if not exists_push:
                print("obj_sequence", obj_sequence)
                return obj_sequence
                
            x = x+dx
            y = y+dy
        
        print("obj_sequence", obj_sequence)
        return obj_sequence
    
    
    def get_pull_chain(self, property_rules, current, direction):
        '''
        PULL SCENARIO:
            Returns a dictionary obj_sequence (mapping an obj (str) to a list of tuple locations)
            of all the objects that will be pulled by you object (str) in the "current" location
        '''
        x, y = current
        dx, dy = direction
        
        # get all the objects who have pull property
        obj_sequence = {}   # maps object (str) to a list of locations (tuple)
        

        # move backwards (opposite of direction) to find a potential pull object
        while (self.is_within_boundaries((x-dx, y-dy)) and
               self.level_description[x-dx][y-dy] != []):
            
            # position of the object that might be pulled
            prev_obj = self.level_description[x-dx][y-dy]
            
            # iterate through each object in the previous position
            for elt in prev_obj:
                
                # if object has PULL property
                if (elt in property_rules) and ("PULL" in property_rules[elt]):
                    
                    # check if it can be pulled to a valid position
                    if self.is_within_boundaries((x, y)) and self.is_not_stop(property_rules, (x, y)):
                        
                        if elt not in obj_sequence:
                            obj_sequence[elt] = []
                        obj_sequence[elt].append((x-dx, y-dy))
                        
                        
                        # Also check that the pulled object can push another one
                        current_obj = self.level_description[x][y]
                        for elt in current_obj:
                            if (elt in property_rules) and ("PUSH" in property_rules[elt]):
                                if elt not in obj_sequence:
                                    obj_sequence[elt] = []
                                obj_sequence[elt].append((x, y))
                                    
                    # stop checking for more pull objects if the chain breaks
                    else:
                        return obj_sequence
                            
            x = x-dx
            y = y-dy
        
        return obj_sequence
        
        
    
    def move_chain(self, obj_sequence, direction):
        '''
        Given an obj_sequence dict (maps obj to a tuple of locations), moves
        all the objects in the given direction.
        '''
        for obj, locations in obj_sequence.items():
            for loc in locations:                
                self.move_obj(obj, loc, direction)
                
    
    def pull(self, you, property_rules, current, direction):
        '''
        Given the 'you' object with property YOU, move all the associated objects
        that can be PULLed by you.
        '''
        pull_sequence = self.get_pull_chain(property_rules, current, direction)
        self.move_chain(pull_sequence, direction)
        print(f"pull_sequence from {current}:", pull_sequence)
        
        
    def push(self, you, property_rules, current, direction):
        '''
        Given the 'you' object with property YOU, move all the associated objects
        that can be PUSHed by you.
        '''
        
        dx, dy = direction
        push_sequence = self.get_push_chain(property_rules, current, direction)
        
        # check that each elt in obj sequence has a valid new position
        for obj, locations in push_sequence.items():
            for loc in locations:
                x, y = loc  # current location of each push obj
                if not (self.is_within_boundaries((x+dx, y+dy))
                        and self.is_not_stop(property_rules, (x+dx, y+dy))):
                    return False    # means that YOU also can't be moved
            
        self.move_chain(push_sequence, direction)
        print(f"push_sequence from {current}:", push_sequence)
                
    
    def move(self, property_rules, direction):
        '''
        Given the property_rules (dict) and direction, move all the YOU objects
        according to rules in lab 10.
        '''
        # unpack direction components
        dx, dy = direction_vector[direction]
        
        # get all the unique objects with property YOU
        YOU_objects = {obj for obj in property_rules if "YOU" in property_rules[obj]}
        
        # loop through each YOU object
        for you in YOU_objects:
            # get a list of tuples
            locations = self.get_locations(you)
            
            # loop through each location of the YOU object
            for loc in locations:
                # unpack x,y components
                you_x, you_y = loc
                
                # check if the new position is a valid move
                if (self.is_within_boundaries((you_x+dx, you_y+dy)) and
                    self.is_not_stop(property_rules, (you_x+dx, you_y+dy))):
                    
                    
                    next_obj = self.level_description[you_x+dx][you_y+dy]
                    try:
                        prev_obj = self.level_description[you_x-dx][you_y-dy]
                    except IndexError:
                        prev_obj = []
                    
                    
                    # if next_obj and prev_obj is empty, simply move the YOU object
                    if len(next_obj) == len(prev_obj) == 0:
                        self.move_obj(you, (you_x,you_y), (dx,dy))
                    
                    
                    # if next obj and prev obj != 0: push and pull
                    elif len(next_obj) != 0 and len(prev_obj) != 0:
                        # push is not allowed, so YOU also can't move
                        if self.push(you, property_rules, (you_x,you_y), (dx,dy)) == False:
                            continue
                        self.pull(you, property_rules, (you_x,you_y), (dx,dy))
                        self.move_obj(you, (you_x,you_y), (dx,dy))
                    
                    
                    # elif next_obj != 0: push
                    elif len(next_obj) != 0:
                        # push is not allowed, so YOU also can't move
                        if self.push(you, property_rules, (you_x,you_y), (dx,dy)) == False:
                            continue
                        self.move_obj(you, (you_x,you_y), (dx,dy))
                    
                    
                    # elif prev_obj != 0: pull
                    elif len(prev_obj) != 0:
                        self.pull(you, property_rules, (you_x,you_y), (dx,dy))
                        self.move_obj(you, (you_x,you_y), (dx,dy))
                    

    def is_defeat(self, property_rules):
        '''
        Eliminate all YOU objects that land on a square where an object has
        property DEFEAT.
        '''
        for r in range(self.rows):
            for c in range(self.cols):
                square = self.level_description[r][c]
                
                you_objs = [obj for obj, property_ in property_rules.items() if "YOU" in property_]
                defeat_objs = [obj for obj, property_ in property_rules.items() if "DEFEAT" in property_]
                
                # Check if there is a DEFEAT object in the given square
                is_DEFEAT = False
                for elt in square:
                    if elt in defeat_objs:
                        is_DEFEAT = True
                        break
                
                # if there's a DEFEAT object, eliminate all the YOU objects
                defeated_square = []
                if is_DEFEAT:
                    for obj in square:
                        if obj not in you_objs:
                            defeated_square.append(obj)
                    self.level_description[r][c] = defeated_square
        
        
    
    def is_win(self, property_rules):
        '''
        Return True if a YOU object lands on a square that contains an object
        with a WIN property. Else returns False.
        '''
        for r in range(self.rows):
            for c in range(self.cols):
                square = self.level_description[r][c]
                
                you_objs = [obj for obj, property_ in property_rules.items() if "YOU" in property_]
                win_objs = [obj for obj, property_ in property_rules.items() if "WIN" in property_]
                
                # Check if there is a WIN object in the given square
                is_WIN = False
                for elt in square:
                    if elt in win_objs:
                        is_WIN = True
                        break
                
                # if there's a WIN object, return True if you find a YOU object
                if is_WIN:
                    for obj in square:
                        if obj in you_objs:
                            return True
        return False    # default to False if you exited the loop
    
    
    def adjust_nouns(self, noun_rules):
        '''
        Given noun_rules (dict) mapping, change all key object to the value
        object.
        '''
        for r in range(self.rows):
            for c in range(self.cols):
                for i in range(len(self.level_description[r][c])):
                    current_obj = self.level_description[r][c][i]
                    if current_obj in noun_rules:
                        self.level_description[r][c][i] = noun_rules[current_obj]
    
    
def new_game(level_description):
    """
    Given a description of a game state, create and return a Board instance
    that contains level_description.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).
    """
    return Board(level_description)


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    property_rules, noun_rules = parse_rules(game)   # evaluate the initial rules

    game.move(property_rules, direction)     # move according to initial rules and direction
    
    property_rules, noun_rules = parse_rules(game)   # Parse the text objects and update the rules accordingly
    game.adjust_nouns(noun_rules)    # Adjust object types based on rules whose predicate is a noun
    
    game.is_defeat(property_rules)  # Eliminate any objects that are on DEFEAT squares
    
    return game.is_win(property_rules)  # Check if player won


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game.level_description


def beautify(level):
    result = ""
    for line in level:
        result += str(line) + "\n"
    return result


if __name__=="__main__":
    
    
    level = [
              [
                ["COMPUTER"],
                ["IS"],
                ["YOU"],
                [],
                [],
                [],
                [],
                ["SNEK"],
                ["IS"],
                ["STOP"],
                ["AND"],
                ["BUG"]
              ],
              [[], [], [], [], [], [], [], [], [], [], [], ["AND"]],
              [[], [], [], [], [], [], [], [], [], [], [], ["YOU"]],
              [["BUG"], [], [], [], [], [], ["computer"], ["snek"], [], [], [], []],
              [["IS"], [], [], [], [], [], [], [], [], [], [], []],
              [["PUSH"], [], [], [], [], [], [], [], [], [], [], []]
            ]




    game=Board(level)
    parse_rules(game)
