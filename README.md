# PyTune 執行方式指南

## 📁 專案結構

```
pyTune/
├── music_lang/
│   ├── main.py                 # 主執行檔
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── parser.py           # 語法解析器
│   │   └── music_lang.lark     # 語法定義檔
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_engine.py     # 音訊引擎
│   │   └── interpreter.py      # 程式碼解釋器
│   └── examples/
│       ├── twinkle_star.ml     # 小星星範例
│       ├── for_loop_demo.ml    # for迴圈範例
│       └── logic_demo.ml       # 邏輯控制範例
├── requirements.txt            # 相依套件
└── README.md                  # 專案說明
```

## 🚀 快速開始

### 1. 環境設定

#### 安裝 Python 相依套件
```bash
# 進入專案目錄
cd pyTune

# 安裝相依套件
pip install -r requirements.txt
```

#### requirements.txt 內容
```txt
lark-parser>=0.12.0
pygame>=2.1.0
numpy>=1.21.0
```

### 2. 基本執行方式

#### 方式一：執行 .ml 檔案
```bash
# 進入音樂語言目錄
cd music_lang

# 執行音樂程式檔案
python main.py examples/twinkle_star.ml
```

#### 方式二：直接執行程式碼
```bash
# 執行字串形式的程式碼
python main.py --code "tempo 120; note C4, 1.0; chord [C4, E4, G4], 2.0"
```

#### 方式三：互動模式
```bash
# 進入互動模式
python main.py --interactive
```

## 🎵 執行範例

### 範例 1：執行小星星變奏曲
```bash
cd music_lang
python main.py examples/twinkle_star.ml
```

**預期輸出：**
```
🔍 解析程式碼...
✅ 解析成功！
🎵 開始播放音樂...
♪ 播放音符: C4, 時長: 0.5s
♪ 播放音符: C4, 時長: 0.5s
♪ 播放音符: G4, 時長: 0.5s
...
🎵 音樂播放完成！
```

### 範例 2：使用 for 迴圈
```bash
python main.py --code "
tempo 120
for (i, 0:5) {
    note C4, 0.5
    note G4, 0.5
}
"
```

### 範例 3：邏輯控制演奏
```bash
python main.py --code "
tempo 100
mode = 1
if (mode == 1) {
    note [C4, E4, G4], 0.5
} else {
    chord [C4, E4, G4], 1.0
}
"
```

## ⚙️ main.py 程式架構

### 主執行檔結構
```python
#!/usr/bin/env python3
"""
main.py - PyTune 音樂程式語言主執行檔
"""

import sys
import argparse
from parser.parser import MusicLanguageParser
from audio.interpreter import MusicInterpreter
from audio.audio_engine import AudioEngine

def play_music_file(filename):
    """播放音樂檔案"""
    try:
        # 1. 讀取檔案
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 2. 解析程式碼
        print("🔍 解析程式碼...")
        parser = MusicLanguageParser()
        ast = parser.parse(code)
        print("✅ 解析成功！")
        
        # 3. 執行音樂程式
        print("🎵 開始播放音樂...")
        audio_engine = AudioEngine()
        interpreter = MusicInterpreter(audio_engine)
        interpreter.execute(ast)
        print("🎵 音樂播放完成！")
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {filename}")
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")

def play_music_code(code):
    """播放程式碼字串"""
    try:
        # 解析並執行
        print("🔍 解析程式碼...")
        parser = MusicLanguageParser()
        ast = parser.parse(code)
        print("✅ 解析成功！")
        
        print("🎵 開始播放音樂...")
        audio_engine = AudioEngine()
        interpreter = MusicInterpreter(audio_engine)
        interpreter.execute(ast)
        print("🎵 音樂播放完成！")
        
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")

def interactive_mode():
    """互動模式"""
    print("🎹 PyTune 互動模式")
    print("輸入 'exit' 或 'quit' 離開")
    print("輸入 'help' 查看說明")
    
    audio_engine = AudioEngine()
    parser = MusicLanguageParser()
    interpreter = MusicInterpreter(audio_engine)
    
    while True:
        try:
            code = input(">>> ")
            
            if code.lower() in ['exit', 'quit']:
                break
            elif code.lower() == 'help':
                show_help()
                continue
            elif code.strip() == '':
                continue
            
            ast = parser.parse(code)
            interpreter.execute(ast)
            
        except KeyboardInterrupt:
            print("\n👋 再見！")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")

def show_help():
    """顯示說明"""
    help_text = """
🎵 PyTune 音樂程式語言說明

基本語法：
  note C4, 1.0              # 播放音符
  note [C4, D4, E4], 0.5    # 播放音符陣列
  chord [C4, E4, G4], 2.0   # 播放和弦
  tempo 120                 # 設定速度
  volume 0.8                # 設定音量

控制流：
  for (i, 0:5) { ... }      # for 迴圈
  while (condition) { ... } # while 迴圈
  if (condition) { ... }    # 條件判斷

函式：
  fn melody() { ... }       # 定義函式
  melody()                  # 呼叫函式
  refVolume(0.8)           # ref 函式

範例：
  tempo 120; note [C4, E4, G4], 0.5; chord [C4, E4, G4], 1.0
"""
    print(help_text)

def main():
    """主函式"""
    parser = argparse.ArgumentParser(
        description="PyTune - 音樂程式語言執行器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help='要執行的 .ml 音樂程式檔案'
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
    
    args = parser.parse_args()
    
    # 設定詳細模式
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # 執行模式判斷
    if args.interactive:
        interactive_mode()
    elif args.code:
        play_music_code(args.code)
    elif args.file:
        play_music_file(args.file)
    else:
        print("❌ 請指定要執行的檔案或使用 --help 查看說明")
        parser.print_help()

if __name__ == "__main__":
    main()
```

