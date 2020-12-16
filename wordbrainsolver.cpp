// Copyright 2020 Tianyi Xu tyx@bu.edu
// Copyright 2020 Buyuan Lin buruce@bu.edu
// Copyright 2020 Yuhan Hu yuhann@bu.edu

#include<unordered_map>
#include<unordered_set>
#include<set>
#include<iostream>
#include<string>
#include<vector>
#include<fstream>
#include<ostream>

using std::cout;
using std::set;
using std::string;
using std::vector;
using std::unordered_map;
using std::unordered_set;
using std::ostream;

struct Search_result{
    vector<vector<char>> word_list;
    vector<vector<bool>> dirty_bit;
    string prev_string;
    Search_result(vector<vector<char>> word_list,
                            vector<vector<bool>> dirty_bit,
                            string prev_string);
    
};


ostream& operator<<(ostream &os, const Search_result &result_ins){
    os << "dirty_bit is:\n";
    for(auto itr = result_ins.dirty_bit.begin(); itr != result_ins.dirty_bit.end(); ++itr) {
        for (auto i = itr->begin(); i != itr->end(); ++i){
            os << *i << " ";
        }
        os << "\n";
    }
    os << "word_list is:\n";
    for(auto itr = result_ins.word_list.begin(); itr != result_ins.word_list.end(); ++itr) {
        for (auto i = itr->begin(); i != itr->end(); ++i){
            os << *i << " ";
        }
        os << "\n";
    }
    os << "prev_string is: " << result_ins.prev_string << "\n";
    return os;
}


Search_result::Search_result(vector<vector<char>> word_list,
                            vector<vector<bool>> dirty_bit,
                            string prev_string){
    this->word_list = word_list;
    this->dirty_bit = dirty_bit;
    this->prev_string = prev_string;
}


class Puzzle {
private:
    vector<vector<int>> search_grid{{-1, -1}, {-1, 0}, {-1, 1}, 
                                    {0, -1}, {0, 1}, 
                                    {1, -1}, {1, 0}, {1, 1}};
    vector<vector<char>> word_list;
    vector<vector<bool>> dirty_bit;
    string prev_string_collect;
    vector<unordered_map<int, char>> hints_list;
    vector<int> hint_length;
    int degree;

public:
    Puzzle(vector<vector<char>> word_list, 
            vector<vector<bool>> dirty_bit, 
            string prev_str_collect,
            vector<unordered_map<int, char>> hints_list,
            vector<int> hints_length);
    void search_word(int hint_index,
                    unordered_set<string> *dictionary,
                    vector<Search_result> *result_list);
    void append_char(int i, 
                        int j, 
                        int hint_index, 
                        unordered_set<string> *dictionary,
                        string prev_string,
                        vector<Search_result> *result_list);

    bool match_hint(int *hint_index,
                        string prev_string,
                        char *next_char);
    void update_word_list();
    
};

Puzzle::Puzzle(vector<vector<char>> word_list, 
            vector<vector<bool>> dirty_bit, 
            string prev_str_collect,
            vector<unordered_map<int, char>> hints_list,
            vector<int> hints_length){
    this->word_list = word_list;
    this->dirty_bit = dirty_bit;
    this->prev_string_collect = prev_string_collect;
    this->degree = word_list.size();
    this->hints_list = hints_list;
    this->hint_length = hints_length;
    this->update_word_list();
}

void Puzzle::search_word(int hint_index, 
                        unordered_set<string> *dictionary,
                        vector<Search_result> *result_list){
    for(int i = 0; i < this->degree; i++) {
        for (int j = 0; j < this->degree; j++) {
            char *current_char = &this->word_list.at(i).at(j);
            if ( !this->dirty_bit.at(i).at(j) && 
                this->match_hint(&hint_index, "", current_char)) {
                    this->dirty_bit.at(i).at(j) = true;
                    string current_string{*current_char};
                    this->append_char(i, 
                                    j, 
                                    hint_index, 
                                    dictionary, 
                                    current_string,
                                    result_list);
                    this->dirty_bit.at(i).at(j) = false;
                }
        }
    }
}

