import unittest

from markdown_util import gfm_to_html


class GfmToHtmlTest(unittest.TestCase):
    def test_renders_basic_markdown(self):
        result = gfm_to_html('**bold**')
        self.assertIn('<strong>bold</strong>', result)

    def test_renders_table(self):
        md = '| a | b |\n|---|---|\n| 1 | 2 |'
        result = gfm_to_html(md)
        self.assertIn('<table>', result)
        self.assertIn('<td>1</td>', result)

    def test_backslash_n_becomes_br_in_table_cell(self):
        md = '| a | b |\n|---|---|\n| one\\ntwo | c |'
        result = gfm_to_html(md)
        self.assertIn('<td>one<br/>two</td>', result)

    def test_backslash_n_becomes_br_outside_table(self):
        result = gfm_to_html('foo\\nbar')
        self.assertIn('foo<br/>bar', result)

    def test_raw_html_still_sanitized(self):
        result = gfm_to_html('<script>alert(1)</script>')
        self.assertNotIn('<script>', result)
