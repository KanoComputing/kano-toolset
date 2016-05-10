#ifndef __PYTHON_TEST_HELPERS_H__
#define __PYTHON_TEST_HELPERS_H__

#include <string>
#include <iostream>
#include <cstdio>
#include <cstring>
#include <memory>
#include <vector>


std::string remove_character(const std::string &str, char rm_char, std::string replace_str = "")
{
    std::string new_str;

    for (std::string::const_iterator it = str.cbegin(); it != str.cend(); ++it) {
        if (strncmp(&*it, &rm_char, 1) == 0) {
            new_str += replace_str;
        } else {
            new_str += *it;
        }
    }

    return new_str;
}


void strip(std::string &tuple)
{
    std::vector<char> invalid_chars = {'(', ' ', ')', '\n'};

    for (std::vector<char>::iterator it = invalid_chars.begin();
            it != invalid_chars.end(); ++it) {
        tuple = remove_character(tuple, *it);
    }
}


std::string run_python_cmd(const std::string module, const std::string function, const std::string args = "")
{

    std::string cmd = "python -c '";

    if (!module.empty())
        cmd += "from " + module + " import " + function + "; ";

    cmd += "print(" +
        function + "(" + remove_character(args, '\'', "\"") + ")"
    ")'";

    std::shared_ptr<FILE> cmd_pipe(popen(cmd.c_str(), "r"), pclose);

    if (!cmd_pipe)
        return "ERROR";

    char buffer[128];
    std::string result = "";

    while (!feof(cmd_pipe.get())) {
        if (fgets(buffer, sizeof(buffer), cmd_pipe.get()) != NULL)
            result += buffer;
    }

    strip(result);

    return result;
}


std::string get_tuple_item(const std::string &tuple, const int idx)
{
    size_t pos = 0;
    size_t prev_pos = pos;
    int i = 0;

    while (i <= idx && pos != std::string::npos) {
        prev_pos = pos;
        pos = tuple.find(',', pos) + 1;
        i++;
    }

    if (i < idx)
        return "";

    if (pos == std::string::npos)
        pos = tuple.size();

    if (pos == 0)
        pos = tuple.find(',');

    return tuple.substr(prev_pos, pos - (prev_pos + 1));
}


#endif
