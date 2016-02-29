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

## Work-in-progress disclaimer and apology

You might be thinking to yourself, “oh great, another crappy Markdown variant.”
Well, I am thinking the same thing. I did my best to mitigate the damage, but
since this is still an early-development project, there are still major
problems.

The goal is to let you write your favorite markup language, assuming that
language is Markdown, while also supporting the complex and generalized
needs of a software documentation system.

In an ideal world, I could simply describe Computer Flavored Markdown as
“CommonMark, but the output is an abstract syntax tree instead of an HTML
string.” In reality, it is exactly that, with two exceptions:

1. The HTML is parsed by a simple recursive descent parser that I wrote, not
   a proper spec-following web browser.

2. The awkward marriage of a CommonMark parser, which doesn't try to parse
   HTML but merely faithfully pass it through, and a hand-written HTML parser,
   is complicated, and in this case buggy, with
   **extremely bad error messages.**

I'm not yet sure how to solve this problem without forking CommonMark or just
writing a lot of really bad hacks.

## Limitations

You can't currently wrap multiple lines in a tag like this:

```markdown
<div>

Some stuff in between line breaks (this doesn't work yet)

</div>
```

Since this is basic and essential, it will be fixed soon.