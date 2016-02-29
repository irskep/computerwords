# Conceptual information

## Why should I use this?

You probably shouldn't. It's not ready yet.

## Project Core Beliefs

1. Documentation authors are mostly library maintainers.
2. Library maintainers don't want to invest lots of time in their documentation
   system, because it is a distraction from their work.
3. Therefore, using Computer Words should mostly be obvious. Using it should
   not require authors to constantly refer to syntax references or other
   meta-documentation.
4. Since the documentation is for software, Computer Words should make it
   easy to integrate with software. Plugins (custom tags) are a core feature.

## Value Proposition

### The simplicity of Markdown, the power tools of Sphinx

Markdown is the language of GitHub, BitBucket, and GitLab. Software developers
write Markdown *all the time.* Since they already know Markdown, why should
they learn a different language to write their documentation?

If you just write a bunch of Markdown files, you end up hosting your docs
on a GitHub wiki or some similar abomination. There needs to be some kind of
organizing power to bring it together.

### HTML & CSS

The output uses semantic HTML5 markup. That's kind of nice.

It's really to include CSS stylesheets. You might think, “I'm making a web
site, so of course I can style it with CSS!” But if you were using
[another tool](http://sphinx-doc.org), you would find this task to be more
trouble than you were expecting. Computer Words makes it really, really simple
to add your own CSS. And it includes a normalization stylesheet and some
pretty good defaults.

Applying some basic font and color changes is a surprisingly affective way
to brand your documentation. You should do it.

### Simple and powerful plugin API

This isn't really true until I document the API, but trust me...it's good.

<a name="why-python-3.5" />
## Why Python 3.5?

Most importantly, because it is a pleasure to write. Computer Words uses
`pathlib` and `yield from` extensively.

But also, it forces us to treat earlier versions of Python as a *separate
language*, which makes us more likely to write a better API to support
non-Python-3.5 languages!

I suspect the project runs fine under Python 3.4. But since few people even
run Python 3, it might as well be written in OCaml.
