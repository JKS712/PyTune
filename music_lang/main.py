#!/usr/bin/env python3
"""
main.py - PyTune 音樂程式語言主執行檔（支援音色與休止符功能）
"""

import sys
import os
import argparse
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def import_audio_modules():
    """動態導入音訊模組"""
    try:
        # 嘗試導入增強音訊引擎
        from audio.audio_engine import EnhancedAudioEngine
        print("✅ 成功載入增強音訊引擎（支援音色與休止符）")
        return EnhancedAudioEngine, 'enhanced'
    except ImportError as e:
        print(f"⚠️  增強音訊引擎載入失敗: {e}")
        
        try:
            # 回退到原始音訊引擎
            from audio.audio_engine import AudioEngine
            print("✅ 載入原始音訊引擎（支援休止符）")
            return AudioEngine, 'original'
        except ImportError as e:
            print(f"❌ 無法導入音訊引擎模組: {e}")
            print("請確認 audio/audio_engine.py 檔案存在")
            return None, None

def import_parser():
    """動態導入解析器"""
    try:
        # 嘗試導入支援音色和休止符的解析器
        from parser.parser import MusicLanguageParser
        print("✅ 成功載入支援音色與休止符的解析器")
        return MusicLanguageParser, True
    except ImportError:
        try:
            # 回退到原始解析器
            from parser.parser import MusicLanguageParser
            print("⚠️  載入原始解析器（可能不支援部分功能）")
            return MusicLanguageParser, False
        except ImportError as e:
            print(f"❌ 無法導入解析器: {e}")
            return None, False

def play_music_file(filename):
    """播放音樂檔案"""
    try:
        # 檢查檔案是否存在
        if not os.path.exists(filename):
            print(f"❌ 找不到檔案: {filename}")
            return
        
        # 檢查檔案副檔名
        if not filename.endswith(('.ptm', '.ml')):
            print(f"⚠️  建議使用 .ptm 或 .ml 副檔名")
        
        # 讀取檔案
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"📁 讀取檔案: {filename}")
        
        # 導入模組
        AudioEngine, engine_type = import_audio_modules()
        MusicParser, supports_instruments = import_parser()
        
        if not AudioEngine or not MusicParser:
            print("❌ 模組載入失敗，無法執行")
            return
        
        # 解析程式碼
        print("🔍 解析程式碼...")
        parser = MusicParser()
        ast = parser.parse(code)
        print("✅ 解析成功！")
        
        # 初始化音訊系統
        print("🎵 初始化音訊系統...")
        if engine_type == 'enhanced':
            audio_engine = AudioEngine()
        else:
            # 原始引擎需要不同的初始化方式
            try:
                from audio.synthesizer import Synthesizer
                synthesizer = Synthesizer()
                audio_engine = AudioEngine(synthesizer)
            except ImportError:
                audio_engine = AudioEngine()
        
        # 檢查是否使用了音色功能
        if supports_instruments:
            print("🎼 音色與休止符功能已啟用")
        else:
            print("⚠️  當前版本可能不支援部分功能")
        
        # 執行音樂程式
        print("🎵 開始播放音樂...")
        if hasattr(audio_engine, 'execute'):
            audio_engine.execute(ast)
        else:
            # 原始引擎可能使用不同的方法名
            if hasattr(audio_engine, 'play'):
                audio_engine.play(ast)
            else:
                print("❌ 音訊引擎接口不匹配")
                return
        
        print("🎵 音樂播放完成！")
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {filename}")
        print(f"   請確認檔案路徑正確")
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
        print(f"   請檢查 .ptm 檔案的語法")
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

def play_music_code(code):
    """播放程式碼字串"""
    try:
        # 導入模組
        AudioEngine, engine_type = import_audio_modules()
        MusicParser, supports_instruments = import_parser()
        
        if not AudioEngine or not MusicParser:
            print("❌ 模組載入失敗，無法執行")
            return
        
        # 解析並執行
        print("🔍 解析程式碼...")
        parser = MusicParser()
        ast = parser.parse(code)
        print("✅ 解析成功！")
        
        print("🎵 初始化音訊系統...")
        if engine_type == 'enhanced':
            audio_engine = AudioEngine()
        else:
            try:
                from audio.synthesizer import Synthesizer
                synthesizer = Synthesizer()
                audio_engine = AudioEngine(synthesizer)
            except ImportError:
                audio_engine = AudioEngine()
        
        print("🎵 開始播放音樂...")
        if hasattr(audio_engine, 'execute'):
            audio_engine.execute(ast)
        else:
            if hasattr(audio_engine, 'play'):
                audio_engine.play(ast)
            else:
                print("❌ 音訊引擎接口不匹配")
                return
        
        print("🎵 音樂播放完成！")
        
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()

