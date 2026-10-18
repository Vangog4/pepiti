import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import 'onboarding_controller.dart';
import 'voice_input_sheet.dart';

class PetOnboardingScreen extends ConsumerStatefulWidget {
  final VoidCallback onCompleted;

  const PetOnboardingScreen({super.key, required this.onCompleted});

  @override
  ConsumerState<PetOnboardingScreen> createState() => _PetOnboardingScreenState();
}

class _PetOnboardingScreenState extends ConsumerState<PetOnboardingScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _breedController = TextEditingController();

  final List<String> _popularBreeds = [
    'Корги',
    'Шпиц',
    'Лабрадор',
    'Французский бульдог',
    'Немецкая овчарка',
    'Джек-рассел',
    'Пудель',
    'Йоркширский терьер',
    'Метис / Дворняжка',
  ];

  final List<String> _ageCategories = [
    'Щенок (до 4 мес)',
    'Щенок (4–12 мес)',
    'Молодой (1–3 года)',
    'Взрослый (3–7 лет)',
    'Пожилой (7+ лет)',
  ];

  final List<String> _goals = [
    'Базовое послушание',
    'Не тянуть поводок',
    'Приучение к туалету',
    'Отучить кусаться/грызть',
    'Социализация и страхи',
    'Команда «Ко мне!»',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _breedController.dispose();
    super.dispose();
  }

  void _showVoiceInput() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => VoiceInputSheet(
        onExtracted: () {
          Navigator.of(ctx).pop();
          final state = ref.read(onboardingControllerProvider);
          _nameController.text = state.name;
          _breedController.text = state.breed;
        },
      ),
    );
  }

  Future<void> _handleNext() async {
    final notifier = ref.read(onboardingControllerProvider.notifier);
    final state = ref.read(onboardingControllerProvider);

    if (state.step < 3) {
      notifier.setStep(state.step + 1);
    } else {
      final pet = await notifier.submit();
      if (pet != null && mounted) {
        widget.onCompleted();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(onboardingControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Scaffold(
      appBar: AppBar(
        title: Text('Шаг ${state.step + 1} из 4', style: AppTypography.titleMedium(textPrimary)),
        leading: state.step > 0
            ? IconButton(
                icon: const Icon(Icons.arrow_back_ios_rounded),
                onPressed: () => ref.read(onboardingControllerProvider.notifier).setStep(state.step - 1),
              )
            : null,
        actions: [
          IconButton(
            icon: const Icon(Icons.mic_none_rounded, color: AppColors.primary),
            tooltip: 'Заполнить голосом',
            onPressed: _showVoiceInput,
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Progress Bar
              LinearProgressIndicator(
                value: (state.step + 1) / 4,
                backgroundColor: AppColors.cardBorderLight,
                valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                borderRadius: BorderRadius.circular(4),
              ),
              const SizedBox(height: 28),

              // Step Content
              Expanded(
                child: SingleChildScrollView(
                  child: _buildStepContent(state, textPrimary, textSecondary),
                ),
              ),

              // Action Buttons
              if (state.errorMessage != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: Text(
                    state.errorMessage!,
                    style: const TextStyle(color: AppColors.errorRed, fontSize: 13),
                    textAlign: TextAlign.center,
                  ),
                ),

              ElevatedButton(
                onPressed: state.isSubmitting || !state.canProceed ? null : _handleNext,
                child: state.isSubmitting
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text(state.step == 3 ? 'Создать план тренировок 🚀' : 'Продолжить'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepContent(OnboardingState state, Color textPrimary, Color textSecondary) {
    switch (state.step) {
      case 0:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Как зовут вашего питомца?', style: AppTypography.titleLarge(textPrimary)),
            const SizedBox(height: 8),
            Text('Мы будем обращаться к собаке по имени в упражнениях', style: AppTypography.bodyMedium(textSecondary)),
            const SizedBox(height: 24),
            TextField(
              controller: _nameController,
              autofocus: true,
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(hintText: 'Например, Бруно или Луна', prefixIcon: Icon(Icons.pets_rounded)),
              onChanged: (val) => ref.read(onboardingControllerProvider.notifier).setName(val),
            ),
            const SizedBox(height: 24),
            Text('Пол собаки', style: AppTypography.titleMedium(textPrimary)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildChoiceChip(
                    title: '🐶 Мальчик',
                    isSelected: state.sex == 'мальчик',
                    onTap: () => ref.read(onboardingControllerProvider.notifier).setSex('мальчик'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildChoiceChip(
                    title: '🎀 Девочка',
                    isSelected: state.sex == 'девочка',
                    onTap: () => ref.read(onboardingControllerProvider.notifier).setSex('девочка'),
                  ),
                ),
              ],
            ),
          ],
        );

      case 1:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Какая порода у ${state.name}?', style: AppTypography.titleLarge(textPrimary)),
            const SizedBox(height: 8),
            Text('Порода помогает адаптировать нагрузку и рекомендации лакомств', style: AppTypography.bodyMedium(textSecondary)),
            const SizedBox(height: 20),
            TextField(
              controller: _breedController,
              decoration: const InputDecoration(hintText: 'Введите породу', prefixIcon: Icon(Icons.search_rounded)),
              onChanged: (val) => ref.read(onboardingControllerProvider.notifier).setBreed(val),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _popularBreeds.map((b) {
                final isSelected = state.breed == b;
                return ActionChip(
                  label: Text(b),
                  backgroundColor: isSelected ? AppColors.primary.withOpacity(0.15) : null,
                  side: BorderSide(color: isSelected ? AppColors.primary : AppColors.cardBorderLight),
                  onPressed: () {
                    _breedController.text = b;
                    ref.read(onboardingControllerProvider.notifier).setBreed(b);
                  },
                );
              }).toList(),
            ),
          ],
        );

      case 2:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Сколько лет ${state.name}?', style: AppTypography.titleLarge(textPrimary)),
            const SizedBox(height: 8),
            Text('В разном возрасте собаки учатся разным командам', style: AppTypography.bodyMedium(textSecondary)),
            const SizedBox(height: 20),
            ..._ageCategories.map((cat) {
              final isSelected = state.ageCategory == cat;
              return Padding(
                padding: const EdgeInsets.only(bottom: 10.0),
                child: _buildChoiceChip(
                  title: cat,
                  isSelected: isSelected,
                  onTap: () => ref.read(onboardingControllerProvider.notifier).setAgeCategory(cat),
                ),
              );
            }),
          ],
        );

      case 3:
      default:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Главная цель тренировок', style: AppTypography.titleLarge(textPrimary)),
            const SizedBox(height: 8),
            Text('Мы сгенерируем персональный 7-дневный план под вашу задачу', style: AppTypography.bodyMedium(textSecondary)),
            const SizedBox(height: 20),
            ..._goals.map((g) {
              final isSelected = state.goal == g;
              return Padding(
                padding: const EdgeInsets.only(bottom: 10.0),
                child: _buildChoiceChip(
                  title: g,
                  isSelected: isSelected,
                  onTap: () => ref.read(onboardingControllerProvider.notifier).setGoal(g),
                ),
              );
            }),
          ],
        );
    }
  }

  Widget _buildChoiceChip({
    required String title,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary.withOpacity(0.12) : null,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.cardBorderLight,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                title,
                style: AppTypography.titleMedium(
                  isSelected ? AppColors.primary : AppColors.textPrimaryLight,
                ),
              ),
            ),
            if (isSelected) const Icon(Icons.check_circle_rounded, color: AppColors.primary, size: 22),
          ],
        ),
      ),
    );
  }
}
