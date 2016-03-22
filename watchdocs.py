#!/usr/bin/env python
from livereload import Server, shell
server = Server()
server.watch('docs/*.md', shell('make docs'))
server.serve(root='docs/build')