from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/checkout", methods=["POST"])
def checkout():
    """
    结账端点：计算购物车总价
    """
    data = request.get_json()
    items = data.get("items", [])
    
    if not items:
        return jsonify({"error": "empty cart"}), 400
    
    total = sum(i["price"] * i["quantity"] for i in items)
    return jsonify({"total": total, "status": "ok"}), 200

@app.route("/health", methods=["GET"])
def health():
    """
    健康检查端点
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)