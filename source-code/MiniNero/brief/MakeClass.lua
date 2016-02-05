--for quick conversion of the MiniNero python code to c++
--
if #arg > 0 then
  class = string.lower(arg[1]) --asdf
  object = arg[1] --Asdf
  deff = string.upper(arg[1]) --ASDF
  hfile = io.input("TemplateHead"):read("*a")
  cppfile = io.input("TemplateBody"):read("*a")
  hfile = string.gsub(hfile, "asdf", class)
  hfile = string.gsub(hfile, "Asdf", object)
  hfile = string.gsub(hfile, "ASDF", deff)
  cppfile = string.gsub(cppfile, "asdf", class)
  cppfile = string.gsub(cppfile, "Asdf", object)
  cppfile = string.gsub(cppfile, "ASDF", deff)
  io.output(object..".h"):write(hfile)
  io.output(object..".cpp"):write(cppfile)
end
