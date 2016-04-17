# Tag reference

## Standard HTML tags

The following tags should be usable just as they are in regular HTML:

<html-enumerate-all-tags />

Attributes are passed through verbatim and not checked.

## Table of contents

The Table of Contents plugin introduces one new tag: `<table-of-contents />`.
It accepts a `maxdepth` attribute which can set a maximum number of levels
to output.

```html
<!-- only show 2 levels deep -->
<table-of-contents maxdepth=2 />
```

The table of contents takes the top level of its hierarchy from your config
file. See
[Defining table of contents structure with `file_hierarchy`](configuration.html#Defining-table-of-contents-structure-with-file_hierarchy)
for details.

The titles and intra-document structure are taken from the heading nodes.

The output looks like this:

```html
<nav class="table-of-contents">
  <ol>
    <li>
      Heading 1
      <ol>
        <li>Subheading 1</li>
      </ol>
    </li>
  </ol>
</nav>
```

## Callouts

You can call out a note or a warning using—wait for it—`<note>` and
`<warning>`. Use `no-prefix=true` to omit the automatic first line of bold
text.

<warning>If you want to put multiple paragraphs in an aside, you need to put
the opening and closing tags in their own paragraphs. See
<heading-link name="parser-bugs" />.
</warning>

### Example 1

```html
<note>This is a note.</note>

<note no-prefix=true>
This is another note.
</note>
```

<note>This is a note.</note>

### Example 2

```html
<note no-prefix=true>

**Another note**

This is a multi-paragraph note with a custom first line.

</note>
```

<note no-prefix=true>

**Another note**

This is a multi-paragraph note with a custom first line.

</note>

### Example 3

```html
<warning>This is a warning.</warning>
```

<warning>This is a warning.</warning>

## Linking to sections

You can define a "heading alias" like this:

```html
<heading-alias name="configuration" />
# Configuring Foobar
```

You can then link to the section like this:

```html
Check out the <heading-link name="configuration" /> section.
```

This will automatically include the heading's contents and link to it:

> Check out the [Configuring Foobar](#not-a-real-link) section.

You can set custom link text by just using the non-self-closing version:

```html
Check out the
<heading-link name="configuration">Configuration</heading-link>
```

> Check out the [Configuration](#not-a-real-link) section.

## Python documentation

Computer Words supports including documentation from *symbol files*. These
can be generated for Python 3.5 like this:

```sh
python3 -m computerwords.source_parsers.python35 . mymodule \
  > docs/symbols.json
```

Then tell Computer Words where to find the symbol file in your config like
this:

```js
{
    "python": {
        "symbols_path": "./symbols.json"
    }
}
```

(Remember, all paths in the config file are relative to the config file's
directory.)

Now you can use the `<autodoc-python />` tag to include source docs in your
Markdown files:

```html
<autodoc-python 
    module="my.module"
    include-children=True
    render-absolute-path=True
    heading-level=2 />
```

### Attributes

* `module`/`class`/`method`/`function`: path to the symbol to be included
* `include-children`: If `True`, also show definitions and docstrings of all
  classes and functions in the module
* `render-absolute-path`: If `True` (default), show the fully qualified path
  for the symbol (e.g. `computerwords.plugin.CWPlugin` rather than just
  `CWPlugin`). Children, if included, will be rendered with this value as
  `False`.
* `heading-level`: If you don't want the module's name to be a top-level
  heading, set this to 2 to use `h2`, 3 to use `h3`, etc.

### Missing features

* Including individual classes and functions
* Convenient linking to symbols

### Why the intermediate JSON step?

Because the general interface with source parsers needs to work for languages
besides Python. Languages tend to have parsers for themselves in their standard
libraries; Computer Words should make use of them.
