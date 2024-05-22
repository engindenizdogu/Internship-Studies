"""
Cache using Least Frequently Used (LFU) Algorithm
"""
import ast

MODULE_NAME = 'Least Frequently Used'
CACHE_SIZE = 16

# Implement cache with a list
# When the list is full, least frequent element will be deleted from cache

def add_to_cache(rd, cache_key, value, set_key):
    # Cache is full
    if rd.llen(cache_key) > CACHE_SIZE:
        user = organize_cache(rd, cache_key, value, set_key)
        if user is None:
            return -1 # Error
        else:
            # Remove from cache and then add new user
            rd.lrem(cache_key, 1, user)
            rd.lpush(cache_key, value)
    else:
        rd.lpush(cache_key, value)

    return 0


# LRU operations
# Returns least recently accessed user 
def organize_cache(rd, cache_key, value, set_key):
    i = 0
    while i < rd.zcard(set_key):
        min_user = rd.zrange(set_key, i, i) # Get the user with the minimum associated value
        min_user_name = min_user[0]

        if in_cache(rd, cache_key, min_user_name):
            return min_user_name

        i = i + 1

    return None



# Search cache for value
def in_cache(rd, key, value):
    i = 0
    while i < rd.llen(key):
        user = rd.lrange(key, i, i)
        if value == user[0]:
            return True

        i = i + 1

    return False


# Increment member's value by one
def increment_frequency(rd, key, member, value):
    rd.zincrby(key, member, value)


# Find and remove the 'value' from the list
def remove_from_cache(rd, key, count, value):
    rd.lrem(key, count, value)


# Return the specified user_id from cache
def get_value(rd, key, user_id):
    i = 0
    while i < CACHE_SIZE:
        user = ast.literal_eval(rd.lindex(key, i))

        if user['id'] == user_id:
            return user
        
        i = i + 1

    return None  # User is not in cache