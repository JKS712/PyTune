# PyTune 完整語法規則與用法

## 1. Lexer (詞法分析器)

### Token 定義

```lark
// 基本 Token
NOTE_STRING: "\"" NOTE_PATTERN "\""           // 音符字符串，如 "C4", "A#3"
NOTE_BARE: NOTE_PATTERN                       // 無引號音符，如 C4, A#3
NOTE_PATTERN: /[A-Ga-g][#b]?[0-9]/          // 音符模式：音名 + 可選升降號 + 八度
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/         // 標識符 (變數名、函式名)
NUMBER: /[0-9]+(\.[0-9]+)?/                  // 數字 (整數或浮點數)
COMMENT: "//" /[^\n]*/                       // 註解

// 關鍵字 Token
"note"      // 音符播放關鍵字
"chord"     // 和弦播放關鍵字
"tempo"     // 速度設定關鍵字
"volume"    // 音量設定關鍵字
"loop"      // 固定次數迴圈關鍵字
"while"     // 條件迴圈關鍵字
"for"       // 範圍迴圈關鍵字
"if"        // 條件判斷關鍵字
"elseif"    // 條件分支關鍵字
"else"      // 其他分支關鍵字
"fn"        // 函式定義關鍵字

// 特殊 Token (用於內建函式)
REF_IDENTIFIER: /ref[A-Z][a-zA-Z0-9_]*/      // ref 函式，如 refVolume, refTempo

// 運算符
"+"  "-"  "*"  "/"                           // 算術運算符
"="                                          // 賦值運算符
"=="  "!="  "<"  ">"  "<="  ">="            // 比較運算符
"and"  "or"  "not"                           // 邏輯運算符
":"                                          // 範圍運算符

// 分隔符和括號
"("  ")"  "{"  "}"  "["  "]"                // 括號
","  ";"                                     // 分隔符
```

### Token 範例

```
輸入: note [C4, E4, G4], 1.0
Token 序列:
- KEYWORD("note")
- LSQB("[")
- NOTE_BARE("C4")
- COMMA(",")
- NOTE_BARE("E4") 
- COMMA(",")
- NOTE_BARE("G4")
- RSQB("]")
- COMMA(",")
- NUMBER(1.0)
```

## 2. Parser (語法分析器)

### 完整語法規則

```lark
// 程式結構
?start: statement*                           // 程式 = 語句列表

// 語句類型
?statement: note_stmt                        // 音符語句
          | chord_stmt                       // 和弦語句  
          | tempo_stmt                       // 速度語句
          | volume_stmt                      // 音量語句
          | loop_stmt                        // 固定次數迴圈語句
          | while_stmt                       // 條件迴圈語句
          | for_stmt                         // 範圍迴圈語句
          | if_stmt                          // 條件判斷語句
          | fn_stmt                          // 函式定義
          | fn_call_stmt                     // 函式呼叫
          | assignment                       // 賦值語句
          | expression ";"                   // 表達式語句

// === 音樂語句 ===

// 音符語句 - 支援單個音符和音符陣列
note_stmt: "note" note_value ("," duration)?

// 音符值可以是單個音符或音符陣列
note_value: note_literal
          | note_array

// 音符陣列
note_array: "[" note_list "]"

// 和弦語句  
chord_stmt: "chord" chord_literal ("," duration)?

// 速度設定
tempo_stmt: "tempo" number

// 音量設定
volume_stmt: "volume" number

// === 控制流語句 ===

// 固定次數迴圈語句
loop_stmt: "loop" number "{" statement* "}"

// 條件迴圈語句
while_stmt: "while" "(" logical_expr ")" "{" statement* "}"

// 範圍迴圈語句
for_stmt: "for" "(" identifier "," range_expr ")" "{" statement* "}"

// 範圍表達式
range_expr: number ":" number

// 條件判斷語句
if_stmt: "if" "(" logical_expr ")" "{" statement* "}" elseif_clause* else_clause?

elseif_clause: "elseif" "(" logical_expr ")" "{" statement* "}"

else_clause: "else" "{" statement* "}"

// === 函式語句 ===

// 函數定義
fn_stmt: "fn" identifier "(" parameter_list? ")" "{" statement* "}"

// 函數調用語句 - ref 函數優先匹配
fn_call_stmt: ref_identifier "(" argument_list? ")"
            | identifier "(" argument_list? ")"

// 參數列表
parameter_list: identifier ("," identifier)*

// 參數列表
argument_list: expression ("," expression)*

// 賦值語句
assignment: identifier "=" expression

// === 表達式系統 ===

// 表達式
?expression: logical_expr
           | note_literal
           | chord_literal

// 邏輯表達式
?logical_expr: logical_or

?logical_or: logical_or "or" logical_and   -> or_expr
           | logical_and

?logical_and: logical_and "and" comparison -> and_expr
            | comparison

?comparison: arithmetic_expr "==" arithmetic_expr  -> eq
           | arithmetic_expr "!=" arithmetic_expr  -> neq
           | arithmetic_expr "<" arithmetic_expr   -> lt
           | arithmetic_expr ">" arithmetic_expr   -> gt
           | arithmetic_expr "<=" arithmetic_expr  -> lte
           | arithmetic_expr ">=" arithmetic_expr  -> gte
           | "not" logical_primary                 -> not_expr
           | logical_primary

?logical_primary: "(" logical_expr ")"
                | arithmetic_expr

// 算術表達式
?arithmetic_expr: arithmetic_expr "+" term   -> add
                | arithmetic_expr "-" term   -> sub
                | term

?term: term "*" factor -> mul
     | term "/" factor -> div
     | factor

?factor: "(" arithmetic_expr ")"
       | atom

?atom: number
     | identifier

// === 基本類型 ===

// 音符字面值 - 支援有引號和無引號
note_literal: NOTE_STRING | NOTE_BARE

// 和弦字面值
chord_literal: "[" note_list "]"

// 音符列表
note_list: note_literal ("," note_literal)*

// 其他基本類型
duration: number
identifier: IDENTIFIER
ref_identifier: REF_IDENTIFIER
number: NUMBER
```

