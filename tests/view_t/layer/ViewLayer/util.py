from unittest.mock import Mock


def generate_mock_request(method=None, args=None, cookies=None, form=None,
                          files=None):

    request = Mock()

    if method is None:
        method = 'POST'
    if args is None:
        args = {}
    if cookies is None:
        cookies = {}
    if form is None:
        form = {}
    if files is None:
        files = {}

    request.method = method
    request.args = args
    request.cookies = cookies
    request.form = form
    request.files = files

    return request
