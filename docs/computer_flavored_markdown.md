<a name="computer-flavored-markdown" />
# Computer Flavored Markdown

## CommonMark

The biggest part of Computer Flavored Markdown is Markdown. Specifically,
CFM is mostly just [CommonMark](http://commonmark.org/help/). So this all
works:

```markdown
# Title

This is a [paragraph](https://en.wikipedia.org/wiki/Paragraph)

* un-numbered list
* more list
  1. numbered nested list

> blockquote
> blah blah
```

## Extensible HTML tags

In normal Markdown, whenever you write inline HTML, it's passed through to
the output verbatim. But in Computer Flavored Markdown, it's parsed and can
be transformed during compilation.

Let's use the `<table-of-contents />` tag as an example. This is not an HTML
tag, but it has meaning in Computer Words because of the `table_of_contents`
plugin. If you write this:

```markdown
<table-of-contents />

# Heading 1

## Subheading 1
```

it will be transformed during compilation and rendered like this:

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
<h1>Heading 1</h1>
<h2>Subheading 1</h2>
```

The means by which this happens is described later.

<heading-alias name="parser-bugs" />

## Parser caveats

### Bugs

If you want to put multiple paragraphs inside a tag, the opening and closing
tags must be in their own lines.

**This works:** 

```markdown
<warning>

First paragraph of warning.

Second paragraph of warning.

</warning>
```

**This does not work:** 

```markdown
<warning>
First paragraph of warning.

Second paragraph of warning.
</warning>
```

There are also more bugs. This works:

```markdown
<x>
Blah blah blah
</x>
```

**This does not work:**

```markdown
<x>

Blah blah blah
</x>
```

**This also does not work:**

```markdown
<x>

Blah blah blah</x>
```

This is because I have bolted a CommonMark parser, which doesn't really
understand HTML, to an HTML parser of my own design. I'm still working out
the bugs. You should still be able to express anything if you mess with the
line breaks a little.

### The parser is too picky

If you try to use your Github Flavored Markdown files, a lot of them won't
work because Computer Flavored Markdown throws errors in too many cases instead
of passing strings through verbatim when it can't parse them.

If you have a good example of this, please open a ticket on GitHub.

### Tags must have explicit open/close or be self-closing

Any time you use a tag, it needs to either be of the form
`<my-tag>contents</my-tag>` or `<my-tag />`. Using `<my-tag>` by itself
will result in an error.

### The error messages are crap

Computer Words doesn't know how to tell you what file your problem is in yet.
