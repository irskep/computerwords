# Configuration

All configuration lives in a JSON file that we'll call `conf.json`. Every
path is relative to the directory in which this file lives.

## Complete example

Note: JSON cannot contain comments, so this isn't copy-pasteable.

```js
{
  /* Include all Markdown files in this directory,
     ordered alphabetically, but with index.md first
     if present */
  "file_hierarchy": ["*.md"],

  // Name of the project or web site
  "site_title": "My Cool Web Site",

  // Tag line or whatever
  "site_subtitle": "It's very cool.",

  // Your name
  "author": "Docs McGee",

  // Place to put HTML files, relative to this file
  "output_dir": "./build",

  // HTML output options
  "html": {

      // Absolute URL of where the site will be uploaded
      "site_url": "http://example.com",

      // Stylesheets to add
      "css_files": ["style.css"],

      // Built-in theme to use (can be null)
      "css_theme": "default",

      // Where to keep stylesheets, images, etc
      "static_dir_name": "static",

      // What to put in the <meta name="description"> tag
      "meta_description": ""
  }
}
```

## Defining table of contents structure with `file_hierarchy`

The `file_hierarchy` option, in addition to collecting input files, determines
the structure of the table of contents, and therefore the order in which the
resulting documents are navigated.

The wording in this section might not be great. If something is confusing,
please open a ticket.

### Data types

Each entry in `file_hierarchy` can be one of:

* `string`: a relative path to a file (such as `"index.md"`) or a glob (such
  as `"*.md")
* `list`: a list of strings specifying paths to be sorted together. For
  example, given files `a.txt`, `c.txt`, and `b.md`, the list
  `["*.txt", "*.md"]` would be expanded by Computer Words to
  `["a.txt", "b.md", "c.txt"]`.
* `dict`: should have exactly one key, a file path. The value is a list of
  these data types.

### Sorting

When you use a list and/or glob, multiple files often match. The order in which
these files appear is based on two things:

1. If two files are in the same directory and one file is called `"index.*"`, 
   it will come before the other file.
2. Otherwise, sorting is alphabetical.

### Example 1: All files in a single directory

You can use a single flat glob to collect every file in a directory.

```json
{"file_hierarchy": ["*.md"]}
```

Example tree:

```md
* index.md
* about.md
* computers.md
```

### Example 2: All files in a directory and its subdirectories

```json
{"file_hierarchy": ["**/*.md"]}
```

Note: **this will not create subsections based on directories**. Each
document's headings will be at the top level.

Example tree:

```md
* index.md
* about.md
* computers.md
* examples/example_1.md
* examples/example_2.md
```

### Example 3: Explicit ordering with nesting

```json
{
  "file_hierarchy": [
    "Readme.md",
    "Guide.md",
    {"Examples.md": ["examples/*.md"]}
  ]
}
```

Example tree:

```md
* Readme.md
* Guide.md
* Examples.md
  * examples/example_1.md
  * examples/example_2.md
```
