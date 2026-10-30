import html
import re
import unittest

from tests.util import generate_test_app


class TagFiltersTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        original_secret = self.app.secret_key
        self.app.secret_key = 'tag-filter-test'
        self.addCleanup(setattr, self.app, 'secret_key', original_secret)
        self.client = self.app.test_client()
        pl = self.app.pl
        user = pl.create_user('tag-viewer@example.com')
        pl.add(user)
        tag = pl.create_tag('filtered-tag')
        pl.add(tag)
        for done in (False, True):
            for deleted in (False, True):
                task = pl.create_task(
                    'visible-task-{}-{}'.format(int(done), int(deleted)),
                    is_public=True, is_done=done, is_deleted=deleted)
                task.tags.append(tag)
                pl.add(task)
        private = pl.create_task('private-tagged-task', is_public=False)
        private.tags.append(tag)
        pl.add(private)
        unrelated = pl.create_task('unrelated-public-task', is_public=True)
        pl.add(unrelated)
        pl.commit()
        with self.client.session_transaction() as session:
            session['_user_id'] = user.email
            session['_fresh'] = True
        self.url = '/tags/{}?sort=summary&order=asc'.format(tag.id)

    def toggle(self, page, label):
        link = re.search(r'href="([^"]+)">' + label + r'</a>', page)
        self.assertIsNotNone(link)
        response = self.client.get(html.unescape(link.group(1)))
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.url, response.location)
        response = self.client.get(response.location)
        self.assertEqual(200, response.status_code)
        return response.get_data(as_text=True)

    def assert_tasks(self, page, show_done, show_deleted):
        for done in (False, True):
            for deleted in (False, True):
                summary = 'visible-task-{}-{}'.format(int(done), int(deleted))
                if (show_done or not done) and (show_deleted or not deleted):
                    self.assertIn(summary, page)
                else:
                    self.assertNotIn(summary, page)
        self.assertNotIn('private-tagged-task', page)
        self.assertNotIn('unrelated-public-task', page)
        self.assertIn('hide done' if show_done else 'show done', page)
        self.assertIn('hide deleted' if show_deleted else 'show deleted', page)

    def test_filters_toggle_independently_and_preserve_sort(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        page = response.get_data(as_text=True)
        self.assert_tasks(page, False, False)
        page = self.toggle(page, 'show done')
        self.assert_tasks(page, True, False)
        page = self.toggle(page, 'show deleted')
        self.assert_tasks(page, True, True)
        page = self.toggle(page, 'hide done')
        self.assert_tasks(page, False, True)
        page = self.toggle(page, 'hide deleted')
        self.assert_tasks(page, False, False)
