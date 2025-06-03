import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(__file__))

# 導入並執行 music_lang 中的 main 函數
try:
    from music_lang.main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確認 music_lang 目錄結構正確")
    sys.exit(1)