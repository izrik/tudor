from mock import Mock


def generate_request(args=None, cookies=None):
    request = Mock()
    if args is not None:
        request.args = args
    if cookies is not None:
        request.cookies = cookies
    return request
