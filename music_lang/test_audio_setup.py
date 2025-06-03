import sys
import os

def test_imports():
    """測試所需套件是否已安裝"""
    print("🔍 檢查套件安裝狀態...")
    
    try:
        import numpy as np
        print("✅ NumPy 已安裝")
    except ImportError:
        print("❌ NumPy 未安裝 - 執行: pip install numpy")
        return False
    
    try:
        import pygame
        print("✅ Pygame 已安裝")
    except ImportError:
        print("❌ Pygame 未安裝 - 執行: pip install pygame")
        return False
    
    try:
        import lark
        print("✅ Lark 已安裝")
    except ImportError:
        print("❌ Lark 未安裝 - 執行: pip install lark")
        return False
    
    return True

def test_audio_engine():
    """測試音訊引擎"""
    print("\n🎵 測試音訊引擎...")
    
    # 添加路徑
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'music_lang'))
    
    try:
        from audio.audio_engine import AudioEngine, MusicInterpreter
        print("✅ 音訊引擎模組載入成功")
        
        # 測試基本音訊功能
        engine = AudioEngine()
        
        print("\n🎼 播放測試音符...")
        engine.play_note("C4", 0.5)
        engine.play_note("E4", 0.5)
        engine.play_note("G4", 0.5)
        
        print("\n🎵 播放測試和弦...")
        engine.play_chord(["C4", "E4", "G4"], 1.0)
        
        engine.cleanup()
        print("✅ 音訊引擎測試完成")
        return True
        
    except ImportError as e:
        print(f"❌ 音訊引擎載入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 音訊引擎測試失敗: {e}")
        return False

def test_parser():
    """測試解析器"""
    print("\n📝 測試解析器...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'music_lang'))
    
    try:
        from parser.parser import MusicLanguageParser
        print("✅ 解析器模組載入成功")
        
        parser = MusicLanguageParser()
        
        # 測試簡單程式碼
        test_code = '''
        tempo 120
        note "C4", 1.0
        chord ["C4", "E4", "G4"]
        '''
        
        ast = parser.parse(test_code)
        print("✅ 程式碼解析成功")
        print(f"📊 AST 節點數: {len(ast.get('body', []))}")
        return True
        
    except ImportError as e:
        print(f"❌ 解析器載入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析器測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 pyTune 音訊系統測試")
    print("=" * 50)
    
    # 檢查套件
    if not test_imports():
        print("\n❌ 請先安裝必要套件")
        return False
    
    # 檢查解析器
    if not test_parser():
        print("\n❌ 解析器測試失敗")
        return False
    
    # 檢查音訊引擎
    if not test_audio_engine():
        print("\n❌ 音訊引擎測試失敗")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有測試通過！您的 pyTune 系統已準備就緒")
    print("\n💡 現在您可以執行:")
    print("   python music_lang/main.py --test")
    print("   python music_lang/main.py examples/test_program.mus")
    
    return True

if __name__ == "__main__":
    main()