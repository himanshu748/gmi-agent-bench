"""Parse human-readable durations."""


def parse_duration(text):
    hours, rest = text.split("h")
    minutes = rest.rstrip("m")
    return int(hours) * 3600 + int(minutes) * 60
