# luon.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Output 'pure data' python structures as lua tables.
#
#  The format is a module which returns a function taking a
#  a value to use for 'nil': f(json_nil)
#
#  Arrays are converted to tables with integer keys.
#  however #array is only defined if the array has no nil
#  entries. If this is important, supply a non-nil
#  value for json_nil



def escape_char(c):
    '''
    Escape char 'c' for use in a lua string.

    uses '\d instead of `\u' because we want to be compatible with lua 5.1
    '''

    if ord(c) < ord(' ') or ord(c) >= 127 or c == '"' or c == '\\':
        return '\\{:03d}'.format(ord(c))
    else:
        return c


def escape_string(s):
    '''
    Escape a whole LSON string
    '''
    return ''.join([escape_char(c) for c in s])

NL = '\n'


class lines:
    '''
    Class for outputting formatted data
    '''
    def __init__(self):
        self.prefix = 0  # Number of spaces in indentation prefix
        self.lines = ''  # Current lines
        self.curr = ''   # data to be added to the current line

    def __add__(self, next):
        '''
        Add some data. May include one newline at end only.
        '''

        if next.endswith(NL):
            self.lines += ' '*self.prefix+self.curr+next
            self.curr = ''
        else:
            self.curr += next
        return self

    def push(self):
        '''
        Increment indentation level, flushing current line first.
        '''

        self += NL
        self.prefix += 4

    def pop(self):
        '''
        Decrement indentation level
        '''
        self.prefix -= 4

    def end(self):
        '''
        return finished string
        '''
        return self.lines+self.curr


def to_lua_lines(lines, obj):
    '''
    Convert a data item to lua, adding to the 'lines' object
    '''

    # NB: order of this switch is important because of subtypes
    if isinstance(obj, type(None)):
        lines += 'json_nil'
    elif isinstance(obj, str):
        lines += '"'
        lines += escape_string(obj)
        lines += '"'
    elif isinstance(obj, unicode):
        to_lua_lines(lines, obj.encode('utf8'))
    elif isinstance(obj, list):
        lines + '{'
        lines.push()
        for i in obj:
            lines += NL
            to_lua_lines(lines, i)
            lines += ','
        lines += '}'
        lines.pop()
    elif isinstance(obj, dict):
        lines += '{'
        lines.push()

        for k, i in obj.iteritems():
            if not isinstance(k, str) and not isinstance(k, unicode):
                raise Exception()
            lines += '['
            to_lua_lines(lines, k)
            lines += '] = '
            to_lua_lines(lines, i)
            lines += ', '+NL
        lines.pop()
        lines += '}'
    elif isinstance(obj, bool):
        lines += str(obj).lower()
    elif isinstance(obj, int):
        lines += str(obj)
    elif isinstance(obj, float):
        lines += str(obj)

    else:
        raise Exception()
    return lines


def dumps(x):
    '''
    Convert a data item to lua module, returning as a string
    '''
    l = lines()
    l += "function f(json_nil)\n"
    l.push()
    l += "local val ="
    to_lua_lines(l, x)
    l += "\n"
    l += "return val"
    l += "\n"
    l.pop()
    l += "end\n"
    l += "return f\n"
    return l.end()
