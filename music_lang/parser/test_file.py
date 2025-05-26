#!/usr/bin/env python3
"""
test_file.py - 測試 .ptm 檔案的腳本
"""

from parser import MusicLanguageParser
import os
import sys

def test_ptm_file(filename):
    """測試 .ptm 檔案"""
    if not os.path.exists(filename):
        print(f"❌ 檔案不存在: {filename}")
        return False
    
    print(f"🎵 測試檔案: {filename}")
    print("=" * 50)
    
    try:
        # 讀取檔案內容
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("📄 檔案內容:")
        print("-" * 30)
        print(code)
        print("-" * 30)
        
        # 解析程式碼
        parser = MusicLanguageParser()
        ast = parser.parse(code)
        
        print("✅ 解析成功!")
        print("\n🌳 AST結構:")
        print_ast_summary(ast)
        
        return True
        
    except Exception as e:
        print(f"❌ 解析失敗: {e}")
        return False

def print_ast_summary(ast, level=0):
    """簡化的AST輸出"""
    indent = "  " * level
    
    if isinstance(ast, dict):
        ast_type = ast.get('type', 'unknown')
        print(f"{indent}- {ast_type}")
        
        # 顯示重要資訊
        if ast_type == 'program':
            print(f"{indent}  語句數: {len(ast.get('body', []))}")
        elif ast_type == 'note':
            note_val = ast.get('note', {}).get('value', 'unknown')
            duration = ast.get('duration')
            if duration:
                print(f"{indent}  音符: {note_val}, 時長: {duration['value']}")
            else:
                print(f"{indent}  音符: {note_val}")
        elif ast_type == 'chord':
            notes = ast.get('chord', {}).get('notes', [])
            print(f"{indent}  和弦: {len(notes)} 個音符")
        elif ast_type == 'tempo':
            bpm = ast.get('bpm', {}).get('value', 'unknown')
            print(f"{indent}  速度: {bpm} BPM")
        elif ast_type == 'loop':
            count = ast.get('count', {}).get('value', 'unknown')
            body_len = len(ast.get('body', []))
            print(f"{indent}  迴圈: {count} 次, {body_len} 個語句")
        
        # 遞迴處理子節點
        for key, value in ast.items():
            if key != 'type' and isinstance(value, (dict, list)):
                if isinstance(value, list) and value:
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            print_ast_summary(item, level + 1)
                elif isinstance(value, dict) and 'type' in value:
                    print_ast_summary(value, level + 1)

def create_sample_ptm():
    """創建範例 .ptm 檔案"""
    sample_code = '''// 簡單的音樂程式範例
tempo 120

// 播放音階
note "C4", 0.5
note "D4", 0.5  
note "E4", 0.5
note "F4", 0.5
note "G4", 1.0

// 播放和弦
chord ["C4", "E4", "G4"], 2.0

// 重複旋律
loop 2 {
    note "A4", 0.5
    note "B4", 0.5
    note "C5", 1.0
}
'''
    
    filename = "sample.ptm"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    print(f"✅ 已創建範例檔案: {filename}")
    return filename

def main():
    """主函數"""
    if len(sys.argv) > 1:
        # 測試指定的檔案
        filename = sys.argv[1]
        if not filename.endswith('.ptm'):
            print("⚠️  建議使用 .ptm 副檔名")
        test_ptm_file(filename)
    else:
        # 如果沒有指定檔案，創建並測試範例檔案
        print("🎯 沒有指定檔案，將創建並測試範例檔案")
        sample_file = create_sample_ptm()
        print()
        test_ptm_file(sample_file)

if __name__ == "__main__":
    main()