"""用户 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

users_bp = Blueprint('users', __name__)


@users_bp.route('/login', methods=['POST'])
def login():
    """微信静默登录"""
    body = request.get_json()
    openid = body.get('openid')
    if not openid:
        return jsonify({"error": "openid 必填"}), 400

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (openid,))
        user = cur.fetchone()
        if user:
            return jsonify({"user": user, "is_new": False})
        # 新用户
        cur.execute(
            "INSERT INTO users (id, nickname, default_servings) VALUES (%s, %s, 4)",
            (openid, body.get('nickname', '微信用户'))
        )
        cur.execute("SELECT * FROM users WHERE id = %s", (openid,))
        return jsonify({"user": cur.fetchone(), "is_new": True}), 201


@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        return jsonify(user)


@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET nickname=%s, avatar=%s, default_servings=%s, unit_preference=%s, memory_enabled=%s WHERE id=%s",
            (body.get('nickname'), body.get('avatar'), body.get('default_servings', 4),
             body.get('unit_preference', 'g'), body.get('memory_enabled', 1), user_id)
        )
        return jsonify({"message": "更新成功"})
