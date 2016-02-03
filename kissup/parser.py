"""
// BB_WORD: a valid tag name; essentially a string literal terminated by whitespace or a reserved character
// TEXT: non-BBCode text (i.e. string literal)
// BB_VAL: A string literal inside a BBCode tag
// e.g. [img src="foo"] matches [BB_WORD BB_WORD=BB_VAL]

stmts -> stmt stmts
       | ε

stmt -> TEXT
      | tag

tag -> open_tag stmts close_tag
     | self_closing_tag

open_tag -> [ tag_contents ]

close_tag -> [ / BB_WORD ]

self_closing_tag -> [ tag_contents / ]

tag_contents -> BB_WORD tag_args
              | BB_WORD

tag_args -> tag_arg tag_args
          | ε

tag_arg -> BB_WORD = arg_value

arg_value -> BB_WORD
           | NUMBER
           | STRING
"""
