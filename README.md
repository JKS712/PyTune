# PyTune 

## 1. Lexer (詞法分析器)

### Token 定義 (來自 music_lang.lark)

```lark
// 基本 Token
NOTE_STRING: "\"" NOTE_PATTERN "\""           // 音符字符串，如 "C4", "A#3"
NOTE_PATTERN: /[A-Ga-g]#?[0-9]/              // 音符模式：音名 + 可選升號 + 八度
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/         // 標識符 (變數名、函式名)
NUMBER: /\d+(\.\d+)?/                        // 數字 (整數或浮點數)
COMMENT: "//" /[^\n]/                        // 註解

// 關鍵字 Token (隱含定義)
"note"      // 音符播放關鍵字
"chord"     // 和弦播放關鍵字
"tempo"     // 速度設定關鍵字
"volume"    // 音量設定關鍵字
"loop"      // 迴圈關鍵字
"fn"        // 函式定義關鍵字

// 特殊 Token (用於內建函式)
REF_IDENTIFIER: /ref[A-Z][a-zA-Z0-9_]*/      // ref 函式，如 refVolume, refTempo

// 運算符和分隔符
"+"  "-"  "*"  "/"                           // 算術運算符
"="                                          // 賦值運算符
"("  ")"  "{"  "}"  "["  "]"                // 括號
","  ";"                                     // 分隔符
```

### Token 範例

```
輸入: note "C4", 1.0
Token 序列:
- KEYWORD("note")
- NOTE_STRING("C4") 
- COMMA(",")
- NUMBER(1.0)
```

## 2. Parser (語法分析器)

### 語法規則 (來自 music_lang.lark 和 parser.py)

```lark
// 程式結構
?start: statement*                           // 程式 = 語句列表

// 語句類型
?statement: note_stmt                        // 音符語句
          | chord_stmt                       // 和弦語句  
          | tempo_stmt                       // 速度語句
          | volume_stmt                      // 音量語句
          | loop_stmt                        // 迴圈語句
          | function_def                     // 函式定義
          | function_call                    // 函式呼叫
          | assignment                       // 賦值語句

// 具體語句定義
note_stmt: "note" note_literal ("," expression)?
chord_stmt: "chord" chord_literal ("," expression)?
tempo_stmt: "tempo" expression
volume_stmt: "volume" expression
loop_stmt: "loop" expression "{" statement* "}"
function_def: "fn" identifier "(" parameter_list? ")" "{" statement* "}"
assignment: identifier "=" expression

// 表達式語法
?expression: add_expr
?add_expr: add_expr "+" mul_expr -> add
         | add_expr "-" mul_expr -> sub  
         | mul_expr
?mul_expr: mul_expr "*" atom -> mul
         | mul_expr "/" atom -> div
         | atom
```

### Parser 類別結構

```python
class MusicLanguageParser:
    def __init__(self):
        self.parser = Lark(GRAMMAR, parser='lalr', transformer=MusicTransformer())
    
    def parse(self, code):
        """解析程式碼並返回 AST"""
        return self.parser.parse(code)

class MusicTransformer(Transformer):
    """將 Lark 解析樹轉換為自定義 AST"""
    
    def start(self, items):
        return {"type": "program", "body": items}
    
    def note_stmt(self, items):
        return {"type": "note", "note": items[0], "duration": items[1] if len(items) > 1 else None}
    
    # ... 其他轉換方法
```

## 3. AST (抽象語法樹)

### AST 節點類型

#### 程式根節點
```json
{
    "type": "program",
    "body": [/* 語句列表 */]
}
```

#### 語句節點

**音符語句**
```json
{
    "type": "note",
    "note": {"type": "note_literal", "value": "C4"},
    "duration": {"type": "number", "value": 1.0}
}
```

**和弦語句**
```json
{
    "type": "chord", 
    "chord": {
        "type": "chord_literal",
        "notes": [
            {"type": "note_literal", "value": "C4"},
            {"type": "note_literal", "value": "E4"},
            {"type": "note_literal", "value": "G4"}
        ]
    },
    "duration": {"type": "number", "value": 2.0}
}
```

**速度/音量設定**
```json
{
    "type": "tempo",  // 或 "volume"
    "bpm": {"type": "number", "value": 120}  // 或 "volume"
}
```

**迴圈語句**
```json
{
    "type": "loop",
    "count": {"type": "number", "value": 3},
    "body": [/* 迴圈內的語句 */]
}
```

**函式定義**
```json
{
    "type": "function_def",
    "name": "melody",
    "params": ["note", "duration"],
    "body": [/* 函式體語句 */]
}
```

**函式呼叫**
```json
{
    "type": "function_call",
    "name": "refVolume",  // 或使用者定義函式名
    "args": [{"type": "number", "value": 0.8}]
}
```

**賦值語句**
```json
{
    "type": "assign",
    "var": {"type": "identifier", "name": "x"},
    "value": {"type": "number", "value": 42}
}
```

#### 表達式節點

**數值**
```json
{
    "type": "number",
    "value": 120
}
```

**標識符**
```json
{
    "type": "identifier", 
    "name": "tempo"
}
```

**二元運算**
```json
{
    "type": "binop",
    "op": "+",
    "left": {"type": "number", "value": 60},
    "right": {"type": "number", "value": 60}
}
```

### 範例程式的 AST

對於程式碼：
```
tempo 120
note "C4", 1.0
chord ["C4", "E4", "G4"]
```

生成的 AST：
```json
{
    "type": "program",
    "body": [
        {
            "type": "tempo",
            "bpm": {"type": "number", "value": 120}
        },
        {
            "type": "note", 
            "note": {"type": "note_literal", "value": "C4"},
            "duration": {"type": "number", "value": 1.0}
        },
        {
            "type": "chord",
            "chord": {
                "type": "chord_literal",
                "notes": [
                    {"type": "note_literal", "value": "C4"},
                    {"type": "note_literal", "value": "E4"}, 
                    {"type": "note_literal", "value": "G4"}
                ]
            }
        }
    ]
}
```

## 4. 執行流程

1. **Lexer**: 將源代碼字符串分解為 Token 序列
2. **Parser**: 根據語法規則將 Token 序列構建為解析樹
3. **Transformer**: 將解析樹轉換為 AST
4. **Interpreter**: 遍歷 AST 並執行相應的音訊操作

## 5. 特殊功能

### ref 函式系統
- `refVolume(value)`: 設定音量
- `refTempo(bpm)`: 設定速度  
- `refPlay(note, duration)`: 播放音符

### 音符表示法支援
- 基本音符: C, D, E, F, G, A, B
- 升音: C#, D#, F#, G#, A#
- 降音: Db, Eb, Gb, Ab, Bb
- 八度範圍: 0-8

### 表達式計算
支援基本算術運算：加法、減法、乘法、除法，並遵循運算優先級。