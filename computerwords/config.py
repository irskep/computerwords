DEFAULT_CONFIG = {
    # TODO: auto directory-reading version?
    'file_hierarchy': [
        {'**/*.txt', '**/*.md'},
    ],
    'site_title': 'My Cool Web Site',
    'author': 'Docs McGee',
    'output_file': 'index.html',
}


class DictCascade:
    def __init__(self, *dicts):
        super().__init__()
        self.dicts = list(reversed(dicts))

    def __getitem__(self, k):
        for d in self.dicts:
            if k in d:
                return d[k]
        raise KeyError(k)
