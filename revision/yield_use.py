def traffic_light():
    print("Traffic light is red")
    yield "red"

    print("Traffic light is yellow")
    yield "yellow"

    print("Traffic light is green")
    yield "green"

light = traffic_light()
print("signal is: ",next(light))
print("signal is: ",next(light))
print("signal is: ",next(light))


def count_to(max_num):
    current  =1 
    while current <= max_num:
        yield current
        current+=1

for num in count_to(5):
    print(num)


"""Use B: Setup and Cleanup (How FastAPI Uses It)
When a function has one yield, it splits the function into two halves:

Before yield: Runs on the first next() call (Setup).

After yield: Runs on the second next() call (Cleanup)."""

def manage_resource():
    print("STEP 1: Open file / DB connection")
    yield "MY_DATABASE_OBJECT"
    print("STEP 3: Close file / DB connection")

gen = manage_resource()

# FastAPI calls `next(gen)` before your endpoint runs:
db = next(gen)          # Prints STEP 1, gives you "MY_DATABASE_OBJECT"

print("STEP 2: Endpoint uses", db)

# FastAPI calls `next(gen)` again after your endpoint finishes:
next(gen, None)         # Prints STEP 3 (Cleanup!)