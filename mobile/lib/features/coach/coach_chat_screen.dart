import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/coach_thread.dart';
import '../home/home_controller.dart';
import 'coach_controller.dart';
import 'widgets/premium_upsell_sheet.dart';

class CoachChatScreen extends ConsumerStatefulWidget {
  const CoachChatScreen({super.key});

  @override
  ConsumerState<CoachChatScreen> createState() => _CoachChatScreenState();
}

class _CoachChatScreenState extends ConsumerState<CoachChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = TextEditingController() as ScrollController? ?? ScrollController();
  final ImagePicker _picker = ImagePicker();

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;

    _textController.clear();
    ref.read(coachControllerProvider.notifier).sendMessage(text);

    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 150), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _pickPhoto() async {
    final picked = await _picker.pickImage(source: ImageSource.gallery, imageQuality: 85);
    if (picked != null) {
      ref.read(coachControllerProvider.notifier).sendPhoto(File(picked.path));
      _scrollToBottom();
    }
  }

  Future<void> _recordVideo() async {
    final isPremium = ref.read(homeControllerProvider).user?.isPremium ?? false;
    if (!isPremium) {
      _showPremiumModal();
      return;
    }

    final picked = await _picker.pickVideo(
      source: ImageSource.camera,
      maxDuration: const Duration(seconds: 30),
    );
    if (picked != null) {
      ref.read(coachControllerProvider.notifier).sendVideo(File(picked.path), true);
      _scrollToBottom();
    }
  }

  void _showPremiumModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => const PremiumUpsellSheet(
        featureTitle: 'Видео-разбор выполнения команд с камеры',
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(coachControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;
    final thread = state.activeThread;

    // Listen for rate limit / premium trigger
    ref.listen(coachControllerProvider, (prev, next) {
      if (next.needPremiumModal && !(prev?.needPremiumModal ?? false)) {
        ref.read(coachControllerProvider.notifier).resetPremiumModalFlag();
        _showPremiumModal();
      }
    });

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(thread?.displayTitle ?? 'AI-Кинолог', style: AppTypography.titleMedium(textPrimary)),
            Row(
              children: [
                Container(width: 8, height: 8, decoration: const BoxDecoration(shape: BoxShape.circle, color: AppColors.successGreen)),
                const SizedBox(width: 6),
                Text('На связи 24/7', style: AppTypography.bodySmall(textSecondary)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_comment_outlined, color: AppColors.primary),
            tooltip: 'Новая консультация',
            onPressed: () => ref.read(coachControllerProvider.notifier).createNewThread(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Message list
          Expanded(
            child: thread == null || thread.messages.isEmpty
                ? _buildEmptyPlaceholder(textPrimary, textSecondary)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    itemCount: thread.messages.length,
                    itemBuilder: (context, index) {
                      final msg = thread.messages[index];
                      return _buildMessageBubble(msg, isDark, textPrimary, textSecondary);
                    },
                  ),
          ),

          if (state.isSending)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                  const SizedBox(width: 10),
                  Text('Кинолог думает над ответом...', style: AppTypography.bodySmall(textSecondary)),
                ],
              ),
            ),

          // Input Bar
          _buildInputBar(isDark, textPrimary, textSecondary),
        ],
      ),
    );
  }

  Widget _buildEmptyPlaceholder(Color textPrimary, Color textSecondary) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('🐾', style: TextStyle(fontSize: 48)),
            const SizedBox(height: 16),
            Text('Задайте любой вопрос кинологу', textAlign: TextAlign.center, style: AppTypography.titleMedium(textPrimary)),
            const SizedBox(height: 8),
            Text(
              'Например: «Собака подбирает еду на улице» или «Как научить команду Рядом?»',
              textAlign: TextAlign.center,
              style: AppTypography.bodyMedium(textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(
    CoachMessageModel msg,
    bool isDark,
    Color textPrimary,
    Color textSecondary,
  ) {
    final isUser = msg.isUser;
    final bubbleColor = isUser
        ? AppColors.primary
        : (isDark ? AppColors.surfaceDark : AppColors.cardBorderLight.withOpacity(0.5));
    final textColor = isUser ? Colors.white : textPrimary;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: bubbleColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(18),
            topRight: const Radius.circular(18),
            bottomLeft: Radius.circular(isUser ? 18 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 18),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser)
              Padding(
                padding: const EdgeInsets.only(bottom: 6.0),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('🐕 ', style: TextStyle(fontSize: 14)),
                    Text(
                      'AI-Кинолог Pepito',
                      style: AppTypography.bodySmall(AppColors.primary).copyWith(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
            Text(
              msg.content,
              style: AppTypography.bodyMedium(textColor).copyWith(height: 1.45),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputBar(bool isDark, Color textPrimary, Color textSecondary) {
    final surfaceColor = isDark ? AppColors.surfaceDark : AppColors.surfaceLight;

    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 8,
        bottom: MediaQuery.of(context).viewInsets.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: surfaceColor,
        border: Border(top: BorderSide(color: AppColors.cardBorderLight.withOpacity(0.5))),
      ),
      child: Row(
        children: [
          // Photo attachment
          IconButton(
            icon: const Icon(Icons.photo_camera_outlined, size: 22),
            color: textSecondary,
            onPressed: _pickPhoto,
          ),

          // Video camera (with Premium gate)
          IconButton(
            icon: const Icon(Icons.videocam_outlined, size: 24),
            color: textSecondary,
            onPressed: _recordVideo,
          ),

          // Text Field
          Expanded(
            child: TextField(
              controller: _textController,
              textCapitalization: TextCapitalization.sentences,
              maxLines: 4,
              minLines: 1,
              decoration: const InputDecoration(
                hintText: 'Задайте вопрос...',
                contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),

          // Send Button
          IconButton(
            icon: const Icon(Icons.send_rounded, color: AppColors.primary),
            onPressed: _sendMessage,
          ),
        ],
      ),
    );
  }
}
