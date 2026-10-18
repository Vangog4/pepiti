import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'audio/training_tools_service.dart';
import 'network/api_client.dart';
import 'storage/storage_service.dart';
import 'sync/sync_engine.dart';

// Must be overridden in main() with SharedPreferences.getInstance()
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be initialized before runApp');
});

final storageServiceProvider = Provider<StorageService>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return StorageService(prefs: prefs);
});

final apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(storageServiceProvider);
  return ApiClient(storage);
});

final syncEngineProvider = Provider<SyncEngine>((ref) {
  final api = ref.watch(apiClientProvider);
  final storage = ref.watch(storageServiceProvider);
  final engine = SyncEngine(apiClient: api, storageService: storage);
  ref.onDispose(engine.dispose);
  return engine;
});

final trainingToolsProvider = Provider<TrainingToolsService>((ref) {
  final service = TrainingToolsService();
  ref.onDispose(service.dispose);
  return service;
});
