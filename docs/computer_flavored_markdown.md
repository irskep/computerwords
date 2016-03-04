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

Take for example, the `<table-of-contents />` tag. This is not an HTML tag,
but it has meaning in Computer Words. If you write this:

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

## The parser has bugs

This works:

```markdown
<x>

Blah blah blah

</x>
```

This works:

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
