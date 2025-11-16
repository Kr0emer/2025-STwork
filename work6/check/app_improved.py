"""
改进版 Checkout 微服务
包含输入验证、错误处理和日志记录
"""

from flask import Flask, request, jsonify
from decimal import Decimal, InvalidOperation
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_items(items):
    """
    验证商品列表
    
    Args:
        items: 商品列表
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not items:
        return False, "empty cart"
    
    if not isinstance(items, list):
        return False, "items must be a list"
    
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            return False, f"item {idx} must be an object"
        
        # 检查必填字段
        if "price" not in item:
            return False, f"item {idx}: missing 'price' field"
        
        if "quantity" not in item:
            return False, f"item {idx}: missing 'quantity' field"
        
        # 验证数据类型
        if not isinstance(item["price"], (int, float)):
            return False, f"item {idx}: price must be a number"
        
        if not isinstance(item["quantity"], (int, float)):
            return False, f"item {idx}: quantity must be a number"
        
        # 验证数值范围
        if item["price"] < 0:
            return False, f"item {idx}: price must be non-negative"
        
        if item["quantity"] < 0:
            return False, f"item {idx}: quantity must be non-negative"
        
        # 验证合理范围
        if item["price"] > 1000000:
            return False, f"item {idx}: price exceeds maximum allowed value"
        
        if item["quantity"] > 10000:
            return False, f"item {idx}: quantity exceeds maximum allowed value"
    
    return True, None


@app.route("/checkout", methods=["POST"])
def checkout():
    """
    结账端点：计算购物车总价
    
    请求格式:
    {
        "items": [
            {"price": 100, "quantity": 2},
            {"price": 50.5, "quantity": 1}
        ]
    }
    
    响应格式:
    {
        "total": 250.5,
        "status": "ok",
        "items_count": 2
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if data is None:
            logger.warning("Invalid JSON in request")
            return jsonify({"error": "invalid JSON format"}), 400
        
        items = data.get("items", [])
        
        # 记录请求
        logger.info(f"Checkout request: {len(items)} items")
        
        # 验证输入
        is_valid, error_msg = validate_items(items)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            return jsonify({"error": error_msg}), 400
        
        # 使用 Decimal 进行精确计算
        try:
            total = sum(
                Decimal(str(item["price"])) * Decimal(str(item["quantity"]))
                for item in items
            )
            total = float(total)  # 转换回 float 以便 JSON 序列化
        except (InvalidOperation, ValueError) as e:
            logger.error(f"Calculation error: {e}")
            return jsonify({"error": "invalid numeric values"}), 400
        
        # 记录成功
        logger.info(f"Checkout successful: total={total}, items={len(items)}")
        
        return jsonify({
            "total": total,
            "status": "ok",
            "items_count": len(items)
        }), 200
        
    except Exception as e:
        # 捕获未预期的错误
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "internal server error"}), 500


@app.route("/health", methods=["GET"])
def health():
    """
    健康检查端点
    """
    return jsonify({
        "status": "healthy",
        "service": "checkout"
    }), 200


@app.errorhandler(404)
def not_found(error):
    """处理 404 错误"""
    return jsonify({"error": "endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """处理 405 错误"""
    return jsonify({"error": "method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    """处理 500 错误"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting Checkout Service on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)