def argument(type):
    if type == "good":
        return "Good Argument"

def mockery(person) :
    if person != "adult":
        return "Good Argument"

you = "adult"

if mockery(you) == argument("good"):
    print("You win")
else:
    exit(1)
