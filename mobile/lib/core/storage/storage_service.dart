import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  final FlutterSecureStorage _secureStorage;
  final SharedPreferences _prefs;

  static const String _keyToken = 'pepito_jwt_token';
  static const String _keyDeviceId = 'pepito_device_id';
  static const String _keyUserId = 'pepito_user_id';
  static const String _keyActivePetId = 'pepito_active_pet_id';
  static const String _keyOfflineSyncQueue = 'pepito_offline_sync_queue';
  static const String _keyCachedPull = 'pepito_cached_pull_data';

  StorageService({
    FlutterSecureStorage? secureStorage,
    required SharedPreferences prefs,
  })  : _secureStorage = secureStorage ?? const FlutterSecureStorage(),
        _prefs = prefs;

  // JWT Token
  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: _keyToken, value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: _keyToken);
  }

  Future<void> clearToken() async {
    await _secureStorage.delete(key: _keyToken);
  }

  // Device ID for Guest Mode
  Future<void> saveDeviceId(String deviceId) async {
    await _prefs.setString(_keyDeviceId, deviceId);
  }

  String? getDeviceId() {
    return _prefs.getString(_keyDeviceId);
  }

  // User ID
  Future<void> saveUserId(int userId) async {
    await _prefs.setInt(_keyUserId, userId);
  }

  int? getUserId() {
    return _prefs.getInt(_keyUserId);
  }

  // Active Pet ID
  Future<void> saveActivePetId(int petId) async {
    await _prefs.setInt(_keyActivePetId, petId);
  }

  int? getActivePetId() {
    return _prefs.getInt(_keyActivePetId);
  }

  // Offline Sync Queue (JSON string list)
  List<String> getOfflineSyncQueue() {
    return _prefs.getStringList(_keyOfflineSyncQueue) ?? [];
  }

  Future<void> saveOfflineSyncQueue(List<String> queue) async {
    await _prefs.setStringList(_keyOfflineSyncQueue, queue);
  }

  Future<void> clearOfflineSyncQueue() async {
    await _prefs.remove(_keyOfflineSyncQueue);
  }

  // Cached Pull Data for instant offline launch
  Future<void> saveCachedPullData(String jsonString) async {
    await _prefs.setString(_keyCachedPull, jsonString);
  }

  String? getCachedPullData() {
    return _prefs.getString(_keyCachedPull);
  }

  // Clear all session on logout
  Future<void> clearAll() async {
    await _secureStorage.deleteAll();
    await _prefs.remove(_keyUserId);
    await _prefs.remove(_keyActivePetId);
    await _prefs.remove(_keyOfflineSyncQueue);
    await _prefs.remove(_keyCachedPull);
  }
}
