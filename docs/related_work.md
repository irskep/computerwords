# Related Work

## Docutils and Sphinx

The biggest inspiration for this project is the pairing of
[Docutils](http://docutils.sourceforge.net/) and
[Sphinx](http://sphinx-doc.org). They have a similar design: a parser turns
text documents into a tree, some transforms are done on the tree (including
user plugins), and the output is written to HTML.

My pain points with this system are why I started from scratch. Docutils is
an old, old project with less-than-great documentation, verbose code that
supports Python 2.4(!), and Sourceforge SVN hosting.