## 🎼 程式碼範例檔案

### twinkle_star.ml
```musiclang
// 小星星變奏曲
tempo 100
volume 0.8

fn mainTheme() {
    note [C4, C4, G4, G4, A4, A4], 0.5
    note G4, 1.0
    note [F4, F4, E4, E4, D4, D4], 0.5
    note C4, 1.0
}

mainTheme()
```

### for_loop_demo.ml
```musiclang
// for 迴圈範例
tempo 120
volume 0.7

for (octave, 3:6) {
    if (octave == 3) {
        note [C3, D3, E3], 0.5
    } elseif (octave == 4) {
        note [C4, D4, E4], 0.5
    } else {
        note [C5, D5, E5], 0.5
    }
}
```

### logic_demo.ml
```musiclang
// 邏輯控制範例
tempo 100
mode = 1

if (mode == 1) {
    // 單音模式
    note [C4, D4, E4, F4], 0.5
} elseif (mode == 2) {
    // 和弦模式
    chord [C4, E4, G4], 1.0
    chord [F4, A4, C5], 1.0
} else {
    // 混合模式
    note C4, 0.5
    chord [C4, E4, G4], 0.5
}
```

## 🔧 命令列參數

### 基本用法
```bash
python main.py [OPTIONS] [FILE]
```

### 參數說明
| 參數 | 說明 | 範例 |
|------|------|------|
| `FILE` | 要執行的 .ml 檔案 | `python main.py song.ml` |
| `--code`, `-c` | 直接執行程式碼 | `python main.py -c "note C4, 1.0"` |
| `--interactive`, `-i` | 互動模式 | `python main.py -i` |
| `--verbose`, `-v` | 顯示詳細資訊 | `python main.py -v song.ml` |
| `--help`, `-h` | 顯示說明 | `python main.py -h` |

## 🐛 除錯與錯誤處理

### 常見錯誤與解決方法

#### 1. 語法錯誤
```bash
❌ 語法錯誤: Unexpected token 'C44'
```
**解決方法：** 檢查音符格式，應為 `C4` 而非 `C44`

#### 2. 檔案不存在
```bash
❌ 找不到檔案: song.ml
```
**解決方法：** 確認檔案路徑正確

#### 3. 模組匯入錯誤
```bash
❌ ModuleNotFoundError: No module named 'lark'
```
**解決方法：** 安裝相依套件 `pip install lark-parser`

### 除錯模式
```bash
# 使用 verbose 模式查看詳細執行過程
python main.py --verbose examples/twinkle_star.ml
```

## 🎯 效能調優

### 音訊設定
在 `audio_engine.py` 中可以調整：
```python
# 音訊品質設定
SAMPLE_RATE = 44100    # 取樣率
BUFFER_SIZE = 1024     # 緩衝區大小
CHANNELS = 2           # 聲道數
```

### 記憶體使用
```python
# 大型音樂檔案建議分段執行
python main.py --code "
tempo 120
for (section, 0:10) {
    // 分段演奏，避免記憶體過載
}
"
```

## 📝 開發模式

### 建立新的音樂程式
1. 建立 `.ml` 檔案
2. 編寫音樂程式碼
3. 執行測試：`python main.py your_song.ml`

### 除錯流程
1. 檢查語法：使用 `--verbose` 模式
2. 分段測試：逐步執行程式碼片段
3. 檢查音訊輸出：確認音符播放正確

這份執行指南涵蓋了 PyTune 的完整使用方式，從基本執行到進階除錯都有詳細說明！