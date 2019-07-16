### Notepad++ - Find/Replace: Find: '\r\n' Replace: '\\n'
### Should replace all Carriage Return/Line Feed pairs to literal '\n'
file = ".\\acl.txt"
acl_file = open(file,"r")
acl = acl_file.read()
