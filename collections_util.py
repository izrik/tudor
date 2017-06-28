
def add(c, item):
    try:
        c.add(item)
    except AttributeError:
        c.append(item)


def clear(c):
    try:
        c.clear()
    except AttributeError:
        for item in list(c):
            c.remove(item)


def extend(c, other):
    try:
        c.extend(other)
    except AttributeError:
        for item in list(other):
            add(c, item)
