import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import '../../core/sync/sync_engine.dart';
import '../../data/models/pet.dart';
import '../../data/models/sync_payload.dart';
import '../../data/models/training_task.dart';
import '../../data/models/user_profile.dart';

class HomeState {
  final UserProfile? user;
  final PetModel? activePet;
  final List<TrainingTaskModel> todayTasks;
  final int streakDays;
  final bool isLoading;
  final SyncStatus syncStatus;

  HomeState({
    this.user,
    this.activePet,
    this.todayTasks = const [],
    this.streakDays = 0,
    this.isLoading = false,
    this.syncStatus = SyncStatus.idle,
  });

  int get completedTasksCount => todayTasks.where((t) => t.isCompleted).length;
  bool get isAllCompletedToday => todayTasks.isNotEmpty && completedTasksCount == todayTasks.length;

  HomeState copyWith({
    UserProfile? user,
    PetModel? activePet,
    List<TrainingTaskModel>? todayTasks,
    int? streakDays,
    bool? isLoading,
    SyncStatus? syncStatus,
  }) {
    return HomeState(
      user: user ?? this.user,
      activePet: activePet ?? this.activePet,
      todayTasks: todayTasks ?? this.todayTasks,
      streakDays: streakDays ?? this.streakDays,
      isLoading: isLoading ?? this.isLoading,
      syncStatus: syncStatus ?? this.syncStatus,
    );
  }
}

class HomeController extends StateNotifier<HomeState> {
  final SyncEngine _syncEngine;

  HomeController(this._syncEngine) : super(HomeState(isLoading: true)) {
    _init();
  }

  void _init() {
    _syncEngine.onPullDataReceived = _handlePullData;
    _syncEngine.onStatusChanged = (status) {
      state = state.copyWith(syncStatus: status);
    };

    // Trigger initial pull
    _syncEngine.pullFullState();
  }

  void _handlePullData(SyncPullResponse data) {
    PetModel? pet = data.pets.isNotEmpty ? data.pets.first : null;

    state = state.copyWith(
      user: data.user,
      activePet: pet,
      todayTasks: data.todayTasks,
      streakDays: data.user.trainingDays,
      isLoading: false,
    );
  }

  /// Optimistic task toggle + offline sync queuing
  Future<void> toggleTask(int taskId) async {
    final updatedTasks = state.todayTasks.map((task) {
      if (task.id == taskId) {
        final newStatus = !task.isCompleted;
        // Queue in sync engine
        _syncEngine.queueTaskToggle(taskId, newStatus);

        return task.copyWith(
          isCompleted: newStatus,
          completedAt: newStatus ? DateTime.now() : null,
        );
      }
      return task;
    }).toList();

    // Check if this action completes all tasks for today
    final completedCount = updatedTasks.where((t) => t.isCompleted).length;
    int streak = state.streakDays;
    if (completedCount == updatedTasks.length && updatedTasks.isNotEmpty) {
      streak += 1;
    }

    state = state.copyWith(
      todayTasks: updatedTasks,
      streakDays: streak,
    );
  }

  Future<void> refresh() async {
    await _syncEngine.pullFullState();
  }
}

final homeControllerProvider =
    StateNotifierProvider<HomeController, HomeState>((ref) {
  final sync = ref.watch(syncEngineProvider);
  return HomeController(sync);
});
