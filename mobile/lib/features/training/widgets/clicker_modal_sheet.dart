import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';

class ClickerModalSheet extends ConsumerStatefulWidget {
  const ClickerModalSheet({super.key});

  @override
  ConsumerState<ClickerModalSheet> createState() => _ClickerModalSheetState();
}

class _ClickerModalSheetState extends ConsumerState<ClickerModalSheet> {
  int _clickCount = 0;
  bool _isPressed = false;

  void _handleClick() {
    setState(() {
      _clickCount++;
      _isPressed = true;
    });

    ref.read(trainingToolsProvider).click();

    Future.delayed(const Duration(milliseconds: 120), () {
      if (mounted) setState(() => _isPressed = false);
    });
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
          // Drag handle
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

          Text('Дрессировочный кликер', style: AppTypography.titleLarge(textPrimary)),
          const SizedBox(height: 6),
          Text(
            'Нажимайте в момент правильного действия собаки, затем сразу давайте лакомство.',
            textAlign: TextAlign.center,
            style: AppTypography.bodySmall(textSecondary),
          ),
          const SizedBox(height: 12),

          // Click Counter Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'Кликов: $_clickCount',
              style: AppTypography.bodySmall(AppColors.primary).copyWith(fontWeight: FontWeight.w700),
            ),
          ),
          const SizedBox(height: 36),

          // Big Tactile Clicker Button
          GestureDetector(
            onTapDown: (_) => _handleClick(),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 80),
              width: 170,
              height: 170,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: _isPressed
                      ? [AppColors.primaryDark, AppColors.primary]
                      : [AppColors.primary, AppColors.primaryLight],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: _isPressed
                    ? [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.4),
                          blurRadius: 10,
                          offset: const Offset(0, 2),
                        ),
                      ]
                    : [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.35),
                          blurRadius: 28,
                          offset: const Offset(0, 10),
                        ),
                      ],
              ),
              child: Center(
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withOpacity(0.18),
                    border: Border.all(color: Colors.white.withOpacity(0.4), width: 2),
                  ),
                  child: const Center(
                    child: Text('🔊', style: TextStyle(fontSize: 48)),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 36),

          Text(
            'Нажмите на кнопку для клика с виброоткликом',
            style: AppTypography.bodySmall(textSecondary),
          ),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}
