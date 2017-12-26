import unittest

from in_memory_persistence_layer import InMemoryPersistenceLayer
from models.task import Task
from tudor import make_task_public, make_task_private, Config, \
    get_config_from_command_line


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_make_task_public(self):
        # given
        task = Task('task')
        task.id = 1
        self.pl.add(task)
        self.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertFalse(task.is_public)
        # when
        make_task_public(self.pl, task.id, printer=printer)
        # then
        self.assertTrue(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", public'], output)

    def test_make_task_public_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        # when
        make_task_public(self.pl, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)

    def test_make_task_public_and_descendants(self):
        # given
        t1 = Task('t1', is_public=False)
        t1.id = 1
        self.pl.add(t1)
        t2 = Task('t2', is_public=False)
        t2.id = 2
        self.pl.add(t2)
        t2.parent = t1
        t3 = Task('t3', is_public=False)
        t3.id = 3
        self.pl.add(t3)
        t3.parent = t2
        t4 = Task('t4', is_public=False)
        t4.id = 4
        self.pl.add(t4)
        t4.parent = t1
        t5 = Task('t5', is_public=False)
        t5.id = 5
        self.pl.add(t5)
        self.pl.commit()
        output = set()

        def printer(*args):
            output.add(args[0])

        # precondition
        self.assertFalse(t1.is_public)
        self.assertFalse(t2.is_public)
        self.assertFalse(t3.is_public)
        self.assertFalse(t4.is_public)
        self.assertFalse(t5.is_public)
        # when
        make_task_public(self.pl, t1.id, printer=printer, descendants=True)
        # then
        self.assertTrue(t1.is_public)
        self.assertTrue(t2.is_public)
        self.assertTrue(t3.is_public)
        self.assertTrue(t4.is_public)
        self.assertFalse(t5.is_public)
        # and
        self.assertEqual({'Made task 1, "t1", public',
                          'Made task 2, "t2", public',
                          'Made task 3, "t3", public',
                          'Made task 4, "t4", public'}, output)

    def test_make_task_private(self):
        # given
        task = Task('task', is_public=True)
        task.id = 1
        self.pl.add(task)
        self.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertTrue(task.is_public)
        # when
        make_task_private(self.pl, task.id, printer=printer)
        # then
        self.assertFalse(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", private'], output)

    def test_make_task_private_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        # when
        make_task_private(self.pl, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)

    def test_make_task_private_and_descendants(self):
        # given
        t1 = Task('t1', is_public=True)
        t1.id = 1
        self.pl.add(t1)
        t2 = Task('t2', is_public=True)
        t2.id = 2
        self.pl.add(t2)
        t2.parent = t1
        t3 = Task('t3', is_public=True)
        t3.id = 3
        self.pl.add(t3)
        t3.parent = t2
        t4 = Task('t4', is_public=True)
        t4.id = 4
        self.pl.add(t4)
        t4.parent = t1
        t5 = Task('t5', is_public=True)
        t5.id = 5
        self.pl.add(t5)
        self.pl.commit()
        output = set()

        def printer(*args):
            output.add(args[0])

        # precondition
        self.assertTrue(t1.is_public)
        self.assertTrue(t2.is_public)
        self.assertTrue(t3.is_public)
        self.assertTrue(t4.is_public)
        self.assertTrue(t5.is_public)
        # when
        make_task_private(self.pl, t1.id, printer=printer, descendants=True)
        # then
        self.assertFalse(t1.is_public)
        self.assertFalse(t2.is_public)
        self.assertFalse(t3.is_public)
        self.assertFalse(t4.is_public)
        self.assertTrue(t5.is_public)
        # and
        self.assertEqual({'Made task 1, "t1", private',
                          'Made task 2, "t2", private',
                          'Made task 3, "t3", private',
                          'Made task 4, "t4", private'}, output)


class ConfigTest(unittest.TestCase):
    def test_init_no_args_yields_hard_coded_defaults(self):
        # when
        result = Config()
        # then
        self.assertIs(False, result.DEBUG)
        self.assertEqual('127.0.0.1', result.HOST)
        self.assertEqual(8304, result.PORT)
        self.assertEqual('sqlite:////tmp/test.db', result.DB_URI)
        self.assertEqual('/tmp/tudor/uploads', result.UPLOAD_FOLDER)
        self.assertEqual('txt,pdf,png,jpg,jpeg,gif', result.ALLOWED_EXTENSIONS)
        self.assertIsNone(result.SECRET_KEY)
        self.assertIsNone(result.args)

    def test_debug_sets_debug(self):
        # when
        result = Config(debug=True)
        # then
        self.assertIs(True, result.DEBUG)

    def test_host_sets_(self):
        # when
        result = Config(host='1.2.3.4')
        # then
        self.assertEqual('1.2.3.4', result.HOST)

    def test_port_sets_port(self):
        # when
        result = Config(port=12345)
        # then
        self.assertEqual(12345, result.PORT)

    def test_db_uri_sets_db_uri(self):
        # when
        result = Config(db_uri='sqlite://')
        # then
        self.assertEqual('sqlite://', result.DB_URI)

    def test_upload_folder_sets_upload_folder(self):
        # when
        result = Config(upload_folder='/tmp/folder2')
        # then
        self.assertEqual('/tmp/folder2', result.UPLOAD_FOLDER)

    def test_allowed_extensions_sets_allowed_extensions(self):
        # when
        result = Config(allowed_extensions='zip,exe')
        # then
        self.assertEqual('zip,exe', result.ALLOWED_EXTENSIONS)

    def test_secret_key_sets_secret_key(self):
        # when
        result = Config(secret_key='12345')
        # then
        self.assertEqual('12345', result.SECRET_KEY)

    def test_args_sets_args(self):
        # given
        expected_result = object()
        # when
        result = Config(args=expected_result)
        # then
        self.assertIs(expected_result, result.args)


class GetConfigFromCommandLineTest(unittest.TestCase):
    def setUp(self):
        self.env_configs = Config(
            debug=False, host='5.6.7.8', port=12345, db_uri='sqlite://',
            upload_folder='/tmp/folder3', allowed_extensions='a,b,c',
            secret_key='12345')

    def test_no_args_yields_defaults(self):
        # when
        result = get_config_from_command_line([], self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_debug_arg_yields_debug(self):
        # when
        result = get_config_from_command_line(['--debug'], self.env_configs)
        # then
        self.assertEqual(True, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_host_arg_yields_host(self):
        # when
        result = get_config_from_command_line(['--host', '2.4.6.8'],
                                              self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual('2.4.6.8', result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_port_arg_yields_port(self):
        # when
        result = get_config_from_command_line(['--port', '6789'],
                                              self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(6789, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_db_uri_arg_yields_db_uri(self):
        # when
        result = get_config_from_command_line(
            ['--db-uri', 'sqlite:////tmp/sqlite.db'], self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual('sqlite:////tmp/sqlite.db', result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_upload_folder_arg_yields_upload_folder(self):
        # when
        result = get_config_from_command_line(
            ['--upload-folder', '/tmp/folder4'], self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual('/tmp/folder4', result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_allowed_extensions_arg_yields_allowed_extensions(self):
        # when
        result = get_config_from_command_line(
            ['--allowed-extensions', 'pdf,jkl'], self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual('pdf,jkl', result.ALLOWED_EXTENSIONS)
        self.assertEqual(self.env_configs.SECRET_KEY, result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_secret_key_arg_yields_secret_key(self):
        # when
        result = get_config_from_command_line(
            ['--secret-key', 'abcdefg'], self.env_configs)
        # then
        self.assertEqual(self.env_configs.DEBUG, result.DEBUG)
        self.assertEqual(self.env_configs.HOST, result.HOST)
        self.assertEqual(self.env_configs.PORT, result.PORT)
        self.assertEqual(self.env_configs.DB_URI, result.DB_URI)
        self.assertEqual(self.env_configs.UPLOAD_FOLDER, result.UPLOAD_FOLDER)
        self.assertEqual(self.env_configs.ALLOWED_EXTENSIONS,
                         result.ALLOWED_EXTENSIONS)
        self.assertEqual('abcdefg', result.SECRET_KEY)
        self.assertIsNotNone(result.args)

    def test_create_secret_key_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--create-secret-key'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertTrue(result.args.create_secret_key)

    def test_hash_password_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--hash-password', 'abcdef'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertEqual('abcdef', result.args.hash_password)

    def test_make_public_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--make-public', '123'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertEqual(123, result.args.make_public)

    def test_make_private_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--make-private', '123'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertEqual(123, result.args.make_private)

    def test_descendants_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--descendants'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertTrue(result.args.descendants)

    def test_test_db_conn_yields_command(self):
        # when
        result = get_config_from_command_line(
            ['--test-db-conn'], self.env_configs)
        # then
        self.assertIsNotNone(result.args)
        self.assertTrue(result.args.test_db_conn)
