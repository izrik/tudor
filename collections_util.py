
def add(c, item):
    try:
        c.add(item)
    except AttributeError:
        c.append(item)


def remove(c, item):
    if item in c:
        try:
            c.discard(item)
        except AttributeError:
            c.remove(item)


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


def assign(c, other):
    if c is None:
        c = ()
    if other is None:
        other = ()
    c2 = set(c)
    other2 = set(other)
    to_add = other2 - c2
    to_remove = c2 - other2
    for item in to_add:
        add(c, item)
    for item in to_remove:
        remove(c, item)
