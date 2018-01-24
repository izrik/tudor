from tudor import generate_app, TUDOR_DB_URI, TUDOR_UPLOAD_FOLDER, \
    TUDOR_SECRET_KEY, TUDOR_ALLOWED_EXTENSIONS

app = generate_app(db_uri=TUDOR_DB_URI, upload_folder=TUDOR_UPLOAD_FOLDER,
                   secret_key=TUDOR_SECRET_KEY,
                   allowed_extensions=TUDOR_ALLOWED_EXTENSIONS)
