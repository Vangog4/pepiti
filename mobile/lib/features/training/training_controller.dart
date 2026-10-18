import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/providers.dart';
import '../../core/sync/sync_engine.dart';
import '../../data/models/training_plan.dart';
import '../../data/models/training_task.dart';
import '../home/home_controller.dart';

class TrainingState {
  final int selectedDayOfWeek; // 1 (Mon) .. 7 (Sun)
  final TrainingPlanModel? activePlan;
  final bool isLoading;
  final bool isPdfDownloading;
  final String? errorMessage;

  TrainingState({
    required this.selectedDayOfWeek,
    this.activePlan,
    this.isLoading = false,
    this.isPdfDownloading = false,
    this.errorMessage,
  });

  List<TrainingTaskModel> get tasksForSelectedDay {
    if (activePlan == null) return [];
    return activePlan!.getTasksForDay(selectedDayOfWeek);
  }

  TrainingState copyWith({
    int? selectedDayOfWeek,
    TrainingPlanModel? activePlan,
    bool? isLoading,
    bool? isPdfDownloading,
    String? errorMessage,
  }) {
    return TrainingState(
      selectedDayOfWeek: selectedDayOfWeek ?? this.selectedDayOfWeek,
      activePlan: activePlan ?? this.activePlan,
      isLoading: isLoading ?? this.isLoading,
      isPdfDownloading: isPdfDownloading ?? this.isPdfDownloading,
      errorMessage: errorMessage,
    );
  }
}

class TrainingController extends StateNotifier<TrainingState> {
  final ApiClient _apiClient;
  final SyncEngine _syncEngine;
  final Reader _read;

  TrainingController(this._apiClient, this._syncEngine, this._read)
      : super(TrainingState(selectedDayOfWeek: DateTime.now().weekday)) {
    _init();
  }

  void _init() {
    _syncEngine.onPullDataReceived = (data) {
      if (data.activePlan != null) {
        state = state.copyWith(activePlan: data.activePlan);
      }
    };
    loadPlan();
  }

  void selectDayOfWeek(int day) {
    state = state.copyWith(selectedDayOfWeek: day.clamp(1, 7));
  }

  Future<void> loadPlan() async {
    state = state.copyWith(isLoading: true);
    try {
      final res = await _apiClient.get(ApiConstants.trainingPlan);
      final plan = TrainingPlanModel.fromJson(res as Map<String, dynamic>);
      state = state.copyWith(activePlan: plan, isLoading: false);
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<void> toggleTask(int taskId) async {
    // Forward to HomeController for home state sync
    await _read(homeControllerProvider.notifier).toggleTask(taskId);

    // Update in training plan local tasks
    if (state.activePlan != null) {
      final updated = state.activePlan!.tasks.map((t) {
        if (t.id == taskId) {
          return t.copyWith(isCompleted: !t.isCompleted);
        }
        return t;
      }).toList();

      state = state.copyWith(
        activePlan: state.activePlan!.copyWith(tasks: updated),
      );
    }
  }

  /// Download official PDF plan and open with system viewer
  Future<bool> downloadPdf() async {
    state = state.copyWith(isPdfDownloading: true, errorMessage: null);
    try {
      final bytes = await _apiClient.downloadBytes(ApiConstants.trainingPdf);
      if (bytes.isEmpty) {
        state = state.copyWith(isPdfDownloading: false, errorMessage: 'Пустой PDF ответ');
        return false;
      }

      final tempDir = await getTemporaryDirectory();
      final file = File('${tempDir.path}/pepito_training_plan.pdf');
      await file.writeAsBytes(bytes);

      state = state.copyWith(isPdfDownloading: false);

      // Open PDF file with system viewer / print
      await OpenFilex.open(file.path);
      return true;
    } catch (e) {
      state = state.copyWith(
        isPdfDownloading: false,
        errorMessage: 'Не удалось скачать PDF. Проверьте интернет.',
      );
      return false;
    }
  }
}

typedef Reader = T Function<T>(ProviderListenable<T> provider);

final trainingControllerProvider =
    StateNotifierProvider<TrainingController, TrainingState>((ref) {
  final api = ref.watch(apiClientProvider);
  final sync = ref.watch(syncEngineProvider);
  return TrainingController(api, sync, ref.read);
});
