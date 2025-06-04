#!/usr/bin/env python3
"""
audio_engine.py - PyTune 音訊引擎（支援音色功能）
路徑: D:\parser\pyTune\music_lang\audio\audio_engine.py
"""

import numpy as np
import pygame
import time
from typing import Dict, List, Optional, Any
from enum import Enum

class InstrumentType(Enum):
    """音色類型枚舉"""
    PIANO = "piano"
    VIOLIN = "violin"
    GUITAR = "guitar"
    DRUMS = "drums"
    FLUTE = "flute"
    TRUMPET = "trumpet"
    BASS = "bass"
    ORGAN = "organ"
    SAXOPHONE = "saxophone"
    SYNTHESIZER = "synth"

class AudioEngine:
    """PyTune 音訊引擎 - 支援音色功能"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.current_tempo = 120
        self.current_volume = 0.8
        self.current_instrument = InstrumentType.PIANO
        self.variables = {}
        self.functions = {}
        
        # 初始化 pygame 音訊系統
        try:
            pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            print("🎵 音訊系統初始化完成")
        except Exception as e:
            print(f"⚠️  pygame 初始化警告: {e}")
        
        # 音符頻率映射
        self.note_frequencies = {
            'C': [65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.01],
            'C#': [69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            'Db': [69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            'D': [73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32, 4698.64],
            'D#': [77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            'Eb': [77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            'E': [82.41, 164.81, 329.63, 659.26, 1318.51, 2637.02, 5274.04],
            'F': [87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83, 5587.65],
            'F#': [92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            'Gb': [92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            'G': [98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96, 6271.93],
            'G#': [103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            'Ab': [103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            'A': [110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00, 7040.00],
            'A#': [116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            'Bb': [116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            'B': [123.47, 246.94, 493.88, 987.77, 1975.53, 3951.07, 7902.13]
        }
        
        # 音色配置
        self.instrument_configs = {
            InstrumentType.PIANO: {'wave': 'complex', 'attack': 0.01, 'decay': 0.3, 'sustain': 0.4, 'release': 1.2},
            InstrumentType.VIOLIN: {'wave': 'sawtooth', 'attack': 0.1, 'decay': 0.1, 'sustain': 0.8, 'release': 0.4},
            InstrumentType.GUITAR: {'wave': 'plucked', 'attack': 0.01, 'decay': 0.2, 'sustain': 0.6, 'release': 1.5},
            InstrumentType.DRUMS: {'wave': 'noise', 'attack': 0.001, 'decay': 0.05, 'sustain': 0.0, 'release': 0.1},
            InstrumentType.FLUTE: {'wave': 'sine', 'attack': 0.1, 'decay': 0.1, 'sustain': 0.9, 'release': 0.3},
            InstrumentType.TRUMPET: {'wave': 'brass', 'attack': 0.05, 'decay': 0.1, 'sustain': 0.8, 'release': 0.2},
            InstrumentType.BASS: {'wave': 'square_soft', 'attack': 0.02, 'decay': 0.1, 'sustain': 0.7, 'release': 0.5},
            InstrumentType.ORGAN: {'wave': 'organ', 'attack': 0.0, 'decay': 0.0, 'sustain': 1.0, 'release': 0.1},
            InstrumentType.SAXOPHONE: {'wave': 'reed', 'attack': 0.08, 'decay': 0.2, 'sustain': 0.7, 'release': 0.4},
            InstrumentType.SYNTHESIZER: {'wave': 'square', 'attack': 0.01, 'decay': 0.2, 'sustain': 0.6, 'release': 0.8}
        }
    
    def execute(self, ast: dict):
        """執行 AST"""
        if ast.get('type') == 'program':
            body = ast.get('body', [])
            for statement in body:
                self._execute_node(statement)
    
    def _execute_node(self, node: dict):
        """執行單個 AST 節點"""
        if not isinstance(node, dict):
            return
        
        node_type = node.get('type')
        
        if node_type == 'tempo':
            bpm = self._get_value(node.get('bpm', {}), 120)
            self.current_tempo = bpm
            print(f"🎵 設定速度: {bpm} BPM")
        
        elif node_type == 'volume':
            volume = self._get_value(node.get('volume', {}), 0.8)
            self.current_volume = max(0.0, min(1.0, volume))
            print(f"🔊 設定音量: {self.current_volume}")
        
        elif node_type == 'instrument':
            instrument_info = node.get('instrument', {})
            instrument_name = instrument_info.get('value', 'piano')
            self.set_instrument(instrument_name)
        
        elif node_type == 'note':
            self._execute_note(node)
        
        elif node_type == 'chord':
            self._execute_chord(node)
        
        elif node_type == 'loop':
            self._execute_loop(node)
        
        elif node_type == 'while':
            self._execute_while(node)
        
        elif node_type == 'for':
            self._execute_for(node)
        
        elif node_type == 'if':
            self._execute_if(node)
        
        elif node_type == 'function_def':
            self._execute_function_def(node)
        
        elif node_type == 'function_call':
            self._execute_function_call(node)
        
        elif node_type == 'ref_call':
            self._execute_ref_call(node)
        
        elif node_type == 'assign':
            self._execute_assignment(node)
    
    def set_instrument(self, instrument_name: str):
        """設定當前音色"""
        try:
            instrument = InstrumentType(instrument_name.lower())
            self.current_instrument = instrument
            print(f"🎼 切換音色為: {instrument.value}")
        except ValueError:
            available = [inst.value for inst in InstrumentType]
            print(f"❌ 未知音色: {instrument_name}")
            print(f"🎼 可用音色: {', '.join(available)}")
    
    def _execute_note(self, node: dict):
        """執行音符語句"""
        note_value_info = node.get('note_value', {})
        duration_info = node.get('duration')
        
        duration = self._get_value(duration_info, 1.0)
        
        # 檢查是單個音符還是音符陣列
        if note_value_info.get('type') == 'note_array':
            notes = note_value_info.get('notes', [])
            for note_data in notes:
                note_value = self._get_value(note_data, 'C4')
                self.play_note(note_value, duration)
        else:
            note_value = self._get_value(note_value_info, 'C4')
            self.play_note(note_value, duration)
    
    def _execute_chord(self, node: dict):
        """執行和弦語句"""
        chord_info = node.get('chord', {})
        duration_info = node.get('duration')
        
        duration = self._get_value(duration_info, 1.0)
        notes = chord_info.get('notes', [])
        
        note_values = []
        for note_data in notes:
            note_value = self._get_value(note_data, 'C4')
            note_values.append(note_value)
        
        self.play_chord(note_values, duration)
    
    def _execute_ref_call(self, node: dict):
        """執行 ref 函式呼叫"""
        name_node = node.get('name', {})
        args = node.get('args', [])
        
        func_name = name_node.get('name', '') if isinstance(name_node, dict) else str(name_node)
        
        if func_name == 'refVolume':
            if args:
                volume = self._get_value(args[0], 0.8)
                self.current_volume = max(0.0, min(1.0, volume))
                print(f"🔊 refVolume: {self.current_volume}")
        
        elif func_name == 'refTempo':
            if args:
                tempo = self._get_value(args[0], 120)
                self.current_tempo = tempo
                print(f"🎵 refTempo: {tempo} BPM")
        
        elif func_name == 'refInstrument':
            if args:
                instrument_name = self._get_value(args[0], 'piano')
                # 移除引號如果存在
                if isinstance(instrument_name, str) and instrument_name.startswith('"') and instrument_name.endswith('"'):
                    instrument_name = instrument_name[1:-1]
                self.set_instrument(instrument_name)
    
    def play_note(self, note: str, duration: float):
        """播放音符"""
        frequency = self._note_to_frequency(note)
        if frequency:
            print(f"♪ 播放音符 ({self.current_instrument.value}): {note}, 時長: {duration}s")
            wave_data = self._generate_wave(frequency, duration)
            self._play_wave(wave_data)
    
    def play_chord(self, notes: List[str], duration: float):
        """播放和弦"""
        print(f"♫ 播放和弦 ({self.current_instrument.value}): {notes}, 時長: {duration}s")
        
        # 生成每個音符的波形並混合
        mixed_wave = None
        for note in notes:
            frequency = self._note_to_frequency(note)
            if frequency:
                wave = self._generate_wave(frequency, duration)
                if mixed_wave is None:
                    mixed_wave = wave
                else:
                    mixed_wave += wave
        
        if mixed_wave is not None:
            # 標準化音量
            mixed_wave = mixed_wave / len(notes)
            self._play_wave(mixed_wave)
    
    def _generate_wave(self, frequency: float, duration: float) -> np.ndarray:
        """根據當前音色生成波形"""
        config = self.instrument_configs[self.current_instrument]
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 根據音色類型生成不同的波形
        wave_type = config['wave']
        
        if wave_type == 'complex':  # 鋼琴
            wave = np.sin(2 * np.pi * frequency * t)
            wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
            wave += 0.25 * np.sin(2 * np.pi * frequency * 3 * t)
            wave += 0.125 * np.sin(2 * np.pi * frequency * 4 * t)
        
        elif wave_type == 'sawtooth':  # 小提琴
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            # 添加輕微的弓弦噪音
            if samples > 0:
                bow_noise = 0.02 * np.random.normal(0, 1, samples)
                wave += bow_noise
        
        elif wave_type == 'plucked':  # 吉他
            sine_wave = np.sin(2 * np.pi * frequency * t)
            decay = np.exp(-t * 3)  # 快速衰減
            wave = sine_wave * decay
            # 添加撥弦的初始噪音
            if samples > 100:
                pluck_noise = np.random.normal(0, 0.1, 100)
                wave[:100] += pluck_noise
        
        elif wave_type == 'noise':  # 鼓
            if frequency < 100:  # 底鼓
                sine_part = np.sin(2 * np.pi * frequency * t)
                noise_part = np.random.normal(0, 0.5, samples)
                wave = sine_part * 0.6 + noise_part * 0.4
            elif frequency < 200:  # 小鼓
                noise = np.random.normal(0, 1, samples)
                tone = np.sin(2 * np.pi * frequency * t)
                wave = noise * 0.8 + tone * 0.2
            else:  # 踩鈸/嗵鼓
                metallic = np.sin(2 * np.pi * frequency * t) + 0.5 * np.sin(2 * np.pi * frequency * 1.6 * t)
                noise = np.random.normal(0, 0.4, samples)
                wave = metallic * 0.5 + noise * 0.5
        
        elif wave_type == 'sine':  # 長笛
            wave = np.sin(2 * np.pi * frequency * t)
            # 添加輕微的氣息效果
            breath_noise = 0.01 * np.random.normal(0, 1, samples)
            wave += breath_noise
        
        elif wave_type == 'brass':  # 小號
            wave = np.sin(2 * np.pi * frequency * t)
            wave += 0.6 * np.sin(2 * np.pi * frequency * 2 * t)
            wave += 0.4 * np.sin(2 * np.pi * frequency * 3 * t)
            wave += 0.2 * np.sin(2 * np.pi * frequency * 4 * t)
        
        elif wave_type == 'square_soft':  # 貝斯
            square = np.sign(np.sin(2 * np.pi * frequency * t))
            # 軟化邊緣
            wave = square * 0.8
        
        elif wave_type == 'organ':  # 管風琴
            wave = np.sin(2 * np.pi * frequency * t)
            wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
            wave += 0.8 * np.sin(2 * np.pi * frequency * 3 * t)
            wave += 0.3 * np.sin(2 * np.pi * frequency * 4 * t)
            wave += 0.6 * np.sin(2 * np.pi * frequency * 5 * t)
        
        elif wave_type == 'reed':  # 薩克斯風
            wave = np.sin(2 * np.pi * frequency * t)
            wave += 0.7 * np.sin(2 * np.pi * frequency * 2 * t)
            wave += 0.5 * np.sin(2 * np.pi * frequency * 3 * t)
            # 添加簧片振動效果
            vibrato = 1 + 0.05 * np.sin(2 * np.pi * 6 * t)
            wave = wave * vibrato
        
        else:  # square (合成器)
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # 應用包絡線
        envelope = self._generate_envelope(samples, config)
        wave = wave * envelope * self.current_volume
        
        return wave
    
    def _generate_envelope(self, samples: int, config: dict) -> np.ndarray:
        """生成音量包絡線"""
        envelope = np.ones(samples)
        
        attack_samples = int(config['attack'] * self.sample_rate)
        decay_samples = int(config['decay'] * self.sample_rate)
        release_samples = int(config['release'] * self.sample_rate)
        
        # Attack
        if attack_samples > 0 and attack_samples < samples:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0 and (attack_samples + decay_samples) < samples:
            decay_end = attack_samples + decay_samples
            envelope[attack_samples:decay_end] = np.linspace(1, config['sustain'], decay_samples)
        
        # Sustain
        sustain_start = attack_samples + decay_samples
        sustain_end = max(sustain_start, samples - release_samples)
        if sustain_start < samples:
            envelope[sustain_start:sustain_end] = config['sustain']
        
        # Release
        if release_samples > 0 and sustain_end < samples:
            envelope[sustain_end:] = np.linspace(config['sustain'], 0, 
                                               min(release_samples, samples - sustain_end))
        
        return envelope
    
    def _play_wave(self, wave_data: np.ndarray):
        """播放波形數據"""
        try:
            # 確保數據在有效範圍內
            wave_data = np.clip(wave_data, -1, 1)
            wave_data = (wave_data * 32767).astype(np.int16)
            
            # 立體聲
            if len(wave_data) > 0:
                stereo_wave = np.column_stack((wave_data, wave_data))
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                
                # 等待播放完成
                wait_time = int(len(wave_data) / self.sample_rate * 1000)
                pygame.time.wait(wait_time)
        except Exception as e:
            print(f"⚠️  音訊播放警告: {e}")
    
    def _note_to_frequency(self, note: str) -> Optional[float]:
        """將音符轉換為頻率"""
        if len(note) < 2:
            return 440.0  # 預設 A4
        
        # 解析音符名稱和八度
        if '#' in note or 'b' in note:
            note_name = note[:-1].upper()
            octave_str = note[-1]
        else:
            note_name = note[:-1].upper()
            octave_str = note[-1]
        
        try:
            octave = int(octave_str)
            if note_name in self.note_frequencies and 2 <= octave <= 8:
                octave_index = octave - 2  # 調整到陣列索引
                if octave_index < len(self.note_frequencies[note_name]):
                    return self.note_frequencies[note_name][octave_index]
        except (ValueError, IndexError):
            pass
        
        return 440.0  # 預設頻率 A4
    
    # 控制流執行方法
    def _execute_loop(self, node: dict):
        count = self._get_value(node.get('count', {}), 1)
        body = node.get('body', [])
        
        print(f"🔄 loop 迴圈開始，重複 {count} 次")
        for i in range(int(count)):
            print(f"   第 {i+1}/{count} 次迴圈")
            for stmt in body:
                self._execute_node(stmt)
        print("🔄 loop 迴圈結束")
    
    def _execute_while(self, node: dict):
        condition = node.get('condition', {})
        body = node.get('body', [])
        
        print("🔄 while 迴圈開始")
        loop_count = 0
        max_iterations = 1000
        
        while self._evaluate_condition(condition) and loop_count < max_iterations:
            loop_count += 1
            print(f"   第 {loop_count} 次迴圈")
            for stmt in body:
                self._execute_node(stmt)
        
        if loop_count >= max_iterations:
            print("⚠️  迴圈達到最大次數限制，自動終止")
        
        print("🔄 while 迴圈結束")
    
    def _execute_for(self, node: dict):
        variable = node.get('variable', {})
        range_expr = node.get('range', {})
        body = node.get('body', [])
        
        var_name = self._get_name(variable)
        start_val = int(self._get_value(range_expr.get('start', {}), 0))
        end_val = int(self._get_value(range_expr.get('end', {}), 0))
        
        print(f"🔄 for 迴圈開始 ({var_name}: {start_val} 到 {end_val})")
        
        for i in range(start_val, end_val):
            self.variables[var_name] = i
            print(f"   第 {i+1}/{end_val-start_val} 次，{var_name} = {i}")
            
            for stmt in body:
                self._execute_node(stmt)
        
        print("🔄 for 迴圈結束")
    
    def _execute_if(self, node: dict):
        condition = node.get('condition', {})
        then_body = node.get('then_body', [])
        elseif_clauses = node.get('elseif_clauses', [])
        else_body = node.get('else_body', [])
        
        if self._evaluate_condition(condition):
            print("🔀 執行 if 分支")
            for stmt in then_body:
                self._execute_node(stmt)
        else:
            # 檢查 elseif 條件
            executed = False
            for elseif_clause in elseif_clauses:
                elseif_condition = elseif_clause.get('condition', {})
                if self._evaluate_condition(elseif_condition):
                    print("🔀 執行 elseif 分支")
                    elseif_body = elseif_clause.get('body', [])
                    for stmt in elseif_body:
                        self._execute_node(stmt)
                    executed = True
                    break
            
            # 如果沒有 elseif 執行，執行 else
            if not executed and else_body:
                print("🔀 執行 else 分支")
                for stmt in else_body:
                    self._execute_node(stmt)
    
    def _execute_function_def(self, node: dict):
        name = self._get_name(node.get('name', {}))
        params = node.get('params', [])
        body = node.get('body', [])
        
        param_names = [self._get_name(param) for param in params]
        self.functions[name] = {
            'params': param_names,
            'body': body
        }
        print(f"📝 定義函式: {name}({', '.join(param_names)})")
    
    def _execute_function_call(self, node: dict):
        name = self._get_name(node.get('name', {}))
        args = node.get('args', [])
        
        if name in self.functions:
            func = self.functions[name]
            param_names = func['params']
            body = func['body']
            
            # 保存當前變數狀態
            old_vars = self.variables.copy()
            
            # 設定參數值
            for i, param_name in enumerate(param_names):
                if i < len(args):
                    arg_value = self._get_value(args[i], None)
                    self.variables[param_name] = arg_value
            
            print(f"🔧 執行函式: {name}")
            
            # 執行函式體
            for stmt in body:
                self._execute_node(stmt)
            
            # 恢復變數狀態
            self.variables = old_vars
        else:
            print(f"❌ 未找到函式: {name}")
    
    def _execute_assignment(self, node: dict):
        var_name = self._get_name(node.get('var', {}))
        value = self._get_value(node.get('value', {}), 0)
        
        self.variables[var_name] = value
        print(f"📝 賦值: {var_name} = {value}")
    
    def _get_value(self, node: dict, default=None):
        """獲取節點的值"""
        if not isinstance(node, dict):
            return default
        
        node_type = node.get('type')
        
        if node_type == 'number':
            return node.get('value', default)
        elif node_type == 'identifier':
            var_name = node.get('name', '')
            return self.variables.get(var_name, default)
        elif node_type == 'note_literal':
            return node.get('value', default)
        elif node_type == 'binop':
            left = self._get_value(node.get('left', {}), 0)
            right = self._get_value(node.get('right', {}), 0)
            op = node.get('op', '+')
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right if right != 0 else 0
            elif op == '%':
                return left % right if right != 0 else 0
        elif node_type == 'string_literal':
            # 處理字符串字面值（移除引號）
            value = node.get('value', default)
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                return value[1:-1]
            return value
        
        return default
    
    def _get_name(self, node: dict):
        """獲取標識符的名稱"""
        if isinstance(node, dict):
            return node.get('name', '')
        return str(node)
    
    def _evaluate_condition(self, condition: dict) -> bool:
        """評估條件表達式"""
        if not isinstance(condition, dict):
            return False
        
        condition_type = condition.get('type')
        
        if condition_type == 'comparison':
            left = self._get_value(condition.get('left', {}), 0)
            right = self._get_value(condition.get('right', {}), 0)
            op = condition.get('op', '==')
            
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
        
        elif condition_type == 'logical_op':
            left = self._evaluate_condition(condition.get('left', {}))
            right = self._evaluate_condition(condition.get('right', {}))
            op = condition.get('op', 'and')
            
            if op == 'and':
                return left and right
            elif op == 'or':
                return left or right
        
        elif condition_type == 'unary_op':
            operand = self._evaluate_condition(condition.get('operand', {}))
            op = condition.get('op', 'not')
            
            if op == 'not':
                return not operand
        
        elif condition_type == 'number':
            return condition.get('value', 0) != 0
        
        elif condition_type == 'identifier':
            var_name = condition.get('name', '')
            return self.variables.get(var_name, 0) != 0
        
        return False
    
    def cleanup(self):
        """清理資源"""
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass

# 測試函式
def test_audio_engine():
    """測試音訊引擎"""
    print("🎵 測試 PyTune 音訊引擎")
    
    engine = AudioEngine()
    
    # 測試基本功能
    print("\n📝 測試基本音符播放")
    engine.play_note("C4", 0.5)
    engine.play_note("E4", 0.5)
    engine.play_note("G4", 0.5)
    
    # 測試音色切換
    print("\n🎼 測試音色切換")
    engine.set_instrument("violin")
    engine.play_note("C5", 1.0)
    
    engine.set_instrument("guitar")
    engine.play_chord(["C4", "E4", "G4"], 1.0)
    
    engine.set_instrument("drums")
    engine.play_note("C2", 0.5)  # 底鼓
    engine.play_note("D3", 0.5)  # 小鼓
    
    engine.cleanup()
    print("✅ 測試完成")

if __name__ == "__main__":
    test_audio_engine()