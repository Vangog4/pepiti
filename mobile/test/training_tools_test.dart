import 'package:flutter_test/flutter_test.dart';
import 'package:pepito_mobile/core/audio/training_tools_service.dart';

void main() {
  group('Training Tools Service Tests', () {
    test('Whistle presets definitions', () {
      expect(WhistlePreset.come.frequencyHz, 14000);
      expect(WhistlePreset.sit.frequencyHz, 16000);
      expect(WhistlePreset.attention.frequencyHz, 18000);
      expect(WhistlePreset.highFrequency.frequencyHz, 20000);
    });

    test('Frequency clamping logic', () {
      int clampFreq(int hz) => hz.clamp(12000, 20000);

      expect(clampFreq(8000), 12000);
      expect(clampFreq(15500), 15500);
      expect(clampFreq(25000), 20000);
    });

    test('Timer string formatting', () {
      String formatTimer(int totalSeconds) {
        final m = totalSeconds ~/ 60;
        final s = totalSeconds % 60;
        return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
      }

      expect(formatTimer(300), '05:00');
      expect(formatTimer(45), '00:45');
      expect(formatTimer(0), '00:00');
      expect(formatTimer(65), '01:05');
    });
  });
}
