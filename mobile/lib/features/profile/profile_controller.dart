import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/providers.dart';
import '../../core/sync/sync_engine.dart';
import '../../data/models/pet.dart';
import '../../data/models/user_profile.dart';
import '../auth/auth_controller.dart';
import '../home/home_controller.dart';

class ProfileState {
  final UserProfile? user;
  final PetModel? pet;
  final bool isSaving;
  final bool pushNotificationsEnabled;
  final bool telegramNotificationsEnabled;
  final String? message;

  ProfileState({
    this.user,
    this.pet,
    this.isSaving = false,
    this.pushNotificationsEnabled = true,
    this.telegramNotificationsEnabled = true,
    this.message,
  });

  ProfileState copyWith({
    UserProfile? user,
    PetModel? pet,
    bool? isSaving,
    bool? pushNotificationsEnabled,
    bool? telegramNotificationsEnabled,
    String? message,
  }) {
    return ProfileState(
      user: user ?? this.user,
      pet: pet ?? this.pet,
      isSaving: isSaving ?? this.isSaving,
      pushNotificationsEnabled: pushNotificationsEnabled ?? this.pushNotificationsEnabled,
      telegramNotificationsEnabled:
          telegramNotificationsEnabled ?? this.telegramNotificationsEnabled,
      message: message,
    );
  }
}

class ProfileController extends StateNotifier<ProfileState> {
  final ApiClient _apiClient;
  final SyncEngine _syncEngine;
  final Reader _read;

  ProfileController(this._apiClient, this._syncEngine, this._read) : super(ProfileState()) {
    _init();
  }

  void _init() {
    _syncEngine.onPullDataReceived = (data) {
      state = state.copyWith(
        user: data.user,
        pet: data.pets.isNotEmpty ? data.pets.first : null,
      );
    };
  }

  Future<void> updateReminderTime(String time) async {
    state = state.copyWith(isSaving: true);
    try {
      await _apiClient.patch(ApiConstants.profile, data: {'reminder_time': time});
      if (state.user != null) {
        state = state.copyWith(user: state.user!.copyWith(reminderTime: time), isSaving: false);
      }
    } catch (_) {
      state = state.copyWith(isSaving: false);
    }
  }

  Future<void> updateLanguage(String lang) async {
    state = state.copyWith(isSaving: true);
    try {
      await _apiClient.patch(ApiConstants.profile, data: {'language_code': lang});
      if (state.user != null) {
        state = state.copyWith(user: state.user!.copyWith(languageCode: lang), isSaving: false);
      }
    } catch (_) {
      state = state.copyWith(isSaving: false);
    }
  }

  void togglePushNotifications(bool val) {
    state = state.copyWith(pushNotificationsEnabled: val);
  }

  void toggleTelegramNotifications(bool val) {
    state = state.copyWith(telegramNotificationsEnabled: val);
  }

  Future<void> updatePetInfo({
    required String name,
    required String breed,
    required String goal,
  }) async {
    final pet = state.pet;
    if (pet == null) return;

    state = state.copyWith(isSaving: true);
    try {
      final res = await _apiClient.patch(
        ApiConstants.petById(pet.id),
        data: {'name': name, 'breed': breed, 'goal': goal},
      );
      final updated = PetModel.fromJson(res as Map<String, dynamic>);
      state = state.copyWith(pet: updated, isSaving: false);
    } catch (_) {
      state = state.copyWith(isSaving: false);
    }
  }

  Future<void> logout() async {
    await _read(authControllerProvider.notifier).logout();
  }
}

final profileControllerProvider =
    StateNotifierProvider<ProfileController, ProfileState>((ref) {
  final api = ref.watch(apiClientProvider);
  final sync = ref.watch(syncEngineProvider);
  return ProfileController(api, sync, ref.read);
});
