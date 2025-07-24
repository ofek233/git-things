from functools import reduce


l = [x*3 for x in range(51) if (x*3) % 4 != 0]
lis = [1, 2, 3, 4, 5, 6]
new_list = reduce(lambda x, y: x + y, lis)
##print(l)
print(new_list)


def f(d):
    d["last_name"] = "Smith"

student = {"first_name": "John", "last_name": "Doe", "age": 20, "grade": "A", "major": "Computer Science"}
f(student)
print(student)