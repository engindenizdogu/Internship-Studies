from flask import Flask, jsonify, render_template, redirect, url_for, flash
from users import users
import redis

""" Select an algorithm to use """
#from cache_designs import redis_fifo as cache_module
#from cache_designs import redis_lifo as cache_module
#from cache_designs import redis_rr as cache_module
from cache_designs import redis_lfu as cache_module

module_name = cache_module.MODULE_NAME
cache_size = cache_module.CACHE_SIZE

redis_key = 'cache:users'  # Used as the 'key' parameter of functions
redis_key_freq = 'cache:frequency' # Hold frequensies in this

app = Flask(__name__)

# Assign secret key for HTML pages
app.config['SECRET_KEY'] = 'a_secret_key'

# Redis object which will act as the cache
rd = redis.StrictRedis()

# Clear cache each time the program starts
rd.flushdb()

# Initialize if RR is in use
if module_name == 'Random Replacement':
    cache_module.initialize_random_cache(rd, redis_key)

# In the beginning, iterate through users and add them to the cache their status is 1
for user in users:
    # If LFU is used, add users to the freq list
    if module_name == 'Least Frequently Used':
        rd.zadd(redis_key_freq, 0, user['username'])

    val = -1
    if user['status'] == '1':
        val = cache_module.add_to_cache(rd, redis_key, user, redis_key_freq)
        user_id = int(val)  # Convert to int (from string)

        # Increment frequency
        if module_name == 'Least Frequently Used':
            cache_module.increment_frequency(rd, redis_key_freq, user['username'], 1)

        """ IMPORTANT: For this to work, user IDs should be the same as their index
        in the users array """
        if user_id != -1:  # A user was popped out
            users[user_id]['status'] = '0'


# Testing
print(rd.lrange(redis_key, 0, -1))
print(rd.zrange(redis_key_freq, 0 ,-1, withscores=True))


##-------------------------------------------------------------------

# Home
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', users=users,
                           cache_size=cache_size, cache_status=rd.llen(redis_key), algorithm=module_name)


# Button action
@app.route('/change_status/<string:user_id>/<string:user_status>', methods=['GET', 'POST'])
def change_status(user_id, user_status):
    if user_status == '0':  # Add user to cache
        # If we are using LIFO, we have a special condition
        if module_name == 'Last In First Out' and rd.llen(redis_key) == cache_size:
            flash("Cache is full!")
            flash(
                "You are using the LIFO algorithm. Can't add a new user until a cache slot is free.")
            return redirect(url_for('index'))

        # Get user from the disk (type dictionary)
        user = users[int(user_id)]
        val = cache_module.add_to_cache(rd, redis_key, user, redis_key_freq)
        index_added = int(user['id'])  # Index/ID of added user
        index_popped = int(val)  # Index/ID of popped user

        # Change user status of both
        users[index_added]['status'] = '1'
        if index_popped != -1:  # A user was popped out
            flash("User with ID {} was succesfully removed from cache.".format(
                index_popped))
            users[index_popped]['status'] = '0'  # Set status to 0

        flash("User with ID {} was succesfully added to cache.".format(index_added))
    elif user_status == '1':  # Remove user from cache
        user = cache_module.get_value(
            rd, redis_key, user_id)  # User to be deleted

        if user is None:
            flash("Unexpected error! Can't find the user in cache.")
            return redirect(url_for('index'))

        if module_name == 'Random Replacement':
            cache_index = cache_module.get_cache_index(rd, redis_key, str(user))
            if cache_index != -1:
                # Instead of removing set to 0 so that the cache won't throw
                # index out of bounds error
                rd.lset(redis_key, cache_index, '0')
            else:
                flash("Unexpected error! Can't remove from cache.")
                return redirect(url_for('index'))
        else:
            cache_module.remove_from_cache(
                rd, redis_key, 1, str(user))  # Remove user from list

        # Set user status to 0
        index = int(user['id'])  # Convert to int, get user id/index
        users[index]['status'] = '0'

        flash("User with ID {} was succesfully removed from cache.".format(index))

    return redirect(url_for('index'))


# Run
if __name__ == '__main__':
    app.run(debug=True)
