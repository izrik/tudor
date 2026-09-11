from tests.util import generate_test_app


def generate_ll(db_uri='sqlite://', upload_folder=None,
                allowed_extensions=None):
    return generate_test_app(db_uri=db_uri, upload_folder=upload_folder,
                             allowed_extensions=allowed_extensions).ll
