import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/audio/training_tools_service.dart';
import '../../../core/providers.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';

class WhistleModalSheet extends ConsumerStatefulWidget {
  const WhistleModalSheet({super.key});

  @override
  ConsumerState<WhistleModalSheet> createState() => _WhistleModalSheetState();
}

class _WhistleModalSheetState extends ConsumerState<WhistleModalSheet> {
  double _frequency = 16000;
  bool _isPlaying = false;

  void _toggleWhistle() {
    final tools = ref.read(trainingToolsProvider);
    if (_isPlaying) {
      tools.stopWhistle();
      setState(() => _isPlaying = false);
    } else {
      tools.startWhistle(frequencyHz: _frequency.toInt());
      setState(() => _isPlaying = true);
    }
  }

  void _selectPreset(WhistlePreset preset) {
    setState(() => _frequency = preset.frequencyHz.toDouble());
    ref.read(trainingToolsProvider).setWhistleFrequency(preset.frequencyHz);
    if (_isPlaying) {
      ref.read(trainingToolsProvider).startWhistle(frequencyHz: preset.frequencyHz);
    }
  }

  @override
  void dispose() {
    ref.read(trainingToolsProvider).stopWhistle();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.surfaceDark : AppColors.surfaceLight;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Container(
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: textSecondary.withOpacity(0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text('Ультразвуковой свисток', style: AppTypography.titleLarge(textPrimary)),
          const SizedBox(height: 6),
          Text(
            'Собаки слышат ультразвук до 45 000 Гц. Человек слышит до ~16 000 Гц.',
            textAlign: TextAlign.center,
            style: AppTypography.bodySmall(textSecondary),
          ),
          const SizedBox(height: 20),

          // Current Frequency Display
          Text(
            '${_frequency.toInt()} Гц',
            style: AppTypography.displayMedium(AppColors.infoBlue),
          ),
          const SizedBox(height: 8),

          // Frequency Slider
          Slider(
            value: _frequency,
            min: 12000,
            max: 20000,
            divisions: 16,
            activeColor: AppColors.infoBlue,
            label: '${_frequency.toInt()} Гц',
            onChanged: (val) {
              setState(() => _frequency = val);
              ref.read(trainingToolsProvider).setWhistleFrequency(val.toInt());
            },
          ),
          const SizedBox(height: 12),

          // Presets
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: WhistlePreset.values.map((p) {
              final isSelected = _frequency.toInt() == p.frequencyHz;
              return ChoiceChip(
                label: Text(p.label, style: const TextStyle(fontSize: 12)),
                selected: isSelected,
                selectedColor: AppColors.infoBlue.withOpacity(0.2),
                onSelected: (_) => _selectPreset(p),
              );
            }).toList(),
          ),
          const SizedBox(height: 28),

          // Big Whistle Action Button
          GestureDetector(
            onTap: _toggleWhistle,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              width: 110,
              height: 110,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _isPlaying ? AppColors.infoBlue : AppColors.infoBlue.withOpacity(0.12),
                border: Border.all(color: AppColors.infoBlue, width: 2),
                boxShadow: _isPlaying
                    ? [
                        BoxShadow(
                          color: AppColors.infoBlue.withOpacity(0.4),
                          blurRadius: 20,
                          spreadRadius: 4,
                        ),
                      ]
                    : null,
              ),
              child: Center(
                child: Icon(
                  _isPlaying ? Icons.stop_rounded : Icons.volume_up_rounded,
                  size: 48,
                  color: _isPlaying ? Colors.white : AppColors.infoBlue,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text(
            _isPlaying ? 'Свисток активен. Нажмите для остановки' : 'Нажмите для воспроизведения сигнала',
            style: AppTypography.bodySmall(textSecondary),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}
