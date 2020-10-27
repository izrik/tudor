import os
import unittest
from unittest.mock import patch, MagicMock

from persistence.in_memory.layer import InMemoryPersistenceLayer
from tudor import make_task_public, make_task_private, Config, \
    get_config_from_command_line, create_user, get_db_uri, ConfigError, \
    get_secret_key


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_make_task_public(self):
        # given
        task = self.pl.create_task('task')
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
        t1 = self.pl.create_task('t1', is_public=False)
        t1.id = 1
        self.pl.add(t1)
        t2 = self.pl.create_task('t2', is_public=False)
        t2.id = 2
        self.pl.add(t2)
        t2.parent = t1
        t3 = self.pl.create_task('t3', is_public=False)
        t3.id = 3
        self.pl.add(t3)
        t3.parent = t2
        t4 = self.pl.create_task('t4', is_public=False)
        t4.id = 4
        self.pl.add(t4)
        t4.parent = t1
        t5 = self.pl.create_task('t5', is_public=False)
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
        task = self.pl.create_task('task', is_public=True)
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
        t1 = self.pl.create_task('t1', is_public=True)
        t1.id = 1
        self.pl.add(t1)
        t2 = self.pl.create_task('t2', is_public=True)
        t2.id = 2
        self.pl.add(t2)
        t2.parent = t1
        t3 = self.pl.create_task('t3', is_public=True)
        t3.id = 3
        self.pl.add(t3)
        t3.parent = t2
        t4 = self.pl.create_task('t4', is_public=True)
        t4.id = 4
        self.pl.add(t4)
        t4.parent = t1
        t5 = self.pl.create_task('t5', is_public=True)
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

    def test_create_user(self):
        # precondition
        self.assertEqual(0, self.pl.count_users())
        # when
        create_user(self.pl, email='name@example.org', hashed_password='asdf')
        # then
        self.assertEqual(1, self.pl.count_users())
        user = self.pl.get_user_by_email('name@example.org')
        self.assertIsNotNone(user)
        self.assertEqual('asdf', user.hashed_password)
        self.assertFalse(user.is_admin)

    def test_create_user_as_admin(self):
        # precondition
        self.assertEqual(0, self.pl.count_users())
        # when
        create_user(self.pl, email='name@example.org', hashed_password='asdf',
                    is_admin=True)
        # then
        self.assertEqual(1, self.pl.count_users())
        user = self.pl.get_user_by_email('name@example.org')
        self.assertIsNotNone(user)
        self.assertEqual('asdf', user.hashed_password)
        self.assertTrue(user.is_admin)

    def test_create_user_not_as_admin(self):
        # precondition
        self.assertEqual(0, self.pl.count_users())
        # when
        create_user(self.pl, email='name@example.org', hashed_password='asdf',
                    is_admin=False)
        # then
        self.assertEqual(1, self.pl.count_users())
        user = self.pl.get_user_by_email('name@example.org')
        self.assertIsNotNone(user)
        self.assertEqual('asdf', user.hashed_password)
        self.assertFalse(user.is_admin)


class ConfigTest(unittest.TestCase):
    def test_init_no_args_yields_none(self):
        # when
        result = Config()
        # then
        self.assertIsNone(result.DEBUG)
        self.assertIsNone(result.HOST)
        self.assertIsNone(result.PORT)
        self.assertIsNone(result.DB_URI)
        self.assertIsNone(result.UPLOAD_FOLDER)
        self.assertIsNone(result.ALLOWED_EXTENSIONS)
        self.assertIsNone(result.SECRET_KEY)
        self.assertIsNone(result.args)

    def test_debug_sets_debug(self):
        # when
        result = Config(debug=True)
        # then
        self.assertIs(True, result.DEBUG)

    def test_host_sets_host(self):
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


