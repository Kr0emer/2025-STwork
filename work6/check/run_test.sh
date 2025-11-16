#!/bin/bash

# Checkout 微服务测试运行脚本

echo "================================"
echo "Checkout 微服务测试套件"
echo "================================"
echo ""

# 检查服务是否运行
check_service() {
    echo "🔍 检查服务状态..."
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ 服务正在运行"
        return 0
    else
        echo "❌ 服务未运行"
        echo ""
        echo "请在另一个终端窗口启动服务："
        echo "  python app.py"
        echo ""
        return 1
    fi
}

# 运行测试
run_tests() {
    echo ""
    echo "🧪 运行测试..."
    echo "================================"
    pytest test_checkout.py -v --tb=short
    
    TEST_RESULT=$?
    
    echo ""
    echo "================================"
    if [ $TEST_RESULT -eq 0 ]; then
        echo "✅ 所有测试通过！"
    else
        echo "❌ 部分测试失败"
    fi
    
    return $TEST_RESULT
}

# 生成测试报告
generate_report() {
    echo ""
    echo "📊 生成 HTML 测试报告..."
    pytest test_checkout.py --html=report.html --self-contained-html -v
    
    if [ -f "report.html" ]; then
        echo "✅ 报告已生成: report.html"
        
        # 尝试在浏览器中打开报告
        if command -v open > /dev/null 2>&1; then
            open report.html
        elif command -v xdg-open > /dev/null 2>&1; then
            xdg-open report.html
        else
            echo "请手动打开 report.html 查看报告"
        fi
    fi
}

# 主函数
main() {
    # 检查依赖
    if ! command -v pytest > /dev/null 2>&1; then
        echo "❌ pytest 未安装"
        echo "请运行: pip install -r requirements.txt"
        exit 1
    fi
    
    # 检查服务
    if ! check_service; then
        exit 1
    fi
    
    # 显示菜单
    echo ""
    echo "请选择测试类型："
    echo "1) 运行所有测试"
    echo "2) 仅运行功能测试"
    echo "3) 仅运行性能测试"
    echo "4) 生成 HTML 报告"
    echo "5) 退出"
    echo ""
    read -p "请输入选项 (1-5): " choice
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            echo ""
            echo "🧪 运行功能测试..."
            pytest test_checkout.py::TestCheckoutService -v
            ;;
        3)
            echo ""
            echo "🧪 运行性能测试..."
            pytest test_checkout.py::TestPerformance -v -s
            ;;
        4)
            generate_report
            ;;
        5)
            echo "退出"
            exit 0
            ;;
        *)
            echo "无效选项"
            exit 1
            ;;
    esac
}

# 运行主函数
main