# Copyright 2020 Tianyi Xu tyx@bu.edu
# Copyright 2020 Buyuan Lin buruce@bu.edu
# Copyright 2020 Yuhan Hu yuhann@bu.edu


import sys
import numpy as np


class Puzzle:
    search_grid = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    def __init__(self, word_list, solution_temp, dirty_bit):
        # Constructor
        
        # size of the input string
        self.degree = len(word_list[0])

        # initiate the using record (dirty_bit)
        self.dirty_bit = dirty_bit
        
        # initiate the word list
        self.word_list = np.flip(np.array(word_list).T) 
        
        # update the Puzzle if possible
        self.update_word_list()

        # initiate the hints_list
        self.hints_list = [] # for each hint, construct a dictionary
        self.hints_length = [] # for each hint, store its length
        for j, hint in enumerate(solution_temp):
            self.hints_list.append({})
            for i, char in enumerate(hint):
                if char != '*':
                    self.hints_list[j][i] = char
            self.hints_length.append(len(hint))
        print("hints_list: ",self.hints_list)
        print("hints_length: ", self.hints_length)
        pass
    
    def search_word(self, hint_index, dictionary):
        result_list = []
        print("hint_index ", hint_index)

        for i, row_content in enumerate(self.word_list):
            for j, char in enumerate(row_content):
                # start searching with each char as the leading char. 
                if char in dictionary and self.dirty_bit[i][j] == 0:
                    dirty_bit = self.dirty_bit
                    dirty_bit[i][j] = 1 # mark as dirty for the leading char

                    print("\n################# try append char #################   ", char)
                    # find out all possible words with this starting char
                    self.append_char(i,j,hint_index, dictionary[char], dirty_bit, char, result_list)
                    
                    print("Finish searching of char: ", char, " at Position: ",i, " ", j)
                    dirty_bit[i][j] = 0
                    print("     dirty_bits: ", self.dirty_bit, "\n")
                    print("################# end of this search_word iteration #################\n")
        return result_list
    
    def append_char(self,i, j, hint_index, dictionary, dirty_bit, prev_string, result_list):
        print("     prev_string is: ", prev_string)
        if len(prev_string) == self.hints_length[hint_index]: 
            if 'end' in dictionary: # find a string and also in dictionary, word found!
                print("word found!!!\n")
                ## record the content of this word, the dirty_bit grid and the string
                result_list.append((self.dirty_bit.copy(), prev_string))
                return 0
            else: # find a string with right length, but not in dictionary
                print("find a string with right length, but not in dictionary")  
                return 0 # roll back one bit
        else: # need more chars to append to 
            for a, b in Puzzle.search_grid:
                # find next_char based on search_grid
                if 0 <= i+a and i+a <= self.degree-1 and 0<= j+b and j+b <= self.degree-1: 
                    if dirty_bit[i+a][j+b] == 0: # not dirty
                        next_char = self.word_list[i+a][j+b] # update with the new char
                    else: continue
                else: continue
                print('\n       next char: ', next_char)
                print(self.word_list)
                print(self.dirty_bit)
                print(dictionary)
                if self.match_hint(hint_index, prev_string, next_char): # match hint
                    if next_char in dictionary: # match dictionary
                        dirty_bit[i+a][j+b] = 1 # mark as dirty
                        print(self.dirty_bit)
                        next_string = prev_string + next_char # append to string
                        self.append_char(i+a, j+b, hint_index,
                                        dictionary[next_char],
                                        dirty_bit, next_string, result_list) # find next char
                        dirty_bit[i+a][j+b] = 0 # mark back to clean
                    else: # in hint but not in dictionary, find next char
                        print("In hint but not in dictionary, find next char")
                        continue
                else: # not match with the hint, find next char
                    print(" Not match with the hints_list, find next char")
                    continue
            return 0 # end of search_grid, no other possible next_char, end this iteration

        

    def match_hint(self, hint_index, prev_string, next_char):
        # if hints_list for this index is not empty (there exist hints)
        # and there is a hint char for this index
        if self.hints_list[hint_index] and len(prev_string) in self.hints_list[hint_index]:
            if self.hints_list[hint_index][len(prev_string)] == next_char: # if match
                return 1
            else: return 0
        else: return 1

    def update_word_list(self):
        for i, row_content in enumerate(self.dirty_bit):
            for j, key in enumerate(row_content):
                if key == 1: # key is dirty
                    # update word_list
                    self.word_list[i].pop(j) # pop the key
                    self.word_list[i].append('0') # append 0 to the end
                    # update dirty_bit
                    self.dirty_bit[i].pop(j) 
                    self.dirty_bit[i].append(0)
                else: continue


def make_dict(length, word, dictionary):
    """Make dictionary tree based on list"""
    if length == len(word) - 1:
        dictionary.setdefault(word[length], {})['end'] = True
    else:
        make_dict(length + 1, word, dictionary.setdefault(word[length], {}))


def main():
    small_word_list = open(sys.argv[1], 'r').read().split()
    # large_word_list = open(sys.argv[2]).read().split()    
    
    # small dictionary
    small_dict =  {}
    for word in small_word_list:
        make_dict(0, word, small_dict)    
    print(small_dict)

    ############################## test code ##############################
    # test input matrix
    input_matrix = ["tva", 'esb','nce']
    input_list = [list(k) for k in input_matrix]
    for l in input_list: l.reverse()
    word_list = np.flip(np.array(input_list).T) 

    # test solution template    
    solution_temp = ['**', '**s****']

    # test dirty_bit, start with all zero
    degree = len(input_matrix[0])
    dirty_bit = np.zeros((degree, degree), int)

    # construct the test Puzzle object
    puzzle_test = Puzzle(word_list, solution_temp, dirty_bit)

    # start search word with hint_index = 0, 
    #   referencing small dictionary, 
    #   unified result_list
    test_result_0 = puzzle_test.search_word(0, small_dict)
    print(test_result_0)


    # while True:
    #     puzzle = []
    #     while True:
    #         try: line = input()
    #         except EOFError: exit(0)
    #         if line:
    #             if '*' in line:
    #                 solution_temp= line.split()                    
    #                 break
    #             else: 
    #                 tmp = list(line)
    #                 tmp.reverse()
    #                 puzzle.append(tmp)
    #         else: exit(0)
    #     origin_word_list = Puzzle(puzzle, solution_temp)
    #     origin_word_list.search_word(0, small_dict)





if __name__ == "__main__":
    main()
    pass


{'t': {'v': {'exist': True}},
 'k': {'e': {'y': {'r': {'i': {'n': {'g': {'exist': True}}}}}}}, 
 'a': {'exist': True, 
        'b': {'s': {'e': {'n': {'c': {'e': {'exist': True}}}}, 
                    'o': {'l': {'u': {'t': {'e': {'exist': True, 
                                                'l': {'y': {'exist': True}}}}}}}}}}}