## 3. 完整 AST 節點類型

### 程式結構節點

#### 程式根節點
```json
{
    "type": "program",
    "body": [/* 語句列表 */]
}
```

### 音樂語句節點

#### 音符語句
```json
// 單個音符
{
    "type": "note",
    "note_value": {"type": "note_literal", "value": "C4"},
    "duration": {"type": "number", "value": 1.0}
}

// 音符陣列
{
    "type": "note",
    "note_value": {
        "type": "note_array",
        "notes": [
            {"type": "note_literal", "value": "C4"},
            {"type": "note_literal", "value": "D4"},
            {"type": "note_literal", "value": "E4"}
        ]
    },
    "duration": {"type": "number", "value": 0.5}
}
```

#### 和弦語句
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

#### 速度/音量設定
```json
{
    "type": "tempo",
    "bpm": {"type": "number", "value": 120}
}

{
    "type": "volume",
    "volume": {"type": "number", "value": 0.8}
}
```

### 控制流語句節點

#### 固定次數迴圈
```json
{
    "type": "loop",
    "count": {"type": "number", "value": 3},
    "body": [/* 迴圈內的語句 */]
}
```

#### 條件迴圈
```json
{
    "type": "while",
    "condition": {
        "type": "comparison",
        "op": "<",
        "left": {"type": "identifier", "name": "counter"},
        "right": {"type": "number", "value": 10}
    },
    "body": [/* 迴圈體語句 */]
}
```

#### 範圍迴圈
```json
{
    "type": "for",
    "variable": {"type": "identifier", "name": "i"},
    "range": {
        "type": "range",
        "start": {"type": "number", "value": 0},
        "end": {"type": "number", "value": 10}
    },
    "body": [/* 迴圈體語句 */]
}
```

#### 條件判斷
```json
{
    "type": "if",
    "condition": {
        "type": "comparison",
        "op": "==",
        "left": {"type": "identifier", "name": "mode"},
        "right": {"type": "number", "value": 1}
    },
    "then_body": [/* if 分支語句 */],
    "elseif_clauses": [
        {
            "type": "elseif_clause",
            "condition": {/* 條件 */},
            "body": [/* elseif 分支語句 */]
        }
    ],
    "else_body": [/* else 分支語句 */]
}
```

### 函式語句節點

#### 函式定義
```json
{
    "type": "function_def",
    "name": {"type": "identifier", "name": "melody"},
    "params": [
        {"type": "identifier", "name": "note"},
        {"type": "identifier", "name": "duration"}
    ],
    "body": [/* 函式體語句 */]
}
```

#### 函式呼叫
```json
// 使用者定義函式呼叫
{
    "type": "function_call",
    "name": {"type": "identifier", "name": "melody"},
    "args": [
        {"type": "note_literal", "value": "C4"},
        {"type": "number", "value": 1.0}
    ]
}

// ref 函式呼叫
{
    "type": "ref_call",
    "name": {"type": "ref_identifier", "name": "refVolume"},
    "args": [{"type": "number", "value": 0.8}]
}
```

#### 賦值語句
```json
{
    "type": "assign",
    "var": {"type": "identifier", "name": "tempo_value"},
    "value": {"type": "number", "value": 120}
}
```

### 表達式節點

#### 基本值
```json
// 數值
{
    "type": "number",
    "value": 120
}

// 標識符
{
    "type": "identifier",
    "name": "tempo_value"
}

// 音符字面值
{
    "type": "note_literal",
    "value": "C4"
}
```

