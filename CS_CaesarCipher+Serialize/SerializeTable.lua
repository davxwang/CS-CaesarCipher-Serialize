local serpent = require('serpent')

local function getTables (path)
    local mt = {__newindex = {}}
    local newENV = {}
    setmetatable(newENV, mt)
    File = loadfile(path,"bt",newENV)
    File()

    return mt["__newindex"]
end

local file_output = io.open('temp_serialized.txt','w')
local file_output_type = io.open('temp_serialized_tablename.txt','w')

local result = getTables(arg[1])
local not_first_write = false;

for key, value in pairs(result) do
    if not_first_write then
        io.output(file_output)
        io.write("\n\n");
        io.output(file_output_type)
        io.write("\n")
    end

    io.output(file_output)
    io.write(key .. " =\n" .. serpent.block(value, {comment = false, indent = '\t', numformat = "%.15g"}))
    io.output(file_output_type)
    io.write(key)

    not_first_write = true;
end

io.close(file_output)
io.close(file_output_type)