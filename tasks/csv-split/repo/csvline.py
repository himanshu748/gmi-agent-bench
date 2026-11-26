"""Minimal CSV line splitting."""


def split_csv_line(line, sep=","):
    return [field.strip('"') for field in line.split(sep)]
