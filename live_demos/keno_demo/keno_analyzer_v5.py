#!/usr/bin/env python3
"""
Advanced Time-Based Keno Pattern Analyzer V5 - COMPLETE UPGRADE
Fully compatible with Keno Time Predictor V5 HTML system
Features: Timing correction, flexible ball selection (1-8), enhanced patterns
Generates V5-compatible JSON and JavaScript configurations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
import re
from itertools import combinations
import statistics


class TimeBasedKenoAnalyzerV5:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.df = None
        self.time_patterns = {}
        self.time_window_patterns = {}
        self.combination_patterns = {}
        self.optimal_times = {}
        self.confidence_scores = {}
        
        # V5 Configuration Constants
        self.V5_CONFIG = {
            'VERSION': '5.0',
            'DEFAULT_BALL_COUNT': 4,
            'TIMING_OFFSET_MINUTES': -5,  # Correction for early prediction issue
            'DRAW_INTERVAL_MINUTES': 5,
            'MULTIPLIERS': {
                1: 3.6, 2: 15.0, 3: 60.0, 4: 240.0,
                5: 1000.0, 6: 3800.0, 7: 12500.0, 8: 35000.0
            },
            'MIN_DRAWS_FOR_ANALYSIS': 5,
            'MAX_RECOMMENDATIONS': 15,
            'CONFIDENCE_FACTORS': {
                'BASE_CONFIDENCE': 50,
                'DRAW_MULTIPLIER': 1.5,
                'CONSISTENCY_MULTIPLIER': 0.4,
                'COMBINATION_MULTIPLIER': 2.0,
                'MAX_CONFIDENCE': 95
            }
        }

    def load_and_prepare_data(self):
        """Load CSV and prepare data for V5 time-based analysis"""
        print("🔄 Loading and preparing Keno data for V5 analysis...")
        print("=" * 70)

        try:
            self.df = pd.read_csv(self.csv_file_path)
            print(f"✅ Successfully loaded {len(self.df)} draws")
            print(f"📊 Columns: {list(self.df.columns)}")

            # Clean and standardize time format
            self.df['Time'] = self.df['Time'].astype(str)
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')

            # Extract hour and minute for precise analysis
            self.df['Hour'] = self.df['Time'].str.extract(r'(\d{1,2}):', expand=False).astype(int)
            self.df['Minute'] = self.df['Time'].str.extract(r':(\d{2}):', expand=False).astype(int)
            self.df['TimeKey'] = self.df['Hour'].astype(str).str.zfill(2) + ':' + self.df['Minute'].astype(str).str.zfill(2)

            # Apply V5 timing correction
            self.df['CorrectedTimeKey'] = self.df.apply(self._apply_timing_correction, axis=1)

            # Create 5-minute time windows for V5 compatibility
            self.df['TimeWindow'] = self.df.apply(self._create_v5_time_window, axis=1)

            print(f"📅 Date range: {self.df['Date'].min()} to {self.df['Date'].max()}")
            print(f"⏰ Time range: {self.df['TimeKey'].min()} to {self.df['TimeKey'].max()}")
            print(f"🔧 Applied {self.V5_CONFIG['TIMING_OFFSET_MINUTES']}-minute timing correction")

            return True

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

    def _apply_timing_correction(self, row):
        """Apply V5 timing correction to fix 'one draw early' issue"""
        hour = row['Hour']
        minute = row['Minute']
        
        # Apply offset
        corrected_minute = minute + self.V5_CONFIG['TIMING_OFFSET_MINUTES']
        
        if corrected_minute < 0:
            corrected_hour = hour - 1
            corrected_minute = 60 + corrected_minute
            if corrected_hour < 0:
                corrected_hour = 23
        elif corrected_minute >= 60:
            corrected_hour = hour + 1
            corrected_minute = corrected_minute - 60
            if corrected_hour >= 24:
                corrected_hour = 0
        else:
            corrected_hour = hour
            
        return f"{corrected_hour:02d}:{corrected_minute:02d}"

    def _create_v5_time_window(self, row):
        """Create 5-minute time windows for V5 system (matching draw intervals)"""
        hour = row['Hour']
        minute = row['Minute']

        # Group into 5-minute windows to match draw schedule
        window_start_minute = (minute // 5) * 5
        window_end_minute = window_start_minute + 4
        
        if window_end_minute >= 60:
            end_hour = hour + 1 if hour < 23 else 0
            window_end_minute = window_end_minute - 60
            window_end = f"{end_hour:02d}:{window_end_minute:02d}"
        else:
            window_end = f"{hour:02d}:{window_end_minute:02d}"

        window_start = f"{hour:02d}:{window_start_minute:02d}"
        return f"{window_start}-{window_end}"

    def analyze_exact_time_patterns_v5(self):
        """V5: Analyze patterns for exact times with enhanced ball flexibility"""
        print("\n🎯 V5: Analyzing Exact Time Patterns (1-8 ball compatibility)...")
        print("=" * 70)

        # Get number columns
        number_cols = [col for col in self.df.columns if col.startswith('Ball')]

        # Group by both original and corrected time for comparison
        time_groups = self.df.groupby(['TimeKey', 'CorrectedTimeKey'])

        pattern_count = 0
        for (time_key, corrected_time), group in time_groups:
            if len(group) >= self.V5_CONFIG['MIN_DRAWS_FOR_ANALYSIS']:
                numbers_at_time = []

                # Extract all numbers for this exact time
                for _, row in group.iterrows():
                    draw_numbers = []
                    for col in number_cols:
                        if pd.notna(row[col]):
                            draw_numbers.append(int(row[col]))
                    numbers_at_time.append(sorted(draw_numbers))

                # Enhanced V5 analysis with multi-ball support
                all_numbers = [num for draw in numbers_at_time for num in draw]
                number_frequency = Counter(all_numbers)

                # Generate recommendations for different ball counts (1-8)
                ball_recommendations = {}
                for ball_count in range(1, 9):
                    top_for_count = [num for num, _ in number_frequency.most_common(ball_count * 3)]
                    ball_recommendations[ball_count] = {
                        'primary': top_for_count[:ball_count],
                        'backup': top_for_count[ball_count:ball_count*2],
                        'extended': top_for_count[:ball_count*3]
                    }

                # Calculate V5 enhanced consistency score
                consistency_score = self._calculate_v5_consistency(numbers_at_time, number_frequency)

                # Analyze combination patterns for V5
                frequent_combinations = self._analyze_v5_combinations(numbers_at_time)

                self.time_patterns[time_key] = {
                    'total_draws': len(group),
                    'corrected_time': corrected_time,
                    'numbers_frequency': dict(number_frequency),
                    'hot_numbers': [num for num, _ in number_frequency.most_common(self.V5_CONFIG['MAX_RECOMMENDATIONS'])],
                    'ball_recommendations': ball_recommendations,
                    'consistency_score': consistency_score,
                    'frequent_combinations': frequent_combinations,
                    'all_draws': numbers_at_time,
                    'average_per_draw': len(all_numbers) / len(numbers_at_time) if numbers_at_time else 0,
                    'multiplier_potential': self._calculate_multiplier_potential(number_frequency, len(group))
                }

                pattern_count += 1
                print(f"⏰ {time_key} → {corrected_time} - {len(group)} draws, consistency: {consistency_score:.1f}%")
                print(f"   🔥 Hot numbers: {self.time_patterns[time_key]['hot_numbers'][:8]}")

        print(f"✅ Analyzed {pattern_count} time patterns with V5 enhancements")

    def _calculate_v5_consistency(self, draws_list, number_frequency):
        """V5: Calculate enhanced consistency score"""
        if not draws_list:
            return 0

        total_draws = len(draws_list)
        total_numbers = sum(len(draw) for draw in draws_list)
        
        # Get top 10 most frequent numbers
        top_numbers = [num for num, _ in number_frequency.most_common(10)]
        
        # Calculate how often top numbers appear
        top_appearances = sum(count for num, count in number_frequency.most_common(10))
        consistency = (top_appearances / total_numbers) * 100 if total_numbers > 0 else 0
        
        # V5 adjustment based on draw frequency
        frequency_bonus = min(total_draws / 20, 5)  # Up to 5% bonus for more data
        
        return min(consistency + frequency_bonus, 100)

    def _analyze_v5_combinations(self, draws_list):
        """V5: Analyze frequent number combinations (2-4 numbers)"""
        if len(draws_list) < 3:
            return []

        combination_counter = Counter()
        
        for draw in draws_list:
            # Analyze 2-number combinations
            for pair in combinations(draw, 2):
                combination_counter[tuple(sorted(pair))] += 1
                
            # Analyze 3-number combinations if draw has enough numbers
            if len(draw) >= 3:
                for triple in combinations(draw, 3):
                    combination_counter[tuple(sorted(triple))] += 1

        # Return frequent combinations (appeared at least twice)
        frequent_combos = []
        for combo, count in combination_counter.items():
            if count >= 2:
                frequency = (count / len(draws_list)) * 100
                frequent_combos.append({
                    'numbers': list(combo),
                    'frequency': count,
                    'percentage': frequency
                })

        return sorted(frequent_combos, key=lambda x: x['frequency'], reverse=True)[:10]

    def _calculate_multiplier_potential(self, number_frequency, total_draws):
        """V5: Calculate potential multiplier success for different ball counts"""
        multiplier_potential = {}
        
        for ball_count in range(1, 9):
            # Get top numbers for this ball count
            top_numbers = [num for num, _ in number_frequency.most_common(ball_count)]
            
            # Calculate average frequency of top numbers
            if top_numbers:
                avg_frequency = sum(number_frequency[num] for num in top_numbers) / len(top_numbers)
                success_rate = (avg_frequency / total_draws) * 100 if total_draws > 0 else 0
                
                multiplier_potential[ball_count] = {
                    'success_rate': success_rate,
                    'multiplier': self.V5_CONFIG['MULTIPLIERS'][ball_count],
                    'expected_value': success_rate * self.V5_CONFIG['MULTIPLIERS'][ball_count] / 100
                }
            else:
                multiplier_potential[ball_count] = {
                    'success_rate': 0,
                    'multiplier': self.V5_CONFIG['MULTIPLIERS'][ball_count],
                    'expected_value': 0
                }

        return multiplier_potential

    def analyze_time_window_patterns_v5(self):
        """V5: Analyze 5-minute window patterns for enhanced predictions"""
        print("\n🕐 V5: Analyzing 5-Minute Time Window Patterns...")
        print("=" * 70)

        number_cols = [col for col in self.df.columns if col.startswith('Ball')]
        window_groups = self.df.groupby('TimeWindow')

        window_count = 0
        for window, group in window_groups:
            if len(group) >= 8:  # Minimum draws for reliable V5 analysis
                numbers_in_window = []

                # Extract all numbers for this time window
                for _, row in group.iterrows():
                    draw_numbers = []
                    for col in number_cols:
                        if pd.notna(row[col]):
                            draw_numbers.append(int(row[col]))
                    numbers_in_window.append(sorted(draw_numbers))

                # V5 enhanced window analysis
                all_window_numbers = [num for draw in numbers_in_window for num in draw]
                window_frequency = Counter(all_window_numbers)
                
                # Calculate V5 window consistency
                window_consistency = self._calculate_window_consistency_v5(numbers_in_window)
                
                # Find persistent numbers across different thresholds
                persistent_numbers = self._find_v5_persistent_numbers(numbers_in_window, window_frequency)

                self.time_window_patterns[window] = {
                    'total_draws': len(group),
                    'numbers_frequency': dict(window_frequency),
                    'hot_numbers': [num for num, _ in window_frequency.most_common(20)],
                    'consistency_score': window_consistency,
                    'all_draws': numbers_in_window,
                    'persistent_numbers': persistent_numbers,
                    'window_combinations': self._analyze_v5_combinations(numbers_in_window)
                }

                window_count += 1
                print(f"🕐 {window} - {len(group)} draws, consistency: {window_consistency:.1f}%")
                print(f"   📌 Persistent: {persistent_numbers[:8]}")

        print(f"✅ Analyzed {window_count} time windows with V5 enhancements")

    def _calculate_window_consistency_v5(self, draws_list):
        """V5: Enhanced window consistency calculation"""
        if not draws_list:
            return 0

        number_counts = Counter()
        for draw in draws_list:
            for num in draw:
                number_counts[num] += 1

        total_draws = len(draws_list)
        
        # V5: More nuanced consistency thresholds
        very_consistent = sum(1 for count in number_counts.values() if count >= total_draws * 0.4)
        somewhat_consistent = sum(1 for count in number_counts.values() if count >= total_draws * 0.25)
        
        # Weight very consistent numbers more heavily
        consistency_score = (very_consistent * 2 + somewhat_consistent) / len(number_counts) * 100 if number_counts else 0
        
        return min(consistency_score, 100)

    def _find_v5_persistent_numbers(self, draws_list, frequency_counter):
        """V5: Find numbers persistent across different frequency thresholds"""
        if not draws_list:
            return []

        total_draws = len(draws_list)
        persistent_tiers = {
            'very_high': [],    # 40%+ appearance
            'high': [],         # 25%+ appearance  
            'moderate': []      # 15%+ appearance
        }
        
        for num, count in frequency_counter.items():
            appearance_rate = count / total_draws
            if appearance_rate >= 0.4:
                persistent_tiers['very_high'].append((num, count))
            elif appearance_rate >= 0.25:
                persistent_tiers['high'].append((num, count))
            elif appearance_rate >= 0.15:
                persistent_tiers['moderate'].append((num, count))

        # Combine and sort by frequency
        all_persistent = (
            persistent_tiers['very_high'] + 
            persistent_tiers['high'] + 
            persistent_tiers['moderate']
        )
        
        return [num for num, _ in sorted(all_persistent, key=lambda x: x[1], reverse=True)]

    def identify_optimal_times_v5(self):
        """V5: Identify optimal playing times with enhanced scoring"""
        print("\n🎯 V5: Identifying Optimal Playing Times...")
        print("=" * 70)

        time_scores = {}
        
        for time_key, pattern_data in self.time_patterns.items():
            if pattern_data['total_draws'] >= self.V5_CONFIG['MIN_DRAWS_FOR_ANALYSIS']:
                
                # V5 Enhanced Scoring System
                scores = self._calculate_v5_time_score(pattern_data)
                
                time_scores[time_key] = {
                    'total_score': scores['total'],
                    'draw_score': scores['draws'],
                    'consistency_score': scores['consistency'],
                    'combination_score': scores['combinations'],
                    'multiplier_score': scores['multiplier'],
                    'frequency_score': scores['frequency'],
                    'total_draws': pattern_data['total_draws'],
                    'corrected_time': pattern_data['corrected_time']
                }

        # Sort by total score
        self.optimal_times = dict(sorted(time_scores.items(),
                                       key=lambda x: x[1]['total_score'],
                                       reverse=True))

        print("🏆 Top 10 V5 Optimal Playing Times:")
        print("-" * 70)
        for i, (time_key, scores) in enumerate(list(self.optimal_times.items())[:10]):
            print(f"{i+1:2d}. {time_key} → {scores['corrected_time']} - Score: {scores['total_score']:.1f}")
            print(f"     Draws: {scores['total_draws']}, Consistency: {scores['consistency_score']:.1f}")
            print(f"     Multiplier Potential: {scores['multiplier_score']:.1f}, Combinations: {scores['combination_score']:.1f}")
            print()

    def _calculate_v5_time_score(self, pattern_data):
        """V5: Calculate comprehensive time score with multiple factors"""
        scores = {}
        
        # Factor 1: Historical draw count (reliability)
        scores['draws'] = min(pattern_data['total_draws'] / 30 * 25, 25)
        
        # Factor 2: Pattern consistency
        scores['consistency'] = pattern_data['consistency_score'] * 0.3
        
        # Factor 3: Combination patterns strength
        combo_count = len(pattern_data['frequent_combinations'])
        combo_strength = sum(combo['frequency'] for combo in pattern_data['frequent_combinations'])
        scores['combinations'] = min(combo_count * 2 + combo_strength * 0.5, 20)
        
        # Factor 4: Multiplier potential (V5 new factor)
        multiplier_scores = []
        for ball_count in [4, 5, 6]:  # Focus on common ball counts
            if ball_count in pattern_data['multiplier_potential']:
                expected_value = pattern_data['multiplier_potential'][ball_count]['expected_value']
                multiplier_scores.append(expected_value)
        scores['multiplier'] = np.mean(multiplier_scores) * 0.1 if multiplier_scores else 0
        
        # Factor 5: Number frequency distribution
        if pattern_data['numbers_frequency']:
            frequency_values = list(pattern_data['numbers_frequency'].values())
            frequency_std = np.std(frequency_values)
            scores['frequency'] = max(0, 10 - frequency_std * 0.5)  # Lower std = more predictable
        else:
            scores['frequency'] = 0
        
        scores['total'] = sum(scores.values())
        
        return scores

    def generate_v5_recommendations(self, target_time=None, ball_count=None):
        """V5: Generate recommendations with flexible ball selection"""
        print(f"\n🎲 V5: Generating Recommendations...")
        if ball_count:
            print(f"🎱 Ball Count: {ball_count} (Multiplier: {self.V5_CONFIG['MULTIPLIERS'].get(ball_count, 'N/A')}x)")
        print("=" * 70)

        if target_time:
            times_to_analyze = [target_time] if target_time in self.time_patterns else []
        else:
            times_to_analyze = list(self.optimal_times.keys())[:5]

        recommendations = {}

        for time_key in times_to_analyze:
            if time_key in self.time_patterns:
                pattern_data = self.time_patterns[time_key]
                
                # V5: Generate recommendations for specific ball count or all counts
                if ball_count:
                    ball_recommendations = self._get_v5_ball_recommendations(pattern_data, ball_count)
                else:
                    ball_recommendations = pattern_data['ball_recommendations']

                # V5: Calculate enhanced confidence
                confidence = self._calculate_v5_confidence(pattern_data, time_key)

                # V5: Generate strategy recommendations
                strategies = self._generate_v5_strategies(pattern_data, confidence, ball_count or 4)

                recommendations[time_key] = {
                    'confidence_level': confidence,
                    'corrected_time': pattern_data['corrected_time'],
                    'timing_offset': self.V5_CONFIG['TIMING_OFFSET_MINUTES'],
                    'ball_recommendations': ball_recommendations,
                    'hot_numbers': pattern_data['hot_numbers'][:15],
                    'combination_plays': pattern_data['frequent_combinations'][:5],
                    'historical_draws': pattern_data['total_draws'],
                    'consistency_score': pattern_data['consistency_score'],
                    'strategies': strategies,
                    'multiplier_analysis': pattern_data['multiplier_potential']
                }

                print(f"\n⏰ V5 Recommendations for {time_key} → {pattern_data['corrected_time']}:")
                print(f"   🎯 Confidence Level: {confidence:.1f}%")
                print(f"   📊 Historical Data: {pattern_data['total_draws']} draws")
                print(f"   🔥 Hot Numbers: {pattern_data['hot_numbers'][:8]}")
                if ball_count:
                    rec = ball_recommendations.get(ball_count, {})
                    print(f"   🎱 {ball_count}-Ball Rec: {rec.get('primary', [])} (+ backups: {rec.get('backup', [])})")
                print(f"   📈 Top Strategies: {strategies[:2]}")

        return recommendations

    def _get_v5_ball_recommendations(self, pattern_data, ball_count):
        """V5: Get specific recommendations for given ball count"""
        if ball_count in pattern_data['ball_recommendations']:
            return {ball_count: pattern_data['ball_recommendations'][ball_count]}
        else:
            # Generate on-the-fly for non-standard ball counts
            hot_numbers = pattern_data['hot_numbers']
            return {
                ball_count: {
                    'primary': hot_numbers[:ball_count],
                    'backup': hot_numbers[ball_count:ball_count*2],
                    'extended': hot_numbers[:ball_count*3]
                }
            }

    def _calculate_v5_confidence(self, pattern_data, time_key):
        """V5: Calculate enhanced confidence with timing correction factor"""
        base = self.V5_CONFIG['CONFIDENCE_FACTORS']['BASE_CONFIDENCE']
        
        # Draw count boost
        draw_boost = min(
            pattern_data['total_draws'] * self.V5_CONFIG['CONFIDENCE_FACTORS']['DRAW_MULTIPLIER'], 
            25
        )
        
        # Consistency boost
        consistency_boost = (
            pattern_data['consistency_score'] * 
            self.V5_CONFIG['CONFIDENCE_FACTORS']['CONSISTENCY_MULTIPLIER']
        )
        
        # Combination pattern boost
        combo_boost = (
            len(pattern_data['frequent_combinations']) * 
            self.V5_CONFIG['CONFIDENCE_FACTORS']['COMBINATION_MULTIPLIER']
        )
        
        # V5: Timing correction confidence boost
        timing_boost = 5 if pattern_data['corrected_time'] != time_key else 0
        
        # V5: Optimal time boost
        optimal_boost = 10 if time_key in list(self.optimal_times.keys())[:5] else 0
        
        total_confidence = base + draw_boost + consistency_boost + combo_boost + timing_boost + optimal_boost
        
        return min(total_confidence, self.V5_CONFIG['CONFIDENCE_FACTORS']['MAX_CONFIDENCE'])

    def _generate_v5_strategies(self, pattern_data, confidence, ball_count):
        """V5: Generate playing strategies based on analysis"""
        strategies = []
        multiplier = self.V5_CONFIG['MULTIPLIERS'].get(ball_count, 0)
        
        if confidence >= 85:
            strategies.extend([
                f"🔥 HIGH CONFIDENCE - Play {ball_count} balls for {multiplier}x potential",
                "💎 Timing corrected for optimal hit rate",
                f"🎯 Expected: {max(1, int(ball_count * 0.6))}-{ball_count} numbers to hit",
                "🚀 Consider increasing ball count for higher multiplier"
            ])
        elif confidence >= 75:
            strategies.extend([
                f"⚡ GOOD PATTERNS - {ball_count} balls at {multiplier}x multiplier",
                "🔧 Timing correction applied for better accuracy", 
                f"📊 Expected: {max(1, int(ball_count * 0.4))}-{max(1, int(ball_count * 0.7))} numbers to hit",
                "🎲 Solid play with moderate risk"
            ])
        elif confidence >= 65:
            strategies.extend([
                f"⚠️ MODERATE CONFIDENCE - Consider {max(1, ball_count-1)} balls",
                "🛡️ Conservative approach recommended",
                f"📈 Expected: {max(1, int(ball_count * 0.3))}-{max(1, int(ball_count * 0.5))} numbers to hit",
                "⏳ Consider waiting for higher confidence time"
            ])
        else:
            strategies.extend([
                "❌ LOW CONFIDENCE - Wait for optimal time window",
                f"🔒 High risk play - reduce to {max(1, ball_count-2)} balls if playing",
                "📉 Limited historical data for reliable prediction",
                "🎯 Check for better time slots in optimal times list"
            ])
        
        return strategies

    def export_v5_analysis_results(self):
        """V5: Export comprehensive analysis results"""
        print("\n💾 V5: Exporting Analysis Results...")
        print("=" * 70)

        # Get always hot and cold numbers globally
        global_frequency = Counter()
        for pattern in self.time_patterns.values():
            for num, count in pattern['numbers_frequency'].items():
                global_frequency[num] += count

        always_hot = [num for num, _ in global_frequency.most_common(10)]
        always_cold = [num for num, _ in global_frequency.most_common()[-10:]]

        # Prepare V5 export data
        export_data = {
            'analysis_metadata': {
                'version': self.V5_CONFIG['VERSION'],
                'total_draws': len(self.df),
                'analysis_date': datetime.now().isoformat(),
                'csv_file': self.csv_file_path,
                'unique_times': len(self.time_patterns),
                'time_windows': len(self.time_window_patterns),
                'timing_correction': self.V5_CONFIG['TIMING_OFFSET_MINUTES'],
                'default_ball_count': self.V5_CONFIG['DEFAULT_BALL_COUNT']
            },
            'v5_config': self.V5_CONFIG,
            'optimal_times': self.optimal_times,
            'time_patterns': self.time_patterns,
            'time_window_patterns': self.time_window_patterns,
            'always_hot_numbers': always_hot,
            'always_cold_numbers': always_cold,
            'top_active_hours': self._get_top_active_hours(),
            'top_intervals': list(self.optimal_times.keys())[:10]
        }

        # Save V5 JSON
        with open('keno_time_analysis_v5.json', 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        # Generate V5 JavaScript config
        self._generate_v5_web_config(export_data)

        # Generate V5 Python module
        self._generate_v5_python_config(export_data)

        print("✅ V5 Analysis results exported:")
        print("   📄 keno_time_analysis_v5.json - Complete V5 analysis data")
        print("   📄 keno_config_v5.js - V5 JavaScript configuration") 
        print("   📄 keno_patterns_v5.py - V5 Python patterns module")

    def _get_top_active_hours(self):
        """Get the most active hours based on pattern strength"""
        hour_scores = defaultdict(list)
        
        for time_key, pattern in self.time_patterns.items():
            hour = time_key.split(':')[0]
            score = pattern['consistency_score'] * pattern['total_draws']
            hour_scores[hour].append(score)
        
        # Average scores per hour
        hour_averages = {}
        for hour, scores in hour_scores.items():
            hour_averages[hour] = np.mean(scores)
        
        # Get top 5 hours
        top_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [f"{hour}:00-{hour}:59" for hour, _ in top_hours]

    def _generate_v5_web_config(self, export_data):
        """Generate V5 JavaScript configuration for HTML system"""
        
        # Prepare simplified time patterns for JavaScript
        js_time_patterns = {}
        for time_key, pattern in list(self.time_patterns.items())[:10]:  # Top 10 times
            js_time_patterns[time_key] = {
                'hot_numbers': pattern['hot_numbers'][:15],
                'total_draws': pattern['total_draws'],
                'consistency': round(pattern['consistency_score'], 2),
                'combinations': [
                    {'numbers': combo['numbers'], 'frequency': combo['frequency']}
                    for combo in pattern['frequent_combinations'][:5]
                ]
            }

        js_config = f'''// Advanced Keno Time Configuration V5 - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Compatible with Keno Time Predictor V5 HTML System
const KENO_TIME_CONFIG_V5 = {{
    TOTAL_DRAWS: {len(self.df)},
    ANALYSIS_VERSION: "5.0",
    DEFAULT_BALL_COUNT: {self.V5_CONFIG['DEFAULT_BALL_COUNT']},
    TIMING_OFFSET_MINUTES: {self.V5_CONFIG['TIMING_OFFSET_MINUTES']},
    DRAW_INTERVAL_MINUTES: {self.V5_CONFIG['DRAW_INTERVAL_MINUTES']},
    
    MULTIPLIERS: {json.dumps(self.V5_CONFIG['MULTIPLIERS'])},
    
    OPTIMAL_TIMES: {json.dumps(list(self.optimal_times.keys())[:10])},
    
    ALWAYS_HOT_NUMBERS: {json.dumps(export_data['always_hot_numbers'])},
    ALWAYS_COLD_NUMBERS: {json.dumps(export_data['always_cold_numbers'])},
    
    TOP_ACTIVE_HOURS: {json.dumps(export_data['top_active_hours'])},
    TOP_INTERVALS: {json.dumps(export_data['top_intervals'][:10])},
    
    TIME_PATTERNS: {json.dumps(js_time_patterns, indent=4)}
}};

// V5 Helper Functions
function getOptimalNumbersForTime(timeKey, ballCount = 4) {{
    const pattern = KENO_TIME_CONFIG_V5.TIME_PATTERNS[timeKey];
    if (pattern && pattern.hot_numbers) {{
        return pattern.hot_numbers.slice(0, ballCount * 2);
    }}
    return KENO_TIME_CONFIG_V5.ALWAYS_HOT_NUMBERS.slice(0, ballCount * 2);
}}

function getBestCombinationsForTime(timeKey) {{
    const pattern = KENO_TIME_CONFIG_V5.TIME_PATTERNS[timeKey];
    return pattern && pattern.combinations ? pattern.combinations : [];
}}

function getConfidenceForTime(timeKey) {{
    const pattern = KENO_TIME_CONFIG_V5.TIME_PATTERNS[timeKey];
    if (!pattern) return 60;
    
    const base = 50;
    const drawBoost = Math.min(pattern.total_draws * 1.5, 25);
    const consistencyBoost = pattern.consistency * 0.4;
    const comboBoost = pattern.combinations ? pattern.combinations.length * 2 : 0;
    
    return Math.min(base + drawBoost + consistencyBoost + comboBoost, 95);
}}

function getMultiplierForBallCount(ballCount) {{
    return KENO_TIME_CONFIG_V5.MULTIPLIERS[ballCount] || 0;
}}

// V5 Time Correction Function
function applyTimingCorrection(timeKey) {{
    const [hour, minute] = timeKey.split(':').map(Number);
    const correctedMinute = minute + KENO_TIME_CONFIG_V5.TIMING_OFFSET_MINUTES;
    
    if (correctedMinute < 0) {{
        const newHour = hour - 1 < 0 ? 23 : hour - 1;
        return `${{newHour.toString().padStart(2, '0')}}:${{(60 + correctedMinute).toString().padStart(2, '0')}}`;
    }} else if (correctedMinute >= 60) {{
        const newHour = hour + 1 > 23 ? 0 : hour + 1;
        return `${{newHour.toString().padStart(2, '0')}}:${{(correctedMinute - 60).toString().padStart(2, '0')}}`;
    }}
    
    return `${{hour.toString().padStart(2, '0')}}:${{correctedMinute.toString().padStart(2, '0')}}`;
}}'''

        with open('keno_config_v5.js', 'w') as f:
            f.write(js_config)

    def _generate_v5_python_config(self, export_data):
        """Generate V5 Python configuration module"""
        
        python_config = f'''"""
