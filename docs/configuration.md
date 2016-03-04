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

## `file_hierarchy`
