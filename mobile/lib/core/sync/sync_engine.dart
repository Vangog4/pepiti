import 'dart:async';
import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../constants/api_constants.dart';
import '../network/api_client.dart';
import '../storage/storage_service.dart';
import '../../data/models/sync_payload.dart';

enum SyncStatus { idle, syncing, offline, error }

class SyncEngine {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final Connectivity _connectivity;

  SyncStatus _status = SyncStatus.idle;
  SyncStatus get status => _status;

  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  // Callbacks for UI reactive updates
  void Function(SyncPullResponse data)? onPullDataReceived;
  void Function(SyncStatus status)? onStatusChanged;

  SyncEngine({
    required ApiClient apiClient,
    required StorageService storageService,
    Connectivity? connectivity,
  })  : _apiClient = apiClient,
        _storageService = storageService,
        _connectivity = connectivity ?? Connectivity() {
    _initConnectivityListener();
  }

  void _initConnectivityListener() {
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen((results) {
      final hasConnection = results.any((r) => r != ConnectivityResult.none);
      if (hasConnection && _hasPendingChanges()) {
        pushPendingChanges();
      }
    });
  }

  void dispose() {
    _connectivitySubscription?.cancel();
  }

  // --- Offline Queue Handling ---

  bool _hasPendingChanges() {
    return _storageService.getOfflineSyncQueue().isNotEmpty;
  }

  /// Adds a task toggle to offline queue and triggers push if online
  Future<void> queueTaskToggle(int taskId, bool isCompleted) async {
    final queue = _storageService.getOfflineSyncQueue();
    final item = TaskChangeItem(
      taskId: taskId,
      isCompleted: isCompleted,
      completedAt: DateTime.now().toUtc(),
    );

    // Replace if same task was queued earlier
    queue.removeWhere((rawJson) {
      try {
        final decoded = jsonDecode(rawJson);
        return decoded['task_id'] == taskId;
      } catch (_) {
        return false;
      }
    });

    queue.add(jsonEncode(item.toJson()));
    await _storageService.saveOfflineSyncQueue(queue);

    // Attempt push immediately
    unawaited(pushPendingChanges());
  }

  /// Push all queued offline changes to server
  Future<SyncPushResponse?> pushPendingChanges() async {
    final queue = _storageService.getOfflineSyncQueue();
    if (queue.isEmpty) return null;

    _updateStatus(SyncStatus.syncing);

    final List<Map<String, dynamic>> tasksData = [];
    for (final raw in queue) {
      try {
        tasksData.add(jsonDecode(raw) as Map<String, dynamic>);
      } catch (_) {}
    }

    try {
      final responseData = await _apiClient.post(
        ApiConstants.syncPush,
        data: {'task_changes': tasksData},
      );

      final pushResponse = SyncPushResponse.fromJson(responseData as Map<String, dynamic>);

      // Clear processed queue
      await _storageService.clearOfflineSyncQueue();
      _updateStatus(SyncStatus.idle);

      // Trigger full state refresh to keep all models in sync
      unawaited(pullFullState());

      return pushResponse;
    } catch (e) {
      _updateStatus(SyncStatus.offline);
      return null;
    }
  }

  /// Pull full state from server and cache locally
  Future<SyncPullResponse?> pullFullState() async {
    _updateStatus(SyncStatus.syncing);
    try {
      final responseData = await _apiClient.get(ApiConstants.syncPull);
      final pullResponse = SyncPullResponse.fromJson(responseData as Map<String, dynamic>);

      // Cache locally for instant launch next time
      await _storageService.saveCachedPullData(jsonEncode(pullResponse.toJson()));

      _updateStatus(SyncStatus.idle);
      onPullDataReceived?.call(pullResponse);
      return pullResponse;
    } catch (e) {
      _updateStatus(SyncStatus.offline);
      // Fallback to local cached data if offline
      final cachedJson = _storageService.getCachedPullData();
      if (cachedJson != null) {
        try {
          final cached = SyncPullResponse.fromJson(jsonDecode(cachedJson) as Map<String, dynamic>);
          onPullDataReceived?.call(cached);
          return cached;
        } catch (_) {}
      }
      return null;
    }
  }

  void _updateStatus(SyncStatus newStatus) {
    _status = newStatus;
    onStatusChanged?.call(newStatus);
  }
}
