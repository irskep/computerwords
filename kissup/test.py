from lexer import lex_kissup

nice_tests = [
  "[",
  # should be TEXT
  "abc",
  # should be TEXT BRACKET_LEFT WHITESPACE BRACKET_RIGHT
  "abc[ ]",
]

for test in nice_tests:
  print("TESTING: {}".format(test))
  print("         {}".format(repr(list(lex_kissup(test)))))

