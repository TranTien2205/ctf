# The marshal walk — the recursive dump


marshal.loads gives the module code — walk every nested code object
recursively: the check may live in a nested function, a class, a
lambda.
