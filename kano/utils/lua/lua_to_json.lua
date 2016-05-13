-- lua_to_json.lua
--
-- Copyright (C) 2016 Kano Computing Ltd.
-- License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
--
-- Read a lua module and output it as json

local ToJson = require "to_json"

if #arg ~= 2 then
    io.stderr:write("Usage: lua lua_to_json.lua data.lua data.json\n")
    os.exit(1)
end

local json_nil = {}
local function get_lua_data(filename)

    local c = loadfile(filename)
    local success, result = pcall(c)
    if success then
        success, result = pcall(result, json_nil)
    end
    return result, success
end
local result, success = get_lua_data(arg[1])
if not success then
    io.stderr:write("Error loading file!\n")
    os.exit(1)
else
    local json, status = ToJson.dumps(result, json_nil)
    if not status then
            io.stderr:write("error converting to json\n")
            os.exit(1)
    end
    local jf, estr  = io.open(arg[2], "w")
    if jf == nil then
        io.stderr:write("Error outputting to file".. estr.."\n")
        os.exit(1)
    end
    local enil
    enil, estr = jf:write(json)
    if enil == nil then
        io.stderr:write("Error outputting to file".. estr.."\n")
        os.exit(1)        
    end
    jf:close()
end

