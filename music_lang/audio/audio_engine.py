#!/usr/bin/env python3
"""
audio_engine.py - 完整的多樂器音訊引擎 (修復版)
支援10種樂器音色、多軌道演奏、動態樂器切換
"""

import pygame
import numpy as np
import threading
import time
import math
from collections import defaultdict

class InstrumentSynthesizer:
    """樂器合成器 - 為不同樂器生成不同音色"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # 樂器音色配置 - 全面柔和化
        self.instrument_configs = {
            'piano': {
                'waveform': 'soft_piano',
                'attack': 0.08,   # 更長的起音時間
                'decay': 0.5,
                'sustain': 0.5,   # 降低持續音量
                'release': 1.0,   # 延長釋音
                'harmonics': [1.0, 0.12, 0.04, 0.015, 0.008],  # 大幅減少泛音
                'volume_scale': 0.6  # 整體音量縮放
            },
            'violin': {
                'waveform': 'soft_violin',
                'attack': 0.15,   # 更柔和的起音
                'decay': 0.3,
                'sustain': 0.65,  # 適中的持續音量
                'release': 0.4,
                'harmonics': [1.0, 0.25, 0.12, 0.06, 0.03],  # 減少尖銳泛音
                'vibrato': {'rate': 4.5, 'depth': 0.015},  # 更輕微的顫音
                'volume_scale': 0.5
            },
            'guitar': {
                'waveform': 'soft_plucked',
                'attack': 0.02,
                'decay': 1.2,     # 更長的自然衰減
                'sustain': 0.2,   # 較低的持續音量
                'release': 1.5,
                'harmonics': [1.0, 0.2, 0.08, 0.04, 0.02],
                'volume_scale': 0.4
            },
            'drums': {
                'waveform': 'soft_percussion',
                'attack': 0.002,
                'decay': 0.15,
                'sustain': 0.0,
                'release': 0.3,
                'volume_scale': 0.3  # 鼓聲音量大幅降低
            },
            'flute': {
                'waveform': 'soft_sine',
                'attack': 0.08,   # 更柔和的起音
                'decay': 0.15,
                'sustain': 0.85,
                'release': 0.3,
                'harmonics': [1.0, 0.06, 0.02, 0.008],  # 非常純淨的音色
                'breath': {'noise': 0.02},  # 減少氣息噪音
                'volume_scale': 0.45
            },
            'trumpet': {
                'waveform': 'soft_brass',
                'attack': 0.08,
                'decay': 0.2,
                'sustain': 0.7,
                'release': 0.3,
                'harmonics': [1.0, 0.4, 0.2, 0.1, 0.05, 0.025],  # 減少尖銳感
                'volume_scale': 0.5
            },
            'saxophone': {
                'waveform': 'soft_reed',
                'attack': 0.12,   # 更柔和的起音
                'decay': 0.25,
                'sustain': 0.75,
                'release': 0.4,
                'harmonics': [1.0, 0.35, 0.18, 0.08, 0.04],
                'volume_scale': 0.55
            },
            'cello': {
                'waveform': 'soft_cello',
                'attack': 0.2,    # 非常柔和的起音
                'decay': 0.4,
                'sustain': 0.75,
                'release': 0.6,
                'harmonics': [1.0, 0.4, 0.2, 0.1, 0.05],
                'vibrato': {'rate': 3.5, 'depth': 0.02},  # 溫暖的顫音
                'volume_scale': 0.6
            },
            'bass': {
                'waveform': 'soft_bass',
                'attack': 0.05,
                'decay': 0.6,
                'sustain': 0.55,
                'release': 1.0,
                'harmonics': [1.0, 0.5, 0.15, 0.05, 0.02],
                'volume_scale': 0.7  # 低音稍微響一些，但仍控制
            },
            'organ': {
                'waveform': 'soft_organ',
                'attack': 0.03,
                'decay': 0.05,
                'sustain': 0.8,
                'release': 0.2,
                'harmonics': [1.0, 0.25, 0.5, 0.15, 0.4, 0.1, 0.3],  # 柔和的管風琴音栓
                'volume_scale': 0.4
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
        
        # 生成基礎波形 - 新增柔和版本
        if config['waveform'] == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif config['waveform'] == 'soft_sine':
            wave = self._generate_soft_sine_wave(frequency, t)
        elif config['waveform'] == 'sawtooth':
            wave = 2 * (t * frequency % 1) - 1
        elif config['waveform'] == 'soft_violin':
            wave = self._generate_soft_violin_wave(frequency, t)
        elif config['waveform'] == 'soft_cello':
            wave = self._generate_soft_cello_wave(frequency, t)
        elif config['waveform'] == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif config['waveform'] == 'triangle':
            wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif config['waveform'] == 'soft_piano':
            wave = self._generate_soft_piano_wave(frequency, t)
        elif config['waveform'] == 'complex_piano':
            wave = self._generate_piano_wave(frequency, t)
        elif config['waveform'] == 'plucked':
            wave = self._generate_plucked_wave(frequency, t)
        elif config['waveform'] == 'soft_plucked':
            wave = self._generate_soft_plucked_wave(frequency, t)
        elif config['waveform'] == 'noise':
            wave = self._generate_drum_wave(frequency, t)
        elif config['waveform'] == 'soft_percussion':
            wave = self._generate_soft_percussion_wave(frequency, t)
        elif config['waveform'] == 'brass':
            wave = self._generate_brass_wave(frequency, t)
        elif config['waveform'] == 'soft_brass':
            wave = self._generate_soft_brass_wave(frequency, t)
        elif config['waveform'] == 'reed':
            wave = self._generate_reed_wave(frequency, t)
        elif config['waveform'] == 'soft_reed':
            wave = self._generate_soft_reed_wave(frequency, t)
        elif config['waveform'] == 'sine_rich':
            wave = self._generate_rich_sine_wave(frequency, t)
        elif config['waveform'] == 'soft_bass':
            wave = self._generate_soft_bass_wave(frequency, t)
        elif config['waveform'] == 'organ':
            wave = self._generate_organ_wave(frequency, t)
        elif config['waveform'] == 'soft_organ':
            wave = self._generate_soft_organ_wave(frequency, t)
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        # 添加泛音 - 使用音量縮放
        if 'harmonics' in config:
            for i, amplitude in enumerate(config['harmonics'][1:], 2):
                if amplitude > 0:
                    # 進一步降低泛音強度，避免疊加破音
                    harmonic_amplitude = amplitude * 0.3  # 大幅降低泛音
                    harmonic = harmonic_amplitude * np.sin(2 * np.pi * frequency * i * t)
                    wave += harmonic
        
        # 添加顫音 (vibrato) - 但強度降低
        if 'vibrato' in config:
            vibrato_rate = config['vibrato']['rate']
            vibrato_depth = config['vibrato']['depth'] * 0.7  # 降低顫音深度
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
            wave *= vibrato
        
        # 添加氣息噪音 (用於管樂器) - 但強度降低
        if 'breath' in config:
            noise_level = config['breath']['noise'] * 0.5  # 降低噪音
            breath_noise = noise_level * np.random.normal(0, 0.05, len(t))
            wave += breath_noise
        
        # 應用包絡
        envelope = self._create_envelope(samples, config)
        wave *= envelope
        
        # 應用樂器特定的音量縮放，防止破音
        volume_scale = config.get('volume_scale', 0.5)
        wave *= volume_scale
        
        return wave
    
    def _generate_soft_piano_wave(self, frequency, t):
        """生成柔和鋼琴音色"""
        # 主要使用正弦波，添加少量溫暖的泛音
        wave = np.sin(2 * np.pi * frequency * t)
        
        # 添加非常輕微的二次泛音（八度）
        wave += 0.08 * np.sin(2 * np.pi * frequency * 2 * t)
        
        # 添加微弱的三次泛音（十二度）
        wave += 0.03 * np.sin(2 * np.pi * frequency * 3 * t)
        
        # 添加極微弱的高頻泛音，模擬鋼琴的金屬感，但很輕微
        wave += 0.01 * np.sin(2 * np.pi * frequency * 5 * t)
        
        # 添加低頻溫暖感
        wave += 0.05 * np.sin(2 * np.pi * frequency * 0.5 * t)
        
        return wave
    
    def _generate_soft_sine_wave(self, frequency, t):
        """生成柔和正弦波 (長笛等)"""
        wave = np.sin(2 * np.pi * frequency * t)
        # 添加極輕微的二次泛音增加溫暖感
        wave += 0.03 * np.sin(2 * np.pi * frequency * 2 * t)
        return wave
    
    def _generate_soft_violin_wave(self, frequency, t):
        """生成柔和小提琴音色"""
        # 使用正弦波基礎而非鋸齒波，減少尖銳感
        wave = np.sin(2 * np.pi * frequency * t)
        # 添加溫暖的泛音
        wave += 0.15 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.08 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.04 * np.sin(2 * np.pi * frequency * 4 * t)
        return wave
    
    def _generate_soft_cello_wave(self, frequency, t):
        """生成柔和大提琴音色"""
        # 豐富但不尖銳的低音
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)
        # 添加低頻溫暖感
        wave += 0.1 * np.sin(2 * np.pi * frequency * 0.5 * t)
        return wave
    
    def _generate_soft_plucked_wave(self, frequency, t):
        """生成柔和撥弦音色 (吉他)"""
        # 使用柔和的衰減曲線
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.12 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.06 * np.sin(2 * np.pi * frequency * 3 * t)
        # 柔和的指數衰減
        decay = np.exp(-t * 1.5)
        return wave * decay
    
    def _generate_soft_percussion_wave(self, frequency, t):
        """生成柔和打擊樂音色"""
        # 減少噪音比例，增加調性
        noise = np.random.normal(0, 0.15, len(t))  # 減少噪音強度
        tone = 0.6 * np.sin(2 * np.pi * frequency * t)  # 增加調性成分
        # 更快的衰減
        decay = np.exp(-t * 12)
        return (0.4 * noise + 0.6 * tone) * decay
    
    def _generate_soft_brass_wave(self, frequency, t):
        """生成柔和銅管音色"""
        # 減少尖銳的泛音
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.08 * np.sin(2 * np.pi * frequency * 4 * t)
        return wave
    
    def _generate_soft_reed_wave(self, frequency, t):
        """生成柔和簧片音色 (薩克斯風)"""
        # 使用更多正弦波，減少方波成分
        sine_wave = np.sin(2 * np.pi * frequency * t)
        square_component = 0.2 * np.sign(np.sin(2 * np.pi * frequency * t))  # 減少方波比例
        return 0.8 * sine_wave + 0.2 * square_component
    
    def _generate_soft_bass_wave(self, frequency, t):
        """生成柔和低音提琴音色"""
        wave = np.sin(2 * np.pi * frequency * t)
        # 強調低頻泛音
        wave += 0.4 * np.sin(2 * np.pi * frequency * 0.5 * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
        return wave
    
    def _generate_soft_organ_wave(self, frequency, t):
        """生成柔和管風琴音色"""
        # 減少高頻泛音的強度
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)   # 八度
        wave += 0.3 * np.sin(2 * np.pi * frequency * 3 * t)   # 十二度
        wave += 0.1 * np.sin(2 * np.pi * frequency * 4 * t)   # 十五度
        wave += 0.25 * np.sin(2 * np.pi * frequency * 6 * t)  # 十九度
        return wave * frequency * t
        wave += 0.12 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.06 * np.sin(2 * np.pi * frequency * 3 * t)
        # 柔和的指數衰減
        decay = np.exp(-t * 1.5)
        return wave * decay
    
    def _generate_soft_percussion_wave(self, frequency, t):
        """生成柔和打擊樂音色"""
        # 減少噪音比例，增加調性
        noise = np.random.normal(0, 0.15, len(t))  # 減少噪音強度
        tone = 0.6 * np.sin(2 * np.pi * frequency * t)  # 增加調性成分
        # 更快的衰減
        decay = np.exp(-t * 12)
        return (0.4 * noise + 0.6 * tone) * decay
    
    def _generate_soft_brass_wave(self, frequency, t):
        """生成柔和銅管音色"""
        # 減少尖銳的泛音
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.08 * np.sin(2 * np.pi * frequency * 4 * t)
        return wave
    
    def _generate_soft_reed_wave(self, frequency, t):
        """生成柔和簧片音色 (薩克斯風)"""
        # 使用更多正弦波，減少方波成分
        sine_wave = np.sin(2 * np.pi * frequency * t)
        square_component = 0.2 * np.sign(np.sin(2 * np.pi * frequency * t))  # 減少方波比例
        return 0.8 * sine_wave + 0.2 * square_component
    
    def _generate_soft_bass_wave(self, frequency, t):
        """生成柔和低音提琴音色"""
        wave = np.sin(2 * np.pi * frequency * t)
        # 強調低頻泛音
        wave += 0.4 * np.sin(2 * np.pi * frequency * 0.5 * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
        return wave
    
    def _generate_soft_organ_wave(self, frequency, t):
        """生成柔和管風琴音色"""
        # 減少高頻泛音的強度
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 2 * t)   # 八度
        wave += 0.3 * np.sin(2 * np.pi * frequency * 3 * t)   # 十二度
        wave += 0.1 * np.sin(2 * np.pi * frequency * 4 * t)   # 十五度
        wave += 0.25 * np.sin(2 * np.pi * frequency * 6 * t)  # 十九度
        return wave
    
    def _generate_piano_wave(self, frequency, t):
        """生成原始鋼琴音色（保留作為對比）"""
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.05 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.02 * np.sin(2 * np.pi * frequency * 7 * t)
        return wave
    
    def _generate_plucked_wave(self, frequency, t):
        """生成撥弦音色 (吉他)"""
        wave = 2 * (t * frequency % 1) - 1
        decay = np.exp(-t * 3)
        return wave * decay
    
    def _generate_drum_wave(self, frequency, t):
        """生成鼓聲"""
        noise = np.random.normal(0, 1, len(t))
        low_freq = np.sin(2 * np.pi * (frequency * 0.5) * t)
        decay = np.exp(-t * 8)
        return (0.7 * noise + 0.3 * low_freq) * decay
    
    def _generate_brass_wave(self, frequency, t):
        """生成銅管樂器音色"""
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.6 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.4 * np.sin(2 * np.pi * frequency * 4 * t)
        return wave
    
    def _generate_reed_wave(self, frequency, t):
        """生成簧片樂器音色 (薩克斯風)"""
        square_wave = np.sign(np.sin(2 * np.pi * frequency * t))
        sine_wave = np.sin(2 * np.pi * frequency * t)
        return 0.6 * square_wave + 0.4 * sine_wave
    
    def _generate_rich_sine_wave(self, frequency, t):
        """生成豐富的正弦波 (低音提琴)"""
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 0.5 * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        return wave
    
    def _generate_organ_wave(self, frequency, t):
        """生成管風琴音色"""
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 1.0 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 4 * t)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 6 * t)
        return wave
    
    def _create_envelope(self, samples, config):
        """創建包絡 (ADSR) - 針對鋼琴優化"""
        attack_samples = int(samples * config['attack'])
        decay_samples = int(samples * config['decay'])
        release_samples = int(samples * config['release'])
        sustain_samples = samples - attack_samples - decay_samples - release_samples
        
        envelope = np.ones(samples)
        
        # Attack - 使用平滑曲線而非線性
        if attack_samples > 0:
            # 使用平方根曲線讓起音更自然
            attack_curve = np.sqrt(np.linspace(0, 1, attack_samples))
            envelope[:attack_samples] = attack_curve
        
        # Decay - 使用指數衰減
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            # 使用指數曲線讓衰減更自然
            decay_curve = np.exp(np.linspace(0, -2, decay_samples)) * (1 - config['sustain']) + config['sustain']
            envelope[start_idx:end_idx] = decay_curve
        
        # Sustain
        if sustain_samples > 0:
            start_idx = attack_samples + decay_samples
            end_idx = start_idx + sustain_samples
            envelope[start_idx:end_idx] = config['sustain']
        
        # Release - 使用平滑的指數衰減
        if release_samples > 0:
            start_idx = samples - release_samples
            # 使用指數曲線讓釋音更自然
            release_curve = np.exp(np.linspace(0, -4, release_samples)) * config['sustain']
            envelope[start_idx:] = release_curve
        
        return envelope


class AudioEngine:
    """完整的音訊引擎 - 支援多樂器和程式碼執行"""
    
    def __init__(self):
        # 初始化 pygame mixer
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            print("🎵 pygame mixer 初始化成功")
        except Exception as e:
            print(f"❌ pygame mixer 初始化失敗: {e}")
            return
        
        self.synthesizer = InstrumentSynthesizer()
        
        # 音樂狀態
        self.current_tempo = 120  # BPM
        self.current_volume = 0.8
        self.current_instrument = 'piano'
        
        # 多軌道支援
        self.tracks = defaultdict(list)
        self.active_sounds = []
        
        # 變數存儲
        self.variables = {}
        
        print("🎵 多樂器音訊引擎初始化完成")
        print(f"📀 支援樂器: {', '.join(self.synthesizer.instrument_configs.keys())}")
    
    def set_tempo(self, bpm):
        """設定速度"""
        self.current_tempo = bpm
        print(f"🎼 設定速度: {bpm} BPM")
    
    def set_volume(self, volume):
        """設定音量"""
        self.current_volume = max(0.0, min(1.0, volume))
        print(f"🔊 設定音量: {self.current_volume:.1f}")
    
    def set_instrument(self, instrument):
        """設定樂器"""
        if instrument in self.synthesizer.instrument_configs:
            self.current_instrument = instrument
            print(f"🎹 切換樂器: {instrument}")
        else:
            print(f"⚠️  未知樂器: {instrument}，使用預設樂器 piano")
            self.current_instrument = 'piano'
    
    def play_note(self, note, duration=None):
        """播放音符"""
        if duration is None:
            duration = 60.0 / self.current_tempo
        
        self._play_single_note(note, duration)
    
    def play_chord(self, notes, duration=None):
        """播放和弦"""
        if duration is None:
            duration = 60.0 / self.current_tempo * 2
        
        print(f"🎹 播放和弦 ({self.current_instrument}): [{', '.join(notes)}], 時長: {duration:.1f}s")
        
        # 同時播放所有音符
        threads = []
        for note in notes:
            thread = threading.Thread(target=self._play_single_note, args=(note, duration))
            threads.append(thread)
            thread.start()
        
        # 等待所有音符播放完成
        for thread in threads:
            thread.join()
    
    def _play_single_note(self, note_str, duration):
        """播放單個音符 - 修復版本，防止破音"""
        try:
            print(f"♪ 播放音符 ({self.current_instrument}): {note_str}, 時長: {duration:.1f}s")
            
            # 生成波形
            wave = self.synthesizer.generate_waveform(
                self.synthesizer.note_to_frequency(note_str),
                duration,
                self.current_instrument
            )
            
            # 應用用戶設定的音量，但限制最大值防止破音
            effective_volume = min(self.current_volume * 0.4, 0.6)  # 大幅降低音量上限
            wave = wave * effective_volume
            
            # 更嚴格的音量限制
            wave = np.clip(wave, -0.8, 0.8)  # 限制在更安全的範圍
            
            # 轉換為 pygame 可用的格式，使用較小的範圍
            wave_int = (wave * 20000).astype(np.int16)  # 進一步降低音量範圍
            
            # 檢查 pygame mixer 設定
            mixer_init = pygame.mixer.get_init()
            if mixer_init is None:
                print("❌ pygame mixer 未正確初始化")
                return
            
            # 兼容不同版本的 pygame - 支援3或4個返回值
            if len(mixer_init) == 4:
                frequency, format_val, channels, buffer = mixer_init
            elif len(mixer_init) == 3:
                frequency, format_val, channels = mixer_init
            else:
                print(f"❌ 未知的 mixer 初始化格式: {mixer_init}")
                channels = 2  # 預設立體聲
            
            # 根據聲道數處理音訊
            if channels == 2:
                # 立體聲：使用 column_stack 創建立體聲陣列
                stereo_wave = np.column_stack((wave_int, wave_int))
                sound = pygame.sndarray.make_sound(stereo_wave)
            else:
                # 單聲道
                sound = pygame.sndarray.make_sound(wave_int)
            
            # 播放音效
            sound.play()
            
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
            import traceback
            print("詳細錯誤資訊：")
            traceback.print_exc()
    
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
    
    def _execute_node(self, node):
        """執行 AST 節點"""
        if not isinstance(node, dict):
            return
        
        node_type = node.get('type', '')
        
        if node_type == 'tempo':
            bpm = self._get_value(node.get('bpm', {}), 120)
            self.set_tempo(bpm)
        
        elif node_type == 'volume':
            volume = self._get_value(node.get('volume', {}), 0.8)
            self.set_volume(volume)
        
        elif node_type == 'instrument':
            instrument_node = node.get('instrument', {})
            instrument_name = instrument_node.get('name', 'piano')
            self.set_instrument(instrument_name)
        
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
                executed = False
                for elseif_clause in elseif_clauses:
                    elseif_condition = elseif_clause.get('condition', {})
                    if self._evaluate_condition(elseif_condition):
                        print("✅ elseif 條件成立")
                        for stmt in elseif_clause.get('body', []):
                            self._execute_node(stmt)
                        executed = True
                        break
                
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
                    self.set_volume(volume)
            
            elif func_name == 'refTempo':
                if args:
                    tempo = self._get_value(args[0], 120)
                    self.set_tempo(tempo)
            
            elif func_name == 'refInst':
                if args:
                    instrument = self._get_name(args[0])
                    self.set_instrument(instrument)
    
    def _play_note(self, node):
        """播放音符或音符陣列"""
        note_value = node.get('note_value', {})
        duration_node = node.get('duration')
        
        if duration_node:
            duration = self._get_value(duration_node, 1.0)
        else:
            duration = 60.0 / self.current_tempo
        
        if note_value.get('type') == 'note_array':
            notes = note_value.get('notes', [])
            print(f"🎵 播放音符陣列 ({self.current_instrument}): ", end='')
            for note in notes:
                note_str = self._get_note_string(note)
                print(f"{note_str} ", end='')
                self._play_single_note(note_str, duration)
            print()
        else:
            note_str = self._get_note_string(note_value)
            self._play_single_note(note_str, duration)
    
    def _play_chord(self, node):
        """播放和弦"""
        chord_node = node.get('chord', {})
        duration_node = node.get('duration')
        
        if duration_node:
            duration = self._get_value(duration_node, 2.0)
        else:
            duration = 60.0 / self.current_tempo * 2
        
        notes = chord_node.get('notes', [])
        chord_notes = [self._get_note_string(note) for note in notes]
        
        self.play_chord(chord_notes, duration)
    
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


# 測試範例
if __name__ == "__main__":
    # 測試音訊引擎
    engine = AudioEngine()
    
    print("\n🎼 測試不同樂器...")
    
    # 測試鋼琴
    engine.set_instrument('piano')
    engine.play_note('C4', 1.0)
    
    # 測試小提琴
    engine.set_instrument('violin')
    engine.play_note('G4', 1.0)
    
    # 測試和弦
    engine.set_instrument('organ')
    engine.play_chord(['C4', 'E4', 'G4'], 2.0)
    
    print("🎵 測試完成！")