def interactive_mode():
    """互動模式"""
    print("🎹 PyTune 互動模式")
    print("輸入 'exit' 或 'quit' 離開")
    print("輸入 'help' 查看說明")
    print("輸入 'examples' 查看範例檔案")
    print("輸入 'status' 查看系統狀態")
    print("輸入 'test-rest' 測試休止符功能")
    
    # 導入模組
    AudioEngine, engine_type = import_audio_modules()
    MusicParser, supports_instruments = import_parser()
    
    if not AudioEngine or not MusicParser:
        print("❌ 模組載入失敗，無法進入互動模式")
        return
    
    # 初始化系統
    try:
        if engine_type == 'enhanced':
            audio_engine = AudioEngine()
        else:
            try:
                from audio.synthesizer import Synthesizer
                synthesizer = Synthesizer()
                audio_engine = AudioEngine(synthesizer)
            except ImportError:
                audio_engine = AudioEngine()
        
        parser = MusicParser()
        print(f"🎼 系統狀態: 音色支援 {'✅' if supports_instruments else '❌'}, 休止符支援 ✅")
        
    except Exception as e:
        print(f"❌ 系統初始化失敗: {e}")
        return
    
    while True:
        try:
            code = input("PyTune>>> ")
            
            if code.lower() in ['exit', 'quit']:
                break
            elif code.lower() == 'help':
                show_help(supports_instruments)
                continue
            elif code.lower() == 'examples':
                show_examples()
                continue
            elif code.lower() == 'status':
                show_status(engine_type, supports_instruments)
                continue
            elif code.lower() == 'test-rest':
                test_rest_functionality(audio_engine)
                continue
            elif code.strip() == '':
                continue
            
            # 解析並執行
            ast = parser.parse(code)
            if hasattr(audio_engine, 'execute'):
                audio_engine.execute(ast)
            else:
                if hasattr(audio_engine, 'play'):
                    audio_engine.play(ast)
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")

def test_rest_functionality(audio_engine):
    """測試休止符功能"""
    print("\n🎵 測試休止符功能...")
    
    try:
        # 測試基本休止符
        print("播放音符 C4")
        audio_engine.play_note('C4', 0.5)
        
        print("休止符 1 秒")
        audio_engine.play_rest(1.0)
        
        print("播放音符 E4")
        audio_engine.play_note('E4', 0.5)
        
        print("休止符 0.5 秒")
        audio_engine.play_rest(0.5)
        
        print("播放和弦 [C4, E4, G4]")
        audio_engine.play_chord(['C4', 'E4', 'G4'], 1.0)
        
        print("✅ 休止符功能測試完成！")
        
    except Exception as e:
        print(f"❌ 休止符測試失敗: {e}")

def show_status(engine_type, supports_instruments):
    """顯示系統狀態"""
    print("\n🔧 PyTune 系統狀態:")
    print(f"   音訊引擎: {engine_type}")
    print(f"   音色支援: {'✅ 已啟用' if supports_instruments else '❌ 未支援'}")
    print(f"   休止符支援: ✅ 已啟用")
    print(f"   Python 版本: {sys.version.split()[0]}")
    
    # 檢查相依套件
    try:
        import pygame
        print(f"   Pygame: ✅ {pygame.version.ver}")
    except ImportError:
        print("   Pygame: ❌ 未安裝")
    
    try:
        import numpy
        print(f"   NumPy: ✅ {numpy.__version__}")
    except ImportError:
        print("   NumPy: ❌ 未安裝")
    
    try:
        import lark
        print(f"   Lark: ✅ {lark.__version__}")
    except ImportError:
        print("   Lark: ❌ 未安裝")

def show_examples():
    """顯示範例檔案"""
    examples_dir = Path(__file__).parent / "examples"
    print("\n📁 可用的範例檔案：")
    
    if examples_dir.exists():
        ptm_files = list(examples_dir.glob("*.ptm"))
        ml_files = list(examples_dir.glob("*.ml"))
        
        for ptm_file in ptm_files:
            print(f"   • {ptm_file.name}")
        for ml_file in ml_files:
            print(f"   • {ml_file.name}")
        
        if ptm_files or ml_files:
            print(f"\n💡 使用方式: python main.py examples/檔案名.ptm")
        else:
            print("   ⚠️  examples 目錄為空")
    else:
        print("   ❌ 找不到 examples 目錄")
    
    # 顯示休止符範例
    print("\n🔇 休止符範例：")
    print("   note C4, 1.0; rest 0.5; note E4, 1.0")
    print("   chord [C4, E4, G4], 2.0; rest 1.0; note C5, 1.0")

