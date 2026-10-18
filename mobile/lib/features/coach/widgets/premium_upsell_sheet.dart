import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';

class PremiumUpsellSheet extends StatelessWidget {
  final String featureTitle;

  const PremiumUpsellSheet({
    super.key,
    this.featureTitle = 'Видео-разбор выполнения команд',
  });

  Future<void> _openTelegramStarsBot() async {
    final uri = Uri.parse('https://t.me/${ApiConstants.botUsername}?start=premium');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
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
          const SizedBox(height: 20),

          // Crown Icon
          Center(
            child: Container(
              width: 64,
              height: 64,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.premiumGradient,
              ),
              child: const Center(
                child: Text('⭐', style: TextStyle(fontSize: 32)),
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text(
            'Pepito Premium',
            textAlign: TextAlign.center,
            style: AppTypography.displayMedium(textPrimary),
          ),
          const SizedBox(height: 6),
          Text(
            featureTitle,
            textAlign: TextAlign.center,
            style: AppTypography.titleMedium(AppColors.primary),
          ),
          const SizedBox(height: 20),

          // Benefits List
          _buildBenefitItem('📹 Анализ видео тренировок с камеры (тайминг и ошибки)', textPrimary),
          _buildBenefitItem('💬 Безлимитные вопросы AI-кинологу 24/7 (вместо 5 в день)', textPrimary),
          _buildBenefitItem('🎙 Голосовой ввод и распознавание аудиосообщений', textPrimary),
          _buildBenefitItem('🧠 Память на 20 сообщений контекста диалога', textPrimary),
          _buildBenefitItem('🎁 Постоянная скидка 10% в магазине лакомств', textPrimary),
          const SizedBox(height: 24),

          // Main Buy Action (Tinkoff / Store)
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // Trigger in-app purchase flow
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
            ),
            child: const Text('Оформить за 590 ₽ / месяц'),
          ),
          const SizedBox(height: 10),

          // Telegram Stars alternative
          OutlinedButton.icon(
            onPressed: () {
              Navigator.of(context).pop();
              _openTelegramStarsBot();
            },
            icon: const Icon(Icons.star_rounded, color: AppColors.premiumGold, size: 20),
            label: const Text('Оплатить дешевле через Telegram Stars (299 ★)'),
          ),
          const SizedBox(height: 8),

          Text(
            'Подписка активируется сразу во всех устройствах и в Telegram-боте.',
            textAlign: TextAlign.center,
            style: AppTypography.bodySmall(textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildBenefitItem(String text, Color textPrimary) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_rounded, color: AppColors.successGreen, size: 20),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: AppTypography.bodyMedium(textPrimary))),
        ],
      ),
    );
  }
}
