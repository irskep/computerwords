Computer Words is a tool and document processing API that helps you write
documentation for your software library. It is conceptually similar to
[Sphinx](http://sphinx-doc.org/).

The page you are reading was written in
[Computer Flavored Markdown](#computer-flavored-markdown) and compiled
with Computer Words.

[Computer Words on GitHub](https://github.com/irskep/computerwords)

[Source code for this page](https://github.com/irskep/computerwords/tree/master/docs)

<h1 skip_toc=True>Table of Contents</h1>

<table-of-contents />

# Basics

First, install Python 3.5. (Yes, I'm serious. See
[Why Python 3.5?](#why-python-3.5)) Then get the source code of this project
(that's right, I haven't released it yet) and install the requirements.
Now you're ready to run! You just need to write a Markdown file and a config.

`docs/index.md`:

```markdown filename=docs/index.md
# My Cool Project

Hello world!
```

`docs/conf.json`:

```json filename=docs/conf.json
{
  "site_title": "My Cool Project",
  "site_subtitle": "The coolest project ever",
  "css_files": ["style.css"],
  "file_hierarchy": ["*.md"]
}
```

command:
```sh
> python3 -m computerwords --conf docs/conf.json
```

The built docs are now in `docs/build/`.