Advanced Keno Time Patterns V5 - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Compatible with Keno Time Predictor V5 System
Features: Timing correction, flexible ball selection (1-8), enhanced confidence scoring
"""

import json
from datetime import datetime

# V5 Configuration Constants
V5_CONFIG = {json.dumps(self.V5_CONFIG, indent=4)}

# Analysis Results
TOTAL_DRAWS = {len(self.df)}
OPTIMAL_TIMES = {json.dumps(list(self.optimal_times.keys())[:10], indent=4)}
ALWAYS_HOT_NUMBERS = {json.dumps(export_data['always_hot_numbers'], indent=4)}
ALWAYS_COLD_NUMBERS = {json.dumps(export_data['always_cold_numbers'], indent=4)}
TOP_ACTIVE_HOURS = {json.dumps(export_data['top_active_hours'], indent=4)}

# Time Pattern Data (Top 10)
TIME_PATTERNS = {json.dumps({k: v for k, v in list(self.time_patterns.items())[:10]}, indent=4, default=str)}

def get_v5_recommendations(time_key, ball_count=4):
    """Get V5 recommendations for specific time and ball count"""
    if time_key not in TIME_PATTERNS:
        return {{
            "error": "No data for specified time",
            "fallback_numbers": ALWAYS_HOT_NUMBERS[:ball_count * 2],
            "confidence": 60
        }}

    pattern = TIME_PATTERNS[time_key]
    
    # Get recommendations for ball count
    hot_numbers = pattern["hot_numbers"][:ball_count * 3]
    primary_numbers = hot_numbers[:ball_count]
    backup_numbers = hot_numbers[ball_count:ball_count * 2]
    
    # Calculate V5 confidence
    confidence = calculate_v5_confidence(time_key)
    
    return {{
        "primary_numbers": primary_numbers,
        "backup_numbers": backup_numbers,
        "extended_numbers": hot_numbers,
        "confidence": confidence,
        "historical_draws": pattern["total_draws"],
        "consistency_score": pattern["consistency_score"],
        "multiplier": V5_CONFIG["MULTIPLIERS"].get(ball_count, 0),
        "combinations": pattern.get("frequent_combinations", [])[:3],
        "timing_corrected": True
    }}

def calculate_v5_confidence(time_key):
    """Calculate V5 enhanced confidence score"""
    if time_key not in TIME_PATTERNS:
        return 60

    pattern = TIME_PATTERNS[time_key]
    
    base = V5_CONFIG["CONFIDENCE_FACTORS"]["BASE_CONFIDENCE"]
    draw_boost = min(
        pattern["total_draws"] * V5_CONFIG["CONFIDENCE_FACTORS"]["DRAW_MULTIPLIER"], 
        25
    )
    consistency_boost = (
        pattern["consistency_score"] * 
        V5_CONFIG["CONFIDENCE_FACTORS"]["CONSISTENCY_MULTIPLIER"]
    )
    combo_boost = (
        len(pattern.get("frequent_combinations", [])) * 
        V5_CONFIG["CONFIDENCE_FACTORS"]["COMBINATION_MULTIPLIER"]
    )
    
    # Optimal time boost
    optimal_boost = 10 if time_key in OPTIMAL_TIMES[:5] else 0
    
    total = base + draw_boost + consistency_boost + combo_boost + optimal_boost
    return min(total, V5_CONFIG["CONFIDENCE_FACTORS"]["MAX_CONFIDENCE"])

def get_optimal_ball_count(time_key, risk_tolerance="medium"):
    """Get optimal ball count based on risk tolerance"""
    if time_key not in TIME_PATTERNS:
        return V5_CONFIG["DEFAULT_BALL_COUNT"]
    
    confidence = calculate_v5_confidence(time_key)
    
    if risk_tolerance == "low":
        if confidence >= 80:
            return 3
        elif confidence >= 70:
            return 2
        else:
            return 1
    elif risk_tolerance == "high":
        if confidence >= 85:
            return 6
        elif confidence >= 75:
            return 5
        else:
            return 4
    else:  # medium
        if confidence >= 80:
            return 4
        elif confidence >= 70:
            return 3
        else:
            return 2

def apply_timing_correction(time_key):
    """Apply V5 timing correction"""
    hour, minute = map(int, time_key.split(':'))
    corrected_minute = minute + V5_CONFIG["TIMING_OFFSET_MINUTES"]
    
    if corrected_minute < 0:
        corrected_hour = hour - 1 if hour > 0 else 23
        corrected_minute = 60 + corrected_minute
    elif corrected_minute >= 60:
        corrected_hour = hour + 1 if hour < 23 else 0
        corrected_minute = corrected_minute - 60
    else:
        corrected_hour = hour
    
    return f"{{corrected_hour:02d}}:{{corrected_minute:02d}}"

def get_next_optimal_time(current_time):
    """Find next optimal playing time after current time"""
    current_hour, current_minute = map(int, current_time.split(':'))
    current_minutes = current_hour * 60 + current_minute
    
    best_time = None
    min_wait = float('inf')
    
    for opt_time in OPTIMAL_TIMES:
        opt_hour, opt_minute = map(int, opt_time.split(':'))
        opt_minutes = opt_hour * 60 + opt_minute
        
        # Calculate wait time (handle next day)
        if opt_minutes <= current_minutes:
            wait_minutes = (24 * 60) - current_minutes + opt_minutes
        else:
            wait_minutes = opt_minutes - current_minutes
        
        if wait_minutes < min_wait:
            min_wait = wait_minutes
            best_time = opt_time
    
    return {{
        "next_optimal_time": best_time,
        "wait_minutes": min_wait,
        "wait_hours": min_wait // 60,
        "wait_mins_remainder": min_wait % 60
    }}

# Export data for external use
EXPORT_DATA = {{
    "config": V5_CONFIG,
    "patterns": TIME_PATTERNS,
    "optimal_times": OPTIMAL_TIMES,
    "always_hot": ALWAYS_HOT_NUMBERS,
    "always_cold": ALWAYS_COLD_NUMBERS
}}

if __name__ == "__main__":
    print("Keno Patterns V5 Module Loaded Successfully!")
    print(f"Total analyzed draws: {{TOTAL_DRAWS}}")
    print(f"Optimal times available: {{len(OPTIMAL_TIMES)}}")
    print(f"Top 3 optimal times: {{OPTIMAL_TIMES[:3]}}")
'''

        with open('keno_patterns_v5.py', 'w') as f:
            f.write(python_config)

    def run_complete_v5_analysis(self):
        """Run the complete V5 analysis pipeline"""
        print("🚀 Starting Advanced Keno Time Analysis V5")
        print("🎯 Features: Timing correction, 1-8 ball flexibility, enhanced confidence")
        print("=" * 80)

        # Load and prepare data
        if not self.load_and_prepare_data():
            print("❌ Data loading failed!")
            return False

        # Run V5 analysis components
        print("\n📊 Running V5 Analysis Components...")
        self.analyze_exact_time_patterns_v5()
        self.analyze_time_window_patterns_v5()
        self.identify_optimal_times_v5()

        # Generate V5 recommendations
        print("\n🎲 Generating V5 Recommendations...")
        recommendations = self.generate_v5_recommendations()

        # Export V5 results
        print("\n💾 Exporting V5 Results...")
        self.export_v5_analysis_results()

        # Display V5 summary
        self._display_v5_summary()

        return True

    def _display_v5_summary(self):
        """Display comprehensive V5 analysis summary"""
        print("\n🎉 V5 ANALYSIS COMPLETE!")
        print("=" * 80)
        print("📋 V5 Analysis Summary:")
        print(f"   ✅ Analyzed {len(self.df):,} total draws")
        print(f"   ⏰ Identified {len(self.time_patterns)} specific time patterns")
        print(f"   🕐 Analyzed {len(self.time_window_patterns)} time windows") 
        print(f"   🎯 Identified {len(self.optimal_times)} optimal playing times")
        print(f"   🔧 Applied {self.V5_CONFIG['TIMING_OFFSET_MINUTES']}-minute timing correction")
        print(f"   🎱 Supports 1-8 ball selection with multipliers up to {max(self.V5_CONFIG['MULTIPLIERS'].values())}x")

        print(f"\n🏆 TOP 5 V5 OPTIMAL TIMES:")
        print("-" * 50)
        for i, (time_key, scores) in enumerate(list(self.optimal_times.items())[:5]):
            pattern = self.time_patterns[time_key]
            confidence = self._calculate_v5_confidence(pattern, time_key)
            print(f"  {i+1}. {time_key} → {scores['corrected_time']}")
            print(f"      📊 Score: {scores['total_score']:.1f} | Confidence: {confidence:.1f}%")
            print(f"      🔥 Hot numbers: {pattern['hot_numbers'][:6]}")
            print(f"      📈 {pattern['total_draws']} draws | {pattern['consistency_score']:.1f}% consistency")
            print()

        print(f"🎯 V5 RECOMMENDATIONS FOR DIFFERENT BALL COUNTS:")
        print("-" * 50)
        best_time = list(self.optimal_times.keys())[0]
        for ball_count in [1, 2, 4, 6, 8]:
            multiplier = self.V5_CONFIG['MULTIPLIERS'][ball_count]
            pattern = self.time_patterns[best_time]
            numbers = pattern['hot_numbers'][:ball_count]
            print(f"  🎱 {ball_count} balls: {numbers} → {multiplier}x multiplier")

        print(f"\n📁 V5 FILES GENERATED:")
        print("-" * 30)
        print("  📄 keno_time_analysis_v5.json - Complete analysis data")
        print("  📄 keno_config_v5.js - JavaScript configuration for HTML V5 system")
        print("  📄 keno_patterns_v5.py - Python module for backend integration")

        print(f"\n🎊 Ready for V5 System Integration!")
        print("=" * 80)


def main():
    """Main execution function for V5 analysis"""
    CSV_FILE_PATH = "keno_final_cleaned.csv"  # Update with your CSV file path

    print("🎯 Advanced Time-Based Keno Pattern Analyzer V5")
    print("🚀 Full compatibility with Keno Time Predictor V5 HTML System")
    print("=" * 80)
    print(f"📁 Target file: {CSV_FILE_PATH}")
    print("⚙️  V5 Features: Timing correction, 1-8 ball selection, enhanced confidence")
    print()

    # Initialize V5 analyzer
    analyzer = TimeBasedKenoAnalyzerV5(CSV_FILE_PATH)

    # Run complete V5 analysis
    success = analyzer.run_complete_v5_analysis()

    if success:
        print(f"\n✅ V5 ANALYSIS SUCCESSFUL!")
        print(f"🎊 All V5 configuration files generated and ready!")
        print(f"🔗 Perfect compatibility with your V5 HTML system!")
        
        # Show integration instructions
        print(f"\n📋 INTEGRATION INSTRUCTIONS:")
        print(f"-" * 40)
        print(f"1. 📄 Replace old config with keno_config_v5.js in your HTML")
        print(f"2. 🔄 Update KENO_TIME_CONFIG_V5 variable reference")
        print(f"3. 🎯 Your V5 system is now fully data-driven!")
        print(f"4. 🧪 Test with different ball counts (1-8) and timing corrections")
        
    else:
        print(f"\n❌ V5 Analysis failed. Please check your CSV file path and format.")

    print("\n" + "=" * 80)
    print("🎉 Keno Analyzer V5 - Ready to power your prediction system! 🚀")


if __name__ == "__main__":
    main()