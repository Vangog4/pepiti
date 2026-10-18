import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/api_constants.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import 'auth_controller.dart';

class TelegramConnectSheet extends ConsumerStatefulWidget {
  final VoidCallback onSuccess;

  const TelegramConnectSheet({super.key, required this.onSuccess});

  @override
  ConsumerState<TelegramConnectSheet> createState() => _TelegramConnectSheetState();
}

class _TelegramConnectSheetState extends ConsumerState<TelegramConnectSheet> {
  final TextEditingController _codeController = TextEditingController();
  bool _isLoading = false;
  String? _errorText;

  Future<void> _handleConnect() async {
    final code = _codeController.text.trim();
    if (code.length != 6) {
      setState(() => _errorText = 'Введите 6-значный код');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorText = null;
    });

    final success = await ref.read(authControllerProvider.notifier).loginWithTelegramCode(code);

    setState(() => _isLoading = false);

    if (success) {
      widget.onSuccess();
    } else {
      final err = ref.read(authControllerProvider).errorMessage;
      setState(() => _errorText = err ?? 'Неверный код. Попробуйте еще раз');
    }
  }

  Future<void> _openTelegramBot() async {
    final uri = Uri.parse('https://t.me/${ApiConstants.botUsername}?start=connect');
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
      padding: EdgeInsets.only(
        top: 24,
        left: 24,
        right: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
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
          const SizedBox(height: 20),

          Text(
            'Вход через Telegram-бота',
            textAlign: TextAlign.center,
            style: AppTypography.titleLarge(textPrimary),
          ),
          const SizedBox(height: 8),
          Text(
            'Откройте бота @pepitopetbot и отправьте команду /connect для получения 6-значного кода привязки.',
            textAlign: TextAlign.center,
            style: AppTypography.bodyMedium(textSecondary),
          ),
          const SizedBox(height: 24),

          // Code textfield
          TextField(
            controller: _codeController,
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            style: AppTypography.titleLarge(textPrimary).copyWith(letterSpacing: 10),
            decoration: InputDecoration(
              hintText: '• • • • • •',
              counterText: '',
              errorText: _errorText,
            ),
            onChanged: (val) {
              if (val.length == 6) {
                _handleConnect();
              }
            },
          ),
          const SizedBox(height: 18),

          ElevatedButton(
            onPressed: _isLoading ? null : _handleConnect,
            child: _isLoading
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Text('Подтвердить код'),
          ),
          const SizedBox(height: 12),

          TextButton.icon(
            onPressed: _openTelegramBot,
            icon: const Icon(Icons.open_in_new_rounded, size: 18),
            label: const Text('Открыть @pepitopetbot в Telegram'),
          ),
        ],
      ),
    );
  }
}
