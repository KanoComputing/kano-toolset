# luon.py
#
# Copyright (C) 2016-2019 Kano Computing Ltd.
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


def escape_char(c, ascii_only):
    r'''
    Escape char 'c' for use in a lua string.

    uses '\d' instead of '\u' because we want to be compatible with lua 5.1
    '''

    if ord(c) < ord(' ') or ord(c) >= 127 or c == '"' or c == '\\':
        if ascii_only:
            return ''
        else:
            return '\\{:03d}'.format(ord(c))
    else:
        return c


def escape_string(s, ascii_only):
    '''
    Escape a whole LSON string
    '''
    return ''.join([escape_char(c, ascii_only) for c in s])


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
            self.lines += ' ' * self.prefix + self.curr + next
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
        return self.lines + self.curr


def to_lua_lines(lines, obj, ascii_only):
    '''
    Convert a data item to lua, adding to the 'lines' object
    '''

    # NB: order of this switch is important because of subtypes
    if isinstance(obj, type(None)):
        lines += 'json_nil'
    elif isinstance(obj, str):
        lines += '"'
        lines += escape_string(obj, ascii_only)
        lines += '"'
    elif isinstance(obj, unicode):
        to_lua_lines(lines, obj.encode('utf8'), ascii_only)
    elif isinstance(obj, list):
        lines + '{'
        lines.push()
        for i in obj:
            lines += NL
            to_lua_lines(lines, i, ascii_only)
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
            to_lua_lines(lines, k, ascii_only)
            lines += '] = '
            to_lua_lines(lines, i, ascii_only)
            lines += ', ' + NL
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


def dumps(x, ascii_only=False):
    '''
    Convert a data item to lua module, returning as a string
    '''
    lua = lines()
    lua += "function f(json_nil)\n"
    lua.push()
    lua += "local val ="
    to_lua_lines(lua, x, ascii_only)
    lua += "\n"
    lua += "return val"
    lua += "\n"
    lua.pop()
    lua += "end\n"
    lua += "return f\n"
    return lua.end()
