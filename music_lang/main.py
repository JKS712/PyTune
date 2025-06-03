#!/usr/bin/env python3
"""
main.py - 音樂程式語言主執行檔
位於 music_lang/ 目錄內
"""

import sys
import os
import argparse

# 添加當前目錄和上級目錄到 Python 路徑
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

try:
    from parser.parser import MusicLanguageParser
except ImportError:
    try:
        from music_lang.parser.parser import MusicLanguageParser
    except ImportError:
        print("❌ 無法導入解析器模組")
        print("請確認 parser/parser.py 檔案存在")
        sys.exit(1)

try:
    from audio.audio_engine import MusicInterpreter
except ImportError:
    try:
        from music_lang.audio.audio_engine import MusicInterpreter
    except ImportError:
        print("❌ 無法導入音訊引擎模組")
        print("請確認 audio/audio_engine.py 檔案存在")
        sys.exit(1)

def find_ptm_files():
    """尋找專案中的 .ptm 檔案"""
    ptm_files = []
    
    # 搜尋常見目錄
    search_dirs = [
        '.',
        '..',
        'parser',
        '../examples',
        '../tests',
        os.path.join('..', 'examples'),
        os.path.join('..', 'tests')
    ]
    
    for directory in search_dirs:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.ptm') or file.endswith('.mus'):
                        ptm_files.append(os.path.join(root, file))
    
    return ptm_files