#### 運算表達式
```json
// 算術運算
{
    "type": "binop",
    "op": "+",
    "left": {"type": "identifier", "name": "base_tempo"},
    "right": {"type": "number", "value": 20}
}

// 比較運算
{
    "type": "comparison",
    "op": ">=",
    "left": {"type": "identifier", "name": "volume"},
    "right": {"type": "number", "value": 0.5}
}

// 邏輯運算
{
    "type": "logical_op",
    "op": "and",
    "left": {
        "type": "comparison",
        "op": ">",
        "left": {"type": "identifier", "name": "tempo"},
        "right": {"type": "number", "value": 100}
    },
    "right": {
        "type": "comparison",
        "op": "<",
        "left": {"type": "identifier", "name": "volume"},
        "right": {"type": "number", "value": 0.8}
    }
}

// 一元運算
{
    "type": "unary_op",
    "op": "not",
    "operand": {
        "type": "comparison",
        "op": "==",
        "left": {"type": "identifier", "name": "playing"},
        "right": {"type": "number", "value": 0}
    }
}
```

## 4. 語法使用範例

### 基本音樂語句

```musiclang
// 設定速度和音量
tempo 120
volume 0.8

// 單個音符 (兩種寫法)
note "C4", 1.0
note C4, 1.0

// 音符陣列
note [C4, D4, E4, F4], 0.5

// 和弦
chord [C4, E4, G4], 2.0
chord ["C4", "E4", "G4"], 2.0
```

### 控制流語句

```musiclang
// 固定次數迴圈
loop 4 {
    note C4, 0.5
    note G4, 0.5
}

// 條件迴圈
counter = 0
while (counter < 5) {
    note C4, 0.5
    counter = counter + 1
}

// 範圍迴圈
for (i, 0:8) {
    if (i < 4) {
        note C4, 0.5
    } else {
        note G4, 0.5
    }
}

// 條件判斷
mode = 1
if (mode == 1) {
    note C4, 1.0
} elseif (mode == 2) {
    chord [C4, E4, G4], 1.0
} else {
    note [C4, D4, E4], 0.5
}
```

### 函式定義與呼叫

```musiclang
// 函式定義
fn playScale(start_note, duration) {
    note [C4, D4, E4, F4, G4], duration
}

fn conditionalPlay(mode) {
    if (mode == 1) {
        note C4, 0.5
    } else {
        chord [C4, E4, G4], 0.5
    }
}

// 函式呼叫
playScale(C4, 0.5)
conditionalPlay(2)

// ref 函式呼叫
refVolume(0.8)
refTempo(140)
```

### 複雜表達式

```musiclang
// 算術表達式
base_tempo = 100
fast_tempo = base_tempo + 40
slow_tempo = base_tempo - 20

// 條件表達式
volume_level = 8
if (volume_level > 5 and volume_level <= 10) {
    refVolume(0.8)
}

if (fast_tempo >= 120 or slow_tempo <= 80) {
    // 調整演奏方式
}

// 複雜條件
mode = 2
style = 1
if (not (mode == 1) and style > 0) {
    // 複雜邏輯
}
```

## 5. 特殊功能

### ref 函式系統
```musiclang
refVolume(0.8)      // 設定音量為 0.8
refTempo(120)       // 設定速度為 120 BPM
```

### 音符表示法支援
```musiclang
// 基本音符
note C4, 0.5    // Do
note D4, 0.5    // Re
note E4, 0.5    // Mi

// 升音
note C#4, 0.5   // 升 Do
note F#4, 0.5   // 升 Fa

// 降音  
note Db4, 0.5   // 降 Re
note Bb3, 0.5   // 降 Si

// 不同八度
note C3, 0.5    // 低八度
note C5, 0.5    // 高八度
```

### 變數與運算
```musiclang
// 變數賦值
tempo_value = 120
volume_level = 8
octave = 4

// 算術運算
new_tempo = tempo_value * 2
half_volume = volume_level / 2
next_octave = octave + 1

// 在音樂語句中使用變數
refTempo(new_tempo)
refVolume(half_volume)
```

## 6. 運算符優先級

1. `()` - 括號
2. `not` - 邏輯非
3. `*`, `/` - 乘法、除法
4. `+`, `-` - 加法、減法
5. `<`, `>`, `<=`, `>=` - 比較運算
6. `==`, `!=` - 等於、不等於
7. `and` - 邏輯且
8. `or` - 邏輯或
9. `=` - 賦值

## 7. 註解支援

```musiclang
// 這是單行註解
tempo 120  // 設定速度為 120 BPM

// 演奏主旋律
note [C4, D4, E4], 0.5
```

## 8. 語法錯誤處理

常見語法錯誤：
- 缺少分號: `note C4, 0.5;` (表達式語句需要分號)
- 括號不匹配: `if (condition { }`
- 音符格式錯誤: `note C44, 0.5` (正確: `C4`)
- 函式參數錯誤: `refVolume()` (缺少參數)