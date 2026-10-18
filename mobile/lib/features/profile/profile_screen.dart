import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/pet.dart';
import '../../data/models/user_profile.dart';
import '../auth/telegram_connect_sheet.dart';
import '../coach/widgets/premium_upsell_sheet.dart';
import 'profile_controller.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  void _showTelegramConnect(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => TelegramConnectSheet(
        onSuccess: () => Navigator.of(ctx).pop(),
      ),
    );
  }

  void _showPremiumModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => const PremiumUpsellSheet(),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(profileControllerProvider);
    final user = state.user;
    final pet = state.pet;

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Scaffold(
      appBar: AppBar(
        title: Text('Профиль и настройки', style: AppTypography.titleLarge(textPrimary)),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        children: [
          // 1. Pet Profile Card
          _buildPetCard(context, pet, textPrimary, textSecondary),
          const SizedBox(height: 16),

          // 2. Premium Status Card
          _buildPremiumCard(context, user, textPrimary, textSecondary),
          const SizedBox(height: 16),

          // 3. Telegram Link Status
          _buildTelegramLinkCard(context, user, textPrimary, textSecondary),
          const SizedBox(height: 16),

          // 4. Smart Notifications
          _buildNotificationsCard(context, ref, state, user, textPrimary, textSecondary),
          const SizedBox(height: 16),

          // 5. Referral Hub Card
          _buildReferralCard(context, user, textPrimary, textSecondary),
          const SizedBox(height: 24),

          // Logout Button
          OutlinedButton(
            onPressed: () => ref.read(profileControllerProvider.notifier).logout(),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.errorRed,
              side: const BorderSide(color: AppColors.errorRed),
            ),
            child: const Text('Выйти из аккаунта'),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildPetCard(BuildContext context, PetModel? pet, Color textPrimary, Color textSecondary) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.primaryGradient,
              ),
              child: const Center(child: Text('🐕', style: TextStyle(fontSize: 30))),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(pet?.name ?? 'Питомец', style: AppTypography.titleLarge(textPrimary)),
                  const SizedBox(height: 2),
                  Text('${pet?.breed ?? "Порода не указана"} • ${pet?.ageCategory ?? ""}', style: AppTypography.bodySmall(textSecondary)),
                  const SizedBox(height: 4),
                  Text('🔥 ${pet?.trainingDays ?? 0} дней тренировок', style: AppTypography.bodySmall(AppColors.streakOrange)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPremiumCard(BuildContext context, UserProfile? user, Color textPrimary, Color textSecondary) {
    final isPremium = user?.isPremium ?? false;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: isPremium
            ? AppColors.premiumGradient
            : LinearGradient(
                colors: [AppColors.cardBorderLight.withOpacity(0.5), AppColors.cardBorderLight.withOpacity(0.2)],
              ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(shape: BoxShape.circle, color: Colors.white.withOpacity(0.9)),
            child: const Text('⭐', style: TextStyle(fontSize: 26)),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isPremium ? 'Pepito Premium активен' : 'Pepito Premium',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: isPremium ? Colors.black87 : textPrimary),
                ),
                Text(
                  isPremium
                      ? 'Безлимитный AI-кинолог и видео-анализ'
                      : 'Видео-разбор команд и безлимит вопросов',
                  style: TextStyle(fontSize: 13, color: isPremium ? Colors.black54 : textSecondary),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: () => _showPremiumModal(context),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(90, 36),
              padding: const EdgeInsets.symmetric(horizontal: 14),
              backgroundColor: isPremium ? Colors.black87 : AppColors.primary,
            ),
            child: Text(isPremium ? 'Инфо' : 'Купить', style: const TextStyle(fontSize: 13)),
          ),
        ],
      ),
    );
  }

  Widget _buildTelegramLinkCard(BuildContext context, UserProfile? user, Color textPrimary, Color textSecondary) {
    final isLinked = user?.isTelegramLinked ?? false;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFF24A1DE).withOpacity(0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.send_rounded, color: Color(0xFF24A1DE), size: 24),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isLinked ? 'Telegram привязан' : 'Telegram не привязан',
                    style: AppTypography.titleMedium(textPrimary),
                  ),
                  Text(
                    isLinked
                        ? 'Данные синхронизируются с @${user?.username ?? user?.telegramId}'
                        : 'Свяжите аккаунт, чтобы бот знал вашего питомца',
                    style: AppTypography.bodySmall(textSecondary),
                  ),
                ],
              ),
            ),
            if (!isLinked)
              ElevatedButton(
                onPressed: () => _showTelegramConnect(context),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(90, 36),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                ),
                child: const Text('Связать', style: TextStyle(fontSize: 13)),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationsCard(
    BuildContext context,
    WidgetRef ref,
    ProfileState state,
    UserProfile? user,
    Color textPrimary,
    Color textSecondary,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.notifications_active_outlined, color: AppColors.primary, size: 22),
                const SizedBox(width: 10),
                Text('Умные напоминания', style: AppTypography.titleMedium(textPrimary)),
              ],
            ),
            const SizedBox(height: 12),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Push-уведомления на телефон', style: AppTypography.bodyMedium(textPrimary)),
              value: state.pushNotificationsEnabled,
              onChanged: (val) => ref.read(profileControllerProvider.notifier).togglePushNotifications(val),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Напоминания в Telegram-боте', style: AppTypography.bodyMedium(textPrimary)),
              value: state.telegramNotificationsEnabled,
              onChanged: (val) => ref.read(profileControllerProvider.notifier).toggleTelegramNotifications(val),
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.cardBorderLight.withOpacity(0.4),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Text('💡', style: TextStyle(fontSize: 16)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Если тренировка за день уже выполнена, напоминания автоматически отменяются.',
                      style: AppTypography.bodySmall(textSecondary),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildReferralCard(BuildContext context, UserProfile? user, Color textPrimary, Color textSecondary) {
    final refLink = user?.telegramId != null
        ? 'https://t.me/${ApiConstants.botUsername}?start=ref_${user!.telegramId}'
        : 'https://pepitopet.ru/app';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text('🎁 ', style: TextStyle(fontSize: 20)),
                Text('Позови друга — получи Premium', style: AppTypography.titleMedium(textPrimary)),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              'Подарите другу 3 дня Premium. При его регистрации вы тоже получите +3 дня подписки!',
              style: AppTypography.bodySmall(textSecondary),
            ),
            const SizedBox(height: 16),

            // Milestone chips
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildMilestoneBadge('3 друга', '+7 дней'),
                _buildMilestoneBadge('5 друзей', '+14 дней'),
                _buildMilestoneBadge('10 друзей', '+30 дней'),
                _buildMilestoneBadge('25 друзей', '+90 дней'),
              ],
            ),
            const SizedBox(height: 16),

            ElevatedButton.icon(
              onPressed: () async {
                final uri = Uri.parse(refLink);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri, mode: LaunchMode.externalApplication);
                }
              },
              icon: const Icon(Icons.share_rounded, size: 18),
              label: const Text('Поделиться ссылкой с другом'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMilestoneBadge(String friends, String reward) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.primary.withOpacity(0.2)),
      ),
      child: Text(
        '$friends: $reward',
        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary),
      ),
    );
  }
}
