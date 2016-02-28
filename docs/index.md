Computer Words is a tool and document processing API that helps you write
documentation for your software library. It is conceptually similar to
[Sphinx](http://sphinx-doc.org/).

The page you are reading was written in
[Computer Flavored Markdown](#computer-flavored-markdown) and compiled
with Computer Words.

<h1 skip_toc=True>Table of Contents</h1>

<table-of-contents />

# Basics

First, install Python 3.5. Yes, I'm serious. Python 3.4 may honestly be the
lowest version this project supports. But that doesn't mean you can only
document Python 3.4+ code in it! More on that later. For now, get it installed
and then write some files.

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
