#!/usr/bin/env python3
"""
PyTune 音色系統
支援鋼琴、提琴、吉他、鼓聲等多種音色
"""

import numpy as np
import pygame
from enum import Enum
from typing import Dict, Optional
import math

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

class InstrumentSynthesizer:
    """音色合成器"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.current_instrument = InstrumentType.PIANO
        
        # 音色參數配置
        self.instrument_configs = {
            InstrumentType.PIANO: {
                'attack': 0.01,
                'decay': 0.3,
                'sustain': 0.4,
                'release': 1.2,
                'harmonics': [1.0, 0.8, 0.6, 0.4, 0.25, 0.15, 0.1],
                'wave_type': 'complex'
            },
            InstrumentType.VIOLIN: {
                'attack': 0.1,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.4,
                'harmonics': [1.0, 0.6, 0.8, 0.5, 0.4, 0.3],
                'wave_type': 'sawtooth_filtered'
            },
            InstrumentType.GUITAR: {
                'attack': 0.01,
                'decay': 0.2,
                'sustain': 0.6,
                'release': 1.5,
                'harmonics': [1.0, 0.7, 0.5, 0.3, 0.2],
                'wave_type': 'plucked'
            },
            InstrumentType.DRUMS: {
                'attack': 0.001,
                'decay': 0.05,
                'sustain': 0.0,
                'release': 0.1,
                'harmonics': [1.0],
                'wave_type': 'noise'
            },
            InstrumentType.FLUTE: {
                'attack': 0.1,
                'decay': 0.1,
                'sustain': 0.9,
                'release': 0.3,
                'harmonics': [1.0, 0.2, 0.1, 0.05],
                'wave_type': 'sine_pure'
            },
            InstrumentType.TRUMPET: {
                'attack': 0.05,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.2,
                'harmonics': [1.0, 0.8, 0.6, 0.4, 0.3, 0.2],
                'wave_type': 'brass'
            },
            InstrumentType.BASS: {
                'attack': 0.02,
                'decay': 0.1,
                'sustain': 0.7,
                'release': 0.5,
                'harmonics': [1.0, 0.8, 0.3, 0.1],
                'wave_type': 'square_soft'
            },
            InstrumentType.ORGAN: {
                'attack': 0.0,
                'decay': 0.0,
                'sustain': 1.0,
                'release': 0.1,
                'harmonics': [1.0, 0.5, 0.8, 0.3, 0.6, 0.2, 0.4],
                'wave_type': 'organ_complex'
            },
            InstrumentType.SAXOPHONE: {
                'attack': 0.08,
                'decay': 0.2,
                'sustain': 0.7,
                'release': 0.4,
                'harmonics': [1.0, 0.9, 0.7, 0.5, 0.3],
                'wave_type': 'reed'
            },
            InstrumentType.SYNTHESIZER: {
                'attack': 0.01,
                'decay': 0.2,
                'sustain': 0.6,
                'release': 0.8,
                'harmonics': [1.0, 0.5, 0.3, 0.2, 0.1],
                'wave_type': 'square'
            }
        }
    
    def set_instrument(self, instrument: InstrumentType):
        """設定當前音色"""
        self.current_instrument = instrument
        print(f"🎼 切換音色為: {instrument.value}")
    
    def generate_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """根據當前音色生成波形"""
        config = self.instrument_configs[self.current_instrument]
        
        # 生成基本波形
        if config['wave_type'] == 'complex':
            wave = self._generate_complex_wave(frequency, duration, config['harmonics'])
        elif config['wave_type'] == 'sawtooth_filtered':
            wave = self._generate_sawtooth_filtered(frequency, duration)
        elif config['wave_type'] == 'plucked':
            wave = self._generate_plucked_string(frequency, duration)
        elif config['wave_type'] == 'noise':
            wave = self._generate_drum_sound(frequency, duration)
        elif config['wave_type'] == 'sine_pure':
            wave = self._generate_pure_sine(frequency, duration, config['harmonics'])
        elif config['wave_type'] == 'brass':
            wave = self._generate_brass_sound(frequency, duration, config['harmonics'])
        elif config['wave_type'] == 'square_soft':
            wave = self._generate_soft_square(frequency, duration)
        elif config['wave_type'] == 'organ_complex':
            wave = self._generate_organ_sound(frequency, duration, config['harmonics'])
        elif config['wave_type'] == 'reed':
            wave = self._generate_reed_sound(frequency, duration, config['harmonics'])
        else:  # square (synthesizer)
            wave = self._generate_square_wave(frequency, duration)
        
        # 應用包絡
        envelope = self._generate_envelope(duration, config)
        wave = wave * envelope * amplitude
        
        return wave
    
    def _generate_complex_wave(self, frequency: float, duration: float, harmonics: list) -> np.ndarray:
        """生成複雜波形（鋼琴）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave = np.zeros(samples)
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # 添加輕微的調制
        modulation = 1 + 0.02 * np.sin(2 * np.pi * 5 * t)  # 5Hz 顫音
        wave = wave * modulation
        
        return wave / len(harmonics)
    
    def _generate_sawtooth_filtered(self, frequency: float, duration: float) -> np.ndarray:
        """生成過濾的鋸齒波（提琴）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 基本鋸齒波
        wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        
        # 添加弓弦效果（隨機微小變化）
        bow_noise = 0.02 * np.random.normal(0, 1, samples)
        wave += bow_noise
        
        # 低通濾波器效果
        cutoff = frequency * 8
        wave = self._apply_lowpass_filter(wave, cutoff)
        
        return wave
    
    def _generate_plucked_string(self, frequency: float, duration: float) -> np.ndarray:
        """生成撥弦音色（吉他）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 基本正弦波與方波混合
        sine_wave = np.sin(2 * np.pi * frequency * t)
        square_wave = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # 混合比例隨時間變化
        mix_factor = np.exp(-t * 3)  # 快速衰減的方波成分
        wave = sine_wave * (1 - mix_factor) + square_wave * mix_factor * 0.3
        
        # 添加撥弦的初始噪音
        if samples > 0:
            pluck_noise = np.random.normal(0, 0.1, min(100, samples))
            wave[:len(pluck_noise)] += pluck_noise
        
        return wave
    
    def _generate_drum_sound(self, frequency: float, duration: float) -> np.ndarray:
        """生成鼓聲"""
        samples = int(self.sample_rate * duration)
        
        # 不同鼓聲類型根據頻率判斷
        if frequency < 80:  # 底鼓
            # 低頻正弦波 + 噪音
            t = np.linspace(0, duration, samples, False)
            sine_part = np.sin(2 * np.pi * frequency * t)
            noise_part = np.random.normal(0, 0.3, samples)
            wave = sine_part * 0.7 + noise_part * 0.3
        elif frequency < 200:  # 小鼓
            # 主要是噪音 + 輕微調性
            noise = np.random.normal(0, 1, samples)
            tone = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples, False))
            wave = noise * 0.8 + tone * 0.2
        else:  # 嗵鼓/鈸
            # 金屬音色：複雜頻率 + 噪音
            t = np.linspace(0, duration, samples, False)
            metallic = np.sin(2 * np.pi * frequency * t) + 0.5 * np.sin(2 * np.pi * frequency * 1.6 * t)
            noise = np.random.normal(0, 0.4, samples)
            wave = metallic * 0.6 + noise * 0.4
        
        return wave
    
    def _generate_pure_sine(self, frequency: float, duration: float, harmonics: list) -> np.ndarray:
        """生成純正弦波音色（長笛）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave = np.zeros(samples)
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # 添加輕微的氣息效果
        breath_noise = 0.01 * np.random.normal(0, 1, samples)
        wave += breath_noise
        
        return wave / len(harmonics)
    
    def _generate_brass_sound(self, frequency: float, duration: float, harmonics: list) -> np.ndarray:
        """生成銅管樂器音色（小號）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave = np.zeros(samples)
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            # 銅管樂器的諧波有輕微的相位偏移
            phase = i * 0.2
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t + phase)
        
        # 添加銅管特有的邊音
        if samples > 0:
            attack_samples = min(int(samples * 0.1), samples)
            buzz = 0.1 * np.random.normal(0, 1, attack_samples)
            wave[:attack_samples] += buzz
        
        return wave / len(harmonics)
    
    def _generate_soft_square(self, frequency: float, duration: float) -> np.ndarray:
        """生成柔和方波（貝斯）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 基本方波
        square = np.sign(np.sin(2 * np.pi * frequency * t))
        
        # 軟化邊緣
        smoothed = self._apply_lowpass_filter(square, frequency * 4)
        
        return smoothed
    
    def _generate_organ_sound(self, frequency: float, duration: float, harmonics: list) -> np.ndarray:
        """生成管風琴音色"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave = np.zeros(samples)
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # 管風琴特有的穩定性
        return wave / len(harmonics)
    
    def _generate_reed_sound(self, frequency: float, duration: float, harmonics: list) -> np.ndarray:
        """生成簧片樂器音色（薩克斯風）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave = np.zeros(samples)
        for i, harmonic_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            # 簧片樂器有特殊的諧波結構
            wave += harmonic_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # 添加簧片振動的特色
        reed_vibration = 0.05 * np.sin(2 * np.pi * 8 * t)  # 8Hz 振動
        wave = wave * (1 + reed_vibration)
        
        return wave / len(harmonics)
    
    def _generate_square_wave(self, frequency: float, duration: float) -> np.ndarray:
        """生成方波（合成器）"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        return np.sign(np.sin(2 * np.pi * frequency * t))
    
    def _generate_envelope(self, duration: float, config: dict) -> np.ndarray:
        """生成音量包絡線"""
        samples = int(self.sample_rate * duration)
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
    
    def _apply_lowpass_filter(self, signal: np.ndarray, cutoff_freq: float) -> np.ndarray:
        """簡單的低通濾波器"""
        # 簡化的一階低通濾波器
        alpha = cutoff_freq / (cutoff_freq + self.sample_rate / (2 * np.pi))
        filtered = np.zeros_like(signal)
        
        if len(signal) > 0:
            filtered[0] = signal[0]
            for i in range(1, len(signal)):
                filtered[i] = alpha * signal[i] + (1 - alpha) * filtered[i-1]
        
        return filtered

