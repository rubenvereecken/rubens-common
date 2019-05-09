from collections import OrderedDict
import os
import csv
import numpy as np


class Reporter:
    pass

class CSVDialect(csv.excel_tab):
    pass

class CSVReporter(Reporter):
    def __init__(self, name, header):
        """
        Header should be an iterable of strings
        or a dict of formatters
        """
        from psr import config
        header_names = list(header)
        path = '{}/{}.csv'.format(config.logpath, name)

        if os.path.exists(path):
            existing = True
            with open(path, 'r') as f:
                reader = csv.DictReader(f, dialect=CSVDialect)
                if set(header_names) != set(reader.fieldnames):
                    raise Exception('Existing CSV does not match headers')
        else:
            existing = False

        self.fieldnames = header_names
        self.path = path
        self.name = name
        self.f = open(path, 'a')
        self.writer = csv.DictWriter(self.f, fieldnames=header_names,
                                     dialect=CSVDialect)

        if not existing:
            self.writer.writeheader()


    def writerow(self, *items):
        if len(items) == 1 and type(items[0]) in [dict, OrderedDict]:
            items = items[0]
        else:
            items = dict(zip(self.fieldnames, items))

        items = { k: self.format_entry(v) for k, v in items.items() }

        self.writer.writerow(items)
        self.f.flush()


    def format_entry(self, s):
        if isinstance(s, str):
            return s
        if np.issubdtype(type(s), np.floating):
            return np.round(s, 4)
        return s
