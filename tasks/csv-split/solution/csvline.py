"""Minimal CSV line splitting."""


def split_csv_line(line, sep=","):
    fields, buf, i, n = [], [], 0, len(line)
    in_quotes = False
    while i < n:
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    buf.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                buf.append(ch)
        elif ch == '"':
            in_quotes = True
        elif ch == sep:
            fields.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    if in_quotes:
        raise ValueError("unterminated quoted field")
    fields.append("".join(buf))
    return fields
