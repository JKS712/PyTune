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

## 🎵 PyTune 語法說明

```
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


### 建立新的音樂程式
1. 建立 `.ptm` 檔案
2. 編寫音樂程式碼
3. 執行測試：`python main.py your_song.ptm`

#
