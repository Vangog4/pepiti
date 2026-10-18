import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/providers.dart';
import '../../core/storage/storage_service.dart';
import '../../data/models/pet.dart';

class OnboardingState {
  final int step; // 0, 1, 2, 3
  final String name;
  final String sex;
  final String breed;
  final String ageCategory;
  final String trainingLevel;
  final String goal;
  final bool isSubmitting;
  final bool isVoiceExtracting;
  final String? errorMessage;

  OnboardingState({
    this.step = 0,
    this.name = '',
    this.sex = 'мальчик',
    this.breed = '',
    this.ageCategory = 'Щенок (4–12 мес)',
    this.trainingLevel = '1',
    this.goal = 'Базовое послушание',
    this.isSubmitting = false,
    this.isVoiceExtracting = false,
    this.errorMessage,
  });

  bool get canProceed {
    if (step == 0) return name.trim().isNotEmpty;
    if (step == 1) return breed.trim().isNotEmpty;
    return true;
  }

  OnboardingState copyWith({
    int? step,
    String? name,
    String? sex,
    String? breed,
    String? ageCategory,
    String? trainingLevel,
    String? goal,
    bool? isSubmitting,
    bool? isVoiceExtracting,
    String? errorMessage,
  }) {
    return OnboardingState(
      step: step ?? this.step,
      name: name ?? this.name,
      sex: sex ?? this.sex,
      breed: breed ?? this.breed,
      ageCategory: ageCategory ?? this.ageCategory,
      trainingLevel: trainingLevel ?? this.trainingLevel,
      goal: goal ?? this.goal,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      isVoiceExtracting: isVoiceExtracting ?? this.isVoiceExtracting,
      errorMessage: errorMessage,
    );
  }
}

class OnboardingController extends StateNotifier<OnboardingState> {
  final ApiClient _apiClient;
  final StorageService _storageService;

  OnboardingController(this._apiClient, this._storageService)
      : super(OnboardingState());

  void setStep(int step) => state = state.copyWith(step: step);
  void setName(String val) => state = state.copyWith(name: val);
  void setSex(String val) => state = state.copyWith(sex: val);
  void setBreed(String val) => state = state.copyWith(breed: val);
  void setAgeCategory(String val) => state = state.copyWith(ageCategory: val);
  void setTrainingLevel(String val) => state = state.copyWith(trainingLevel: val);
  void setGoal(String val) => state = state.copyWith(goal: val);

  // Auto-fill from voice input file
  Future<bool> extractFromVoice(File audioFile) async {
    state = state.copyWith(isVoiceExtracting: true, errorMessage: null);
    try {
      final res = await _apiClient.uploadFile(
        '${ApiConstants.pets}/extract-voice',
        file: audioFile,
        fieldName: 'audio',
      );

      final extracted = res as Map<String, dynamic>;
      state = state.copyWith(
        name: extracted['name'] as String? ?? state.name,
        breed: extracted['breed'] as String? ?? state.breed,
        sex: extracted['sex'] as String? ?? state.sex,
        ageCategory: extracted['age_category'] as String? ?? state.ageCategory,
        goal: extracted['goal'] as String? ?? state.goal,
        isVoiceExtracting: false,
      );
      return true;
    } catch (_) {
      state = state.copyWith(
        isVoiceExtracting: false,
        errorMessage: 'Не удалось распознать голос. Пожалуйста, заполните форму вручную.',
      );
      return false;
    }
  }

  // Create pet in backend and cache ID
  Future<PetModel?> submit() async {
    state = state.copyWith(isSubmitting: true, errorMessage: null);
    try {
      final res = await _apiClient.post(
        ApiConstants.pets,
        data: {
          'name': state.name.trim(),
          'breed': state.breed.trim(),
          'sex': state.sex,
          'age_category': state.ageCategory,
          'training_level': state.trainingLevel,
          'goal': state.goal,
        },
      );

      final pet = PetModel.fromJson(res as Map<String, dynamic>);
      await _storageService.saveActivePetId(pet.id);

      // Trigger first training plan generation
      unawaited(_apiClient.get(ApiConstants.trainingToday));

      state = state.copyWith(isSubmitting: false);
      return pet;
    } catch (e) {
      state = state.copyWith(
        isSubmitting: false,
        errorMessage: 'Ошибка при сохранении питомца. Проверьте интернет.',
      );
      return null;
    }
  }
}

final onboardingControllerProvider =
    StateNotifierProvider<OnboardingController, OnboardingState>((ref) {
  final api = ref.watch(apiClientProvider);
  final storage = ref.watch(storageServiceProvider);
  return OnboardingController(api, storage);
});
