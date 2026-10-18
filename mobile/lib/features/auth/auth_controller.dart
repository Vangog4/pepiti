import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/providers.dart';
import '../../core/storage/storage_service.dart';
import '../../core/sync/sync_engine.dart';

enum AuthStatus { initial, authenticated, guest, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final int? userId;
  final String? errorMessage;

  AuthState({
    required this.status,
    this.userId,
    this.errorMessage,
  });

  bool get isAuthenticated => status == AuthStatus.authenticated || status == AuthStatus.guest;

  AuthState copyWith({
    AuthStatus? status,
    int? userId,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      userId: userId ?? this.userId,
      errorMessage: errorMessage,
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final SyncEngine _syncEngine;

  AuthController({
    required ApiClient apiClient,
    required StorageService storageService,
    required SyncEngine syncEngine,
  })  : _apiClient = apiClient,
        _storageService = storageService,
        _syncEngine = syncEngine,
        super(AuthState(status: AuthStatus.initial)) {
    checkInitialAuth();
  }

  Future<void> checkInitialAuth() async {
    final token = await _storageService.getToken();
    final userId = _storageService.getUserId();

    if (token != null && token.isNotEmpty) {
      state = state.copyWith(status: AuthStatus.authenticated, userId: userId);
      // Trigger background sync
      unawaited(_syncEngine.pullFullState());
    } else {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  // Zero-friction instant guest login
  Future<bool> loginAsGuest(String deviceId) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);
    try {
      final res = await _apiClient.post(
        ApiConstants.authGuest,
        data: {'device_id': deviceId, 'platform': 'android'},
      );

      final token = (res['access_token'] ?? res['token']) as String;
      final userId = (res['user_id'] as num).toInt();

      await _storageService.saveToken(token);
      await _storageService.saveUserId(userId);
      await _storageService.saveDeviceId(deviceId);

      state = state.copyWith(status: AuthStatus.guest, userId: userId);
      unawaited(_syncEngine.pullFullState());
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        errorMessage: 'Не удалось войти как гость. Проверьте интернет.',
      );
      return false;
    }
  }

  // 6-digit code login from Telegram bot (/connect command)
  Future<bool> loginWithTelegramCode(String code) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);
    try {
      final res = await _apiClient.post(
        ApiConstants.authTelegramCode,
        data: {'code': code.trim()},
      );

      final token = (res['access_token'] ?? res['token']) as String;
      final userId = (res['user_id'] as num).toInt();

      await _storageService.saveToken(token);
      await _storageService.saveUserId(userId);

      state = state.copyWith(status: AuthStatus.authenticated, userId: userId);
      unawaited(_syncEngine.pullFullState());
      return true;
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        errorMessage: 'Неверный или устаревший код из Telegram бота.',
      );
      return false;
    }
  }

  // Deep-link session creation
  Future<String?> createTelegramSession() async {
    try {
      final res = await _apiClient.post(ApiConstants.authTelegramSession);
      return res['session_token'] as String?;
    } catch (_) {
      return null;
    }
  }

  // Poll for Telegram session confirmation
  Future<bool> checkTelegramSession(String sessionToken) async {
    try {
      final res = await _apiClient.get(
        ApiConstants.authTelegramCheck,
        queryParameters: {'session_token': sessionToken},
      );

      final tokenData = res['token_data'] as Map<String, dynamic>?;
      if (res['status'] == 'authenticated' && tokenData != null) {
        final token = tokenData['access_token'] as String;
        final userId = (tokenData['user_id'] as num).toInt();

        await _storageService.saveToken(token);
        await _storageService.saveUserId(userId);

        state = state.copyWith(status: AuthStatus.authenticated, userId: userId);
        unawaited(_syncEngine.pullFullState());
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  // Link existing guest account to Telegram
  Future<bool> linkTelegramAccount(String code) async {
    try {
      final res = await _apiClient.post(
        ApiConstants.authLink,
        data: {
          'provider': 'telegram_code',
          'credential': code.trim(),
        },
      );

      final tokenData = res['token_data'] as Map<String, dynamic>?;
      if (tokenData != null) {
        final token = tokenData['access_token'] as String;
        final userId = (tokenData['user_id'] as num).toInt();
        await _storageService.saveToken(token);
        await _storageService.saveUserId(userId);
      } else if (res['merged_user_id'] != null) {
        await _storageService.saveUserId((res['merged_user_id'] as num).toInt());
      }

      state = state.copyWith(status: AuthStatus.authenticated);
      unawaited(_syncEngine.pullFullState());
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _storageService.clearAll();
    state = AuthState(status: AuthStatus.unauthenticated);
  }
}

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>((ref) {
  final api = ref.watch(apiClientProvider);
  final storage = ref.watch(storageServiceProvider);
  final sync = ref.watch(syncEngineProvider);

  return AuthController(
    apiClient: api,
    storageService: storage,
    syncEngine: sync,
  );
});
