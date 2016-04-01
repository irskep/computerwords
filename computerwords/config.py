from collections.abc import Mapping


DEFAULT_CONFIG = {
    "file_hierarchy": [
        {"**/*.txt", "**/*.md"},
    ],
    "site_title": "My Cool Web Site",
    "site_subtitle": "",
    "project_version": None,
    "author": "Docs McGee",
    "output_dir": "./build",
    "plugins": [
        "computerwords.plugins.callouts",
        "computerwords.plugins.heading_aliases",
        "computerwords.plugins.htmlwriter",
        "computerwords.plugins.graphviz",
        "computerwords.plugins.pygments",
        "computerwords.plugins.python35",
    ],
    "python3.5": {
        "symbols_path": "symbols.json",
    },
}


class DictCascade(Mapping):
    def __init__(self, *dicts):
        super().__init__()
        self.dicts = list(reversed(dicts))

    def __getitem__(self, k):
        matching_dicts = [d for d in self.dicts if k in d]
        matching_values = [d[k] for d in matching_dicts]
        if matching_values:
            if isinstance(matching_values[0], dict):
                return dict(DictCascade(*reversed(matching_values)))
            else:
                return matching_dicts[0][k]
        else:
            raise KeyError(k)

    def keys(self):
        keys = set()
        for d in self.dicts:
            keys = keys | set(d.keys())
        return keys

    def __iter__(self):
        return self.keys().__iter__()

    def __repr__(self):
        return repr({k: self[k] for k in sorted(self)})

    def __len__(self):
        return len(self.keys())

