# Copyright 2020 Tianyi Xu tyx@bu.edu
# Copyright 2020 Buyuan Lin buruce@bu.edu
# Copyright 2020 Yuhan Hu yuhann@bu.edu


import sys
import numpy as np


class Puzzle:
    search_grid = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    def __init__(self, word_list, solution_temp):
        # Constructor
        self.found = 0
        self.result = ['0']* len(solution_temp)
        self.degree = len(word_list[0])
        # initiate the used record
        self.dirty_bit = np.zeros((self.degree, self.degree), int)
        
        # initiate the word list
        self.word_list = np.flip(np.array(word_list).T) 
        

        print(self.word_list)
        print(solution_temp)
        
        # initiate the hints list
        self.hints = []
        self.hints_length = []
        for j, hint in enumerate(solution_temp):
            self.hints.append({})
            for i, char in enumerate(hint):
                if char != '*':
                    self.hints[j][i] = char
            self.hints_length.append(len(hint))
        print("hints: ",self.hints)
        print("length: ", self.hints_length)
        pass
    
    def search_word(self, hint_index, dictionary):
        print("hint_index ", hint_index)

        for i, row_content in enumerate(self.word_list):
            for j, char in enumerate(row_content):
                # start searching with each char as the starting. 
                if char in dictionary and self.dirty_bit[i][j] == 0:
                    dirty_bit = self.dirty_bit
                    dirty_bit[i][j] = 1
                    print("\n try append char ", char)
                    tmp = self.append_char(i,j,hint_index, dictionary[char], dirty_bit, char)
                    print("we are back to search word", tmp)
                    print("dirty_bits: ", self.dirty_bit)
                    print("end of this search_word \n")
                    return 1
    
    def append_char(self,i, j, hint_index, dictionary, dirty_bit, prev_string):
        print(prev_string)
        if len(prev_string) == self.hints_length[hint_index]:
            if 'end' in dictionary:
                print("found")
                self.result[hint_index] = prev_string
                self.dirty_bit = dirty_bit
                self.found = 1
                return 1
            else: 
                print("case 2") # found ab, but no ab in dict. needs to pick the next start
                return 0
        else:
            for a, b in Puzzle.search_grid:
                if 0 <= i+a and i+a <= self.degree-1 and 0<= j+b and j+b <= self.degree-1: 
                    if dirty_bit[i+a][j+b] == 0: 
                        next_char = self.word_list[i+a][j+b]
                    else: continue
                else: continue
                print('\n       next char: ', next_char)
                print(dictionary)
                if self.match_hint(hint_index, prev_string, next_char):
                    if next_char in dictionary:
                        dirty_bit[i+a][j+b] = 1
                        print(self.dirty_bit)
                        next_string = prev_string + next_char
                        next_itr = self.append_char(i+a, j+b, hint_index,
                                        dictionary[next_char],
                                        dirty_bit, next_string)
                        if next_itr == 0: 
                            print("This char not in hint or sub_dictionary")
                            dirty_bit[i+a][j+b] = 0
                        elif next_itr == 1: 
                            print("Hit in hint or sub_dict")
                            return 1
                    else: continue
                else: continue
            
            else: 
                print(" case 1 ")
                return 0

        

    def match_hint(self, hint_index, prev_string, next_char):

        # if hints for this index is not empty
        if self.hints[hint_index]:
            if len(prev_string) in self.hints[hint_index]:
                if self.hints[hint_index][len(prev_string)] == next_char:
                    return 1
                else: return 0
            else: return 1
        else:
            return 1



    def update_word_list(self):
        pass


def make_dict(length, word, dictionary):
    """Make dictionary tree based on list"""
    if length == len(word) - 1:
        dictionary.setdefault(word[length], {})['end'] = True
    else:
        make_dict(length + 1, word, dictionary.setdefault(word[length], {}))


def main():
    small_word_list = open(sys.argv[1], 'r').read().split()
    # large_word_list = open(sys.argv[2]).read().split()    
    small_dict =  {}
    for word in small_word_list:
        make_dict(0, word, small_dict)    
    print(small_dict)

    input_matrix = ["tva", 'esb','nce']
    input_list = [list(k) for k in input_matrix]
    print(input_list)
    for l in input_list: l.reverse()
    print(input_list)
    print("\nTry without tips: \n")
    solution_temp = ['**', '*******']
    puzzle_test = Puzzle(input_list, solution_temp)
    for i in range(len(solution_temp)):
        puzzle_test.search_word(i, small_dict)
    print("finished first try \n")
    
    print("\nTry with tips: \n")
    solution_temp = ['**', '**s****']
    puzzle_test = Puzzle(input_list, solution_temp)
    for i in range(len(solution_temp)):
        puzzle_test.search_word(i, small_dict)
    print("finished second try \n")
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