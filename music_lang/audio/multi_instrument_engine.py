#!/usr/bin/env python3
"""
multi_instrument_engine.py - 支援多樂器的音訊引擎
"""

import pygame
import numpy as np
import threading
import time
from collections import defaultdict
import math

class InstrumentSynthesizer:
    """樂器合成器 - 為不同樂器生成不同音色"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # 樂器音色配置
        self.instrument_configs = {
            'piano': {
                'waveform': 'complex_piano',
                'attack': 0.01,
                'decay': 0.3,
                'sustain': 0.7,
                'release': 0.5,
                'harmonics': [1.0, 0.3, 0.1, 0.05, 0.02]
            },
            'violin': {
                'waveform': 'sawtooth',
                'attack': 0.1,
                'decay': 0.2,
                'sustain': 0.8,
                'release': 0.3,
                'harmonics': [1.0, 0.5, 0.3, 0.2, 0.1],
                'vibrato': {'rate': 5, 'depth': 0.02}
            },
            'guitar': {
                'waveform': 'plucked',
                'attack': 0.01,
                'decay': 0.8,
                'sustain': 0.3,
                'release': 1.0,
                'harmonics': [1.0, 0.4, 0.2, 0.1, 0.05]
            },
            'drums': {
                'waveform': 'noise',
                'attack': 0.001,
                'decay': 0.1,
                'sustain': 0.0,
                'release': 0.2,
                'pitch_envelope': True
            },
            'flute': {
                'waveform': 'sine',
                'attack': 0.05,
                'decay': 0.1,
                'sustain': 0.9,
                'release': 0.2,
                'harmonics': [1.0, 0.1, 0.02, 0.01],
                'breath': {'noise': 0.05}
            },
            'trumpet': {
                'waveform': 'brass',
                'attack': 0.05,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.2,
                'harmonics': [1.0, 0.8, 0.6, 0.4, 0.2, 0.1]
            },
            'saxophone': {
                'waveform': 'reed',
                'attack': 0.08,
                'decay': 0.2,
                'sustain': 0.8,
                'release': 0.3,
                'harmonics': [1.0, 0.6, 0.4, 0.3, 0.2]
            },
            'cello': {
                'waveform': 'sawtooth',
                'attack': 0.15,
                'decay': 0.3,
                'sustain': 0.8,
                'release': 0.4,
                'harmonics': [1.0, 0.7, 0.5, 0.3, 0.2],
                'vibrato': {'rate': 4, 'depth': 0.03}
            },
            'bass': {
                'waveform': 'sine_rich',
                'attack': 0.02,
                'decay': 0.4,
                'sustain': 0.6,
                'release': 0.8,
                'harmonics': [1.0, 0.8, 0.3, 0.1, 0.05]
            },
            'organ': {
                'waveform': 'organ',
                'attack': 0.01,
                'decay': 0.0,
                'sustain': 1.0,
                'release': 0.1,
                'harmonics': [1.0, 0.5, 1.0, 0.3, 0.8, 0.2, 0.6]
            }
        }
    
    def note_to_frequency(self, note):
        """將音符轉換為頻率"""
        note_frequencies = {
            'C': 261.63, 'C#': 277.18, 'Db': 277.18,
            'D': 293.66, 'D#': 311.13, 'Eb': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'Gb': 369.99,
            'G': 392.00, 'G#': 415.30, 'Ab': 415.30,
            'A': 440.00, 'A#': 466.16, 'Bb': 466.16,
            'B': 493.88
        }
        
        if len(note) < 2:
            return 440.0
            
        note_name = note[:-1]
        octave = int(note[-1])
        
        base_freq = note_frequencies.get(note_name, 440.0)
        return base_freq * (2 ** (octave - 4))
    
    def generate_waveform(self, frequency, duration, instrument):
        """根據樂器類型生成波形"""
        config = self.instrument_configs.get(instrument, self.instrument_configs['piano'])
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 生成基礎波形
        if config['waveform'] == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif config['waveform'] == 'sawtooth':
            wave = 2 * (t * frequency % 1) - 1
        elif config['waveform'] == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif config['waveform'] == 'triangle':
            wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif config['waveform'] == 'complex_piano':
            wave = self._generate_piano_wave(frequency, t)
        elif config['waveform'] == 'plucked':
            wave = self._generate_plucked_wave(frequency, t)
        elif config['waveform'] == 'noise':
            wave = self._generate_drum_wave(frequency, t)
        elif config['waveform'] == 'brass':
            wave = self._generate_brass_wave(frequency, t)
        elif config['waveform'] == 'reed':
            wave = self._generate_reed_wave(frequency, t)
        elif config['waveform'] == 'sine_rich':
            wave = self._generate_rich_sine_wave(frequency, t)
        elif config['waveform'] == 'organ':
            wave = self._generate_organ_wave(frequency, t)
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        # 添加泛音
        if 'harmonics' in config:
            for i, amplitude in enumerate(config['harmonics'][1:], 2):
                if amplitude > 0:
                    harmonic = amplitude * np.sin(2 * np.pi * frequency * i * t)
                    wave += harmonic
        
        # 添加顫音 (vibrato)
        if 'vibrato' in config:
            vibrato_rate = config['vibrato']['rate']
            vibrato_depth = config['vibrato']['depth']
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
            wave *= vibrato
        
        # 添加氣息噪音 (用於管樂器)
        if 'breath' in config:
            noise_level = config['breath']['noise']
            breath_noise = noise_level * np.random.normal(0, 0.1, len(t))
            wave += breath_noise
        
        # 應用包絡
        envelope = self._create_envelope(samples, config)
        wave *= envelope
        
        return wave
    
    def _generate_piano_wave(self, frequency, t):
        """生成鋼琴音色"""
        # 基礎正弦波 + 輕微的方波成分
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.05 * np.sin(2 * np.pi * frequency * 3 * t)
        # 添加輕微的金屬感
        wave += 0.02 * np.sin(2 * np.pi * frequency * 7 * t)
        return wave
    
    def _generate_plucked_wave(self, frequency, t):
        """生成撥弦音色 (吉他)"""
        # 鋸齒波基礎 + 指數衰減
        wave = 2 * (t * frequency % 1) - 1
        # 模擬弦的振動衰減
        decay = np.exp(-t * 3)
        return wave * decay
    
    def _generate_drum_wave(self, frequency, t):
        """生成鼓聲"""
        # 主要是噪音 + 低頻震盪
        noise = np.random.normal(0, 1, len(t))
        # 添加低頻成分
        low_freq = np.sin(2 * np.pi * (frequency * 0.5) * t)
        # 快速衰減
        decay = np.exp(-t * 8)
        return (0.7 * noise + 0.3 * low_freq) * decay
    
    def _generate_brass_wave(self, frequency, t):
        """生成銅管樂器音色"""
        # 豐富的泛音結構
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.6 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.4 * np.sin(2 * np.pi * frequency * 4 * t)
        return wave
    
    def _generate_reed_wave(self, frequency, t):
        """生成簧片樂器音色 (薩克斯風)"""
        # 方波基礎 + 豐富泛音
        square_wave = np.sign(np.sin(2 * np.pi * frequency * t))
        sine_wave = np.sin(2 * np.pi * frequency * t)
        return 0.6 * square_wave + 0.4 * sine_wave
    
    def _generate_rich_sine_wave(self, frequency, t):
        """生成豐富的正弦波 (低音提琴)"""
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 0.5 * t)  # 低八度
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        return wave
    
    def _generate_organ_wave(self, frequency, t):
        """生成管風琴音色"""
        # 多個正弦波組合 (模擬管風琴的音栓)
        wave = np.sin(2 * np.pi * frequency * t)           # 基音
        wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)   # 八度
        wave += 1.0 * np.sin(2 * np.pi * frequency * 3 * t)   # 十二度
        wave += 0.3 * np.sin(2 * np.pi * frequency * 4 * t)   # 十五度
        wave += 0.8 * np.sin(2 * np.pi * frequency * 6 * t)   # 十九度
        return wave
    
    def _create_envelope(self, samples, config):
        """創建包絡 (ADSR)"""
        attack_samples = int(samples * config['attack'])
        decay_samples = int(samples * config['decay'])
        release_samples = int(samples * config['release'])
        sustain_samples = samples - attack_samples - decay_samples - release_samples
        
        envelope = np.ones(samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            envelope[start_idx:end_idx] = np.linspace(1, config['sustain'], decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            start_idx = attack_samples + decay_samples
            end_idx = start_idx + sustain_samples
            envelope[start_idx:end_idx] = config['sustain']
        
        # Release
        if release_samples > 0:
            start_idx = samples - release_samples
            envelope[start_idx:] = np.linspace(config['sustain'], 0, release_samples)
        
        return envelope

class MultiInstrumentAudioEngine:
    """多樂器音訊引擎"""
    
    def __init__(self):
        # 初始化 pygame mixer
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        self.synthesizer = InstrumentSynthesizer()
        
        # 音樂狀態
        self.current_tempo = 120  # BPM
        self.current_volume = 0.8
        self.current_instrument = 'piano'
        
        # 多軌道支援
        self.tracks = defaultdict(list)  # {instrument: [sounds]}
        self.active_sounds = []
        
        # 變數存儲
        self.variables = {}
        
        print("🎵 多樂器音訊引擎初始化完成")
        print(f"📀 支援樂器: {', '.join(self.synthesizer.instrument_configs.keys())}")
    
    def _execute_node(self, node):
        """執行 AST 節點"""
        if not isinstance(node, dict):
            return
        
        node_type = node.get('type', '')
        
        if node_type == 'tempo':
            bpm = self._get_value(node.get('bpm', {}), 120)
            self.current_tempo = bpm
            print(f"🎼 設定速度: {bpm} BPM")
        
        elif node_type == 'volume':
            volume = self._get_value(node.get('volume', {}), 0.8)
            self.current_volume = max(0.0, min(1.0, volume))
            print(f"🔊 設定音量: {self.current_volume:.1f}")
        
        elif node_type == 'instrument':
            instrument_node = node.get('instrument', {})
            instrument_name = instrument_node.get('name', 'piano')
            self.current_instrument = instrument_name
            print(f"🎹 切換樂器: {instrument_name}")
        
        elif node_type == 'note':
            self._play_note(node)
        
        elif node_type == 'chord':
            self._play_chord(node)
        
        elif node_type == 'loop':
            count = int(self._get_value(node.get('count', {}), 1))
            body = node.get('body', [])
            
            print(f"🔄 迴圈 {count} 次")
            for i in range(count):
                print(f"   第 {i+1}/{count} 次迴圈")
                for stmt in body:
                    self._execute_node(stmt)
        
        elif node_type == 'while':
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
        
        elif node_type == 'for':
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
        
        elif node_type == 'if':
            condition = node.get('condition', {})
            then_body = node.get('then_body', [])
            elseif_clauses = node.get('elseif_clauses', [])
            else_body = node.get('else_body', [])
            
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
                        for stmt in elseif_clause.get('body', []):
                            self._execute_node(stmt)
                        executed = True
                        break
                
                # 如果沒有 elseif 條件成立，執行 else
                if not executed and else_body:
                    print("✅ 執行 else 分支")
                    for stmt in else_body:
                        self._execute_node(stmt)
        
        elif node_type == 'assign':
            var_node = node.get('var', {})
            value_node = node.get('value', {})
            
            var_name = self._get_name(var_node)
            value = self._get_value(value_node, 0)
            
            self.variables[var_name] = value
            print(f"📝 設定變數: {var_name} = {value}")
        
        elif node_type == 'function_def':
            name_node = node.get('name', {})
            func_name = self._get_name(name_node)
            params = node.get('params', [])
            body = node.get('body', [])
            
            self.variables[func_name] = {
                'type': 'function',
                'params': params,
                'body': body
            }
            print(f"📋 定義函式: {func_name}")
        
        elif node_type == 'function_call':
            name_node = node.get('name', {})
            func_name = self._get_name(name_node)
            args = node.get('args', [])
            
            if func_name in self.variables:
                func_def = self.variables[func_name]
                if isinstance(func_def, dict) and func_def.get('type') == 'function':
                    print(f"🎯 呼叫函式: {func_name}")
                    # 簡化的函式執行
                    for stmt in func_def.get('body', []):
                        self._execute_node(stmt)
        
        elif node_type == 'ref_call':
            name_node = node.get('name', {})
            func_name = self._get_name(name_node)
            args = node.get('args', [])
            
            print(f"🔧 呼叫 ref 函式: {func_name}")
            
            if func_name == 'refVolume':
                if args:
                    volume = self._get_value(args[0], 0.8)
                    self.current_volume = max(0.0, min(1.0, volume))
                    print(f"🔊 ref設定音量: {self.current_volume:.1f}")
            
            elif func_name == 'refTempo':
                if args:
                    tempo = self._get_value(args[0], 120)
                    self.current_tempo = tempo
                    print(f"🎼 ref設定速度: {tempo} BPM")
            
            elif func_name == 'refInst':
                if args:
                    instrument = self._get_name(args[0])
                    self.current_instrument = instrument
                    print(f"🎹 ref設定樂器: {instrument}")
    
    def _play_note(self, node):
        """播放音符或音符陣列"""
        note_value = node.get('note_value', {})
        duration_node = node.get('duration')
        
        # 計算持續時間
        if duration_node:
            duration = self._get_value(duration_node, 1.0)
        else:
            duration = 60.0 / self.current_tempo  # 預設一拍
        
        # 處理音符值
        if note_value.get('type') == 'note_array':
            # 音符陣列 - 依序播放
            notes = note_value.get('notes', [])
            print(f"🎵 播放音符陣列 ({self.current_instrument}): ", end='')
            for note in notes:
                note_str = self._get_note_string(note)
                print(f"{note_str} ", end='')
                self._play_single_note(note_str, duration)
            print()
        else:
            # 單個音符
            note_str = self._get_note_string(note_value)
            print(f"♪ 播放音符 ({self.current_instrument}): {note_str}, 時長: {duration:.1f}s")
            self._play_single_note(note_str, duration)
    
    def _play_chord(self, node):
        """播放和弦"""
        chord_node = node.get('chord', {})
        duration_node = node.get('duration')
        
        if duration_node:
            duration = self._get_value(duration_node, 2.0)
        else:
            duration = 60.0 / self.current_tempo * 2  # 預設兩拍
        
        notes = chord_node.get('notes', [])
        chord_notes = [self._get_note_string(note) for note in notes]
        
        print(f"🎹 播放和弦 ({self.current_instrument}): [{', '.join(chord_notes)}], 時長: {duration:.1f}s")
        
        # 同時播放所有音符
        threads = []
        for note_str in chord_notes:
            thread = threading.Thread(target=self._play_single_note, args=(note_str, duration))
            threads.append(thread)
            thread.start()
        
        # 等待所有音符播放完成
        for thread in threads:
            thread.join()
    
    def _play_single_note(self, note_str, duration):
        """播放單個音符"""
        try:
            # 生成波形
            wave = self.synthesizer.generate_waveform(
                self.synthesizer.note_to_frequency(note_str),
                duration,
                self.current_instrument
            )
            
            # 應用音量
            wave = wave * self.current_volume
            
            # 確保音量在合理範圍內
            wave = np.clip(wave, -1.0, 1.0)
            
            # 轉換為 pygame 可用的格式
            wave_int = (wave * 32767).astype(np.int16)
            
            # 如果是立體聲，複製到兩個聲道
            if pygame.mixer.get_init()[3] == 2:
                stereo_wave = np.array([wave_int, wave_int]).T
                sound = pygame.sndarray.make_sound(stereo_wave)
            else:
                sound = pygame.sndarray.make_sound(wave_int)
            
            # 播放音效
            channel = sound.play()
            
            # 記錄到對應軌道
            self.tracks[self.current_instrument].append({
                'note': note_str,
                'duration': duration,
                'timestamp': time.time()
            })
            
            # 等待播放完成
            time.sleep(duration)
            
        except Exception as e:
            print(f"❌ 播放音符時發生錯誤: {e}")
    
    def _get_note_string(self, note_node):
        """從節點獲取音符字符串"""
        if isinstance(note_node, dict):
            return note_node.get('value', 'C4')
        else:
            return str(note_node)
    
    def _get_value(self, node, default=0):
        """從節點獲取數值"""
        if not isinstance(node, dict):
            return default
        
        node_type = node.get('type', '')
        
        if node_type == 'number':
            return node.get('value', default)
        elif node_type == 'identifier':
            var_name = node.get('name', '')
            return self.variables.get(var_name, default)
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
                return left / right if right != 0 else left
        
        return default
    
    def _get_name(self, node):
        """從節點獲取名稱"""
        if isinstance(node, dict):
            return node.get('name', '')
        else:
            return str(node)
    
    def _evaluate_condition(self, condition):
        """評估條件表達式"""
        if not isinstance(condition, dict):
            return False
        
        cond_type = condition.get('type', '')
        
        if cond_type == 'comparison':
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
        
        elif cond_type == 'logical_op':
            left_result = self._evaluate_condition(condition.get('left', {}))
            right_result = self._evaluate_condition(condition.get('right', {}))
            op = condition.get('op', 'and')
            
            if op == 'and':
                return left_result and right_result
            elif op == 'or':
                return left_result or right_result
        
        elif cond_type == 'unary_op':
            operand_result = self._evaluate_condition(condition.get('operand', {}))
            op = condition.get('op', 'not')
            
            if op == 'not':
                return not operand_result
        
        elif cond_type == 'number':
            return condition.get('value', 0) != 0
        
        elif cond_type == 'identifier':
            var_name = condition.get('name', '')
            return self.variables.get(var_name, 0) != 0
        
        return False
    
    def execute(self, ast):
        """執行 AST"""
        if not isinstance(ast, dict):
            print("❌ 無效的 AST")
            return
        
        program_body = ast.get('body', [])
        
        print("🎵 開始執行音樂程式...")
        print(f"📊 程式包含 {len(program_body)} 個語句")
        
        for i, stmt in enumerate(program_body, 1):
            print(f"\n--- 執行語句 {i}/{len(program_body)} ---")
            self._execute_node(stmt)
        
        print("\n🎵 音樂程式執行完成！")
        self._show_track_summary()
    
    def _show_track_summary(self):
        """顯示軌道摘要"""
        if not self.tracks:
            return
        
        print("\n📊 演奏摘要:")
        for instrument, notes in self.tracks.items():
            print(f"  🎹 {instrument}: {len(notes)} 個音符")
        
        total_notes = sum(len(notes) for notes in self.tracks.values())
        print(f"  🎵 總計: {total_notes} 個音符")
    
    def stop(self):
        """停止所有播放"""
        pygame.mixer.stop()
        print("⏹️  停止播放")
    
    def get_supported_instruments(self):
        """獲取支援的樂器列表"""
        return list(self.synthesizer.instrument_configs.keys())

# 使用範例
if __name__ == "__main__":
    # 測試多樂器音訊引擎
    engine = MultiInstrumentAudioEngine()
    
    print("\n🎼 測試不同樂器...")
    
    # 測試鋼琴
    engine.current_instrument = 'piano'
    engine._play_single_note('C4', 1.0)
    
    # 測試小提琴
    engine.current_instrument = 'violin'
    engine._play_single_note('G4', 1.0)
    
    # 測試吉他
    engine.current_instrument = 'guitar'
    engine._play_single_note('E4', 1.0)
    
    # 測試鼓
    engine.current_instrument = 'drums'
    engine._play_single_note('C2', 0.5)
    
    print("🎵 測試完成！")