import 'training_task.dart';

class TrainingPlanModel {
  final int id;
  final int userId;
  final int petId;
  final String title;
  final String? goal;
  final int? weekNumber;
  final bool isActive;
  final List<TrainingTaskModel> tasks;

  TrainingPlanModel({
    required this.id,
    required this.userId,
    required this.petId,
    required this.title,
    this.goal,
    this.weekNumber,
    this.isActive = true,
    this.tasks = const [],
  });

  bool get isWeeklyPlan => weekNumber != null;

  // Filter tasks for a specific day of week (1..7)
  List<TrainingTaskModel> getTasksForDay(int dayOfWeek) {
    if (!isWeeklyPlan) return tasks;
    return tasks.where((t) => t.dayOfWeek == dayOfWeek).toList();
  }

  // Count completed tasks for today
  int completedCount(int currentDayOfWeek) {
    final dayTasks = getTasksForDay(currentDayOfWeek);
    return dayTasks.where((t) => t.isCompleted).length;
  }

  factory TrainingPlanModel.fromJson(Map<String, dynamic> json) {
    var rawTasks = json['tasks'] as List? ?? [];
    List<TrainingTaskModel> parsedTasks =
        rawTasks.map((t) => TrainingTaskModel.fromJson(t as Map<String, dynamic>)).toList();

    return TrainingPlanModel(
      id: json['id'] as int? ?? 0,
      userId: json['user_id'] as int? ?? 0,
      petId: json['pet_id'] as int? ?? 0,
      title: json['title'] as String? ?? 'План тренировок',
      goal: json['goal'] as String?,
      weekNumber: json['week_number'] as int?,
      isActive: json['is_active'] as bool? ?? true,
      tasks: parsedTasks,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'pet_id': petId,
      'title': title,
      'goal': goal,
      'week_number': weekNumber,
      'is_active': isActive,
      'tasks': tasks.map((t) => t.toJson()).toList(),
    };
  }

  TrainingPlanModel copyWith({
    int? id,
    int? userId,
    int? petId,
    String? title,
    String? goal,
    int? weekNumber,
    bool? isActive,
    List<TrainingTaskModel>? tasks,
  }) {
    return TrainingPlanModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      petId: petId ?? this.petId,
      title: title ?? this.title,
      goal: goal ?? this.goal,
      weekNumber: weekNumber ?? this.weekNumber,
      isActive: isActive ?? this.isActive,
      tasks: tasks ?? this.tasks,
    );
  }
}
