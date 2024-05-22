import init
from init import zk as zk
from init import zk_queue as zk_queue
from init import handler as handler

# Create a node for each operation
zk.create("/app/addition", "empty")
zk.create("/app/subtraction", "empty")
zk.create("/app/multiplication", "empty")
zk.create("/app/division", "empty")

handler.start() # Start worker threads

handler.sleep_func(0.2) # Wait a while before taking input

# Initiliaze queue, if this line is not used it throws an error
zk_queue.put(b"Queue initialized")

# Get user input
print("Type 'done' to process the data.")
while True:
    user_input = raw_input("Enter an integer: ")
    if user_input != "done":
        print("")
        zk_queue.put(user_input)
        zk.set("/app/queue", "UPDATE - Integer pushed to list")
        handler.sleep_func(0.001)
    elif user_input == "done":
        print("")
        break
    else:
        print("Invalid input! Try Again.")

# Get rid of the first element: 'Queue initialized'
zk_queue.get()
zk_queue.consume()

init.input_done = True # Queue node is now ready for distribution

# Process data
while zk_queue.__len__() > 0:
    data = zk_queue.get()
    zk.set("/app/queue", data)
    handler.sleep_func(1) # To prevent rush conditions
    zk_queue.consume()
    print("Item consumed: %s" % data)
    

data_add, stat_add = zk.get("/app/addition")
data_sub, stat_sub = zk.get("/app/subtraction")
data_mul, stat_mul = zk.get("/app/multiplication")
data_div, stat_div = zk.get("/app/division")

print("\nResults:")
print("Addition: %s" %data_add.decode("utf-8"))
print("Subtraction: %s" %data_sub.decode("utf-8"))
print("Multiplication: %s" %data_mul.decode("utf-8"))
print("Division: %s" %data_div.decode("utf-8"))

# Stop
zk.stop()
print("\nClient stopped!")
