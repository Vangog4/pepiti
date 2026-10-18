class UserProfile {
  final int id;
  final int? telegramId;
  final String? username;
  final String? firstName;
  final bool isPremium;
  final DateTime? subscriptionExpiresAt;
  final int trainingDays;
  final String? reminderTime;
  final String timezone;
  final String languageCode;

  UserProfile({
    required this.id,
    this.telegramId,
    this.username,
    this.firstName,
    this.isPremium = false,
    this.subscriptionExpiresAt,
    this.trainingDays = 0,
    this.reminderTime,
    this.timezone = 'UTC',
    this.languageCode = 'ru',
  });

  bool get isTelegramLinked => telegramId != null && telegramId! > 0;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as int? ?? 0,
      telegramId: json['telegram_id'] as int?,
      username: json['username'] as String?,
      firstName: json['first_name'] as String?,
      isPremium: json['is_premium'] as bool? ?? false,
      subscriptionExpiresAt: json['subscription_expires_at'] != null
          ? DateTime.tryParse(json['subscription_expires_at'].toString())
          : null,
      trainingDays: json['training_days'] as int? ?? 0,
      reminderTime: json['reminder_time'] as String?,
      timezone: json['timezone'] as String? ?? 'UTC',
      languageCode: json['language_code'] as String? ?? 'ru',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'telegram_id': telegramId,
      'username': username,
      'first_name': firstName,
      'is_premium': isPremium,
      'subscription_expires_at': subscriptionExpiresAt?.toIso8601String(),
      'training_days': trainingDays,
      'reminder_time': reminderTime,
      'timezone': timezone,
      'language_code': languageCode,
    };
  }

  UserProfile copyWith({
    int? id,
    int? telegramId,
    String? username,
    String? firstName,
    bool? isPremium,
    DateTime? subscriptionExpiresAt,
    int? trainingDays,
    String? reminderTime,
    String? timezone,
    String? languageCode,
  }) {
    return UserProfile(
      id: id ?? this.id,
      telegramId: telegramId ?? this.telegramId,
      username: username ?? this.username,
      firstName: firstName ?? this.firstName,
      isPremium: isPremium ?? this.isPremium,
      subscriptionExpiresAt: subscriptionExpiresAt ?? this.subscriptionExpiresAt,
      trainingDays: trainingDays ?? this.trainingDays,
      reminderTime: reminderTime ?? this.reminderTime,
      timezone: timezone ?? this.timezone,
      languageCode: languageCode ?? this.languageCode,
    );
  }
}
