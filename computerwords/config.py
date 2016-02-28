from collections.abc import Mapping


DEFAULT_CONFIG = {
    # TODO: auto directory-reading version?
    'file_hierarchy': [
        {'**/*.txt', '**/*.md'},
    ],
    'site_title': 'My Cool Web Site',
    'author': 'Docs McGee',
    'output_dir': './build',
    'static_dir_name': 'static',
    'meta_description': '',
    'css_files': None,
}


class DictCascade(Mapping):
    def __init__(self, *dicts):
        super().__init__()
        self.dicts = list(reversed(dicts))

    def __getitem__(self, k):
        for d in self.dicts:
            if k in d:
                return d[k]
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

