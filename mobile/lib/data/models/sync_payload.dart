import 'user_profile.dart';
import 'pet.dart';
import 'training_plan.dart';
import 'training_task.dart';
import 'subscription.dart';
import 'coach_thread.dart';

class TaskChangeItem {
  final int taskId;
  final bool isCompleted;
  final DateTime completedAt;

  TaskChangeItem({
    required this.taskId,
    required this.isCompleted,
    required this.completedAt,
  });

  factory TaskChangeItem.fromJson(Map<String, dynamic> json) {
    return TaskChangeItem(
      taskId: json['task_id'] as int,
      isCompleted: json['is_completed'] as bool,
      completedAt: DateTime.parse(json['completed_at'].toString()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'task_id': taskId,
      'is_completed': isCompleted,
      'completed_at': completedAt.toUtc().toIso8601String(),
    };
  }
}

class SyncPullResponse {
  final UserProfile user;
  final List<PetModel> pets;
  final TrainingPlanModel? activePlan;
  final List<TrainingTaskModel> todayTasks;
  final SubscriptionStatusModel subscription;
  final List<CoachThreadModel> coachThreads;
  final DateTime? serverTime;
  final int? activePetId;

  SyncPullResponse({
    required this.user,
    required this.pets,
    this.activePlan,
    required this.todayTasks,
    required this.subscription,
    required this.coachThreads,
    this.serverTime,
    this.activePetId,
  });

  factory SyncPullResponse.fromJson(Map<String, dynamic> json) {
    var rawPets = json['pets'] as List? ?? [];
    var rawTasks = json['today_tasks'] as List? ?? [];
    var rawThreads = json['coach_threads'] as List? ?? [];

    return SyncPullResponse(
      user: UserProfile.fromJson((json['profile'] ?? json['user']) as Map<String, dynamic>? ?? {}),
      pets: rawPets.map((p) => PetModel.fromJson(p as Map<String, dynamic>)).toList(),
      activePlan: json['active_plan'] != null
          ? TrainingPlanModel.fromJson(json['active_plan'] as Map<String, dynamic>)
          : null,
      todayTasks: rawTasks.map((t) => TrainingTaskModel.fromJson(t as Map<String, dynamic>)).toList(),
      subscription: SubscriptionStatusModel.fromJson(
        json['subscription'] as Map<String, dynamic>? ?? {},
      ),
      coachThreads:
          rawThreads.map((th) => CoachThreadModel.fromJson(th as Map<String, dynamic>)).toList(),
      serverTime: json['server_time'] != null ? DateTime.tryParse(json['server_time'].toString()) : null,
      activePetId: json['active_pet_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'profile': user.toJson(),
      'pets': pets.map((p) => p.toJson()).toList(),
      'active_pet_id': activePetId,
      'active_plan': activePlan?.toJson(),
      'today_tasks': todayTasks.map((t) => t.toJson()).toList(),
      'subscription': {
        'is_premium': subscription.isPremium,
        'expires_at': subscription.expiresAt?.toIso8601String(),
        'days_left': subscription.daysLeft,
      },
      'coach_threads': coachThreads.map((th) => th.toJson()).toList(),
      'server_time': serverTime?.toIso8601String(),
    };
  }
}

class SyncPushResponse {
  final String status;
  final int syncedTasksCount;
  final DateTime? syncedAt;
  final bool profileUpdated;
  final bool petUpdated;
  final SyncPullResponse? currentState;

  SyncPushResponse({
    required this.status,
    required this.syncedTasksCount,
    this.syncedAt,
    this.profileUpdated = false,
    this.petUpdated = false,
    this.currentState,
  });

  int get currentStreak => currentState?.user.trainingDays ?? 0;
  List<TrainingTaskModel> get todayTasks => currentState?.todayTasks ?? [];

  factory SyncPushResponse.fromJson(Map<String, dynamic> json) {
    final state = json['current_state'] != null
        ? SyncPullResponse.fromJson(json['current_state'] as Map<String, dynamic>)
        : null;
    return SyncPushResponse(
      status: json['status'] as String? ?? 'ok',
      syncedTasksCount: (json['tasks_applied'] ?? json['synced_tasks_count'] ?? 0) as int,
      syncedAt: json['synced_at'] != null ? DateTime.tryParse(json['synced_at'].toString()) : null,
      profileUpdated: json['profile_updated'] as bool? ?? false,
      petUpdated: json['pet_updated'] as bool? ?? false,
      currentState: state,
    );
  }
}
