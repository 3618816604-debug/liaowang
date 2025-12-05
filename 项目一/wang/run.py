from app import app, db
from app.routes import init_db

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)