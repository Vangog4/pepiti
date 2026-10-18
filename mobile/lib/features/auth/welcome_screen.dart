import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import 'auth_controller.dart';
import 'telegram_connect_sheet.dart';

class WelcomeScreen extends ConsumerStatefulWidget {
  final VoidCallback onContinueToOnboarding;
  final VoidCallback onAuthenticated;

  const WelcomeScreen({
    super.key,
    required this.onContinueToOnboarding,
    required this.onAuthenticated,
  });

  @override
  ConsumerState<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends ConsumerState<WelcomeScreen> {
  bool _isLoading = false;

  Future<void> _handleGuestLogin() async {
    setState(() => _isLoading = true);
    final deviceId = 'guest_${DateTime.now().millisecondsSinceEpoch}';
    final success = await ref.read(authControllerProvider.notifier).loginAsGuest(deviceId);
    setState(() => _isLoading = false);

    if (success && mounted) {
      widget.onContinueToOnboarding();
    }
  }

  void _showTelegramConnectSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => TelegramConnectSheet(
        onSuccess: () {
          Navigator.of(ctx).pop();
          widget.onAuthenticated();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Brand Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text('🐾', style: TextStyle(fontSize: 16)),
                        const SizedBox(width: 8),
                        Text(
                          'Pepito Cynology',
                          style: AppTypography.bodySmall(AppColors.primary).copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              // Central Hero Illustration & Headline
              Column(
                children: [
                  Container(
                    width: 140,
                    height: 140,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: AppColors.primaryGradient,
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.25),
                          blurRadius: 30,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: const Center(
                      child: Text('🐕', style: TextStyle(fontSize: 72)),
                    ),
                  ),
                  const SizedBox(height: 32),
                  Text(
                    'Твой карманный\nAI-кинолог',
                    textAlign: TextAlign.center,
                    style: AppTypography.displayLarge(textPrimary),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    'Персональные тренировки собаки, умный кликер с виброоткликом и помощь зоопсихолога 24/7.',
                    textAlign: TextAlign.center,
                    style: AppTypography.bodyLarge(textSecondary),
                  ),
                ],
              ),

              // Action Buttons
              Column(
                children: [
                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleGuestLogin,
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                          )
                        : const Text('Начать дрессировку'),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _showTelegramConnectSheet,
                    icon: const Icon(Icons.send_rounded, size: 20),
                    label: const Text('Войти через Telegram'),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Нажимая «Начать дрессировку», вы принимаете правила сервиса',
                    textAlign: TextAlign.center,
                    style: AppTypography.bodySmall(textSecondary.withOpacity(0.7)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
