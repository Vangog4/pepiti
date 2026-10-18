import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/sync/sync_engine.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/training_task.dart';
import '../training/widgets/clicker_modal_sheet.dart';
import '../training/widgets/whistle_modal_sheet.dart';
import 'home_controller.dart';

class HomeScreen extends ConsumerWidget {
  final Function(int tabIndex)? onNavigateToTab;

  const HomeScreen({super.key, this.onNavigateToTab});

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
    final state = ref.watch(homeControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;
    final pet = state.activePet;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 20,
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.primaryGradient,
              ),
              child: const Center(child: Text('🐶', style: TextStyle(fontSize: 22))),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(pet?.name ?? 'Питомец', style: AppTypography.titleMedium(textPrimary)),
                Text(pet?.breed ?? 'Порода не указана', style: AppTypography.bodySmall(textSecondary)),
              ],
            ),
          ],
        ),
        actions: [
          // Offline / Sync indicator
          if (state.syncStatus == SyncStatus.syncing)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16.0),
              child: SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
            )
          else if (state.syncStatus == SyncStatus.offline)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Icon(Icons.cloud_off_rounded, color: AppColors.errorRed.withOpacity(0.8), size: 20),
            ),
        ],
      ),
      body: state.isLoading && pet == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () => ref.read(homeControllerProvider.notifier).refresh(),
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                children: [
                  // Streak Card
                  _buildStreakCard(context, state, textPrimary),
                  const SizedBox(height: 20),

                  // Quick Tools Bar
                  _buildQuickToolsBar(context),
                  const SizedBox(height: 24),

                  // Today's Plan Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Цель на сегодня', style: AppTypography.titleLarge(textPrimary)),
                      Text(
                        '${state.completedTasksCount} из ${state.todayTasks.length}',
                        style: AppTypography.bodyMedium(AppColors.primary).copyWith(fontWeight: FontWeight.w700),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Task Checklist
                  if (state.todayTasks.isEmpty)
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Center(
                          child: Text(
                            'На сегодня заданий нет. Отличный день для отдыха и прогулки! 🌿',
                            textAlign: TextAlign.center,
                            style: AppTypography.bodyMedium(textSecondary),
                          ),
                        ),
                      ),
                    )
                  else
                    ...state.todayTasks.map((task) => _buildTaskCard(context, ref, task, textPrimary, textSecondary)),

                  const SizedBox(height: 24),

                  // Daily Cynologist Tip Card
                  _buildDailyTipCard(context, pet?.name ?? 'питомца', textPrimary, textSecondary),
                  const SizedBox(height: 40),
                ],
              ),
            ),
    );
  }

  Widget _buildStreakCard(BuildContext context, HomeState state, Color textPrimary) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.streakOrange.withOpacity(0.12),
            AppColors.primaryLight.withOpacity(0.15),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.streakOrange.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: AppColors.streakOrange.withOpacity(0.2),
                  blurRadius: 15,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Center(child: Text('🔥', style: TextStyle(fontSize: 32))),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('${state.streakDays} ', style: AppTypography.streakNumber(AppColors.streakOrange)),
                    Text('дней подряд', style: AppTypography.titleMedium(textPrimary)),
                  ],
                ),
                Text(
                  state.isAllCompletedToday
                      ? 'Все задачи на сегодня выполнены! Вы супер!'
                      : 'Занимайтесь каждый день, чтобы закрепить команды',
                  style: AppTypography.bodySmall(AppColors.textSecondaryLight),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickToolsBar(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _buildToolButton(
            icon: '🔊',
            label: 'Кликер',
            color: AppColors.primary,
            onTap: () => _openClicker(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildToolButton(
            icon: '📣',
            label: 'Свисток',
            color: AppColors.infoBlue,
            onTap: () => _openWhistle(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildToolButton(
            icon: '💬',
            label: 'Кинолог',
            color: AppColors.successGreen,
            onTap: () => onNavigateToTab?.call(2), // Switch to Coach tab
          ),
        ),
      ],
    );
  }

  Widget _buildToolButton({
    required String icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Column(
          children: [
            Text(icon, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 6),
            Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
          ],
        ),
      ),
    );
  }

  Widget _buildTaskCard(
    BuildContext context,
    WidgetRef ref,
    TrainingTaskModel task,
    Color textPrimary,
    Color textSecondary,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => ref.read(homeControllerProvider.notifier).toggleTask(task.id),
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              // Checkbox icon
              AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: task.isCompleted ? AppColors.successGreen : Colors.transparent,
                  border: Border.all(
                    color: task.isCompleted ? AppColors.successGreen : AppColors.cardBorderLight,
                    width: 2,
                  ),
                ),
                child: task.isCompleted
                    ? const Icon(Icons.check, size: 18, color: Colors.white)
                    : null,
              ),
              const SizedBox(width: 16),

              // Title & details
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.title,
                      style: AppTypography.titleMedium(textPrimary).copyWith(
                        decoration: task.isCompleted ? TextDecoration.lineThrough : null,
                        color: task.isCompleted ? textSecondary : textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.timer_outlined, size: 14, color: textSecondary),
                        const SizedBox(width: 4),
                        Text('${task.durationMinutes ?? 5} мин', style: AppTypography.bodySmall(textSecondary)),
                        const SizedBox(width: 12),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            task.difficultyLabel,
                            style: AppTypography.bodySmall(AppColors.primary).copyWith(fontSize: 11),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const Icon(Icons.chevron_right_rounded, color: AppColors.cardBorderLight),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDailyTipCard(BuildContext context, String petName, Color textPrimary, Color textSecondary) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.primaryLight.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('💡', style: TextStyle(fontSize: 20)),
              const SizedBox(width: 8),
              Text('Совет зоопсихолога', style: AppTypography.titleMedium(AppColors.primaryDark)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Всегда поощряйте $petName в первые 1.5 секунды после выполнения команды. Для этого идеально подходят мелкие тренировочные лакомства из утки или говяжьего легкого.',
            style: AppTypography.bodyMedium(textPrimary),
          ),
          const SizedBox(height: 12),
          TextButton(
            onPressed: () => onNavigateToTab?.call(3), // Switch to Shop tab
            style: TextButton.styleFrom(
              padding: EdgeInsets.zero,
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Подобрать лакомства для тренировок', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700)),
                const SizedBox(width: 4),
                const Icon(Icons.arrow_forward_rounded, size: 16, color: AppColors.primary),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
