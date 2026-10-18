import 'dart:async';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_haptic_feedback/flutter_haptic_feedback.dart';

enum WhistlePreset {
  come(14000, 'Ко мне!'),
  sit(16000, 'Сидеть/Стоп'),
  attention(18000, 'Внимание'),
  highFrequency(20000, 'Ультразвук');

  final int frequencyHz;
  final String label;
  const WhistlePreset(this.frequencyHz, this.label);
}

class TrainingToolsService {
  final AudioPlayer _clickerPlayer = AudioPlayer();
  final AudioPlayer _whistlePlayer = AudioPlayer();

  bool _isWhistlePlaying = false;
  bool get isWhistlePlaying => _isWhistlePlaying;

  int _whistleFrequency = 16000;
  int get whistleFrequency => _whistleFrequency;

  // Exercise countdown timer state
  Timer? _countdownTimer;
  int _remainingSeconds = 0;
  int get remainingSeconds => _remainingSeconds;
  bool get isTimerRunning => _countdownTimer != null && _countdownTimer!.isActive;

  void Function(int remaining)? onTimerTick;
  void Function()? onTimerFinished;

  TrainingToolsService() {
    _initAudio();
  }

  Future<void> _initAudio() async {
    // Configure player mode for sub-25ms lowest latency
    await _clickerPlayer.setPlayerMode(PlayerMode.lowLatency);
    await _clickerPlayer.setReleaseMode(ReleaseMode.stop);

    await _whistlePlayer.setPlayerMode(PlayerMode.mediaPlayer);
    await _whistlePlayer.setReleaseMode(ReleaseMode.loop);
  }

  /// Triggers instant physical-like clicker with sound and strong haptic feedback
  Future<void> click() async {
    // Haptic kick immediately
    await FlutterHapticFeedback.vibrate(HapticsType.heavy);

    // Audio click trigger
    try {
      await _clickerPlayer.play(AssetSource('sounds/clicker.mp3'));
    } catch (_) {
      // Fallback secondary haptic pulse if audio fails
      await FlutterHapticFeedback.vibrate(HapticsType.selection);
    }
  }

  /// Sets whistle frequency in Hz (12 000 to 20 000)
  void setWhistleFrequency(int hz) {
    _whistleFrequency = hz.clamp(12000, 20000);
  }

  /// Starts whistle sound loop
  Future<void> startWhistle({int? frequencyHz}) async {
    if (frequencyHz != null) {
      setWhistleFrequency(frequencyHz);
    }
    _isWhistlePlaying = true;
    await FlutterHapticFeedback.vibrate(HapticsType.light);
    try {
      await _whistlePlayer.play(AssetSource('sounds/whistle_${_whistleFrequency}hz.mp3'));
    } catch (_) {}
  }

  /// Stops whistle
  Future<void> stopWhistle() async {
    _isWhistlePlaying = false;
    await _whistlePlayer.stop();
  }

  // --- Exercise Timer ---

  void startTimer(int seconds) {
    stopTimer();
    _remainingSeconds = seconds;
    onTimerTick?.call(_remainingSeconds);

    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 1) {
        _remainingSeconds--;
        onTimerTick?.call(_remainingSeconds);
      } else {
        _remainingSeconds = 0;
        stopTimer();
        onTimerTick?.call(0);
        onTimerFinished?.call();
        // Vibrate upon finish
        FlutterHapticFeedback.vibrate(HapticsType.success);
      }
    });
  }

  void stopTimer() {
    _countdownTimer?.cancel();
    _countdownTimer = null;
  }

  void dispose() {
    _countdownTimer?.cancel();
    _clickerPlayer.dispose();
    _whistlePlayer.dispose();
  }
}
