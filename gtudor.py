from tudor import generate_app, Config

config = Config.from_environ()
app = generate_app(db_uri=config.DB_URI, upload_folder=config.UPLOAD_FOLDER,
                   secret_key=config.SECRET_KEY,
                   allowed_extensions=config.ALLOWED_EXTENSIONS)
