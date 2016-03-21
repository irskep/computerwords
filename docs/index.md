Computer Words is a tool that helps you write documentation for software. It
is extensible and you can write Markdown. Computer Words is conceptually
similar to [Sphinx](http://sphinx-doc.org/).

The page you are reading was written in
[Computer Flavored Markdown](computer_flavored_markdown.html#computer-flavored-markdown) and compiled
with Computer Words.

[Computer Words on GitHub](https://github.com/irskep/computerwords)

[Source code for this page](https://github.com/irskep/computerwords/tree/master/docs)

<warning>This is alpha-quality software. Most of it works very well, but be
sure to read the parser caveats if you intend to really use it.</warning>

<h1 skip_toc=True>Table of Contents</h1>

<table-of-contents maxdepth=2 />

# Basics

```sh
# if necessary, install Python 3.5:
brew install python3.5  # or whatever

# then install Computer Words
pip install -e git+https://github.com/irskep/computerwords.git@master#egg=computerwords
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
  "file_hierarchy": ["*.md"]
}
```

```sh
> python3 -m computerwords --conf docs/conf.json
```

The built docs are now in `docs/build/`.