def play_music_file(filepath):
    """播放音樂檔案"""
    if not os.path.exists(filepath):
        print(f"❌ 檔案不存在: {filepath}")
        return False
    
    print(f"🎵 載入音樂檔案: {filepath}")
    print("=" * 60)
    
    try:
        # 讀取檔案
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("📄 程式碼內容:")
        print("-" * 40)
        print(code)
        print("-" * 40)
        
        # 解析程式碼
        print("🔍 解析程式碼...")
        parser = MusicLanguageParser()
        ast = parser.parse(code)
        
        print("✅ 解析成功!")
        print(f"🌳 AST 結構: {ast.get('type', 'unknown')}")
        print(f"📊 語句數量: {len(ast.get('body', []))}")
        
        # 詢問是否播放
        print("\n🎼 準備播放音樂...")
        response = input("是否開始播放? (y/n/s=顯示AST): ").lower().strip()
        
        if response == 's':
            print("\n🌳 完整 AST 結構:")
            print_ast_detailed(ast)
            response = input("\n現在播放音樂? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', 'Y', '']:
            print("\n🎵 開始播放...")
            print("   (按 Ctrl+C 可中斷播放)")
            print("=" * 40)
            
            # 執行音樂
            interpreter = MusicInterpreter()
            interpreter.execute(ast)
            
            return True
        else:
            print("⏹️  取消播放")
            return True
            
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷")
        return True
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_ast_detailed(ast, level=0):
    """詳細顯示 AST 結構"""
    indent = "  " * level
    
    if isinstance(ast, dict):
        ast_type = ast.get('type', 'unknown')
        print(f"{indent}📍 {ast_type}")
        
        # 顯示具體內容
        for key, value in ast.items():
            if key == 'type':
                continue
            elif key == 'body' and isinstance(value, list):
                print(f"{indent}  📋 {key}: [{len(value)} 項目]")
                for i, item in enumerate(value):
                    print(f"{indent}    [{i}]:")
                    print_ast_detailed(item, level + 2)
            elif isinstance(value, dict):
                print(f"{indent}  🔹 {key}:")
                print_ast_detailed(value, level + 1)
            elif isinstance(value, list):
                print(f"{indent}  📋 {key}: [{len(value)} 項目]")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        print(f"{indent}    [{i}]:")
                        print_ast_detailed(item, level + 2)
                    else:
                        print(f"{indent}    [{i}]: {item}")
            else:
                print(f"{indent}  🔸 {key}: {value}")
    else:
        print(f"{indent}📎 {ast}")

def show_project_info():
    """顯示專案資訊"""
    print("""
🎵 音樂程式語言 (Music Programming Language)

專案結構:
  music_lang/
  ├── parser/
  │   ├── parser.py          # 語言解析器
  │   └── test_program.ptm   # 測試程式
  ├── audio/                 # 音訊引擎
  │   └── audio_engine.py
  └── grammar/              # 語法定義

語法支援:
  ✅ 音符播放: note "C4", 1.0
  ✅ 和弦播放: chord ["C4", "E4", "G4"]
  ✅ 速度控制: tempo 120
  ✅ 迴圈結構: loop 3 { ... }
  ✅ 變數賦值: melody = "G4"
  ✅ 數學運算: tempo 60 + 60
  ✅ 註解支援: // 這是註解

音符範圍:
  C0 ~ B8 (支援升降音: C#, Db 等)
    """)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='音樂程式語言執行器',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='要執行的 .ptm 或 .mus 檔案路徑'
    )
    
    parser.add_argument(
        '--find', 
        action='store_true',
        help='尋找專案中的所有音樂程式檔案'
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='執行預設測試檔案'
    )
    
    parser.add_argument(
        '--info', 
        action='store_true',
        help='顯示專案資訊'
    )
    
    args = parser.parse_args()
    
    # 顯示專案資訊
    if args.info:
        show_project_info()
        return
    
    # 尋找音樂檔案
    if args.find:
        print("🔍 搜尋音樂程式檔案...")
        ptm_files = find_ptm_files()
        
        if ptm_files:
            print(f"📁 找到 {len(ptm_files)} 個音樂程式檔案:")
            for i, filepath in enumerate(ptm_files, 1):
                size = os.path.getsize(filepath)
                print(f"  {i:2d}. {filepath} ({size} bytes)")
            
            print(f"\n使用方式:")
            print(f"  python {os.path.basename(__file__)} <檔案路徑>")
            print(f"  python {os.path.basename(__file__)} --test  # 執行預設測試")
        else:
            print("❌ 未找到任何音樂程式檔案")
        return
    
    # 執行測試檔案
    if args.test:
        test_files = [
            "parser/test_program.ptm",
            "../examples/test_program.mus",
            "test_program.ptm",
            "../test_program.ptm"
        ]
        
        test_file = None
        for tf in test_files:
            if os.path.exists(tf):
                test_file = tf
                break
        
        if test_file:
            print(f"🧪 執行測試檔案: {test_file}")
            play_music_file(test_file)
        else:
            print("❌ 找不到測試檔案")
            print("請確認以下路徑是否存在測試檔案:")
            for tf in test_files:
                print(f"   {tf}")
        return
    
    # 執行指定檔案
    if args.file:
        play_music_file(args.file)
        return
    
    # 沒有參數時的預設行為
    print("🎵 音樂程式語言執行器")
    print("=" * 40)
    
    # 自動尋找並顯示可用檔案
    ptm_files = find_ptm_files()
    
    if ptm_files:
        print(f"📁 找到 {len(ptm_files)} 個音樂程式檔案:")
        for i, filepath in enumerate(ptm_files, 1):
            print(f"  {i}. {filepath}")
        
        print(f"\n使用方式:")
        print(f"  python {os.path.basename(__file__)} <檔案路徑>   # 執行指定檔案")
        print(f"  python {os.path.basename(__file__)} --find      # 尋找所有檔案")
        print(f"  python {os.path.basename(__file__)} --test      # 執行測試檔案")
        print(f"  python {os.path.basename(__file__)} --info      # 顯示專案資訊")
    else:
        print("❌ 未找到任何音樂程式檔案")
        print("請確認專案結構或創建測試檔案")
    
    print(f"\n💡 提示: 使用 --help 查看所有選項")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程式結束")
    except Exception as e:
        print(f"\n❌ 程式錯誤: {e}")
        import traceback
        traceback.print_exc()