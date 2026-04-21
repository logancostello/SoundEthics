from flask import Flask, url_for
from flask_cors import CORS
from routes.upload import upload_bp
from routes.download import download_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(upload_bp)
    app.register_blueprint(download_bp)

    @app.get("/")
    def index():
        upload_url = url_for("upload.upload_file", _external=True)
        return f'<p>Hello, World!</p><br><a href="{upload_url}">Upload File</a>'

    return app


if __name__ == "__main__":
    create_app().run(debug=True)