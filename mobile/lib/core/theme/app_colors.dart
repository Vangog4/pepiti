import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Brand Primaries
  static const Color primary = Color(0xFFE06D53); // Тёплый терракот Pepito
  static const Color primaryDark = Color(0xFFC7553C);
  static const Color primaryLight = Color(0xFFF9A875); // Персиковый акцент

  // Accents & Badges
  static const Color streakOrange = Color(0xFFF39C12); // Огонёк стрика 🔥
  static const Color successGreen = Color(0xFF4E9F6E); // Галочки выполненных задач
  static const Color premiumGold = Color(0xFFFFB800); // Золотой Premium
  static const Color errorRed = Color(0xFFE74C3C);
  static const Color infoBlue = Color(0xFF3498DB);

  // Light Theme Surfaces
  static const Color bgLight = Color(0xFFFAF8F5); // Мягкий тёплый молочный фон
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color cardBorderLight = Color(0xFFEFECE6);
  static const Color textPrimaryLight = Color(0xFF2C2725);
  static const Color textSecondaryLight = Color(0xFF7A726E);
  static const Color textMutedLight = Color(0xFFA8A19C);

  // Dark Theme Surfaces
  static const Color bgDark = Color(0xFF1A1817); // Глубокий шоколадно-графитовый фон
  static const Color surfaceDark = Color(0xFF262220);
  static const Color cardBorderDark = Color(0xFF383230);
  static const Color textPrimaryDark = Color(0xFFFDFBF9);
  static const Color textSecondaryDark = Color(0xFFA8A19C);
  static const Color textMutedDark = Color(0xFF6E6763);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, primaryLight],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient streakGradient = LinearGradient(
    colors: [Color(0xFFF39C12), Color(0xFFE67E22)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient premiumGradient = LinearGradient(
    colors: [Color(0xFFFFD700), Color(0xFFFFA500)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
