class PetModel {
  final int id;
  final int userId;
  final String name;
  final String? breed;
  final String? sex;
  final String? ageCategory;
  final int? ageMonths;
  final String? sizeCategory;
  final double? weightKg;
  final String? trainingLevel;
  final String? temperament;
  final String? behaviorIssues;
  final String? goal;
  final String? energyLevel;
  final String? healthNotes;
  final int trainingDays;

  PetModel({
    required this.id,
    required this.userId,
    required this.name,
    this.breed,
    this.sex,
    this.ageCategory,
    this.ageMonths,
    this.sizeCategory,
    this.weightKg,
    this.trainingLevel,
    this.temperament,
    this.behaviorIssues,
    this.goal,
    this.energyLevel,
    this.healthNotes,
    this.trainingDays = 0,
  });

  bool get isPuppy {
    final cat = (ageCategory ?? '').toLowerCase();
    return cat.contains('щенок') || cat.contains('puppy') || (ageMonths != null && ageMonths! <= 12);
  }

  bool get isSmallBreed {
    final size = (sizeCategory ?? '').toLowerCase();
    return size.contains('маленький') || size.contains('small') || (weightKg != null && weightKg! <= 10);
  }

  factory PetModel.fromJson(Map<String, dynamic> json) {
    return PetModel(
      id: json['id'] as int? ?? 0,
      userId: json['user_id'] as int? ?? 0,
      name: json['name'] as String? ?? 'Питомец',
      breed: json['breed'] as String?,
      sex: json['sex'] as String?,
      ageCategory: json['age_category'] as String?,
      ageMonths: json['age_months'] as int?,
      sizeCategory: json['size_category'] as String?,
      weightKg: (json['weight_kg'] as num?)?.toDouble(),
      trainingLevel: json['training_level'] as String?,
      temperament: json['temperament'] as String?,
      behaviorIssues: json['behavior_issues'] as String?,
      goal: json['goal'] as String?,
      energyLevel: json['energy_level'] as String?,
      healthNotes: json['health_notes'] as String?,
      trainingDays: json['training_days'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'breed': breed,
      'sex': sex,
      'age_category': ageCategory,
      'age_months': ageMonths,
      'size_category': sizeCategory,
      'weight_kg': weightKg,
      'training_level': trainingLevel,
      'temperament': temperament,
      'behavior_issues': behaviorIssues,
      'goal': goal,
      'energy_level': energyLevel,
      'health_notes': healthNotes,
      'training_days': trainingDays,
    };
  }

  PetModel copyWith({
    int? id,
    int? userId,
    String? name,
    String? breed,
    String? sex,
    String? ageCategory,
    int? ageMonths,
    String? sizeCategory,
    double? weightKg,
    String? trainingLevel,
    String? temperament,
    String? behaviorIssues,
    String? goal,
    String? energyLevel,
    String? healthNotes,
    int? trainingDays,
  }) {
    return PetModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      name: name ?? this.name,
      breed: breed ?? this.breed,
      sex: sex ?? this.sex,
      ageCategory: ageCategory ?? this.ageCategory,
      ageMonths: ageMonths ?? this.ageMonths,
      sizeCategory: sizeCategory ?? this.sizeCategory,
      weightKg: weightKg ?? this.weightKg,
      trainingLevel: trainingLevel ?? this.trainingLevel,
      temperament: temperament ?? this.temperament,
      behaviorIssues: behaviorIssues ?? this.behaviorIssues,
      goal: goal ?? this.goal,
      energyLevel: energyLevel ?? this.energyLevel,
      healthNotes: healthNotes ?? this.healthNotes,
      trainingDays: trainingDays ?? this.trainingDays,
    );
  }
}
