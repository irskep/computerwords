"""
### Writing a plugin for Computer Words

Summary: write a class inheriting from `computerwords.plugin.CWPlugin`,
put it in a module accessible in `PYTHONPATH`, and add it to a list of
module paths under the `"plugins"` key in your config file.

#### 1. Inherit from `CWPlugin`

```python
from computerwords.cwdom.nodes import CWTagNode, CWTextNode
from computerwords.plugin import CWPlugin

class MyPlugin(CWPlugin):
    # we want to add some things to the config file
    CONFIG_NAMESPACE = 'my_plugin'

    # here are our default values
    def get_default_config(sel):
        return {
            "files_to_read": []
        }

    # override this method to write to the config after it has
    # been read
    def postprocess_config(self, config):
        local_config = config["my_plugin"]
        local_config["file_contents"] = {}
        for path in local_config["files_to_read"]:
            with open(path, 'r') as f:
                local_config["file_contents"][path] = f.read()

    # If you're writing a custom tag, this is where you
    # implement it.
    def add_processors(self, library):
        @library.processor('under-construction')
        def process_my_tag(tree, node):
            tree.replace(
                node,
                CWTagNode(
                    'marquee',
                    {'class': 'under-construction'},
                    [CWTextNode('Under Construction')]))
```

#### 2. Put your plugin in `PYTHONPATH`

You can either install your plugin as a package or just add
`PYTHONPATH=$PYTHONPATH:$PATH_TO_MODULE_DIR` in front of your invocation of
`python -m computerwords`. Kind of like this:

```sh
# plugin file is at plugins/my_plugin.py
PYTHONPATH=$PYTHONPATH:./plugins \\
    python -m computerwords \\
        --conf docs/conf.json
```

#### 3. Add your plugin to the config file

```json
{
    "plugins": [
        "my_plugin"
    ]
}
```
"""

class CWPlugin:
    """Base class for all Computer Words plugins."""

    """If you want to include custom information in the config file, specify
    a namespace for it to live under. For example, the HTML writer's
    configuration is all under the `"html"` key."""
    CONFIG_NAMESPACE = None

    def get_default_config(self):
        """If you specified `CONFIG_NAMESPACE`, provide a default dictionary
        here"""
        return None

    """Optionally transform the config after it is read"""
    def postprocess_config(self, config):
        pass

    def add_processors(self, library):
        """Use `cwdom.library.Library.processor` to define transforms on the
        tree."""
        pass

    WRITER_NAME = None
    def write(self, config, src_root, dest_root, stdlib, tree):
        pass
