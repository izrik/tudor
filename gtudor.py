from tudor import generate_app, Config, get_db_uri, get_secret_key

config = Config.from_environ()
config.DB_URI = get_db_uri(config.DB_URI, config.DB_URI_FILE)
config.SECRET_KEY = get_secret_key(config.SECRET_KEY, config.SECRET_KEY_FILE)
config = Config.combine(config, Config.from_defaults())
app = generate_app(db_uri=config.DB_URI, upload_folder=config.UPLOAD_FOLDER,
                   secret_key=config.SECRET_KEY,
                   allowed_extensions=config.ALLOWED_EXTENSIONS)
