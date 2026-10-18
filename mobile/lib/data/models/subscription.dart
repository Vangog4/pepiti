class SubscriptionPlanModel {
  final String code; // 'premium_1m', 'premium_3m', 'premium_1y'
  final String title;
  final int durationDays;
  final int priceRub;
  final int starsPrice;
  final String? discountLabel;

  SubscriptionPlanModel({
    required this.code,
    required this.title,
    required this.durationDays,
    required this.priceRub,
    required this.starsPrice,
    this.discountLabel,
  });

  factory SubscriptionPlanModel.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlanModel(
      code: json['code'] as String? ?? 'premium_1m',
      title: json['title'] as String? ?? '1 месяц',
      durationDays: json['duration_days'] as int? ?? 30,
      priceRub: json['price_rub'] as int? ?? 590,
      starsPrice: json['stars_price'] as int? ?? 299,
      discountLabel: json['discount_label'] as String?,
    );
  }
}

class SubscriptionStatusModel {
  final bool isPremium;
  final DateTime? expiresAt;
  final int daysLeft;
  final String? planCode;

  SubscriptionStatusModel({
    required this.isPremium,
    this.expiresAt,
    this.daysLeft = 0,
    this.planCode,
  });

  factory SubscriptionStatusModel.fromJson(Map<String, dynamic> json) {
    return SubscriptionStatusModel(
      isPremium: json['is_premium'] as bool? ?? false,
      expiresAt: json['expires_at'] != null ? DateTime.tryParse(json['expires_at'].toString()) : null,
      daysLeft: json['days_left'] as int? ?? 0,
      planCode: json['plan_code'] as String?,
    );
  }
}
