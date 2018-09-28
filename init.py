from kazoo.client import KazooClient, KazooState, KeeperState
from kazoo.recipe.queue import LockingQueue
from kazoo.recipe.watchers import DataWatch, ChildrenWatch
from kazoo.handlers.threading import SequentialThreadingHandler
import logging
import operations1, operations2, operations3, operations4

logging.basicConfig()

# Boolean values for watchers
input_done = False
is_add_modified = False
is_subtract_modified = False
is_multiply_modified = False
is_divide_modified = False

# Storage for results
add_result = 0
subt_result = 0
mult_result = 1
div_result = 0

# Start client
# read_only mode must be turned on for the servers in the Zookeeper
# cluster for the client to utilize it.
zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()
print("Client started!\n")

# Clear the nodes at the end or else you migth get a NodeExistsError next time
zk.delete("/app", recursive=True)

# Ensure a path, create if it doesn't exist
zk.ensure_path("/app")

# Initialize queue at specified location
zk_queue = LockingQueue(zk, "/app/queue")

# Thread handler
handler = SequentialThreadingHandler()

# Watchers ---------------------------------------------------------------
@zk.DataWatch("/app/queue")
def watch_queue(data, stat):
    if data == "":
        pass
    elif data is not None or stat is not None:
        global input_done
        # print("Queue Node:")
        # print("%s\n" % data)

        # Distrubute incoming data to nodes
        if input_done: # If the user is done with entering inputs
            zk.set("/app/addition", data)
            zk.set("/app/subtraction", data)
            zk.set("/app/multiplication", data)
            zk.set("/app/division", data)


@zk.DataWatch("/app/addition")
def add(data, stat):
    if data is not None or stat is not None:
        global is_add_modified, add_result
        current_data, current_stat = zk.get("/app/addition")
        current_data = current_data.decode("utf-8")

        if current_data != "empty":
            # If the data is modified before, do nothing
            if is_add_modified:
                # So that it does not end in an infinite loop
                is_add_modified = False
                pass
            else:
                # Run the first script
                result = operations1.add(add_result, int(current_data))
                add_result = result
                is_add_modified = True
                zk.set("/app/addition", str(result))
        else:
            print("Addition Node:")
            print("Data is: %s" % data)
            print("Version is %s\n" % stat.version)
    else:
        pass


@zk.DataWatch("/app/subtraction")
def subtract(data, stat):
    if data is not None or stat is not None:
        global is_subtract_modified, subt_result
        current_data, current_stat = zk.get("/app/subtraction")
        current_data = current_data.decode("utf-8")

        if current_data != "empty":
            # If the data is modified before, do nothing
            if is_subtract_modified:
                # So that it does not end in an infinite loop
                is_subtract_modified = False
                pass
            else:
                # Run the second script
                result = operations2.subtract(subt_result, int(current_data))
                subt_result = result
                is_subtract_modified = True
                zk.set("/app/subtraction", str(result))
        else:
            print("Subtraction Node:")
            print("Data is: %s" % data)
            print("Version is %s\n" % stat.version)
    else:
        pass


@zk.DataWatch("/app/multiplication")
def multiply(data, stat):
    if data is not None or stat is not None:
        global is_multiply_modified, mult_result
        current_data, current_stat = zk.get("/app/multiplication")
        current_data = current_data.decode("utf-8")

        if current_data != "empty":
            # If the data is modified before, do nothing
            if is_multiply_modified:
                # So that it does not end in an infinite loop
                is_multiply_modified = False
                pass
            else:
                # Run the third script
                result = operations3.multiply(mult_result, int(current_data))
                mult_result = result
                is_multiply_modified = True
                zk.set("/app/multiplication", str(result))
        else:
            print("Multiplication Node:")
            print("Data is: %s" % data)
            print("Version is %s\n" % stat.version)
    else:
        pass


@zk.DataWatch("/app/division")
def divide(data, stat):
    if data is not None or stat is not None:
        global is_divide_modified, div_result
        current_data, current_stat = zk.get("/app/division")
        current_data = current_data.decode("utf-8")

        if current_data != "empty":
            # If the data is modified before, do nothing
            if is_divide_modified:
                # So that it does not end in an infinite loop
                is_divide_modified = False
                pass
            else:
                # Run the fourth script
                if div_result == 0:
                    div_result = int(current_data)
                else:
                    result = operations4.divide(float(div_result), float(current_data))
                    div_result = result
                    is_divide_modified = True
                    zk.set("/app/division", str(result))
        else:
            print("Division Node:")
            print("Data is: %s" % data)
            print("Version is %s\n" % stat.version)
    else:
        pass

# ------------------------------------------------------------------------
