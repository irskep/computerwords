Computer Words is a tool that helps you write documentation for software. It
is extensible and you can write Markdown. Computer Words is conceptually
similar to [Sphinx](http://sphinx-doc.org/).

The page you are reading was written in
[Computer Flavored Markdown](computer_flavored_markdown.html#computer-flavored-markdown) and compiled
with Computer Words.

[Computer Words on GitHub](https://github.com/irskep/computerwords)

[Source code for this page](https://github.com/irskep/computerwords/tree/master/docs)

Subscribe to the mailing list by emailing
[computerwords+subscribe@googlegroups.com](mailto:computerwords+subscribe@googlegroups.com)
or by visiting [the web interface](https://groups.google.com/forum/#!forum/computerwords).

<warning>This is alpha-quality software. Most of it works very well, but be
sure to read the parser caveats if you intend to really use it.</warning>

# Basics

```sh
# if necessary, install a version of Python ≥ 3.3:
brew install python3.5  # or whatever

# then install Computer Words
pip install computerwords
```

Now you're ready to run! You just need to write a Markdown file and a config.

```markdown filename=docs/index.md
# My Cool Project

Hello world!
```

```json filename=docs/conf.json
{
  "site_title": "My Cool Project",
  "site_subtitle": "The coolest project ever",
  "project_version": "1.0",
  "file_hierarchy": ["*.md"]
}
```

```sh
> python3 -m computerwords --conf docs/conf.json
```

The built docs are now in `docs/build/`.

<h1 skip_toc=True>Table of Contents</h1>

<table-of-contents maxdepth=2 />

# Contributing

## Ideas

Send feature requests, syntax suggestions, and large-scale architecture
proposals to the mailing list. What you see on this site is the result of
one person's ideas about how a tool like this should work. We need more
people's input to make something really great.

## Bug reports

There are a lot of known bad cases, but we need to know which ones people
actually hit. Send these to
[GitHub](http://github.com/irskep/computerwords/issues).

## Code

If this sounds fun to work on, good, because literally everything needs work.
Either email the list or just dive in!