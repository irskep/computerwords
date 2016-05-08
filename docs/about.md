# About

## Your feedback is essential

Right now, the best way to leave feedback is to
[open a ticket on GitHub](http://github.com/irskep/computerwords/issues)
or [subscribe to the mailing list](https://groups.google.com/forum/#!forum/computerwords).
This project is in a “public preview” state
because I want to find all the rough edges before committing to a proper
release.

## Project Core Beliefs

1. Documentation authors are mostly library maintainers.
2. Library maintainers don't want to invest lots of time in their documentation
   system, because it is a distraction from their work. (See also
   <heading-link name="faq" />)
3. Therefore, using Computer Words should mostly be obvious. Using it should
   not require authors to constantly refer to syntax references or other
   meta-documentation.
4. Since the documentation is for software, Computer Words should make it
   easy to integrate with software. Plugins are a core feature.

## Value Proposition

### The simplicity of Markdown, the power tools of Sphinx

Markdown is the language of GitHub, BitBucket, and GitLab. Software developers
write Markdown *all the time.* Since they already know Markdown, why should
they learn a different language to write their documentation, as long as it's
sufficiently powerful?

If you just write a bunch of Markdown files, you end up hosting your docs
on a GitHub wiki or some similar abomination, giving up a lot of convenience
and power. There needs to be some kind of organizing power to bring it
together.

### HTML & CSS

A web page should be more than a sea of `<div>` tags.

The output uses semantic HTML5 markup. That's kind of nice.

It's really easy to include CSS stylesheets. You might think, “I'm making a web
site, so of course I can style it with CSS!” But if you were using
[another tool](http://sphinx-doc.org), you would find this task to be more
trouble than you were expecting. Computer Words makes it really, really simple
to add your own CSS. And it includes a normalization stylesheet and some
pretty good defaults.

Applying some basic font and color changes is a surprisingly affective way
to brand your documentation. You should do it.

### Simple and powerful plugin API

Computer Words has a plugin API that allows you to transform arbitrary nodes in
arbitrary ways. You can implement plugins to replace text inline, collect
information from one place and reformat it for display in another place, or
insert content from external files.

More importantly, you can use plugins other people have written!

## Who should use this?

* Documentation nerds. It's in a useable preview state, which means you can
  see for yourself if the ideas have merit and contribute feedback.
* Projects with an existing set of Markdown docs that happen to work with
  the Computer Flavored Markdown parser. You should be able to set up the
  project with a simple config file and see how it goes.

## Who should *not* use this?

* Anyone who wants a robust, battle-tested system.
* Projects already invested in Sphinx or another non-Markdown system they are
  happy with.
