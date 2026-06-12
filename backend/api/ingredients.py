"""食材库 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

ingredients_bp = Blueprint('ingredients', __name__)


@ingredients_bp.route('', methods=['GET'])
def list_ingredients():
    """食材列表（支持分类筛选、搜索）"""
    category1 = request.args.get('category1')
    category2 = request.args.get('category2')
    search = request.args.get('search')
    created_by = request.args.get('created_by')

    sql = "SELECT * FROM ingredients WHERE 1=1"
    params = []

    if category1:
        sql += " AND category1 = %s"; params.append(category1)
    if category2:
        sql += " AND category2 = %s"; params.append(category2)
    if search:
        sql += " AND name LIKE %s"; params.append(f"%{search}%")
    if created_by:
        sql += " AND created_by = %s"; params.append(created_by)

    sql += " ORDER BY FIELD(category1,'畜禽肉类','鲜蔬类','水产海鲜','五谷干货','调味佐料','水果类'), category2, name"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        # 一级分类统计
        cur.execute("SELECT category1, COUNT(*) as cnt FROM ingredients GROUP BY category1")
        stats = {r['category1']: r['cnt'] for r in cur.fetchall()}
        return jsonify({"data": rows, "stats": stats})


@ingredients_bp.route('/<ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "食材不存在"}), 404
        return jsonify(row)


@ingredients_bp.route('', methods=['POST'])
def create_ingredient():
    """自定义食材"""
    body = request.get_json()
    if not body or not body.get('name'):
        return jsonify({"error": "食材名称必填"}), 400

    ing_id = f"ing_custom_{uuid.uuid4().hex[:8]}"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingredients (id, name, emoji, category1, category2, unit, storage, is_system, created_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s)",
            (ing_id, body['name'], body.get('emoji', '📦'), body.get('category1', ''),
             body.get('category2', ''), body.get('unit', '斤'), body.get('storage', 'room'),
             body.get('created_by', ''))
        )
        return jsonify({"id": ing_id, "message": "创建成功"}), 201


@ingredients_bp.route('/<ingredient_id>', methods=['PUT'])
def update_ingredient(ingredient_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_system FROM ingredients WHERE id = %s", (ingredient_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "食材不存在"}), 404
        if row['is_system']:
            return jsonify({"error": "系统食材不可修改"}), 403

        cur.execute(
            "UPDATE ingredients SET name=%s, emoji=%s, category1=%s, category2=%s, unit=%s WHERE id=%s",
            (body.get('name'), body.get('emoji'), body.get('category1'),
             body.get('category2'), body.get('unit'), ingredient_id)
        )
        return jsonify({"message": "更新成功"})


@ingredients_bp.route('/<ingredient_id>', methods=['DELETE'])
def delete_ingredient(ingredient_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_system FROM ingredients WHERE id = %s", (ingredient_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "食材不存在"}), 404
        if row['is_system']:
            return jsonify({"error": "系统食材不可删除"}), 403
        cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
        return jsonify({"message": "删除成功"})