class ConfigFromEnvironTest(unittest.TestCase):
    def setUp(self):
        if 'TUDOR_DEBUG' in os.environ:
            os.environ.pop('TUDOR_DEBUG')
        if 'TUDOR_HOST' in os.environ:
            os.environ.pop('TUDOR_HOST')
        if 'TUDOR_PORT' in os.environ:
            os.environ.pop('TUDOR_PORT')
        if 'TUDOR_DB_URI' in os.environ:
            os.environ.pop('TUDOR_DB_URI')
        if 'TUDOR_UPLOAD_FOLDER' in os.environ:
            os.environ.pop('TUDOR_UPLOAD_FOLDER')
        if 'TUDOR_ALLOWED_EXTENSIONS' in os.environ:
            os.environ.pop('TUDOR_ALLOWED_EXTENSIONS')
        if 'TUDOR_SECRET_KEY' in os.environ:
            os.environ.pop('TUDOR_SECRET_KEY')

    def tearDown(self):
        if 'TUDOR_DEBUG' in os.environ:
            os.environ.pop('TUDOR_DEBUG')
        if 'TUDOR_HOST' in os.environ:
            os.environ.pop('TUDOR_HOST')
        if 'TUDOR_PORT' in os.environ:
            os.environ.pop('TUDOR_PORT')
        if 'TUDOR_DB_URI' in os.environ:
            os.environ.pop('TUDOR_DB_URI')
        if 'TUDOR_UPLOAD_FOLDER' in os.environ:
            os.environ.pop('TUDOR_UPLOAD_FOLDER')
        if 'TUDOR_ALLOWED_EXTENSIONS' in os.environ:
            os.environ.pop('TUDOR_ALLOWED_EXTENSIONS')
        if 'TUDOR_SECRET_KEY' in os.environ:
            os.environ.pop('TUDOR_SECRET_KEY')

    def test_from_environ_no_envvars_returns_none_or_false(self):
        # when
        result = Config.from_environ()
        # then
        self.assertIs(result.DEBUG, False)
        self.assertIsNone(result.HOST)
        self.assertIsNone(result.PORT)
        self.assertIsNone(result.DB_URI)
        self.assertIsNone(result.UPLOAD_FOLDER)
        self.assertIsNone(result.ALLOWED_EXTENSIONS)
        self.assertIsNone(result.SECRET_KEY)
        self.assertIsNone(result.args)

    def test_from_environ_with_envvars_returns_args(self):
        # given

        os.environ['TUDOR_DEBUG'] = str(True)
        os.environ['TUDOR_HOST'] = '1.2.3.4'
        os.environ['TUDOR_PORT'] = str(12345)
        os.environ['TUDOR_DB_URI'] = 'sqlite://'
        os.environ['TUDOR_UPLOAD_FOLDER'] = '/tmp/folder2'
        os.environ['TUDOR_ALLOWED_EXTENSIONS'] = 'zip,exe'
        os.environ['TUDOR_SECRET_KEY'] = '12345'
        # when
        result = Config.from_environ()
        # then
        self.assertIs(True, result.DEBUG)
        self.assertEqual('1.2.3.4', result.HOST)
        self.assertEqual(12345, result.PORT)
        self.assertEqual('sqlite://', result.DB_URI)
        self.assertEqual('/tmp/folder2', result.UPLOAD_FOLDER)
        self.assertEqual('zip,exe', result.ALLOWED_EXTENSIONS)
        self.assertEqual('12345', result.SECRET_KEY)


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

    @patch('tudor.open')
    def test_get_db_uri_uri_returns_uri(self, _open):
        # when
        result = get_db_uri('asdf', 'zxcv')
        # then
        assert result == 'asdf'
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_db_uri_no_uri_returns_file(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.return_value = 'qwer'
        # when
        result = get_db_uri(None, 'zxcv')
        # then
        assert result == 'qwer'
        # and
        _open.assert_called_once_with('zxcv')
        _f.read.assert_called_once_with()

    @patch('tudor.open')
    def test_get_db_uri_neither_uri_nor_file_returns_none(self, _open):
        # when
        result = get_db_uri(None, None)
        # then
        assert result is None
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_db_uri_no_file_returns_uri(self, _open):
        # when
        result = get_db_uri('asdf', None)
        # then
        assert result == 'asdf'
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_db_uri_raises_when_open_raises_fnf(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = FileNotFoundError
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_db_uri(None, 'zxcv')
        # and
        assert str(exc.exception) == 'Could not find uri file "zxcv".'

    @patch('tudor.open')
    def test_get_db_uri_raises_when_open_raises_perms(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = PermissionError
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_db_uri(None, 'zxcv')
        # and
        assert str(exc.exception) == \
               'Permission error when opening uri file "zxcv".'

    @patch('tudor.open')
    def test_get_db_uri_raises_when_open_raises_other(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = Exception('something')
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_db_uri(None, 'zxcv')
        # and
        assert str(exc.exception) == \
               'Error opening uri file "zxcv": something'

    @patch('tudor.open')
    def test_get_secret_key_uri_returns_uri(self, _open):
        # when
        result = get_secret_key('asdf', 'zxcv')
        # then
        assert result == 'asdf'
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_secret_key_no_uri_returns_file(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.return_value = 'qwer'
        # when
        result = get_secret_key(None, 'zxcv')
        # then
        assert result == 'qwer'
        # and
        _open.assert_called_once_with('zxcv')
        _f.read.assert_called_once_with()

    @patch('tudor.open')
    def test_get_secret_key_neither_uri_nor_file_returns_none(self, _open):
        # when
        result = get_secret_key(None, None)
        # then
        assert result is None
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_secret_key_no_file_returns_uri(self, _open):
        # when
        result = get_secret_key('asdf', None)
        # then
        assert result == 'asdf'
        # and
        _open.assert_not_called()

    @patch('tudor.open')
    def test_get_secret_key_raises_when_open_raises_fnf(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = FileNotFoundError
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_secret_key(None, 'zxcv')
        # and
        assert str(exc.exception) == 'Could not find secret key file "zxcv".'

    @patch('tudor.open')
    def test_get_secret_key_raises_when_open_raises_perms(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = PermissionError
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_secret_key(None, 'zxcv')
        # and
        assert str(exc.exception) == \
               'Permission error when opening secret key file "zxcv".'

    @patch('tudor.open')
    def test_get_secret_key_raises_when_open_raises_other(self, _open):
        # given
        _f = MagicMock()
        _open.return_value = _f
        _f.__enter__.return_value = _f
        _f.read.side_effect = Exception('something')
        # expect
        with self.assertRaises(ConfigError) as exc:
            get_secret_key(None, 'zxcv')
        # and
        assert str(exc.exception) == \
               'Error opening secret key file "zxcv": something'
