import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import 'onboarding_controller.dart';

class VoiceInputSheet extends ConsumerStatefulWidget {
  final VoidCallback onExtracted;

  const VoiceInputSheet({super.key, required this.onExtracted});

  @override
  ConsumerState<VoiceInputSheet> createState() => _VoiceInputSheetState();
}

class _VoiceInputSheetState extends ConsumerState<VoiceInputSheet> {
  late final AudioRecorder _audioRecorder;
  bool _isRecording = false;
  String? _recordedPath;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    final hasPermission = await _audioRecorder.hasPermission();
    if (!hasPermission) return;

    final tempDir = await getTemporaryDirectory();
    final path = '${tempDir.path}/voice_profile_${DateTime.now().millisecondsSinceEpoch}.m4a';

    await _audioRecorder.start(
      const RecordConfig(encoder: AudioEncoder.aacLc, bitRate: 128000),
      path: path,
    );

    setState(() {
      _isRecording = true;
      _recordedPath = path;
    });
  }

  Future<void> _stopAndProcess() async {
    final path = await _audioRecorder.stop();
    setState(() => _isRecording = false);

    if (path != null) {
      final success = await ref
          .read(onboardingControllerProvider.notifier)
          .extractFromVoice(File(path));

      if (success && mounted) {
        widget.onExtracted();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(onboardingControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.surfaceDark : AppColors.surfaceLight;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Container(
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Расскажите о вашей собаке',
            style: AppTypography.titleLarge(textPrimary),
          ),
          const SizedBox(height: 10),
          Text(
            'Например: «У меня корги Арчи, 5 месяцев, очень активный, грызет обувь и тянет поводок»',
            textAlign: TextAlign.center,
            style: AppTypography.bodyMedium(textSecondary),
          ),
          const SizedBox(height: 36),

          // Microphone Button
          GestureDetector(
            onTap: state.isVoiceExtracting
                ? null
                : () {
                    if (_isRecording) {
                      _stopAndProcess();
                    } else {
                      _startRecording();
                    }
                  },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: _isRecording ? 100 : 84,
              height: _isRecording ? 100 : 84,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _isRecording ? AppColors.errorRed : AppColors.primary,
                boxShadow: [
                  BoxShadow(
                    color: (_isRecording ? AppColors.errorRed : AppColors.primary).withOpacity(0.35),
                    blurRadius: 25,
                    spreadRadius: _isRecording ? 8 : 2,
                  ),
                ],
              ),
              child: state.isVoiceExtracting
                  ? const Center(
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3),
                    )
                  : Icon(
                      _isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                      size: 42,
                      color: Colors.white,
                    ),
            ),
          ),
          const SizedBox(height: 24),

          Text(
            state.isVoiceExtracting
                ? 'ИИ анализирует рассказ и заполняет профиль...'
                : _isRecording
                    ? 'Идет запись... Нажмите Стоп по окончании'
                    : 'Нажмите на микрофон для начала записи',
            style: AppTypography.bodySmall(textSecondary),
          ),
        ],
      ),
    );
  }
}
