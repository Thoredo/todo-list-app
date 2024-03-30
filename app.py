from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from database.tables import db, Users
from auth.views import auth_bp
from lists.views import lists_bp
from tasks.views import tasks_bp
from groups.views import groups_bp

load_dotenv()

app = Flask(__name__)
# MYSQL db
mysql_pass = os.getenv("MYSQL_PASS")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://root:{mysql_pass}@localhost/jurgenst_flask_users"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.app_context().push()

db.init_app(app)
migrate = Migrate(app, db)

# Flask_login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(lists_bp, url_prefix="/lists")
app.register_blueprint(tasks_bp, url_prefix="/tasks")
app.register_blueprint(groups_bp, url_prefix="/groups")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


@app.route("/")
def index():
    active_page = "index"

    return render_template("index.html", active_page=active_page)


if __name__ == "__main__":
    app.run(debug=True)
