import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/network/api_exceptions.dart';
import '../../core/providers.dart';
import '../../data/models/coach_thread.dart';

class CoachState {
  final List<CoachThreadModel> threads;
  final CoachThreadModel? activeThread;
  final bool isLoading;
  final bool isSending;
  final String? errorMessage;
  final bool needPremiumModal;

  CoachState({
    this.threads = const [],
    this.activeThread,
    this.isLoading = false,
    this.isSending = false,
    this.errorMessage,
    this.needPremiumModal = false,
  });

  CoachState copyWith({
    List<CoachThreadModel>? threads,
    CoachThreadModel? activeThread,
    bool? isLoading,
    bool? isSending,
    String? errorMessage,
    bool? needPremiumModal,
  }) {
    return CoachState(
      threads: threads ?? this.threads,
      activeThread: activeThread ?? this.activeThread,
      isLoading: isLoading ?? this.isLoading,
      isSending: isSending ?? this.isSending,
      errorMessage: errorMessage,
      needPremiumModal: needPremiumModal ?? this.needPremiumModal,
    );
  }
}

class CoachController extends StateNotifier<CoachState> {
  final ApiClient _apiClient;

  CoachController(this._apiClient) : super(CoachState()) {
    loadThreads();
  }

  Future<void> loadThreads() async {
    state = state.copyWith(isLoading: true);
    try {
      final res = await _apiClient.get(ApiConstants.coachThreads);
      final list = (res as List).map((th) => CoachThreadModel.fromJson(th as Map<String, dynamic>)).toList();

      CoachThreadModel? current = state.activeThread;
      if (current == null && list.isNotEmpty) {
        current = list.first;
      }

      state = state.copyWith(
        threads: list,
        activeThread: current,
        isLoading: false,
      );
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  void selectThread(CoachThreadModel thread) {
    state = state.copyWith(activeThread: thread);
  }

  Future<void> createNewThread({String? initialTitle}) async {
    state = state.copyWith(isLoading: true);
    try {
      final res = await _apiClient.post(
        ApiConstants.coachThreads,
        data: {'title': initialTitle ?? 'Новый вопрос кинологу'},
      );
      final newThread = CoachThreadModel.fromJson(res as Map<String, dynamic>);
      state = state.copyWith(
        threads: [newThread, ...state.threads],
        activeThread: newThread,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false);
    }
  }

  // Send standard text question
  Future<void> sendMessage(String text) async {
    final thread = state.activeThread;
    if (thread == null || text.trim().isEmpty) return;

    final userMsg = CoachMessageModel(
      role: 'user',
      content: text.trim(),
      timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
    );

    // Optimistic UI update
    final currentMsgs = List<CoachMessageModel>.from(thread.messages)..add(userMsg);
    final updatedThread = CoachThreadModel(
      id: thread.id,
      userId: thread.userId,
      title: thread.title,
      status: thread.status,
      summary: thread.summary,
      messageCount: currentMsgs.length,
      messages: currentMsgs,
    );

    state = state.copyWith(
      activeThread: updatedThread,
      isSending: true,
      errorMessage: null,
    );

    try {
      final res = await _apiClient.post(
        ApiConstants.coachThreadMessages(thread.id),
        data: {'content': text.trim()},
      );

      String coachContent = '';
      if (res['coach_message'] is Map) {
        coachContent = (res['coach_message'] as Map)['content'] as String? ?? '';
      } else {
        coachContent = res['answer'] as String? ?? res['content'] as String? ?? '';
      }
      final coachMsg = CoachMessageModel(
        role: 'coach',
        content: coachContent,
        timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
      );

      final finalMsgs = List<CoachMessageModel>.from(currentMsgs)..add(coachMsg);
      state = state.copyWith(
        activeThread: CoachThreadModel(
          id: thread.id,
          userId: thread.userId,
          title: res['thread_title'] as String? ?? thread.title,
          status: thread.status,
          summary: thread.summary,
          messageCount: finalMsgs.length,
          messages: finalMsgs,
        ),
        isSending: false,
      );
    } on RateLimitException catch (e) {
      state = state.copyWith(
        isSending: false,
        errorMessage: e.message,
        needPremiumModal: true,
      );
    } catch (e) {
      state = state.copyWith(
        isSending: false,
        errorMessage: 'Не удалось отправить сообщение. Проверьте интернет.',
      );
    }
  }

  // Upload Photo for analysis
  Future<void> sendPhoto(File imageFile, {String? caption}) async {
    final thread = state.activeThread;
    if (thread == null) return;

    state = state.copyWith(isSending: true);
    try {
      final res = await _apiClient.uploadFile(
        '${ApiConstants.coachThreadMessages(thread.id)}/photo',
        file: imageFile,
        fieldName: 'photo',
        extraData: {'caption': caption ?? ''},
      );

      final coachAnswer = res['answer'] as String? ?? '';
      final coachMsg = CoachMessageModel(
        role: 'coach',
        content: coachAnswer,
        timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
      );

      final msgs = List<CoachMessageModel>.from(thread.messages)..add(coachMsg);
      state = state.copyWith(
        activeThread: CoachThreadModel(
          id: thread.id,
          userId: thread.userId,
          title: thread.title,
          messages: msgs,
        ),
        isSending: false,
      );
    } catch (e) {
      state = state.copyWith(isSending: false, errorMessage: 'Ошибка при анализе фото.');
    }
  }

  // Check Video gate and upload
  Future<void> sendVideo(File videoFile, bool isPremium) async {
    if (!isPremium) {
      state = state.copyWith(needPremiumModal: true);
      return;
    }

    final thread = state.activeThread;
    if (thread == null) return;

    state = state.copyWith(isSending: true);
    try {
      final res = await _apiClient.uploadFile(
        '${ApiConstants.coachThreadMessages(thread.id)}/video',
        file: videoFile,
        fieldName: 'video',
      );

      final coachAnswer = res['answer'] as String? ?? '';
      final coachMsg = CoachMessageModel(
        role: 'coach',
        content: coachAnswer,
        timestamp: DateTime.now().millisecondsSinceEpoch ~/ 1000,
      );

      final msgs = List<CoachMessageModel>.from(thread.messages)..add(coachMsg);
      state = state.copyWith(
        activeThread: CoachThreadModel(
          id: thread.id,
          userId: thread.userId,
          messages: msgs,
        ),
        isSending: false,
      );
    } catch (e) {
      state = state.copyWith(isSending: false, errorMessage: 'Ошибка при анализе видео.');
    }
  }

  void resetPremiumModalFlag() {
    state = state.copyWith(needPremiumModal: false);
  }
}

final coachControllerProvider =
    StateNotifierProvider<CoachController, CoachState>((ref) {
  final api = ref.watch(apiClientProvider);
  return CoachController(api);
});
