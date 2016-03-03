<a name="computer-flavored-markdown" />
# Computer Flavored Markdown

## CommonMark “Plus”

First things first: if you write [CommonMark](http://commonmark.org/help/),
you should have no problems. Great!

## The “Plus”: generalized `<tags>`

In normal Markdown, whenever you write inline HTML, it's passed through to
the output verbatim. But in Computer Flavored Markdown, it's parsed and can
have meaning. It becomes part of the *abstract syntax tree* and can be changed
during compilation.

Take for example, the `<table-of-contents />` tag. This is not an HTML tag,
but it has meaning in Computer Words. Specifically, there is a set of
transforms that collects all your headings, and replaces the contents of
`<table-of-contents />` with:

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
the bugs. You should still be able to express anything.
