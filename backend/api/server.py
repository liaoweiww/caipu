"""家庭私厨 API 服务层"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ====== 注册蓝图 ======
from api.recipes      import recipes_bp
from api.ingredients  import ingredients_bp
from api.meal_plans   import meal_plans_bp
from api.purchases    import purchases_bp
from api.feasts       import feasts_bp
from api.users        import users_bp
from api.checkins     import checkins_bp
from api.tenants      import tenants_bp

app.register_blueprint(recipes_bp,     url_prefix='/api/recipes')
app.register_blueprint(ingredients_bp, url_prefix='/api/ingredients')
app.register_blueprint(meal_plans_bp,  url_prefix='/api/meal-plans')
app.register_blueprint(purchases_bp,   url_prefix='/api/purchases')
app.register_blueprint(feasts_bp,      url_prefix='/api/feasts')
app.register_blueprint(users_bp,       url_prefix='/api/users')
app.register_blueprint(checkins_bp,    url_prefix='/api/checkins')
app.register_blueprint(tenants_bp,     url_prefix='/api/tenants')


@app.route('/api/health')
def health_check():
    from data.database import check_db
    db_ok = check_db()
    return jsonify({
        "status": "ok",
        "app": "家庭私厨",
        "db": "connected" if db_ok else "disconnected"
    })


@app.route('/')
def index():
    root = os.path.join(os.path.dirname(__file__), '..')
    return send_from_directory(root, 'index.html')
