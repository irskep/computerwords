class SourceException(Exception):
    def __init__(self, loc, reason):
        self.loc = loc
        self.reason = reason
        self.path = None  # insert later if you want
        super().__init__("{}: {}".format(loc, reason))

    def apply_config(self, parser_config):
        self.path = parser_config.document_path
        if parser_config.relative_to_loc:
            self.loc = self.loc.relative_to(
                parser_config.relative_to_loc)

    def __str__(self):
        if self.path is None:
            return "{}: {}".format(
                self.loc.short_str, self.reason)
        else:
            return "{!r}:{}: {}".format(
                self.path,
                self.loc.short_str,
                self.reason)