def show_help(supports_instruments=False):
    """顯示說明"""
    help_text = f"""
🎵 PyTune 音樂程式語言說明

基本語法：
  note C4, 1.0              # 播放音符
  note [C4, D4, E4], 0.5    # 播放音符陣列
  chord [C4, E4, G4], 2.0   # 播放和弦
  rest 1.0                  # 休止符（靜默1秒）
  rest 0.5                  # 短休止符
  tempo 120                 # 設定速度
  volume 0.8                # 設定音量"""

    if supports_instruments:
        help_text += """
  refinst = piano           # 設定音色（鋼琴）
  refinst = violin          # 設定音色（小提琴）"""

    help_text += """

休止符用法：
  rest 1.0                  # 1秒休止符
  rest 0.25                 # 0.25秒休止符
  note C4, 0.5; rest 0.5    # 音符後接休止符
  
控制流：
  for (i, 0:5) { ... }      # for 迴圈
  while (condition) { ... } # while 迴圈
  if (condition) { ... }    # 條件判斷
  loop 3 { ... }            # 固定次數迴圈

函式：
  fn melody() { ... }       # 定義函式
  melody()                  # 呼叫函式
  refVolume(0.8)           # ref 函式"""

    if supports_instruments:
        help_text += """
  refInst(piano)           # 設定音色"""

    help_text += """

範例程式：
  // 簡單旋律與休止符
  tempo 120
  refinst = piano
  note C4, 0.5
  rest 0.25
  note E4, 0.5  
  rest 0.25
  note G4, 1.0

  // 節奏模式
  fn rhythm_pattern() {
      note C4, 0.25
      rest 0.25
      note E4, 0.25
      rest 0.25
  }
  
  loop 4 {
      rhythm_pattern()
  }

檔案格式：
  • PyTune 程式檔案使用 .ptm 副檔名
  • 也支援 .ml 副檔名
  • 支援 UTF-8 編碼
  • 支援 // 單行註解

指令：
  status                    # 查看系統狀態
  examples                  # 查看範例檔案
  test-rest                 # 測試休止符功能
  help                      # 顯示此說明
"""
    print(help_text)

def main():
    """主函式"""
    parser = argparse.ArgumentParser(
        description="PyTune - 音樂程式語言執行器（支援休止符）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python main.py examples/twinkle_star.ptm     # 執行檔案
  python main.py -c "note C4, 1.0; rest 0.5"  # 執行程式碼（含休止符）
  python main.py -i                           # 互動模式
  python main.py -v examples/test.ptm         # 詳細模式
  python main.py --status                     # 系統狀態
  python main.py --test                       # 音訊系統測試
        """
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='要執行的 .ptm/.ml 音樂程式檔案'
    )
    
    parser.add_argument(
        '--code', '-c',
        help='直接執行程式碼字串'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='進入互動模式'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細執行資訊'
    )
    
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='顯示系統狀態'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='執行音訊系統測試'
    )
    
    parser.add_argument(
        '--demo-rest', '-dr',
        action='store_true',
        help='演示休止符功能'
    )
    
    args = parser.parse_args()
    
    # 設定詳細模式
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 系統狀態模式
    if args.status:
        AudioEngine, engine_type = import_audio_modules()
        MusicParser, supports_instruments = import_parser()
        show_status(engine_type if AudioEngine else 'unavailable', supports_instruments)
        return
    
    # 音訊測試模式
    if args.test:
        print("🔧 執行音訊系統測試...")
        test_file = Path(__file__).parent / "test_audio_setup.py"
        if test_file.exists():
            os.system(f"python {test_file}")
        else:
            print("❌ 找不到 test_audio_setup.py")
        return
    
    # 休止符演示模式
    if args.demo_rest:
        print("🔇 休止符功能演示...")
        demo_code = '''
        tempo 120
        refinst = piano
        
        note C4, 0.5
        rest 0.5
        note E4, 0.5
        rest 0.5
        note G4, 1.0
        rest 1.0
        
        chord [C4, E4, G4], 2.0
        rest 2.0
        
        fn melody_with_rests() {
            note C4, 0.25
            rest 0.25
            note D4, 0.25
            rest 0.25
            note E4, 0.25
            rest 0.25
            note F4, 0.25
            rest 0.25
        }
        
        melody_with_rests()
        '''
        play_music_code(demo_code)
        return
    
    # 執行模式判斷
    if args.interactive:
        interactive_mode()
    elif args.code:
        play_music_code(args.code)
    elif args.file:
        play_music_file(args.file)
    else:
        print("❌ 請指定要執行的檔案或使用 --help 查看說明")
        show_examples()
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程式被中斷")
    except Exception as e:
        print(f"❌ 程式執行失敗: {e}")
        import traceback
        traceback.print_exc()