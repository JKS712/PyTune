# PyTune 音樂程式語言語法說明

## 📋 目錄

- [基本語法](#基本語法)
- [音樂語句](#音樂語句)
- [樂器支援](#樂器支援)
- [控制流語句](#控制流語句)
- [函式系統](#函式系統)
- [表達式與運算](#表達式與運算)
- [變數與賦值](#變數與賦值)
- [註解語法](#註解語法)
- [完整範例](#完整範例)
- [最佳實踐](#最佳實踐)
- [常見錯誤](#常見錯誤)

## 基本語法

### 檔案格式
- 副檔名：`.ptm` (PyTune Music)
- 編碼：UTF-8
- 語句結尾：大部分語句不需要分號，表達式語句需要分號

### 基本結構
```musiclang
// 設定部分
tempo 120
volume 0.8
refinst = piano

// 音樂內容
note C4, 1.0
chord [C4, E4, G4], 2.0

// 控制流
for (i, 0:4) {
    note C4, 0.5
}
```

## 音樂語句

### 1. 速度設定
```musiclang
tempo <BPM值>
```
**範例：**
```musiclang
tempo 120        // 設定為 120 BPM
tempo 60         // 慢板
tempo 180        // 快板
```

### 2. 音量設定
```musiclang
volume <音量值>
```
**範例：**
```musiclang
volume 0.8       // 80% 音量
volume 0.5       // 50% 音量
volume 1.0       // 最大音量
```

### 3. 音符播放
```musiclang
note <音符>, <時長>
note [<音符列表>], <時長>
```

#### 音符格式
- **音名**：C, D, E, F, G, A, B
- **升音**：C#, D#, F#, G#, A#
- **降音**：Db, Eb, Gb, Ab, Bb
- **八度**：0-8 (4為中央八度)

**範例：**
```musiclang
note C4, 1.0              // 中央C，持續1秒
note [C4, D4, E4], 0.5    // 音符陣列，每個音符0.5秒
note F#5, 0.25            // 高音升F，持續0.25秒
note Bb3, 2.0             // 低音降B，持續2秒
```

### 4. 和弦播放
```musiclang
chord [<音符列表>], <時長>
```
**範例：**
```musiclang
chord [C4, E4, G4], 2.0        // C大調三和弦
chord [C4, E4, G4, C5], 1.5    // C大調加八度
chord [F3, A3, C4, F4], 3.0    // F大調四音和弦
```

## 樂器支援

### 樂器切換語法
```musiclang
refinst = <樂器名稱>
```

### 支援的樂器列表

| 樂器名稱 | 音色特點 | 適用場景 |
|---------|---------|---------|
| `piano` | 溫暖柔和，泛音豐富 | 主旋律、伴奏、獨奏 |
| `violin` | 明亮有顫音，表現力強 | 抒情旋律、和聲聲部 |
| `guitar` | 撥弦音色，自然衰減 | 節奏、分解和弦 |
| `drums` | 打擊樂，低頻豐富 | 節拍、強調、過門 |
| `flute` | 純淨清澈，高音明亮 | 裝飾音、快速音群 |
| `trumpet` | 明亮有力，泛音豐富 | 主題演奏、號角效果 |
| `saxophone` | 溫暖帶簧片質感 | 爵士風格、即興演奏 |
| `cello` | 深沉溫暖，有顫音 | 低音旋律、和聲基礎 |
| `bass` | 厚重低頻，節奏感強 | 低音線、節奏支撐 |
| `organ` | 持續音，多重泛音 | 和聲墊底、教堂風格 |

**範例：**
```musiclang
// 鋼琴主旋律
refinst = piano
note [C4, D4, E4, F4], 0.5

// 小提琴和聲
refinst = violin
note [E5, F5, G5, A5], 0.5

// 鼓聲節拍
refinst = drums
note [C2, C2, C2, C2], 0.25
```

## 控制流語句

### 1. 固定次數迴圈
```musiclang
loop <次數> {
    // 語句
}
```
**範例：**
```musiclang
loop 4 {
    note C4, 0.5
    note G4, 0.5
}
```

### 2. for 迴圈
```musiclang
for (<變數名>, <起始值>:<結束值>) {
    // 語句
}
```
**範例：**
```musiclang
for (i, 0:5) {
    note C4, 0.5
}

for (octave, 3:6) {
    if (octave == 4) {
        note C4, 1.0
    }
}
```

### 3. while 迴圈
```musiclang
while (<條件>) {
    // 語句
}
```
**範例：**
```musiclang
counter = 0
while (counter < 3) {
    note C4, 0.5
    counter = counter + 1
}
```

### 4. 條件判斷
```musiclang
if (<條件>) {
    // 語句
} elseif (<條件>) {
    // 語句
} else {
    // 語句
}
```
**範例：**
```musiclang
mode = 1
if (mode == 1) {
    refinst = piano
    note [C4, E4, G4], 0.5
} elseif (mode == 2) {
    refinst = violin
    note [G4, B4, D5], 0.5
} else {
    refinst = guitar
    note [E3, A3, E4], 0.5
}
```

## 函式系統

### 1. 函式定義
```musiclang
fn <函式名>(<參數列表>) {
    // 函式體
}
```

### 2. 函式呼叫
```musiclang
<函式名>(<參數列表>)
```

**範例：**
```musiclang
// 定義函式
fn playMelody(instrument, duration) {
    refinst = instrument
    note [C4, D4, E4, F4], duration
}

fn arpeggioChord() {
    note C4, 0.25
    note E4, 0.25
    note G4, 0.25
    note C5, 0.25
}

// 呼叫函式
playMelody(piano, 0.5)
arpeggioChord()
```

### 3. ref 函式（內建函式）
```musiclang
refVolume(<音量值>)    // 設定音量
refTempo(<速度值>)     // 設定速度
refInst(<樂器名>)      // 設定樂器
```

**範例：**
```musiclang
refVolume(0.6)         // 設定音量為 60%
refTempo(140)          // 設定速度為 140 BPM
refInst(violin)        // 切換到小提琴
```

## 表達式與運算

### 算術運算符
| 運算符 | 說明 | 範例 |
|--------|------|------|
| `+` | 加法 | `tempo + 20` |
| `-` | 減法 | `volume - 0.1` |
| `*` | 乘法 | `duration * 2` |
| `/` | 除法 | `tempo / 2` |

### 比較運算符
| 運算符 | 說明 | 範例 |
|--------|------|------|
| `==` | 等於 | `mode == 1` |
| `!=` | 不等於 | `counter != 0` |
| `<` | 小於 | `volume < 0.5` |
| `>` | 大於 | `tempo > 120` |
| `<=` | 小於等於 | `octave <= 5` |
| `>=` | 大於等於 | `counter >= 10` |

### 邏輯運算符
| 運算符 | 說明 | 範例 |
|--------|------|------|
| `and` | 邏輯且 | `volume > 0.5 and tempo < 120` |
| `or` | 邏輯或 | `mode == 1 or mode == 2` |
| `not` | 邏輯非 | `not (counter == 0)` |

**範例：**
```musiclang
base_tempo = 120
fast_tempo = base_tempo + 40
slow_tempo = base_tempo - 20

if (fast_tempo > 140 and slow_tempo < 100) {
    refTempo(base_tempo)
}
```

## 變數與賦值

### 變數命名規則
- 以字母或底線開頭
- 可包含字母、數字、底線
- 區分大小寫

### 賦值語法
```musiclang
<變數名> = <表達式>
```

**範例：**
```musiclang
tempo_value = 120
volume_level = 8
current_octave = 4
note_duration = 0.5

// 使用變數
refTempo(tempo_value)
refVolume(volume_level / 10)
note C4, note_duration
```

## 註解語法

### 單行註解
```musiclang
// 這是單行註解
tempo 120  // 行尾註解
```

**範例：**
```musiclang
// 設定基本參數
tempo 120          // 中等速度
volume 0.8         // 較響音量

// 主旋律演奏
refinst = piano    // 使用鋼琴
note [C4, D4, E4], 0.5  // 上行音階
```

## 完整範例

### 範例 1：小星星變奏曲
```musiclang
// 小星星變奏曲
tempo 100
volume 0.8

// 主題函式
fn mainTheme() {
    refinst = piano
    refVolume(0.8)
    
    // 小星星主旋律
    note [C4, C4, G4, G4, A4, A4], 0.5
    note G4, 1.0
    note [F4, F4, E4, E4, D4, D4], 0.5
    note C4, 1.0
}

// 和聲變奏
fn harmonyVariation() {
    refinst = violin
    refVolume(0.6)
    
    note [E5, E5, B5, B5, C6, C6], 0.5
    note B5, 1.0
    note [A5, A5, G5, G5, F5, F5], 0.5
    note E5, 1.0
}

// 低音支撐
fn bassLine() {
    refinst = bass
    refVolume(0.7)
    
    note [C3, G3, F3, C3], 1.0
    note [F3, C3, G3, C3], 1.0
}

// 演奏結構
mainTheme()
harmonyVariation()
bassLine()
mainTheme()
```

### 範例 2：多樂器編排
```musiclang
// 多樂器小品
tempo 120
volume 0.8

// 樂器展示函式
fn instrumentShowcase() {
    instruments = [piano, violin, guitar, flute, trumpet]
    
    for (i, 0:5) {
        if (i == 0) {
            refinst = piano
        } elseif (i == 1) {
            refinst = violin
        } elseif (i == 2) {
            refinst = guitar
        } elseif (i == 3) {
            refinst = flute
        } else {
            refinst = trumpet
        }
        
        // 每種樂器演奏相同旋律
        note [C4, E4, G4, C5], 0.4
    }
}

// 和弦進行
fn chordProgression() {
    refinst = piano
    refVolume(0.6)
    
    chord [C4, E4, G4], 1.0    // C大調
    chord [F4, A4, C5], 1.0    // F大調  
    chord [G4, B4, D5], 1.0    // G大調
    chord [C4, E4, G4], 2.0    // 回到C大調
}

// 鼓聲節拍
fn drumPattern() {
    refinst = drums
    refVolume(0.4)
    
    for (beat, 0:8) {
        if (beat == 0 or beat == 4) {
            note C2, 0.5  // 重拍
        } else {
            note F#2, 0.5 // 輕拍
        }
    }
}

// 執行演奏
instrumentShowcase()
chordProgression()
drumPattern()
```

### 範例 3：動態音樂生成
```musiclang
// 動態音樂生成範例
tempo 110
volume 0.7

// 動態旋律生成
fn generateMelody(mode) {
    refinst = piano
    
    if (mode == 1) {
        // 大調模式
        note [C4, D4, E4, F4, G4, A4, B4, C5], 0.3
    } elseif (mode == 2) {
        // 小調模式  
        note [C4, D4, Eb4, F4, G4, Ab4, Bb4, C5], 0.3
    } else {
        // 五聲音階
        note [C4, D4, F4, G4, A4, C5], 0.4
    }
}

// 動態和聲
fn generateHarmony(complexity) {
    refinst = organ
    refVolume(0.5)
    
    if (complexity == 1) {
        // 簡單三和弦
        chord [C4, E4, G4], 2.0
    } elseif (complexity == 2) {
        // 七和弦
        chord [C4, E4, G4, B4], 2.0
    } else {
        // 複雜和弦
        chord [C4, E4, G4, B4, D5, F5], 2.0
    }
}

// 根據參數生成不同音樂
for (style, 1:4) {
    generateMelody(style)
    generateHarmony(style)
}
```

## 最佳實踐

### 1. 程式碼組織
```musiclang
// 好的組織結構
// ===== 設定區域 =====
tempo 120
volume 0.8

// ===== 函式定義區域 =====
fn melody() {
    // 函式內容
}

// ===== 主程式區域 =====
melody()
```

### 2. 命名慣例
```musiclang
// 使用有意義的名稱
fn mainMelody() { ... }       // 好
fn pianoIntro() { ... }       // 好
fn m1() { ... }               // 不好

// 變數命名
base_tempo = 120              // 好
current_volume = 0.8          // 好
x = 120                       // 不好
```

### 3. 註解使用
```musiclang
// 在複雜邏輯前添加註解
// 檢查是否為快板
if (tempo > 140) {
    refVolume(0.6)  // 快板時降低音量
}

// 為函式添加說明註解
// 演奏主旋律，包含裝飾音
fn ornamentedMelody() {
    // 函式實作
}
```

### 4. 音量管理
```musiclang
// 為不同樂器設定合適音量
refinst = piano
refVolume(0.8)     // 主旋律較響

refinst = violin
refVolume(0.6)     // 和聲較輕

refinst = drums
refVolume(0.4)     // 打擊樂最輕
```

## 常見錯誤

### 1. 語法錯誤
```musiclang
// ❌ 錯誤：缺少逗號
note C4 1.0

// ✅ 正確
note C4, 1.0

// ❌ 錯誤：音符格式錯誤
note C44, 1.0

// ✅ 正確
note C4, 1.0
```

### 2. 邏輯錯誤
```musiclang
// ❌ 錯誤：無限迴圈
counter = 0
while (counter < 10) {
    note C4, 0.5
    // 忘記增加 counter
}

// ✅ 正確
counter = 0
while (counter < 10) {
    note C4, 0.5
    counter = counter + 1
}
```

### 3. 樂器名稱錯誤
```musiclang
// ❌ 錯誤：不存在的樂器
refinst = clarinet

// ✅ 正確：使用支援的樂器
refinst = flute
```

### 4. 音符範圍錯誤
```musiclang
// ❌ 錯誤：八度超出範圍
note C9, 1.0

// ✅ 正確：使用合理八度
note C5, 1.0
```

## 🎯 快速參考

### 基本語句速查
```musiclang
tempo 120                    // 設定速度
volume 0.8                   // 設定音量
refinst = piano              // 切換樂器
note C4, 1.0                 // 播放音符
chord [C4, E4, G4], 2.0      // 播放和弦
```

### 控制流速查
```musiclang
loop 3 { ... }               // 固定迴圈
for (i, 0:5) { ... }         // for 迴圈
while (condition) { ... }    // while 迴圈
if (condition) { ... }       // 條件判斷
```

### 函式速查
```musiclang
fn name() { ... }            // 定義函式
name()                       // 呼叫函式
refVolume(0.8)              // ref 函式
```
#