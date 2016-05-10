-- to_json.lua
--
-- Copyright (C) 2016 Kano Computing Ltd.
-- License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
--
-- Output 'pure data' lua structures as json.
--
-- Exports one module ToJson which has a 'dumps' function which
--  given a lua object, returns a json string

-- If the table is in array form, return a json array, otherwise use a dict
-- Assumes strings are already unicode compatible (only escapes ascii <32)



-- Lines object used for indentation

local lines = {}
lines.__index = lines

local NL = '\n'
function lines.create()
    local self = setmetatable({}, lines)

    self.prefix = 0   -- number of indentation spaces
    self.lines = ''   -- string up to current line
    self.curr = ''    -- current line
    return self
end

function lines:add(nxt) -- Add some data. May include one newline at end only.    
    if nxt:sub(#nxt,#nxt)==NL then
        self.lines = self.lines .. string.rep(' ', self.prefix) .. self.curr .. nxt
        self.curr = ''
    else
        self.curr = self.curr .. nxt
        return self
    end
end

function lines:push() --  Increment indentation level, flushing current line first.
    self:add(NL)
    self.prefix = self.prefix + 4
end

function lines:pop() -- Decrement indentation level
    self.prefix = self.prefix - 4
end

function lines:complete() -- return finished string
    return self.lines .. self.curr
end
    
local function is_array(x)
    -- check if table is in the form of an array. This is true if
    -- all keys are consecutive integers starting at 1.
    -- We check that they are integers at least 1 and that the largest is
    -- equal to the number of items in the table.  By construction the table
    -- has unique keys, so by the pigeon-hole princpal they are consecutive
    local max_key = 0
    local num_items = 0
    for k, _ in pairs(x) do
        num_items = num_items + 1
        if type(k) == 'number' and k == math.floor(k) then
            if k < 1 then
                print("k<1")
                return false
            end
            max_key = math.max(k, max_key)
        end
    end
    if num_items ~= max_key then
        print("items "..tostring(num_items).."max_key "..tostring(max_key))
        return false
    end
    if #x ~= max_key then
        print("#x "..tostring(#x).."max_key "..tostring(max_key))
        return false
    end
    return true
end
    

local function escape_char(c)
    --- escape characters for json
    --- quote marks, slashes plus characters < ' '
    --- Not sure why we need  to quote forward slash? works though.
    local escape_chars = {
        ['"']='"',
        ['\\']="\\",
        ['/']='/',
        ['\b']='b',
        ['\f']='f',
        ['\n']='n',
        ['\r']='r',
        ['\t']='t'
    }        
    if escape_chars[c] then 
        return '\\'..escape_chars[c]
    elseif c:byte(1) < 32 then 
        return string.format('\\u%04x',c:byte(1))
    else
        return c
    end
end

local function escape_string(s) -- escape a whole string.
    -- Escape a string. Assumes it is already unicode safe
    -- >127 chars are valid unicode chars. 
    
    local res = ''
    for i = 1, #s do
        local c = s:sub(i,i)
        res = res .. escape_char(c)
    end
    return res
end
local function to_json_lines(l, x, json_nil )
    -- Convert a data item to lua, adding to the 'lines' object
    local status
    if type(x) == 'nil' or x == json_nil then
        l:add('null')
    elseif type(x) == 'string' then
        l:add('"')
        l:add(escape_string(x))
        l:add('"')
    elseif type(x) == 'table' then
        if is_array(x) then
            l:add('[')
            l:push()
            local first = true
            for _, v  in pairs(x) do
                if not first then 
                    l:add(',')
                end
                first = false
                l:add(NL)
                status = to_json_lines(l, v, json_nil)
                if not status then return false end
                
            end
            l:add(']')
            l:pop()
        else
            l:add('{')
            l:push()

            local first = true
            for k, v in pairs(x) do
                if type(k) ~= 'string' then
                    print("Expected string, got "..type(k).." "..tostring(k))
                    return false
                end
                
                if not first then 
                    l:add(',')
                end
                first = false

                status = to_json_lines(l, k, json_nil)
                if not status then return false end

                l:add(': ')

                status = to_json_lines(l, v, json_nil)
                if not status then return false end
                l:add(NL)
            end
            l:pop()
            l:add('}')
        end
    elseif type(x) == 'number' then
        l:add(tostring(x))
    elseif type(x) == 'boolean' then
        l:add(tostring(x))
    else
        print(type(x))
        return false
    end
    return true
end


local ToJson = {}

function ToJson.dumps(x, json_nil)
    -- Convert data item to json string
    -- 'json_nil' is extra object to be treated as json null
    local l = lines.create()
    local status = to_json_lines(l, x, json_nil)
    return l:complete(), status
end

return ToJson

