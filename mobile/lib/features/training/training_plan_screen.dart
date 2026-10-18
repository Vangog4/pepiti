import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/training_task.dart';
import 'training_controller.dart';
import 'widgets/clicker_modal_sheet.dart';
import 'widgets/exercise_detail_sheet.dart';
import 'widgets/whistle_modal_sheet.dart';

class TrainingPlanScreen extends ConsumerWidget {
  const TrainingPlanScreen({super.key});

  final List<String> _dayNames = const ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  void _openExerciseDetail(BuildContext context, TrainingTaskModel task) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => ExerciseDetailSheet(task: task),
    );
  }

  void _openClicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => const ClickerModalSheet(),
    );
  }

  void _openWhistle(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => const WhistleModalSheet(),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(trainingControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    final currentWeekday = DateTime.now().weekday;
    final dayTasks = state.tasksForSelectedDay;

    return Scaffold(
      appBar: AppBar(
        title: Text('План тренировок', style: AppTypography.titleLarge(textPrimary)),
        actions: [
          IconButton(
            icon: state.isPdfDownloading
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.picture_as_pdf_outlined, color: AppColors.primary),
            tooltip: 'Скачать PDF план',
            onPressed: state.isPdfDownloading
                ? null
                : () => ref.read(trainingControllerProvider.notifier).downloadPdf(),
          ),
        ],
      ),
      body: Column(
        children: [
          const SizedBox(height: 12),

          // Horizontal 7-Day Selector Bar
          SizedBox(
            height: 76,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: 7,
              itemBuilder: (context, index) {
                final dayNumber = index + 1;
                final isSelected = state.selectedDayOfWeek == dayNumber;
                final isToday = currentWeekday == dayNumber;

                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: InkWell(
                    onTap: () => ref.read(trainingControllerProvider.notifier).selectDayOfWeek(dayNumber),
                    borderRadius: BorderRadius.circular(16),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 50,
                      decoration: BoxDecoration(
                        color: isSelected
                            ? AppColors.primary
                            : isToday
                                ? AppColors.primary.withOpacity(0.12)
                                : AppColors.cardBorderLight.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isSelected
                              ? AppColors.primary
                              : isToday
                                  ? AppColors.primary
                                  : Colors.transparent,
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            _dayNames[index],
                            style: AppTypography.bodySmall(
                              isSelected ? Colors.white : textSecondary,
                            ).copyWith(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '$dayNumber',
                            style: AppTypography.titleMedium(
                              isSelected ? Colors.white : textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 16),

          // Tools shortcut bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _openClicker(context),
                    icon: const Text('🔊', style: TextStyle(fontSize: 16)),
                    label: const Text('Кликер'),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(0, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _openWhistle(context),
                    icon: const Text('📣', style: TextStyle(fontSize: 16)),
                    label: const Text('Свисток'),
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(0, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Exercise list for selected day
          Expanded(
            child: state.isLoading
                ? const Center(child: CircularProgressIndicator())
                : dayTasks.isEmpty
                    ? Center(
                        child: Text(
                          'На этот день упражнений не запланировано',
                          style: AppTypography.bodyMedium(textSecondary),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                        itemCount: dayTasks.length,
                        itemBuilder: (context, index) {
                          final task = dayTasks[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              leading: IconButton(
                                icon: Icon(
                                  task.isCompleted ? Icons.check_circle_rounded : Icons.radio_button_unchecked,
                                  color: task.isCompleted ? AppColors.successGreen : AppColors.cardBorderLight,
                                  size: 28,
                                ),
                                onPressed: () =>
                                    ref.read(trainingControllerProvider.notifier).toggleTask(task.id),
                              ),
                              title: Text(
                                task.title,
                                style: AppTypography.titleMedium(textPrimary).copyWith(
                                  decoration: task.isCompleted ? TextDecoration.lineThrough : null,
                                ),
                              ),
                              subtitle: Row(
                                children: [
                                  Icon(Icons.timer_outlined, size: 14, color: textSecondary),
                                  const SizedBox(width: 4),
                                  Text('${task.durationMinutes ?? 5} мин', style: AppTypography.bodySmall(textSecondary)),
                                  const SizedBox(width: 10),
                                  Text(task.difficultyLabel, style: AppTypography.bodySmall(AppColors.primary)),
                                ],
                              ),
                              trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 16),
                              onTap: () => _openExerciseDetail(context, task),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