class InstrumentEngine:
    """音色引擎 - 整合到現有的音訊系統"""
    
    def __init__(self, sample_rate=44100):
        self.synthesizer = InstrumentSynthesizer(sample_rate)
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=1024)
        
        # 音符頻率映射
        self.note_frequencies = {
            'C': [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.01],
            'C#': [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            'Db': [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            'D': [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32, 4698.64],
            'D#': [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            'Eb': [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            'E': [20.60, 41.20, 82.41, 164.81, 329.63, 659.26, 1318.51, 2637.02, 5274.04],
            'F': [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83, 5587.65],
            'F#': [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            'Gb': [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            'G': [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96, 6271.93],
            'G#': [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            'Ab': [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            'A': [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00, 7040.00],
            'A#': [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            'Bb': [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            'B': [30.87, 61.74, 123.47, 246.94, 493.88, 987.77, 1975.53, 3951.07, 7902.13]
        }
    
    def set_instrument(self, instrument_name: str):
        """設定音色"""
        try:
            instrument = InstrumentType(instrument_name.lower())
            self.synthesizer.set_instrument(instrument)
        except ValueError:
            available = [inst.value for inst in InstrumentType]
            print(f"❌ 未知音色: {instrument_name}")
            print(f"🎼 可用音色: {', '.join(available)}")
    
    def play_note(self, note: str, duration: float, volume: float = 0.7):
        """播放音符"""
        frequency = self._note_to_frequency(note)
        if frequency:
            wave_data = self.synthesizer.generate_wave(frequency, duration, volume)
            self._play_wave(wave_data)
    
    def _note_to_frequency(self, note: str) -> Optional[float]:
        """將音符轉換為頻率"""
        if len(note) < 2:
            return None
        
        note_name = note[:-1].upper()
        try:
            octave = int(note[-1])
            if note_name in self.note_frequencies and 0 <= octave <= 8:
                return self.note_frequencies[note_name][octave]
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _play_wave(self, wave_data: np.ndarray):
        """播放波形數據"""
        # 轉換為 pygame 可播放的格式
        wave_data = np.clip(wave_data, -1, 1)
        wave_data = (wave_data * 32767).astype(np.int16)
        
        # 立體聲
        stereo_wave = np.column_stack((wave_data, wave_data))
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.play()
        
        # 等待播放完成
        pygame.time.wait(int(len(wave_data) / self.synthesizer.sample_rate * 1000))

# 使用範例
if __name__ == "__main__":
    # 初始化音色引擎
    engine = InstrumentEngine()
    
    # 測試不同音色
    instruments = ["piano", "violin", "guitar", "drums", "flute"]
    
    for instrument in instruments:
        print(f"\n🎼 測試音色: {instrument}")
        engine.set_instrument(instrument)
        
        if instrument == "drums":
            # 鼓聲測試
            engine.play_note("C2", 0.5)  # 底鼓
            engine.play_note("D3", 0.3)  # 小鼓
            engine.play_note("F#4", 0.2) # 嗵鼓
        else:
            # 音階測試
            for note in ["C4", "D4", "E4", "F4", "G4"]:
                engine.play_note(note, 0.5)
    
    pygame.quit()