def acl_diff(current_acl, desired_acl):
    current_acl_set = set(current_acl)
    desired_acl_set = set(desired_acl)
    to_remove = current_acl_set - desired_acl_set
    to_add = desired_acl_set - current_acl_set
    return list(to_remove), list(to_add)

# Example usage:
current_acl = [(1, 'permit ip any any'), (2, 'deny ip 192.168.1.0 0.0.0.255 any')]
desired_acl = [(1, 'permit ip any any'), (3, 'permit tcp any any eq 80')]

to_remove, to_add = acl_diff(current_acl, desired_acl)
print(f'To remove: {to_remove}')
print(f'To add: {to_add}')
