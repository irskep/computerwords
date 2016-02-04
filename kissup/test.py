from lexer import lex_kissup

nice_tests = [
  "[",
  "abc",
  "abc[ ]",
]

for test in nice_tests:
  print("TESTING: {}".format(test))
  print("         {}".format(repr(list(lex_kissup(test)))))

