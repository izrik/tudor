
class Pager(object):
    page = None
    per_page = None
    items = None
    total = None

    def __init__(self, page, per_page, items, total, num_pages, _pager):
        self.page = page
        self.per_page = per_page
        self.items = list(items)
        self.total = total
        self.num_pages = num_pages
        self._pager = _pager

    def iter_pages(self, left_edge=2, left_current=2, right_current=5,
                   right_edge=2):

        if (left_edge < 1 or left_current < 1 or right_current < 1 or
                right_edge < 1):
            raise ValueError('Parameter must be positive')

        total_pages = self.total // self.per_page
        if self.total % self.per_page > 0:
            total_pages += 1

        left_of_current = max(self.page - left_current, left_edge + 1)
        right_of_current = min(self.page + right_current,
                               total_pages - right_edge + 1)

        for i in range(left_edge):
            yield i + 1

        if left_of_current > left_edge + 1:
            yield None

        for i in range(left_of_current, right_of_current):
            yield i

        if right_of_current < total_pages - right_edge + 1:
            yield None

        for i in range(right_edge):
            yield total_pages - right_edge + i + 1

    @property
    def pages(self):
        return self.num_pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.num_pages

    @property
    def next_num(self):
        return self.page + 1
