from flask import Flask, request, jsonify
app = Flask(__name__)
# 模拟库存
inventory = {"book": 10}
@app.route("/order", methods=["POST"])
def order():
    item = request.json.get("item")
    qty = request.json.get("quantity", 1)
    if item not in inventory:
        return jsonify({"error": "不存在的商品"}), 400
    if inventory[item] < qty:
        return jsonify({"error": "库存不足"}), 400
    inventory[item] -= qty
    return jsonify({"success": True, "剩余库存": inventory[item]})