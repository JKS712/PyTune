#!/usr/bin/env python3
"""
enhanced_audio_engine.py - 增強版音訊引擎
支援音量控制和更好的音質
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
    """增強版音訊引擎"""
    
    def __init__(self):
        self.current_tempo = 120
        self.current_volume = 0.7  # 增加預設音量 (0.0-1.0)
        self.audio_enabled = AUDIO_AVAILABLE
        
        if self.audio_enabled:
            try:
                # 使用更高品質的音訊設定
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.note_frequencies = self._build_note_table()
                print("🎵 音訊引擎已初始化")
                print(f"🔊 當前音量: {self.current_volume:.1%}")
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
    
    def get_note_frequency(self, note_str):
        """取得音符頻率"""
        note_str = note_str.strip().replace('"', '')
        
        if self.audio_enabled and note_str in self.note_frequencies:
            return self.note_frequencies[note_str]
        else:
            return 440.0  # 預設頻率
    
    def _generate_wave(self, freq, duration, wave_type='sine'):
        """生成音訊波形"""
        sample_rate = 44100
        samples = int(sample_rate * duration)
        wave_array = np.zeros(samples)
        
        for i in range(samples):
            time_point = float(i) / sample_rate
            
            if wave_type == 'sine':
                # 基本正弦波
                wave_array[i] = math.sin(2 * math.pi * freq * time_point)
                
                # 添加泛音以增加豐富度
                wave_array[i] += 0.3 * math.sin(2 * math.pi * freq * 2 * time_point)
                wave_array[i] += 0.1 * math.sin(2 * math.pi * freq * 3 * time_point)
                
        # 音量控制
        wave_array *= self.current_volume
        
        # 改善的淡入淡出效果
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
        # 計算實際時長
        beat_duration = 60.0 / self.current_tempo
        actual_duration = duration * beat_duration
        
        if self.audio_enabled:
            freq = self.get_note_frequency(note)
            print(f"🎵 播放: {note} ({freq:.1f}Hz) - {actual_duration:.2f}秒")
            
            try:
                # 生成改善的音訊
                wave_array = self._generate_wave(freq, actual_duration)
                
                # 轉為立體聲
                stereo_wave = np.array([[sample, sample] for sample in wave_array])
                
                # 播放
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                time.sleep(actual_duration)
                
            except Exception as e:
                print(f"   ⚠️  播放錯誤: {e}")
                self._text_mode_play(note, actual_duration)
        else:
            self._text_mode_play(note, actual_duration)
    
    def play_chord(self, notes, duration=1.0):
        """播放和弦"""
        beat_duration = 60.0 / self.current_tempo
        actual_duration = duration * beat_duration
        
        if self.audio_enabled and len(notes) > 0:
            print(f"🎼 播放和弦: {notes} - {actual_duration:.2f}秒")
            
            try:
                sample_rate = 44100
                samples = int(sample_rate * actual_duration)
                mixed_wave = np.zeros(samples)
                
                # 混合各個音符
                for note in notes:
                    freq = self.get_note_frequency(note)
                    note_wave = self._generate_wave(freq, actual_duration)
                    
                    # 確保長度一致
                    if len(note_wave) == len(mixed_wave):
                        mixed_wave += note_wave.astype(np.float64)
                
                # 正規化並避免削波
                max_val = np.max(np.abs(mixed_wave))
                if max_val > 0:
                    mixed_wave = mixed_wave / max_val * 32767 * 0.6
                
                mixed_wave = mixed_wave.astype(np.int16)
                
                # 轉為立體聲
                stereo_wave = np.array([[sample, sample] for sample in mixed_wave])
                
                # 播放
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                time.sleep(actual_duration)
                
            except Exception as e:
                print(f"   ⚠️  播放錯誤: {e}")
                self._text_mode_play(f"和弦{notes}", actual_duration)
        else:
            self._text_mode_play(f"和弦{notes}", actual_duration)
    
    def set_tempo(self, bpm):
        """設定速度"""
        self.current_tempo = max(40, min(200, bpm))  # 限制合理範圍
        print(f"🥁 設定速度: {self.current_tempo} BPM")
    
    def _text_mode_play(self, note, duration):
        """文字模式播放 (無音訊時使用)"""
        print(f"♪ {note} ({duration:.2f}秒) [音量: {self.current_volume:.1%}]")
        time.sleep(min(duration, 1.0))  # 縮短等待時間
    
    def cleanup(self):
        """清理資源"""
        if self.audio_enabled:
            try:
                pygame.mixer.quit()
                print("🎵 音訊引擎已關閉")
            except:
                pass

class MusicInterpreter:
    """音樂解釋器 - 支援函式功能"""
    
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.variables = {}
        self.functions = {}  # 儲存使用者定義的函式
    
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
            note_info = node.get('note', {})
            duration_info = node.get('duration')
            
            note_value = self._get_value(note_info, 'C4')
            duration = self._get_value(duration_info, 1.0)
            
            self.audio_engine.play_note(note_value, duration)
        
        elif node_type == 'chord':
            chord_info = node.get('chord', {})
            duration_info = node.get('duration')
            
            notes = []
            for note_node in chord_info.get('notes', []):
                notes.append(self._get_value(note_node, 'C4'))
            
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
        
        elif node_type == 'function_def':
            func_name = node.get('name', 'unnamed')
            params = node.get('params', [])
            body = node.get('body', [])
            
            self.functions[func_name] = {
                'params': params,
                'body': body
            }
            print(f"📝 函式定義: {func_name}({', '.join(params)})")
        
        elif node_type == 'function_call':
            func_name = node.get('name', '')
            args = node.get('args', [])
            
            if func_name.startswith('ref') or func_name in self.functions:
                self._call_function(func_name, args)
            else:
                print(f"⚠️  未知函式: {func_name}")
        
        elif node_type == 'assign':
            var_info = node.get('var', {})
            value_info = node.get('value')
            
            var_name = self._get_value(var_info, '')
            if isinstance(var_info, dict) and 'name' in var_info:
                var_name = var_info['name']
            
            value = self._evaluate_expression(value_info)
            self.variables[var_name] = value
            print(f"📝 變數設定: {var_name} = {value}")
        
        else:
            print(f"⚠️  未知節點: {node_type}")
    
    def _call_function(self, func_name, args):
        """呼叫函式"""
        # 處理內建的 ref 函式
        if func_name.startswith('ref'):
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
        
        # 處理使用者定義的函式
        elif func_name in self.functions:
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
    
    def _get_value(self, info, default):
        """取得節點值"""
        if info is None:
            return default
        elif isinstance(info, dict):
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

# 測試函數
def test_enhanced_audio():
    """測試增強版音訊功能"""
    print("🧪 測試增強版音訊引擎")
    
    engine = AudioEngine()
    
    # 測試音量控制
    engine.set_volume(0.3)
    engine.play_note("C4", 0.5)
    
    engine.set_volume(0.7)
    engine.play_note("E4", 0.5)
    
    engine.set_volume(1.0)
    engine.play_note("G4", 0.5)
    
    # 測試和弦
    engine.play_chord(["C4", "E4", "G4"], 1.0)
    
    engine.cleanup()

if __name__ == "__main__":
    test_enhanced_audio()