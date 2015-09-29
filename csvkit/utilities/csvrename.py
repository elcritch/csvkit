#!/usr/bin/env python

"""
csvcut is originally the work of eminent hackers Joe Germuska and Aaron Bycoffe.

This code is forked from:
https://gist.github.com/561347/9846ebf8d0a69b06681da9255ffe3d3f59ec2c97

Used and modified with permission.
"""

import itertools

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility, parse_column_identifiers
from csvkit.headers import make_default_headers

class CSVCut(CSVKitUtility):
    description = 'Filter and truncate CSV files. Like unix "cut" command, but for tabular data.'

    def add_arguments(self):
        self.argparser.add_argument('-n', '--names', dest='names_only', action='store_true',
            help='Display column names and indices from the input CSV and exit.')
        self.argparser.add_argument('-c', '--columns', dest='sources',
            help='A comma separated list of column indices or names to be extracted. Defaults to all columns.')
        self.argparser.add_argument('-r', '--renames', dest='renames',
            help='A comma separated list of new column names. Defaults to all columns.')

    def main(self):
        
        if self.args.names_only:
            self.print_column_names()
            return

        rows = CSVKitReader(self.input_file, **self.reader_kwargs)

        # Make Headers 
        if self.args.no_header_row:
            row = next(rows)

            column_names = make_default_headers(len(row))

            # Put the row back on top
            rows = itertools.chain([row], rows)
        else:
            column_names = next(rows)

        # Project Column Names
        all_column_ids = [ i for i,n in enumerate(column_names) ]
        source_column_ids = parse_column_identifiers(self.args.sources, column_names, zero_based=self.args.zero_based)
        
        projected_column_names = [ n for n in column_names ]
        
        for idx, name in zip(source_column_ids, self.args.renames.split(',')):
            projected_column_names[idx] = name
        
        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        
        output.writerow(projected_column_names)

        # Rewrite Rows
        for row in rows:
            out_row = [row[c] if c < len(row) else None for c in all_column_ids]

            output.writerow(out_row)

def launch_new_instance():
    utility = CSVCut()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()

