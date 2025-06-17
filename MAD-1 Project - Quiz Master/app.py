from flask import Flask, render_template,url_for
from controller.database import db
from models import *
# from controller.routes import view

app = Flask(__name__,)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'thisissecretkey'
db.init_app(app)





with app.app_context():
    db.create_all()
    admin = User.query.filter_by(email = 'admin@gmail.com').first()
    if not admin:
        admin = User(
            username = 'admin',
            email = 'admin@gmail.com',
            password = '1234567890',
            # roles = [admin_role]
        )
    db.session.add(admin)
    db.session.commit()




from controller.routes import *




if __name__ == '__main__':
 app.run(debug=True)