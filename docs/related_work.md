# Related Work

## Docutils and Sphinx

The biggest inspiration for this project is the pairing of
[Docutils](http://docutils.sourceforge.net/) and
[Sphinx](http://sphinx-doc.org). They have a similar design: a parser turns
text documents into a tree, some transforms are done on the tree (including
user plugins), and the output is written to HTML.

My pain points with this system are why I started from scratch. Docutils is an
old, old project with less-than-great documentation, verbose code that supports
Python 2.4(!), and Sourceforge SVN hosting. reStructuredText is hard to remember and in many cases incapable of producing certain markup. Sphinx supports many documentation use cases out of the box, but its plugin API
is limited, its tree processing algorithm makes it difficult to write
certain kinds of useful plugins, and its theming system is not straightforward.
(I should know,
[I made a theme.](http://sphinx-better-theme.readthedocs.org/en/latest/))

## Pollen

Pollen gets a lot of things right. It is more conceptually pure and seemingly
more powerful than Computer Words, and if I had the time to grok its docs, I'm
sure I would enjoy using it.

But its Markdown mode doesn't let you use custom tags (I think?), so you get
to pick extensibility, or a markup syntax you already know, but not both.

Sometimes I can't quite convince myself that I'm not just making a worse
version of Pollen using Python. But I honestly think that “native” Markdown
documentation is the best way to get contributions from users and buy-in from
library maintainers. And reading Pollen's documentation, I just don't get the
impression that we really share a target audience.

## Butterick's Practical Typography

The author of Pollen is Matthew Butterick, author of
[Practical Typography](http://practicaltypography.com). It's a fun and useful
read. Many of the defaults in Computer Words are based on its advice. Mr.
Butterick [feels the same way I do about Sphinx's default themes](http://practicaltypography.com/websites.html).

## Jekyll

[Jekyll](http://jekyllrb.com/) is a static site generator that understands
Markdown. It is not good for writing your documentation.