void Puzzle::append_char(int i, 
                        int j, 
                        int hint_index, 
                        unordered_set<string> *dictionary,
                        string prev_string,
                        vector<Search_result> *result_list){
    const bool is_in = dictionary->find(prev_string) != dictionary->end();
    if(prev_string.size() == this->hint_length.at(hint_index) && is_in) {
        if(prev_string.empty()) {
            Search_result result(this->word_list, this->dirty_bit, prev_string);
            result_list->push_back(result);
        } else {
            Search_result result(this->word_list, this->dirty_bit, 
                                this->prev_string_collect + " " + prev_string);
            result_list->push_back(result);
        }
    } else { 
        for (int k = 0; k < this->search_grid.size();k++) {
            int a = this->search_grid.at(k).at(0);
            int b = this->search_grid.at(k).at(1);
            char next_char;
            if (0 <= i+a && i+a <= this->degree-1 && 0 <= j+b && j+b <= this->degree-1) {
                if ( !this->dirty_bit.at(i+a).at(j+b)) {
                    next_char = this->word_list.at(i+a).at(j+b);
                } else {
                    continue;
                }
            } else {
                continue;
            }
            if (this->match_hint(&hint_index, prev_string, &next_char)) {
                this->dirty_bit.at(i+a).at(j+b) = true;
                string next_string = prev_string + next_char;
                this->append_char(i+a, j+b, hint_index, dictionary, next_string, result_list);
                this->dirty_bit.at(i+a).at(j+b) = false;
            } else {
                continue;
            }
        }

    }
}


bool Puzzle::match_hint(int *hint_index,
                        string prev_string,
                        char *next_char){
    const bool is_in = (this->hints_list.at(*hint_index).find(prev_string.size()) 
                        != this->hints_list.at(*hint_index).end());
    if( !this->hints_list.at(*hint_index).empty() && is_in) {
            if (this->hints_list.at(*hint_index).at(prev_string.size()) == *next_char){
                return true;
            } else {
                return false;
            }
    } else {
        return true;
    }
}


void Puzzle::update_word_list(){
    for(int i = 0; i < this->dirty_bit.size(); i++) {
        vector<char> tmp_word_list = this->word_list.at(i);
        vector<bool> tmp_dirty_list = this->dirty_bit.at(i);
        for(int j = 0; j <this->dirty_bit.at(i).size(); j++) {
            if(this->dirty_bit.at(i).at(j)){
                tmp_word_list.push_back('0');
                tmp_dirty_list.push_back(true);
                tmp_word_list.erase(tmp_word_list.begin() + j);
                tmp_dirty_list.erase(tmp_dirty_list.begin() + j);
            } else {
                continue;
            }    
        }
        // tmp_word_list.resize(this->degree,'0');
        this->word_list.at(i) = tmp_word_list;
        // tmp_dirty_list.resize(this->degree, true);
        this->dirty_bit.at(i) = tmp_dirty_list;
    }
}

int main(){
    unordered_set<string> test_dict {"hoe", "square", "aqh", "aus", "hee"};
    
    cout << "************** test with no dirty bit **************" << "\n";
    
    vector<Search_result> final_result{};

    vector<vector<char>> test_word_list {{'s', 'o', 'h'}, 
                                        {'u', 'q', 'e'}, 
                                        {'a', 'r', 'e'}};
    vector<vector<bool>> test_dirty_bit {{false, false, false}, 
                                        {false, false, false},
                                        {false, false, false}};
    vector<unordered_map<int, char>> test_hints_list{{},{}} ;
    vector<int> test_hints_length {3, 5};
    Puzzle test_puzzle(test_word_list, test_dirty_bit, "", test_hints_list, test_hints_length);
    test_puzzle.search_word(0, &test_dict, &final_result);
    for (auto itr = final_result.begin(); itr != final_result.end(); ++itr) {
        cout << *itr << "\n";
    }

    cout << "************** test with dirty bit **************" << "\n";
    vector<Search_result> final_result_1{};

    vector<vector<bool>> test_dirty_bit_1 {{false, false, false}, 
                                        {false, false, false},
                                        {true, true, true}};
    Puzzle test_puzzle_1(test_word_list, test_dirty_bit_1, "", test_hints_list, test_hints_length);
    test_puzzle_1.search_word(0, &test_dict, &final_result_1);
    for (auto itr = final_result_1.begin(); itr != final_result_1.end(); ++itr) {
        cout << *itr << "\n";
    }

    cout << "************** test with dirty bit **************" << "\n";
    vector<Search_result> final_result_2{};

    vector<vector<bool>> test_dirty_bit_2 {{false, false, false}, 
                                        {false, false, false},
                                        {false, false, false}};
    vector<unordered_map<int, char>> test_hints_list_2{{{0,'h'}},{}} ;

    Puzzle test_puzzle_2(test_word_list, test_dirty_bit_2, "", test_hints_list_2, test_hints_length);
    test_puzzle_2.search_word(0, &test_dict, &final_result_2);
    for (auto itr = final_result_2.begin(); itr != final_result_2.end(); ++itr) {
        cout << *itr << "\n";
    }
    

}