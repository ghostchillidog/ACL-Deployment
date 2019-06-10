# Python Script for Updating ACL
## Requires Python 3.x [Tested on 3.7.1]
- The scripts will build a dictionary of switches from a CSV
- Request the password for logging into switches [planned upgrade to use SSH keys]
- Connect to the switches, check existing ACL [based off CSV]
- If the remark with date doesn't match the new string the new ACL will be applied.

## Using the scripts
- Edit the ACL.txt file and update with the generic (using %ACL% placeholder) ACL.
- Edit the acl.py and change 'new_server' variable to the date from remark in current ACL (above)
- Run 'threading_working.py' using a python3 parser. (test.cmd will try to run from C:\Python3\python.exe)
 - The script will prompt for passwords for YDH and SGH switch usernames.

...
