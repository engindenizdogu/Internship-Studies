from flask import Flask, request, jsonify, redirect, url_for
import redis
import json
import ast

app = Flask(__name__)

# Redis object which will act as the cache
rd = redis.StrictRedis()

# Keys
page_key = "action-discovery:pages"
user_key = "page-action:user"
member_key = "page-action:member"

# Clear cache each time the program starts
rd.flushdb()

# Load JSON
with open("page_action.json") as file:
    data = json.load(file)

# Fill redis with data
for page in data['pages']:
    rd.lpush(page_key, page)

    if page['pageName'] == 'user':
        for action in page['actions']:
            rd.lpush(user_key, action)

    elif page['pageName'] == 'member':
        for action in page['actions']:
            rd.lpush(member_key, action)


# Helper funtion
# Search for 'action' in redis with the specified key
def search_for_action(action_key, action):
    size = rd.llen(action_key)
    i = 0
    while i < size:
        act = rd.lindex(action_key, i)  # Get values one by one
        if action in act.lower():
            return jsonify(ast.literal_eval(act))

        i = i + 1

    return -1


# Homepage
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return jsonify(data)


# Get all actions of a page
@app.route('/index/get_page_actions/<string:page_name>', methods=['GET'])
def get_page_actions(page_name):
    name = page_name.lower()
    size = rd.llen(page_key)
    i = 0
    while i < size:
        page = rd.lindex(page_key, i)  # Get values one by one
        if "'pageName': u'{}".format(name) in page:
            return jsonify(ast.literal_eval(page))
        i = i + 1

    return 'Page Not Found!'


# Get information on a single action
@app.route('/index/get_single_action/<string:page_name>/<string:action_name>', methods=['GET'])
def get_single_action(page_name, action_name):
    action = action_name.lower()  # Convert to lowercase
    if page_name.lower() == 'user':
        result = search_for_action(user_key, action)

    elif page_name.lower() == 'member':
        result = search_for_action(member_key, action)

    if result != -1:
        return result
    else:
        return 'Action Not Found!'


# Add new action to specified page
@app.route('/index/add_action/<string:page_name>/<string:action_name>/<string:target_url>', methods=['GET', 'POST'])
def add_action(page_name, action_name, target_url):
    if request.method == 'POST':
        temp_action = {
            "actionName": action_name,
            "targetURL": target_url
        }

        for page in data['pages']:
            if page['pageName'] == page_name.lower():
                page['actions'].append(temp_action)

                # Update cache
                if page_name.lower() == 'user':
                    rd.lpush(user_key, temp_action)
                elif page_name.lower() == 'member':
                    rd.lpush(member_key, temp_action)

        with open("page_action.json", 'w') as file:
            json.dump(data, file, indent=4)

            # Update cache
            for page in data['pages']:
                rd.lpush(page_key, page)

    return redirect(url_for('index'))


# Run
if __name__ == '__main__':
    app.run(debug=True)
