#!/usr/bin/env python3
"""
parser.py - 音樂程式語言解析器（簡化音符語法版）
支援音符陣列和無引號音符
"""

import os
from lark import Lark, Transformer, Tree, Token

class MusicTransformer(Transformer):
    """將解析樹轉換為 AST"""
    
    def start(self, items):
        return {"type": "program", "body": list(items)}
    
    def note_stmt(self, items):
        note_value = items[0]
        duration = items[1] if len(items) > 1 else None
        return {"type": "note", "note_value": note_value, "duration": duration}
    
    def note_value(self, items):
        return items[0]
    
    def note_array(self, items):
        return {"type": "note_array", "notes": items[0]}
    
    def chord_stmt(self, items):
        chord = items[0]
        duration = items[1] if len(items) > 1 else None
        return {"type": "chord", "chord": chord, "duration": duration}
    
    def tempo_stmt(self, items):
        return {"type": "tempo", "bpm": items[0]}
    
    def volume_stmt(self, items):
        return {"type": "volume", "volume": items[0]}
    
    def loop_stmt(self, items):
        count = items[0]
        body = items[1:]
        return {"type": "loop", "count": count, "body": list(body)}
    
    def if_stmt(self, items):
        condition = items[0]
        then_body = []
        elseif_clauses = []
        else_body = []
        
        # 解析 if 語句的各部分
        i = 1
        # 收集 then 部分的語句
        while i < len(items) and not isinstance(items[i], dict):
            then_body.append(items[i])
            i += 1
        
        # 處理 elseif 和 else 子句
        while i < len(items):
            item = items[i]
            if isinstance(item, dict):
                if item.get('type') == 'elseif_clause':
                    elseif_clauses.append(item)
                elif item.get('type') == 'else_clause':
                    else_body = item.get('body', [])
            i += 1
        
        return {
            "type": "if", 
            "condition": condition, 
            "then_body": then_body,
            "elseif_clauses": elseif_clauses,
            "else_body": else_body
        }
    
    def elseif_clause(self, items):
        condition = items[0]
        body = items[1:]
        return {"type": "elseif_clause", "condition": condition, "body": list(body)}
    
    def else_clause(self, items):
        return {"type": "else_clause", "body": list(items)}
    
    def while_stmt(self, items):
        condition = items[0]
        body = items[1:]
        return {"type": "while", "condition": condition, "body": list(body)}
    
    def for_stmt(self, items):
        variable = items[0]  # 迴圈變數
        range_expr = items[1]  # 範圍表達式
        body = items[2:]  # 迴圈體
        return {
            "type": "for", 
            "variable": variable, 
            "range": range_expr, 
            "body": list(body)
        }
    
    def range_expr(self, items):
        start = items[0]  # 起始值
        end = items[1]    # 結束值
        return {"type": "range", "start": start, "end": end}
    
    def fn_stmt(self, items):
        name = items[0]
        params = []
        body_start = 1
        
        # 檢查是否有參數列表
        if len(items) > 1 and isinstance(items[1], list):
            params = items[1]
            body_start = 2
        
        body = items[body_start:] if len(items) > body_start else []
        
        return {
            "type": "function_def", 
            "name": name, 
            "params": params, 
            "body": list(body)
        }
    
    def fn_call_stmt(self, items):
        name = items[0]
        args = items[1] if len(items) > 1 else []
        
        # 檢查是否為 ref 函數
        func_name = self._get_name_from_node(name)
        if func_name.startswith('ref'):
            return {"type": "ref_call", "name": name, "args": args}
        else:
            return {"type": "function_call", "name": name, "args": args}
    
    def _get_name_from_node(self, node):
        """從節點獲取名稱字符串"""
        if isinstance(node, dict):
            return node.get('name', '')
        elif isinstance(node, str):
            return node
        else:
            return str(node)
    
    def parameter_list(self, items):
        return list(items)
    
    def argument_list(self, items):  
        return list(items)
    
    def assignment(self, items):
        return {"type": "assign", "var": items[0], "value": items[1]}
    
    def note_literal(self, items):
        # 處理無引號音符
        note_str = str(items[0])
        return {"type": "note_literal", "value": note_str}
    
    def chord_literal(self, items):
        return {"type": "chord_literal", "notes": items[0]}
    
    def note_list(self, items):
        # 確保返回扁平的音符列表
        result = []
        for item in items:
            if isinstance(item, dict) and item.get('type') == 'note_literal':
                result.append(item)
            elif isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result
    
    def identifier(self, items):
        return {"type": "identifier", "name": str(items[0])}
    
    def ref_identifier(self, items):
        name = str(items[0])
        return {"type": "ref_identifier", "name": name}
    
    def number(self, items):
        val = str(items[0])
        return {"type": "number", "value": float(val) if '.' in val else int(val)}
    
    def duration(self, items):
        return items[0]
    
    # 數學運算
    def add(self, items):
        return {"type": "binop", "op": "+", "left": items[0], "right": items[1]}
    
    def sub(self, items):
        return {"type": "binop", "op": "-", "left": items[0], "right": items[1]}
    
    def mul(self, items):
        return {"type": "binop", "op": "*", "left": items[0], "right": items[1]}
    
    def div(self, items):
        return {"type": "binop", "op": "/", "left": items[0], "right": items[1]}
    
    # 邏輯運算
    def or_expr(self, items):
        return {"type": "logical_op", "op": "or", "left": items[0], "right": items[1]}
    
    def and_expr(self, items):
        return {"type": "logical_op", "op": "and", "left": items[0], "right": items[1]}
    
    def not_expr(self, items):
        return {"type": "unary_op", "op": "not", "operand": items[0]}
    
    # 比較運算
    def eq(self, items):
        return {"type": "comparison", "op": "==", "left": items[0], "right": items[1]}
    
    def neq(self, items):
        return {"type": "comparison", "op": "!=", "left": items[0], "right": items[1]}
    
    def lt(self, items):
        return {"type": "comparison", "op": "<", "left": items[0], "right": items[1]}
    
    def gt(self, items):
        return {"type": "comparison", "op": ">", "left": items[0], "right": items[1]}
    
    def lte(self, items):
        return {"type": "comparison", "op": "<=", "left": items[0], "right": items[1]}
    
    def gte(self, items):
        return {"type": "comparison", "op": ">=", "left": items[0], "right": items[1]}
    
    def logical_primary(self, items):
        return items[0]

