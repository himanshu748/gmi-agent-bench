"""Config dict merging."""


def deep_merge(base, override):
    for key, value in override.items():
        base[key] = value
    return base
