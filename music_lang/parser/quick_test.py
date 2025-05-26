#!/usr/bin/env python3
"""
quick_test.py - 快速測試不同程式碼的腳本
"""

from parser import MusicLanguageParser
import json

def pretty_print_ast(ast, indent=0):
    """美化輸出AST"""
    spaces = "  " * indent
    if isinstance(ast, dict):
        print(f"{spaces}{{")
        for key, value in ast.items():
            print(f"{spaces}  {key}:")
            pretty_print_ast(value, indent + 2)
        print(f"{spaces}}}")
    elif isinstance(ast, list):
        print(f"{spaces}[")
        for item in ast:
            pretty_print_ast(item, indent + 1)
        print(f"{spaces}]")
    else:
        print(f"{spaces}{ast}")

def test_code(code, description=""):
    """測試一段程式碼"""
    print(f"\n{'='*50}")
    if description:
        print(f"測試: {description}")
    print(f"程式碼:")
    print(code)
    print(f"{'-'*30}")
    
    try:
        parser = MusicLanguageParser()
        ast = parser.parse(code)
        print("✅ 解析成功!")
        print("AST結構:")
        pretty_print_ast(ast)
    except Exception as e:
        print(f"❌ 解析失敗: {e}")

def main():
    """主測試函數"""
    
    # 測試案例
    test_cases = [
        # 1. 最簡單的音符
        ('note "C4"', "基本音符"),
        
        # 2. 帶持續時間的音符
        ('note "A4", 1.5', "帶時間的音符"),
        
        # 3. 和弦
        ('chord ["C4", "E4", "G4"]', "基本和弦"),
        
        # 4. 速度設定
        ('tempo 120', "設定速度"),
        
        # 5. 簡單迴圈
        ('loop 2 { note "C4" }', "簡單迴圈"),
        
        # 6. 變數賦值  
        ('melody = "G4"', "變數賦值"),
        
        # 7. 數學運算
        ('tempo 60 + 60', "數學運算"),
        
        # 8. 複合程式
        ('''tempo 120
note "C4", 1.0
chord ["C4", "E4", "G4"]
loop 2 {
    note "A4"
    note "B4"
}''', "複合程式"),
        
        # 9. 錯誤案例 - 測試錯誤處理
        ('note', "錯誤語法測試"),
    ]
    
    print("🎵 音樂程式語言解析器測試")
    print("=" * 50)
    
    for code, desc in test_cases:
        test_code(code, desc)
    
    print(f"\n{'='*50}")
    print("🎯 測試完成!")

def interactive_test():
    """互動式測試"""
    parser = MusicLanguageParser()
    
    print("🎵 互動式測試模式")
    print("輸入程式碼來測試，輸入 'quit' 結束")
    print("=" * 40)
    
    while True:
        try:
            code = input("\n請輸入程式碼: ").strip()
            if code.lower() in ['quit', 'exit', 'q']:
                break
            
            if not code:
                continue
                
            ast = parser.parse(code)
            print("✅ 解析成功!")
            pretty_print_ast(ast)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")
    
    print("\n👋 再見!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        interactive_test()
    else:
        main()