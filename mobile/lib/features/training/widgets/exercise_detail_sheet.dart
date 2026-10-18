import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../data/models/training_task.dart';
import '../training_controller.dart';

class ExerciseDetailSheet extends ConsumerStatefulWidget {
  final TrainingTaskModel task;

  const ExerciseDetailSheet({super.key, required this.task});

  @override
  ConsumerState<ExerciseDetailSheet> createState() => _ExerciseDetailSheetState();
}

class _ExerciseDetailSheetState extends ConsumerState<ExerciseDetailSheet> {
  int _timerSeconds = 0;
  bool _isTimerActive = false;

  @override
  void initState() {
    super.initState();
    _timerSeconds = (widget.task.durationMinutes ?? 5) * 60;

    final tools = ref.read(trainingToolsProvider);
    tools.onTimerTick = (rem) {
      if (mounted) setState(() => _timerSeconds = rem);
    };
    tools.onTimerFinished = () {
      if (mounted) setState(() => _isTimerActive = false);
    };
  }

  void _toggleTimer() {
    final tools = ref.read(trainingToolsProvider);
    if (_isTimerActive) {
      tools.stopTimer();
      setState(() => _isTimerActive = false);
    } else {
      tools.startTimer(_timerSeconds > 0 ? _timerSeconds : (widget.task.durationMinutes ?? 5) * 60);
      setState(() => _isTimerActive = true);
    }
  }

  String _formatTimer(int totalSeconds) {
    final m = totalSeconds ~/ 60;
    final s = totalSeconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
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
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
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
            const SizedBox(height: 18),

            // Header Row: Title & Badges
            Row(
              children: [
                Expanded(
                  child: Text(widget.task.title, style: AppTypography.titleLarge(textPrimary)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    widget.task.difficultyLabel,
                    style: AppTypography.bodySmall(AppColors.primary).copyWith(fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Exercise Countdown Timer Widget
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
              decoration: BoxDecoration(
                color: AppColors.cardBorderLight.withOpacity(0.4),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.timer_outlined, color: AppColors.primary, size: 24),
                      const SizedBox(width: 10),
                      Text(
                        _formatTimer(_timerSeconds),
                        style: AppTypography.titleLarge(textPrimary).copyWith(fontFeatures: const []),
                      ),
                    ],
                  ),
                  ElevatedButton.icon(
                    onPressed: _toggleTimer,
                    icon: Icon(_isTimerActive ? Icons.pause : Icons.play_arrow_rounded, size: 18),
                    label: Text(_isTimerActive ? 'Пауза' : 'Старт таймера'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(130, 42),
                      backgroundColor: _isTimerActive ? AppColors.errorRed : AppColors.primary,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Section 1: Зачем учить
            _buildSection(
              title: '🎯 Зачем учить это упражнение',
              content: widget.task.description ??
                  'Это базовый навык самоконтроля. Собака учится концентрироваться на владельце даже при наличии отвлекающих факторов.',
              textPrimary: textPrimary,
              textSecondary: textSecondary,
            ),
            const SizedBox(height: 20),

            // Section 2: Пошаговый алгоритм
            _buildSection(
              title: '📋 Пошаговый алгоритм',
              content:
                  '1. Приготовьте мелкие лакомства в руке.\n2. Дождитесь зрительного контакта с собакой.\n3. Сделайте клик в момент правильного действия и сразу дайте лакомство.\n4. Повторите 5-7 раз подряд и закончите на позитивной ноте.',
              textPrimary: textPrimary,
              textSecondary: textSecondary,
            ),
            const SizedBox(height: 20),

            // Section 3: Частые ошибки
            _buildSection(
              title: '⚠️ Частые ошибки',
              content:
                  '• Не повторяйте команду много раз, если собака отвлеклась.\n• Не делайте клик слишком поздно — задержка более 2 секунд стирает связь с похвалой.\n• Не ругайте питомца при ошибке: просто сделайте шаг назад и повторите легче.',
              textPrimary: textPrimary,
              textSecondary: textSecondary,
            ),
            const SizedBox(height: 28),

            // Complete Task Action
            ElevatedButton(
              onPressed: () {
                ref.read(trainingControllerProvider.notifier).toggleTask(widget.task.id);
                Navigator.of(context).pop();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.task.isCompleted ? AppColors.textMutedLight : AppColors.successGreen,
              ),
              child: Text(widget.task.isCompleted ? 'Отменить выполнение' : '✅ Отметить как выполненное'),
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required String content,
    required Color textPrimary,
    required Color textSecondary,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTypography.titleMedium(textPrimary)),
        const SizedBox(height: 8),
        Text(content, style: AppTypography.bodyMedium(textSecondary).copyWith(height: 1.5)),
      ],
    );
  }
}
