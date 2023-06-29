import os.path
import sys
import unittest
from unittest.mock import patch

from tudor import main


class MainFunctionTests(unittest.TestCase):
    def test_main(self):
        with patch('tudor.print') as mock_print, \
                patch('tudor.generate_app') as mock_generate:
            app = mock_generate.return_value
            folder = os.path.dirname(__file__)

            # when
            main([])

            # then
            mock_print.assert_any_call('__version__: 0.9', file=sys.stderr)
            mock_print.assert_any_call('__revision__: unknown', file=sys.stderr)
            mock_print.assert_any_call(f'getcwd(): {folder}', file=sys.stderr)
            mock_print.assert_any_call('DEBUG: False', file=sys.stderr)
            mock_print.assert_any_call('HOST: 127.0.0.1', file=sys.stderr)
            mock_print.assert_any_call('PORT: 8304', file=sys.stderr)
            mock_print.assert_any_call('UPLOAD_FOLDER: /tmp/tudor/uploads',
                                       file=sys.stderr)
            mock_print.assert_any_call(
                'ALLOWED_EXTENSIONS: txt,pdf,png,jpg,jpeg,gif',
                file=sys.stderr)
            self.assertEqual(mock_print.call_count, 8)

            # and
            mock_generate.assert_called_once_with(
                db_uri='sqlite:////tmp/test.db',
                db_options=None,
                upload_folder='/tmp/tudor/uploads',
                secret_key=None,
                allowed_extensions='txt,pdf,png,jpg,jpeg,gif')

            app.run.assert_called_once_with(debug=False, host="127.0.0.1",
                port=8304)
            # and
            app.pl.create_all.assert_not_called()
            app.bcrypt.generate_password_hash.assert_not_called()
            app.ll.do_export_data.assert_not_called()
            app.ll.do_import_data.assert_not_called()

