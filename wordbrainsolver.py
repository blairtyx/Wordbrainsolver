# Copyright 2020 Tianyi Xu tyx@bu.edu
# Copyright 2020 Buyuan Lin buruce@bu.edu
# Copyright 2020 Yuhan Hu yuhann@bu.edu


import sys
import numpy as np


class Puzzle:
    search_grid = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    def __init__(self, word_list, hints_list, hints_length, dirty_bit):
        # Constructor
        
        # size of the input string
        self.degree = len(word_list[0])

        # initiate the using record (dirty_bit)
        self.dirty_bit = dirty_bit
        
        # initiate the word list
        self.word_list = word_list
        
        # update the Puzzle if possible
        self.update_word_list()

        # initiate the hints_list
        self.hints_list = hints_list # for each hint, construct a dictionary
        self.hints_length = hints_length # for each hint, store its length
        print("hints_list: ",self.hints_list)
        print("hints_length: ", self.hints_length)
        pass
    
    def search_word(self, hint_index, dictionary, origin_dictionary, result_list):
        print("////////////////hint_index ", hint_index)
        print("////////////////dirty_bit ", self.dirty_bit)
        print("////////////////word_list ", self.word_list)
        for i, row_content in enumerate(self.word_list):
            for j, char in enumerate(row_content):
                # start searching with each char as the leading char. 
                if char in dictionary and self.dirty_bit[i][j] == 0:
                    dirty_bit = self.dirty_bit
                    dirty_bit[i][j] = 1 # mark as dirty for the leading char

                    print("\n################# try append char #################   ", char)
                    # find out all possible words with this starting char
                    self.append_char(i,j,hint_index, dictionary[char], origin_dictionary,dirty_bit, char, result_list)
                    
                    print("Finish searching of char: ", char, " at Position: ",i, " ", j)
                    dirty_bit[i][j] = 0
                    print("     dirty_bits: ", self.dirty_bit, "\n")
                    print("     word_list: ", self.word_list)
                    print("################# end of this search_word iteration #################\n")
    
    def append_char(self,i, j, hint_index, dictionary,origin_dictionary, dirty_bit, prev_string, result_list):
        print("     prev_string is: ", prev_string)
        if len(prev_string) == self.hints_length[hint_index]: 
            if 'end' in dictionary: # find a string and also in dictionary, word found!
                print("word found!!!\n")
                print("hint_index is: ", hint_index)

                # if hint_index == len(self.hints_length)-1: # find the last word
                result_list.append([self.dirty_bit.copy(), self.word_list.copy(), prev_string])
            #         return 0
            #     else:
            #         # result_list.append([self.dirty_bit.copy(),self.word_list.copy(), prev_string]) 
            #         # print("now the result list is: ", result_list)
            #         # print("before update word_list: ", self.word_list)
            #         # print("before update dirty bits: ", self.dirty_bit)
            #         # self.update_word_list()
            #         # print("after update word_list: ", self.word_list)
            #         # print("after update dirty bits: ", self.dirty_bit)
                    
            #         # self.search_word(hint_index+1, origin_dictionary,origin_dictionary, result_list)
            #         # print("**** here it is *****")
            #         # return 0
            # else: # find a string with right length, but not in dictionary
            #     print("find a string with right length, but not in dictionary")  
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
                                        dictionary[next_char],origin_dictionary,
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
        delete_list = [[] for _ in range(self.degree)]
        print(delete_list)
        for i, row_content in enumerate(self.dirty_bit):
            for j, key in enumerate(row_content):
                if key == 1: # key is dirty
                    delete_list[i].append(j)
                else: continue
        print(delete_list)
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
    print(input_list)
    for l in input_list: l.reverse()
    print(input_list)
    word_list = np.flip(np.array(input_list).T) 
    print(word_list)
    # test solution template    
    hints_list = []
    hints_length = []
    solution_temp = ['**', '**s****']
    for j, hint in enumerate(solution_temp):
            hints_list.append({})
            for i, char in enumerate(hint):
                if char != '*':
                    hints_list[j][i] = char
            hints_length.append(len(hint))

    # test dirty_bit, start with all zero
    degree = len(input_matrix[0])
    dirty_bit = np.zeros((degree, degree), int)

    # construct the fist Puzzle object
    puzzle_test = Puzzle(word_list, hints_list, hints_length, dirty_bit)

    # start search word with hint_index = 0, 
    #   referencing small dictionary, 
    #   unified result_list
    result_list = []

    puzzle_test.search_word(0, small_dict,small_dict, result_list)
    

    print(result_list)
    

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