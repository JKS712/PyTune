# PyTune 執行方式指南

## 🚀 快速開始

### 1. 環境設定

#### 進入專案目錄
```bash
cd D:\parser\pyTune
```

#### 安裝 Python 相依套件
```bash
# 安裝相依套件
pip install -r requirements.txt

# 或使用 setup.py 安裝
python setup.py install
```

#### requirements.txt 內容
```txt
lark==1.2.2
numpy==1.24.3
pygame==2.5.2

```

### 2. 基本執行方式

#### 方式一：使用 main.py 執行 .ptm 檔案
```bash
# 進入音樂語言目錄
cd music_lang

# 執行音樂程式檔案 (.ptm 格式)
python main.py examples\twinkle_star.ptm
```
#### 方式二：直接執行程式碼字串
```bash
python main.py --code "tempo 120; note C4, 1.0; chord [C4, E4, G4], 2.0"
```

### 3. 測試音訊設定
```bash
cd music_lang
python test_audio_setup.py
```

## 🎵 執行範例

### 範例 1：執行小星星變奏曲
```bash
cd music_lang
python main.py examples\twinkle_star.ptm
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

## 🎼 程式碼範例檔案

### twinkle_star.ptm
```
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

### little_Star_Pro.ptm
```
// 小星星進階變奏曲
tempo 120
volume 0.8

// 主題函式
fn theme() {
    note [C4, C4, G4, G4, A4, A4], 0.5
    note G4, 1.0
    note [F4, F4, E4, E4, D4, D4], 0.5
    note C4, 1.0
}

// 和弦變奏
fn chordVariation() {
    chord [C4, E4, G4], 1.0
    chord [G4, B4, D5], 1.0
    chord [A4, C5, E5], 1.0
    chord [G4, B4, D5], 1.0
}

// 執行演奏
theme()
chordVariation()
theme()
```

### logic_saptme.ptm
```
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

// for 迴圈範例
for (i, 0:3) {
    note C4, 0.3
    note G4, 0.3
}
```

## 🔧 命令列參數

### 基本用法
```bash
python main.py [OPTIONS] [FILE]
python run_music.py [FILE]
```

### 參數說明
| 參數 | 說明 | 範例 |
|------|------|------|
| `FILE` | 要執行的 .ptm 檔案 | `python main.py song.ptm` |
| `--code`, `-c` | 直接執行程式碼 | `python main.py -c "note C4, 1.0"` |
| `--interactive`, `-i` | 互動模式 | `python main.py -i` |
| `--verbose`, `-v` | 顯示詳細資訊 | `python main.py -v song.ptm` |
| `--test`, `-t` | 音訊系統測試 | `python main.py -t` |
| `--help`, `-h` | 顯示說明 | `python main.py -h` |

### 執行方式比較
| 檔案 | 用途 | 優勢 |
|------|------|------|
| `main.py` | 主要執行器 | 功能完整，支援多種模式 |
| `run_music.py` | 簡化執行器 | 快速執行，專注於音樂播放 |
| `quick_test.py` | 快速測試 | 開發階段測試語法功能 |

## 🐛 除錯與錯誤處理

### 常見錯誤與解決方法

#### 1. 語法錯誤
```bash
❌ 語法錯誤: Unexpected token 'C44'
```
**解決方法：** 檢查音符格式，應為 `C4` 而非 `C44`

#### 2. 檔案不存在
```bash
❌ 找不到檔案: song.ptm
```
**解決方法：** 
- 確認檔案路徑正確
- 確認使用 `.ptm` 副檔名
- 檢查檔案是否在 `examples/` 目錄下

#### 3. 模組匯入錯誤
```bash
❌ ModuleNotFoundError: No module named 'lark'
```
**解決方法：** 
```bash
pip install lark-parser
# 或
pip install -r requirements.txt
```

#### 4. 音訊系統錯誤
```bash
❌ pygame error: No available audio device
```
**解決方法：** 
```bash
# 測試音訊系統
python test_audio_setup.py

# 檢查音訊驅動程式
```

### 除錯工具

#### 1. 使用 verbose 模式
```bash
python main.py --verbose examples/twinkle_star.ptm
```

#### 2. 快速語法測試
```bash
cd music_lang/parser
python quick_test.py
```

#### 3. 音訊系統測試
```bash
cd music_lang
python test_audio_setup.py
```

#### 4. 單元測試
```bash
# 回到專案根目錄
cd D:\parser\pyTune

# 執行所有測試
python -m pytest tests/

# 執行特定測試
python tests/test_parser.py
python tests/test_lexer.py
python tests/test_interpreter.py
```

## 🎵 執行範例

### 範例 1：執行小星星變奏曲
```bash
cd music_lang
python main.py examples/twinkle_star.ptm
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

## ⚙️ main.py 程式架構

### 主執行檔結構
```
🎵 PyTune 語法說明

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

```

## 🎼 程式碼範例檔案

### twinkle_star.ptm
```
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

## 🔧 命令列參數

### 基本用法
```bash
python main.py [OPTIONS] [FILE]
```

### 參數說明
| 參數 | 說明 | 範例 |
|------|------|------|
| `FILE` | 要執行的 .ptm 檔案 | `python main.py song.ptm` |
| `--code`, `-c` | 直接執行程式碼 | `python main.py -c "note C4, 1.0"` |
| `--interactive`, `-i` | 互動模式 | `python main.py -i` |
| `--verbose`, `-v` | 顯示詳細資訊 | `python main.py -v song.ptm` |
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
❌ 找不到檔案: song.ptm
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
python main.py --verbose examples/twinkle_star.ptm
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
1. 建立 `.ptm` 檔案
2. 編寫音樂程式碼
3. 執行測試：`python main.py your_song.ptm`

### 除錯流程
1. 檢查語法：使用 `--verbose` 模式
2. 分段測試：逐步執行程式碼片段
3. 檢查音訊輸出：確認音符播放正確
#
