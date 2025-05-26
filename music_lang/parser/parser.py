from lark import Lark, Transformer

# 簡化的語法定義
GRAMMAR = '''
start: statement*

?statement: note_stmt
          | chord_stmt  
          | tempo_stmt
          | loop_stmt
          | assignment

// 基本語句
note_stmt: "note" note_literal ("," number)?
chord_stmt: "chord" chord_literal ("," number)?
tempo_stmt: "tempo" number
loop_stmt: "loop" number "{" statement* "}"
assignment: identifier "=" expression

// 表達式
?expression: add_expr

?add_expr: add_expr "+" mul_expr  -> add
         | add_expr "-" mul_expr  -> sub
         | mul_expr

?mul_expr: mul_expr "*" atom     -> mul
         | mul_expr "/" atom     -> div
         | atom

?atom: number
     | identifier
     | note_literal
     | chord_literal
     | "(" expression ")"

// 基本元素
note_literal: NOTE_STRING
chord_literal: "[" note_list "]"
note_list: note_literal ("," note_literal)*
identifier: IDENTIFIER
number: NUMBER

// Token定義
NOTE_STRING: "\\\"" /[A-Ga-g]#?[0-9]/ "\\\""
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /\\d+(\\.\\d+)?/

// 忽略空白和註解
%import common.WS
%ignore WS
COMMENT: "//" /[^\\r\\n]*/
%ignore COMMENT
'''

class MusicTransformer(Transformer):
    """轉換器，將解析樹轉為AST"""
    
    def start(self, items):
        return {"type": "program", "body": items}
    
    def note_stmt(self, items):
        note = items[0]
        duration = items[1] if len(items) > 1 else None
        return {"type": "note", "note": note, "duration": duration}
    
    def chord_stmt(self, items):
        chord = items[0]
        duration = items[1] if len(items) > 1 else None
        return {"type": "chord", "chord": chord, "duration": duration}
    
    def tempo_stmt(self, items):
        return {"type": "tempo", "bpm": items[0]}
    
    def loop_stmt(self, items):
        count = items[0]
        body = items[1:]
        return {"type": "loop", "count": count, "body": body}
    
    def assignment(self, items):
        return {"type": "assign", "var": items[0], "value": items[1]}
    
    def note_literal(self, items):
        # 移除引號
        note = str(items[0])[1:-1]  
        return {"type": "note_literal", "value": note}
    
    def chord_literal(self, items):
        return {"type": "chord_literal", "notes": items[0]}
    
    def note_list(self, items):
        return list(items)
    
    def identifier(self, items):
        return {"type": "identifier", "name": str(items[0])}
    
    def number(self, items):
        val = str(items[0])
        return {"type": "number", "value": float(val) if '.' in val else int(val)}
    
    # 數學運算
    def add(self, items):
        return {"type": "binop", "op": "+", "left": items[0], "right": items[1]}
    
    def sub(self, items):
        return {"type": "binop", "op": "-", "left": items[0], "right": items[1]}
    
    def mul(self, items):
        return {"type": "binop", "op": "*", "left": items[0], "right": items[1]}
    
    def div(self, items):
        return {"type": "binop", "op": "/", "left": items[0], "right": items[1]}

class MusicLanguageParser:
    """音樂程式語言解析器"""
    
    def __init__(self):
        self.parser = Lark(
            GRAMMAR,
            parser='lalr',
            transformer=MusicTransformer()
        )
    
    def parse(self, code):
        """解析程式碼"""
        try:
            return self.parser.parse(code)
        except Exception as e:
            raise SyntaxError(f"語法錯誤: {e}")

def test_parser():
    """測試解析器"""
    parser = MusicLanguageParser()
    
    # 測試案例
    test_cases = [
        # 基本音符
        'note "C4"',
        
        # 帶時長的音符
        'note "A4", 1.5',
        
        # 和弦
        'chord ["C4", "E4", "G4"]',
        
        # 速度設定
        'tempo 120',
        
        # 簡單迴圈
        'loop 2 { note "C4" }',
        
        # 複合程式
        '''
        tempo 120
        note "C4", 1.0
        chord ["C4", "E4", "G4"], 2.0
        loop 3 {
            note "A4"
            note "B4"
        }
        '''
    ]
    
    for i, code in enumerate(test_cases):
        print(f"\\n=== 測試案例 {i+1} ===")
        print(f"程式碼: {code.strip()}")
        try:
            ast = parser.parse(code)
            print("✓ 解析成功")
            print(f"AST: {ast}")
        except Exception as e:
            print(f"✗ 解析失敗: {e}")

if __name__ == "__main__":
    test_parser()