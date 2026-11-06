import unittest

from tests.util import generate_test_app


class IndexHideTaskIdsTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_test_app()
        original_secret = self.app.secret_key
        self.app.secret_key = 'hide-task-ids-test'
        self.addCleanup(setattr, self.app, 'secret_key', original_secret)
        self.client = self.app.test_client()
        pl = self.app.pl
        user = pl.create_user('id-hider@example.com')
        pl.add(user)
        task = pl.create_task('a-listed-task', is_public=True)
        pl.add(task)
        pl.commit()
        self.task_id = task.id
        with self.client.session_transaction() as session:
            session['_user_id'] = user.email
            session['_fresh'] = True

    def get_index(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        return response.get_data(as_text=True)

    def toggle(self, hide):
        url = '/show_hide_task_ids?next=%2F'
        if hide:
            url += '&hide_task_ids=1'
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual('/', response.location)
        return self.get_index()

    def assert_ids(self, page, shown):
        task_link = 'href="/task/{}"'.format(self.task_id)
        if shown:
            self.assertIn('>ID</a>', page)
            self.assertEqual(2, page.count(task_link))
            self.assertNotIn('checked', page)
        else:
            self.assertNotIn('>ID</a>', page)
            self.assertEqual(1, page.count(task_link))
            self.assertIn('checked', page)
        self.assertIn('a-listed-task', page)
        self.assertIn('hide ID numbers', page)

    def test_checkbox_hides_and_restores_the_id_column(self):
        self.assert_ids(self.get_index(), True)
        self.assert_ids(self.toggle(True), False)
        self.assert_ids(self.toggle(False), True)