class MusicLanguageParser:
    """音樂程式語言解析器"""
    
    def __init__(self, grammar_file=None):
        if grammar_file and os.path.exists(grammar_file):
            with open(grammar_file, 'r', encoding='utf-8') as f:
                grammar = f.read()
        else:
            # 簡化的內建語法定義
            grammar = '''
// music_lang.lark - 簡化音符語法版本

?start: statement*

?statement: note_stmt
          | chord_stmt  
          | tempo_stmt
          | volume_stmt
          | loop_stmt
          | fn_stmt
          | fn_call_stmt
          | if_stmt
          | while_stmt
          | for_stmt
          | assignment
          | expression ";"

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

// 迴圈語句
loop_stmt: "loop" number "{" statement* "}"

// if 條件語句
if_stmt: "if" "(" logical_expr ")" "{" statement* "}" elseif_clause* else_clause?

elseif_clause: "elseif" "(" logical_expr ")" "{" statement* "}"

else_clause: "else" "{" statement* "}"

// while 迴圈語句
while_stmt: "while" "(" logical_expr ")" "{" statement* "}"

// for 迴圈語句
for_stmt: "for" "(" identifier "," range_expr ")" "{" statement* "}"

// 範圍表達式
range_expr: number ":" number

// 函數定義
fn_stmt: "fn" identifier "(" parameter_list? ")" "{" statement* "}"

// 函數調用語句 - 修改優先級，讓 ref 函數優先匹配
fn_call_stmt: ref_identifier "(" argument_list? ")"
            | identifier "(" argument_list? ")"

// 參數列表
parameter_list: identifier ("," identifier)*

// 參數列表
argument_list: expression ("," expression)*

// 賦值語句
assignment: identifier "=" expression

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

// 基本類型
note_literal: SIMPLE_NOTE
chord_literal: "[" note_list "]"
note_list: note_literal ("," note_literal)*
duration: number
identifier: IDENTIFIER
ref_identifier: REF_IDENTIFIER

// Token 定義 - 簡化版本
SIMPLE_NOTE: /[A-Ga-g][#b]?[0-9]/

IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
REF_IDENTIFIER: /ref[A-Z][a-zA-Z0-9_]*/

number: NUMBER
NUMBER: /[0-9]+(\\.[0-9]+)?/

// 註解和空白字符
COMMENT: "//" /[^\\n]*/
%ignore COMMENT
%ignore /\\s+/
            '''
        
        try:
            self.parser = Lark(
                grammar,
                parser='lalr',
                transformer=MusicTransformer()
            )
            print("✅ 解析器初始化成功")
        except Exception as e:
            print(f"❌ 解析器初始化失敗: {e}")
            raise
    
    def parse(self, code):
        """解析程式碼"""
        try:
            result = self.parser.parse(code)
            return result
        except Exception as e:
            print(f"❌ 語法錯誤: {e}")
            raise SyntaxError(f"語法錯誤: {e}")

def test_parser():
    """測試解析器"""
    parser = MusicLanguageParser()
    
    test_code = '''
    tempo 120
    volume 0.8
    
    fn melody() {
        note [C4, D4, E4], 0.5
        note F4, 1.0
    }
    
    melody()
    chord [C4, E4, G4], 1.0
    '''
    
    try:
        ast = parser.parse(test_code)
        print("✅ 解析成功！")
        print(f"AST: {ast}")
        return ast
    except Exception as e:
        print(f"❌ 解析失敗: {e}")
        return None

if __name__ == "__main__":
    test_parser()