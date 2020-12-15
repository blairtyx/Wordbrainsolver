# Copyright 2020 Tianyi Xu tyx@bu.edu
# Copyright 2020 Buyuan Lin buruce@bu.edu
# Copyright 2020 Yuhan Hu yuhann@bu.edu


import sys
import numpy as np


class Puzzle:
    search_grid = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    hints_length = []
    hints_list = []
    def __init__(self, word_list, dirty_bit, prev_str_list):
        # Constructor
        # print(word_list)
        # print(dirty_bit)
        # print(prev_str_list)



        # size of the input string
        self.degree = len(word_list[0])

        # store the previous iterations' string list
        self.prev_str_list = prev_str_list

        # initiate the using record (dirty_bit)
        self.dirty_bit = dirty_bit
        
        # initiate the word list
        self.word_list = word_list
        
        # update the Puzzle if possible
        self.update_word_list()

        pass
    
    def search_word(self, hint_index, dictionary,  result_list):
        # print("////////////////hint_index ", hint_index)
        # print("////////////////dirty_bit ", self.dirty_bit)
        # print("////////////////word_list ", self.word_list)
        for i, row_content in enumerate(self.word_list):
            for j, char in enumerate(row_content):
                # start searching with each char as the leading char. 
                if char in dictionary and self.dirty_bit[i][j] == 0:
                    dirty_bit = self.dirty_bit
                    dirty_bit[i][j] = 1 # mark as dirty for the leading char

                    # print("\n################# try append char #################   ", char)
                    # find out all possible words with this starting char
                    self.append_char(i,j,hint_index, dictionary[char],dirty_bit, char, result_list)
                    
                    # print("Finish searching of char: ", char, " at Position: ",i, " ", j)
                    dirty_bit[i][j] = 0
                    # print("     dirty_bits: ", self.dirty_bit, "\n")
                    # print("     word_list: ", self.word_list)
                    # print("################# end of this search_word iteration #################\n")
    
    def append_char(self,i, j, hint_index, dictionary,dirty_bit, prev_string, result_list):
        # print("     prev_string is: ", prev_string)
        if len(prev_string) == Puzzle.hints_length[hint_index]: 
            if 'end' in dictionary: # find a string and also in dictionary, word found!
                # print("word found!!!\n")
                # print("hint_index is: ", hint_index)

                # update prev_str_list
                self.prev_str_list.append(prev_string)

                dirty_bit_ins = self.dirty_bit.copy()
                # print(dirty_bit_ins)
                word_list_ins = self.word_list.copy()
                # print(word_list_ins)
                prev_str_list_ins = self.prev_str_list.copy()
                
                
                result_list.append([dirty_bit_ins, word_list_ins, prev_str_list_ins])
                return 1 # roll back one bit and pop prev_string

        else: # need more chars to append to 
            for a, b in Puzzle.search_grid:
                # find next_char based on search_grid
                if 0 <= i+a and i+a <= self.degree-1 and 0<= j+b and j+b <= self.degree-1: 
                    if dirty_bit[i+a][j+b] == 0: # not dirty
                        next_char = self.word_list[i+a][j+b] # update with the new char
                    else: continue
                else: continue
                # print('\n       next char: ', next_char)
                # print(self.word_list)
                # print(self.dirty_bit)
                if self.match_hint(hint_index, prev_string, next_char): # match hint
                    if next_char in dictionary: # match dictionary
                        dirty_bit[i+a][j+b] = 1 # mark as dirty
                        # print(self.dirty_bit)
                        next_string = prev_string + next_char # append to string
                        tmp = self.append_char(i+a, j+b, hint_index,
                                        dictionary[next_char],
                                        dirty_bit, next_string, result_list) # find next char
                        dirty_bit[i+a][j+b] = 0 # mark back to clean
                        if tmp == 1:
                            self.prev_str_list.pop()
                    else: # in hint but not in dictionary, find next char
                        # print("In hint but not in dictionary, find next char")
                        continue
                else: # not match with the hint, find next char
                    # print(" Not match with the hints_list, find next char")
                    continue
            return 0 # end of search_grid, no other possible next_char, end this iteration

        

    def match_hint(self, hint_index, prev_string, next_char):
        # if hints_list for this index is not empty (there exist hints)
        # and there is a hint char for this index
        if Puzzle.hints_list[hint_index] and len(prev_string) in Puzzle.hints_list[hint_index]:
            if Puzzle.hints_list[hint_index][len(prev_string)] == next_char: # if match
                return 1
            else: return 0
        else: return 1

    def update_word_list(self):
        delete_list = [[] for _ in range(self.degree)]
        # print(delete_list)
        for i, row_content in enumerate(self.dirty_bit):
            for j, key in enumerate(row_content):
                if key == 1: # key is dirty
                    delete_list[i].append(j)
                else: continue
        # print(delete_list)
        for k,m in enumerate(delete_list):
            if len(m) > 0:
                self.word_list[k] = np.append(np.delete(self.word_list[k], m), ['0'] * len(m))
                self.dirty_bit[k] = np.append(np.delete(self.dirty_bit[k], m), [1 ]* (len(m)))

def make_dict(length, word, dictionary):
    """Make dictionary tree based on list"""
    if length == len(word) - 1:
        dictionary.setdefault(word[length], {})['end'] = True
    else:
        make_dict(length + 1, word, dictionary.setdefault(word[length], {}))

def find_word_list(itr, stop_num, input_result_list, dictionary, output_result_list, degree):
    if input_result_list: # not empty
        for content in input_result_list:
            result_list = []
            if itr == stop_num:
                output_result_list.append(content[2])                
            else:
                next_puzzle = Puzzle(content[1], content[0], content[2])
                next_puzzle.search_word(itr,dictionary, result_list)
                find_word_list(itr+1, stop_num, result_list, dictionary, output_result_list, degree)

        
def main():
    small_word_list = open(sys.argv[1], 'r').read().split()
    large_word_list = open(sys.argv[2], 'r').read().split()
    
    # small dictionary
    small_dict =  {}
    for word in small_word_list:
        make_dict(0, word, small_dict)

    large_dict = {}
    for word in large_word_list:
        make_dict(0, word, large_dict)
    ############################## test code ##############################
    # test input matrix
    input_matrix = ["yson", 'elnn','hnca','olab']
    input_list = [list(k) for k in input_matrix]
    print(input_list)
    for l in input_list: l.reverse()
    print(input_list)
    word_list = np.flip(np.array(input_list).T) 
    print(word_list)
    # test solution template    
    hints_list = []
    hints_length = []
    solution_temp = ['*****', '*****', '******']
    for j, hint in enumerate(solution_temp):
            hints_list.append({})
            for i, char in enumerate(hint):
                if char != '*':
                    hints_list[j][i] = char
            hints_length.append(len(hint))

    Puzzle.hints_length = hints_length
    Puzzle.hints_list = hints_list
    # test dirty_bit, start with all zero
    degree = len(input_matrix[0])
    dirty_bit = np.zeros((degree, degree), int)

    # construct the fist Puzzle object
    puzzle_test = Puzzle(word_list, dirty_bit, [])

    # start search word with hint_index = 0, 
    #   referencing small dictionary, 
    #   unified result_list
    first_result_list = []

    puzzle_test.search_word(0, small_dict, first_result_list)
    
    universal_list = []
    # print(first_result_list)
    find_word_list(1, len(hints_length), first_result_list, small_dict, universal_list, degree)
    
    final_result = []
    [final_result.append(x) for x in universal_list if x not in final_result]
    print(final_result)


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
