from mock import Mock


def generate_request(args=None, cookies=None, form=None, files=None):

    request = Mock()

    if args is None:
        args = {}
    if cookies is None:
        cookies = {}
    if form is None:
        form = {}
    if files is None:
        files = {}

    request.args = args
    request.cookies = cookies
    request.form = form
    request.files = files

    return request
