#!/usr/bin/env python3
"""
audio_engine.py - 音樂程式語言音訊引擎（修正版）
支援函數定義、調用和音量控制
"""

import math
import time
import sys

# 嘗試導入音訊庫
AUDIO_AVAILABLE = True
try:
    import numpy as np
    import pygame
    print("🎵 音訊庫載入成功")
except ImportError as e:
    AUDIO_AVAILABLE = False
    print(f"⚠️  音訊庫未安裝: {e}")
    print("💡 執行以下命令安裝:")
    print("   pip install numpy pygame")

class AudioEngine:
    """音訊引擎"""
    
    def __init__(self):
        self.current_tempo = 120
        self.current_volume = 0.7
        self.audio_enabled = AUDIO_AVAILABLE
        
        if self.audio_enabled:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.note_frequencies = self._build_note_table()
                print("🎵 音訊引擎已初始化")
            except Exception as e:
                print(f"⚠️  音訊初始化失敗: {e}")
                self.audio_enabled = False
        
        if not self.audio_enabled:
            print("🔇 使用文字模式模擬播放")
    
    def _build_note_table(self):
        """建立音符頻率表"""
        if not self.audio_enabled:
            return {}
            
        notes = {}
        base_freq = 440.0  # A4
        base_note = 69     # A4 的 MIDI 編號
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        for octave in range(9):  # 0-8 八度
            for i, note_name in enumerate(note_names):
                midi_num = octave * 12 + i
                freq = base_freq * (2 ** ((midi_num - base_note) / 12))
                
                # 添加各種表示法
                notes[f"{note_name}{octave}"] = freq
                notes[f"{note_name.lower()}{octave}"] = freq
                
                # 降音表示法
                if '#' in note_name:
                    flat_name = note_names[(i + 1) % 12] + 'b'
                    notes[f"{flat_name}{octave}"] = freq
                    notes[f"{flat_name.lower()}{octave}"] = freq
        
        return notes
    
    def set_volume(self, volume):
        """設定音量 (0.0-1.0)"""
        self.current_volume = max(0.0, min(1.0, volume))
        print(f"🔊 音量設定為: {self.current_volume:.1%}")
    
    def set_tempo(self, bpm):
        """設定速度"""
        self.current_tempo = max(40, min(200, bpm))
        print(f"🥁 設定速度: {self.current_tempo} BPM")
    
    def get_note_frequency(self, note_str):
        """取得音符頻率"""
        # 處理音符字符串，確保是字符串格式
        if isinstance(note_str, dict):
            if note_str.get('type') == 'note_literal':
                note_str = note_str.get('value', 'C4')
            else:
                note_str = str(note_str.get('value', 'C4'))
        
        note_str = str(note_str).strip().replace('"', '')
        
        if self.audio_enabled and note_str in self.note_frequencies:
            return self.note_frequencies[note_str]
        else:
            return 440.0
    
    def _generate_wave(self, freq, duration):
        """生成音訊波形"""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        wave_array = np.zeros(samples)
        
        for i in range(samples):
            time_point = float(i) / sample_rate
            wave_array[i] = math.sin(2 * math.pi * freq * time_point)
            wave_array[i] += 0.3 * math.sin(2 * math.pi * freq * 2 * time_point)
            wave_array[i] += 0.1 * math.sin(2 * math.pi * freq * 3 * time_point)
        
        # 音量控制
        wave_array *= self.current_volume
        
        # 淡入淡出效果
        fade_samples = min(2000, samples // 4)
        for i in range(fade_samples):
            fade_factor = math.sin((i / fade_samples) * math.pi / 2)
            wave_array[i] *= fade_factor
            wave_array[-(i+1)] *= fade_factor
        
        # 轉換為16位整數
        wave_array = (wave_array * 32767 * 0.8).astype(np.int16)
        return wave_array
    
    def play_note(self, note, duration=1.0):
        """播放音符"""
        beat_duration = 60.0 / self.current_tempo
        actual_duration = duration * beat_duration
        
        # 處理音符格式
        if isinstance(note, dict):
            if note.get('type') == 'note_literal':
                note_str = note.get('value', 'C4')
            else:
                note_str = str(note.get('value', 'C4'))
        else:
            note_str = str(note).strip().replace('"', '')
        
        if self.audio_enabled:
            freq = self.get_note_frequency(note_str)
            print(f"🎵 播放: {note_str} ({freq:.1f}Hz) - {actual_duration:.2f}秒")
            
            try:
                wave_array = self._generate_wave(freq, actual_duration)
                stereo_wave = np.array([[sample, sample] for sample in wave_array])
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                time.sleep(actual_duration)
            except Exception as e:
                print(f"   ⚠️  播放錯誤: {e}")
                self._text_mode_play(note_str, actual_duration)
        else:
            self._text_mode_play(note_str, actual_duration)
    
    def play_chord(self, notes, duration=1.0):
        """播放和弦"""
        beat_duration = 60.0 / self.current_tempo
        actual_duration = duration * beat_duration
        
        # 處理和弦音符列表
        processed_notes = []
        for note in notes:
            if isinstance(note, dict):
                if note.get('type') == 'note_literal':
                    processed_notes.append(note.get('value', 'C4'))
                else:
                    processed_notes.append(str(note.get('value', 'C4')))
            elif isinstance(note, list):
                # 處理嵌套列表
                for sub_note in note:
                    if isinstance(sub_note, dict) and sub_note.get('type') == 'note_literal':
                        processed_notes.append(sub_note.get('value', 'C4'))
            else:
                processed_notes.append(str(note).strip().replace('"', ''))
        
        if self.audio_enabled and len(processed_notes) > 0:
            print(f"🎼 播放和弦: {processed_notes} - {actual_duration:.2f}秒")
            
            try:
                sample_rate = 44100
                samples = int(sample_rate * actual_duration)
                mixed_wave = np.zeros(samples)
                
                for note_str in processed_notes:
                    freq = self.get_note_frequency(note_str)
                    note_wave = self._generate_wave(freq, actual_duration)
                    if len(note_wave) == len(mixed_wave):
                        mixed_wave += note_wave.astype(np.float64)
                
                max_val = np.max(np.abs(mixed_wave))
                if max_val > 0:
                    mixed_wave = mixed_wave / max_val * 32767 * 0.6
                
                mixed_wave = mixed_wave.astype(np.int16)
                stereo_wave = np.array([[sample, sample] for sample in mixed_wave])
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                time.sleep(actual_duration)
            except Exception as e:
                print(f"   ⚠️  播放錯誤: {e}")
                self._text_mode_play(f"和弦{processed_notes}", actual_duration)
        else:
            self._text_mode_play(f"和弦{processed_notes}", actual_duration)
    
    def _text_mode_play(self, note, duration):
        """文字模式播放"""
        print(f"♪ {note} ({duration:.2f}秒) [音量: {self.current_volume:.1%}]")
        time.sleep(min(duration, 0.5))
    
    def cleanup(self):
        """清理資源"""
        if self.audio_enabled:
            try:
                pygame.mixer.quit()
                print("🎵 音訊引擎已關閉")
            except:
                pass

class MusicInterpreter:
    """音樂解釋器 - 支援函數功能"""
    
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.variables = {}
        self.functions = {}
    
    def execute(self, ast):
        """執行 AST"""
        try:
            print("\n🚀 開始執行音樂程式")
            print("=" * 60)
            self._execute_node(ast)
            print("=" * 60)
            print("✅ 執行完成")
        except KeyboardInterrupt:
            print("\n⏹️  播放中斷")
        except Exception as e:
            print(f"\n❌ 執行錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.audio_engine.cleanup()
    
    def _execute_node(self, node):
        """執行節點"""
        if not isinstance(node, dict):
            return node
        
        node_type = node.get('type')
        
        if node_type == 'program':
            for stmt in node.get('body', []):
                self._execute_node(stmt)
        
        elif node_type == 'note':
            note_value_info = node.get('note_value', {})
            duration_info = node.get('duration')
            
            duration = self._get_value(duration_info, 1.0)
            
            # 檢查是單個音符還是音符陣列
            if note_value_info.get('type') == 'note_array':
                # 音符陣列：依序播放每個音符
                notes = note_value_info.get('notes', [])
                for note_data in notes:
                    note_value = self._get_value(note_data, 'C4')
                    self.audio_engine.play_note(note_value, duration)
            else:
                # 單個音符
                note_value = self._get_value(note_value_info, 'C4')
                self.audio_engine.play_note(note_value, duration)
        
        elif node_type == 'chord':
            chord_info = node.get('chord', {})
            duration_info = node.get('duration')
            
            notes = []
            chord_notes = chord_info.get('notes', [])
            
            # 處理和弦音符
            for note_node in chord_notes:
                if isinstance(note_node, dict):
                    if note_node.get('type') == 'note_literal':
                        notes.append(note_node.get('value', 'C4'))
                    else:
                        notes.append(self._get_value(note_node, 'C4'))
                elif isinstance(note_node, list):
                    for sub_note in note_node:
                        if isinstance(sub_note, dict) and sub_note.get('type') == 'note_literal':
                            notes.append(sub_note.get('value', 'C4'))
                else:
                    notes.append(str(note_node))
            
            duration = self._get_value(duration_info, 1.0)
            self.audio_engine.play_chord(notes, duration)
        
        elif node_type == 'tempo':
            bpm_info = node.get('bpm', {})
            bpm = self._get_value(bpm_info, 120)
            self.audio_engine.set_tempo(int(bpm))
        
        elif node_type == 'volume':
            volume_info = node.get('volume', {})
            volume = self._get_value(volume_info, 0.7)
            self.audio_engine.set_volume(float(volume))
        
        elif node_type == 'loop':
            count_info = node.get('count', {})
            count = int(self._get_value(count_info, 1))
            body = node.get('body', [])
            
            print(f"🔄 迴圈開始 ({count} 次)")
            for i in range(count):
                print(f"   第 {i+1}/{count} 次")
                for stmt in body:
                    self._execute_node(stmt)
            print("🔄 迴圈結束")
        
        elif node_type == 'if':
            condition = node.get('condition', {})
            then_body = node.get('then_body', [])
            elseif_clauses = node.get('elseif_clauses', [])
            else_body = node.get('else_body', [])
            
            # 評估主條件
            if self._evaluate_condition(condition):
                print("✅ if 條件成立")
                for stmt in then_body:
                    self._execute_node(stmt)
            else:
                # 檢查 elseif 條件
                executed = False
                for elseif_clause in elseif_clauses:
                    elseif_condition = elseif_clause.get('condition', {})
                    if self._evaluate_condition(elseif_condition):
                        print("✅ elseif 條件成立")
                        elseif_body = elseif_clause.get('body', [])
                        for stmt in elseif_body:
                            self._execute_node(stmt)
                        executed = True
                        break
                
                # 如果沒有條件成立，執行 else
                if not executed and else_body:
                    print("✅ 執行 else 分支")
                    for stmt in else_body:
                        self._execute_node(stmt)
        
        elif node_type == 'while':
            condition = node.get('condition', {})
            body = node.get('body', [])
            
            print("🔄 while 迴圈開始")
            loop_count = 0
            max_iterations = 1000  # 防止無限迴圈
            
            while self._evaluate_condition(condition) and loop_count < max_iterations:
                loop_count += 1
                print(f"   第 {loop_count} 次迴圈")
                for stmt in body:
                    self._execute_node(stmt)
            
            if loop_count >= max_iterations:
                print("⚠️  迴圈達到最大次數限制，自動終止")
            
            print("🔄 while 迴圈結束")
        
        elif node_type == 'for':
            variable = node.get('variable', {})
            range_expr = node.get('range', {})
            body = node.get('body', [])
            
            # 獲取迴圈變數名
            var_name = self._get_name(variable)
            
            # 獲取範圍
            start_val = int(self._get_value(range_expr.get('start', {}), 0))
            end_val = int(self._get_value(range_expr.get('end', {}), 0))
            
            print(f"🔄 for 迴圈開始 ({var_name}: {start_val} 到 {end_val})")
            
            for i in range(start_val, end_val):
                # 設定迴圈變數
                self.variables[var_name] = i
                print(f"   第 {i+1}/{end_val-start_val} 次，{var_name} = {i}")
                
                for stmt in body:
                    self._execute_node(stmt)
            
            print("🔄 for 迴圈結束")
        
        elif node_type == 'function_def':
            func_name = self._get_name(node.get('name', {}))
            params = [self._get_name(p) for p in node.get('params', [])]
            body = node.get('body', [])
            
            self.functions[func_name] = {
                'params': params,
                'body': body
            }
            print(f"📝 函式定義: {func_name}({', '.join(params)})")
        
        elif node_type == 'function_call':
            func_name = self._get_name(node.get('name', {}))
            args = node.get('args', [])
            
            if func_name in self.functions:
                self._call_user_function(func_name, args)
            else:
                print(f"⚠️  未知函式: {func_name}")
        
        elif node_type == 'ref_call':
            func_name = self._get_name(node.get('name', {}))
            args = node.get('args', [])
            self._call_ref_function(func_name, args)
        
        elif node_type == 'assign':
            var_info = node.get('var', {})
            value_info = node.get('value')
            
            var_name = self._get_name(var_info)
            value = self._evaluate_expression(value_info)
            self.variables[var_name] = value
            print(f"📝 變數設定: {var_name} = {value}")
        
        else:
            print(f"⚠️  未知節點: {node_type}")
    
    def _call_ref_function(self, func_name, args):
        """呼叫 ref 函式"""
        print(f"🔧 呼叫 ref 函式: {func_name}")
        
        if func_name == 'refVolume':
            if len(args) > 0:
                volume = self._evaluate_expression(args[0])
                self.audio_engine.set_volume(float(volume))
            else:
                print("⚠️  refVolume 需要一個參數")
        
        elif func_name == 'refTempo':
            if len(args) > 0:
                tempo = self._evaluate_expression(args[0])
                self.audio_engine.set_tempo(int(tempo))
            else:
                print("⚠️  refTempo 需要一個參數")
        
        elif func_name == 'refPlay':
            if len(args) >= 1:
                note = self._evaluate_expression(args[0])
                duration = self._evaluate_expression(args[1]) if len(args) > 1 else 1.0
                self.audio_engine.play_note(str(note), float(duration))
            else:
                print("⚠️  refPlay 需要至少一個參數")
        
        else:
            print(f"⚠️  未知的 ref 函式: {func_name}")
    
    def _call_user_function(self, func_name, args):
        """呼叫使用者定義的函式"""
        func_def = self.functions[func_name]
        params = func_def['params']
        body = func_def['body']
        
        # 保存當前變數狀態
        old_vars = self.variables.copy()
        
        # 設定參數
        for i, param in enumerate(params):
            if i < len(args):
                self.variables[param] = self._evaluate_expression(args[i])
            else:
                self.variables[param] = 0
        
        print(f"🔧 呼叫函式: {func_name}")
        
        # 執行函式體
        for stmt in body:
            self._execute_node(stmt)
        
        # 恢復變數狀態
        self.variables = old_vars
    
    def _get_name(self, node):
        """取得名稱"""
        if isinstance(node, dict):
            # 處理 ref_identifier 類型
            if node.get('type') in ['identifier', 'ref_identifier']:
                return node.get('name', '')
            return node.get('name', '')
        return str(node)
    
    def _get_value(self, info, default):
        """取得節點值"""
        if info is None:
            return default
        elif isinstance(info, dict):
            if info.get('type') == 'note_literal':
                return info.get('value', default)
            else:
                return info.get('value', default)
        else:
            return info
    
    def _evaluate_expression(self, expr):
        """評估表達式"""
        if expr is None:
            return 0
        elif isinstance(expr, (int, float, str)):
            return expr
        elif isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'number':
                return expr.get('value', 0)
            elif expr_type == 'identifier':
                var_name = expr.get('name', '')
                return self.variables.get(var_name, 0)
            elif expr_type == 'note_literal':
                return expr.get('value', 'C4')
            elif expr_type == 'binop':
                left = self._evaluate_expression(expr.get('left'))
                right = self._evaluate_expression(expr.get('right'))
                op = expr.get('op')
                
                try:
                    if op == '+':
                        return left + right
                    elif op == '-':
                        return left - right
                    elif op == '*':
                        return left * right
                    elif op == '/':
                        return left / right if right != 0 else 0
                except:
                    return 0
        
        return 0
    
    def _evaluate_condition(self, expr):
        """評估邏輯條件表達式"""
        if expr is None:
            return False
        elif isinstance(expr, bool):
            return expr
        elif isinstance(expr, (int, float)):
            return expr != 0
        elif isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'number':
                return expr.get('value', 0) != 0
            elif expr_type == 'identifier':
                var_name = expr.get('name', '')
                value = self.variables.get(var_name, 0)
                return value != 0
            elif expr_type == 'logical_op':
                op = expr.get('op')
                left = self._evaluate_condition(expr.get('left'))
                right = self._evaluate_condition(expr.get('right'))
                
                if op == 'or':
                    return left or right
                elif op == 'and':
                    return left and right
            elif expr_type == 'unary_op':
                op = expr.get('op')
                operand = self._evaluate_condition(expr.get('operand'))
                
                if op == 'not':
                    return not operand
            elif expr_type == 'comparison':
                op = expr.get('op')
                left = self._evaluate_expression(expr.get('left'))
                right = self._evaluate_expression(expr.get('right'))
                
                try:
                    if op == '==':
                        return left == right
                    elif op == '!=':
                        return left != right
                    elif op == '<':
                        return left < right
                    elif op == '>':
                        return left > right
                    elif op == '<=':
                        return left <= right
                    elif op == '>=':
                        return left >= right
                except:
                    return False
            elif expr_type == 'binop':
                # 數值表達式的結果作為條件
                result = self._evaluate_expression(expr)
                return result != 0
        
        return False

if __name__ == "__main__":
    # 測試音訊引擎
    engine = AudioEngine()
    engine.set_volume(0.5)
    engine.play_note("C4", 0.5)
    engine.cleanup()