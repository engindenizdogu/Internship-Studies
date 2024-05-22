"""
Cache using Random Replacement (RR) Algorithm
"""
from random import randint
import ast

MODULE_NAME = 'Random Replacement'
CACHE_SIZE = 16

# Initialize cache so that it won't throw index out of bounds error
def initialize_random_cache(rd, key):
    i = 0
    while i < CACHE_SIZE:
        rd.lpush(key, "0")
        i = i + 1
    
    return 0


# Insert value to random index between 0 and (CACHE_SIZE - 1)
def add_to_cache(rd, cache_key, value, set_key=None):
    index = randint(0, (CACHE_SIZE - 1))  # Generate a random index
    user = rd.lrange(cache_key, index, index)  # Search for the user in that index

    rd.lset(cache_key, index, value)  # Set new user

    if user[0] != "0":  # A user was replaced, return its ID
        user = ast.literal_eval(user[0]) # Convert to dictionary
        return user['id']

    return -1


# Find and remove the 'value' from the list
def remove_from_cache(rd, key, count, value):
    rd.lrem(key, count, value)


# Return the specified user_id from cache
def get_value(rd, key, user_id):
    i = 0
    while i < CACHE_SIZE:
        user = ast.literal_eval(rd.lindex(key, i)) 
        # If the value is '0', it will be converted to integer
 
        if user != 0 and user['id'] == user_id:
            return user

        i = i + 1

    return None  # User is not in cache


# Return the index of the element in cache
def get_cache_index(rd, key, value):
    length = rd.llen(key)
    i = 0
    while i < length:
        result = rd.lrange(key, i, i) # Search elements one by one
        if result and result[0] == value:
            return i # Index found

        i = i + 1
    
    return -1