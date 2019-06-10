### Notepad++ - Find/Replace: Find: '\r\n' Replace: '\\n'
### Should replace all Carriage Return/Line Feed pairs to literal '\n'
new_server = "Updated 07/02/2019 09:35"
file = ".\\acl.txt"
acl_file = open(file,"r")
acl = acl_file.read()
