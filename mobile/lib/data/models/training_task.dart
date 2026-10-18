class TrainingTaskModel {
  final int id;
  final int? planId;
  final int? dayOfWeek; // 1 (Пн) .. 7 (Вс)
  final String title;
  final String? description;
  final int? durationMinutes;
  final String? difficulty; // easy, medium, hard
  final bool isCompleted;
  final DateTime? completedAt;

  TrainingTaskModel({
    required this.id,
    this.planId,
    this.dayOfWeek,
    required this.title,
    this.description,
    this.durationMinutes,
    this.difficulty,
    this.isCompleted = false,
    this.completedAt,
  });

  String get difficultyLabel {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'Легко';
      case 'hard':
        return 'Сложно';
      case 'medium':
      default:
        return 'Средне';
    }
  }

  factory TrainingTaskModel.fromJson(Map<String, dynamic> json) {
    return TrainingTaskModel(
      id: json['id'] as int? ?? 0,
      planId: json['plan_id'] as int?,
      dayOfWeek: json['day_of_week'] as int?,
      title: json['title'] as String? ?? 'Упражнение',
      description: json['description'] as String?,
      durationMinutes: json['duration_minutes'] as int? ?? 5,
      difficulty: json['difficulty'] as String? ?? 'medium',
      isCompleted: json['is_completed'] as bool? ?? false,
      completedAt: json['completed_at'] != null
          ? DateTime.tryParse(json['completed_at'].toString())
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'plan_id': planId,
      'day_of_week': dayOfWeek,
      'title': title,
      'description': description,
      'duration_minutes': durationMinutes,
      'difficulty': difficulty,
      'is_completed': isCompleted,
      'completed_at': completedAt?.toIso8601String(),
    };
  }

  TrainingTaskModel copyWith({
    int? id,
    int? planId,
    int? dayOfWeek,
    String? title,
    String? description,
    int? durationMinutes,
    String? difficulty,
    bool? isCompleted,
    DateTime? completedAt,
  }) {
    return TrainingTaskModel(
      id: id ?? this.id,
      planId: planId ?? this.planId,
      dayOfWeek: dayOfWeek ?? this.dayOfWeek,
      title: title ?? this.title,
      description: description ?? this.description,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      difficulty: difficulty ?? this.difficulty,
      isCompleted: isCompleted ?? this.isCompleted,
      completedAt: completedAt ?? this.completedAt,
    );
  }
}
