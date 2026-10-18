import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:pepito_mobile/data/models/sync_payload.dart';

void main() {
  group('Sync Protocol & TaskChangeItem Tests', () {
    test('TaskChangeItem JSON structure matches FastAPI backend contract', () {
      final now = DateTime.utc(2026, 10, 18, 12, 0, 0);
      final item = TaskChangeItem(
        taskId: 123,
        isCompleted: true,
        completedAt: now,
      );

      final jsonMap = item.toJson();

      expect(jsonMap['task_id'], 123);
      expect(jsonMap['is_completed'], true);
      expect(jsonMap['completed_at'], '2026-10-18T12:00:00.000Z');

      final reconstructed = TaskChangeItem.fromJson(jsonMap);
      expect(reconstructed.taskId, 123);
      expect(reconstructed.isCompleted, true);
    });

    test('Offline queue deduplication logic', () {
      final List<String> queue = [];

      void queueTask(int taskId, bool isCompleted) {
        final item = TaskChangeItem(
          taskId: taskId,
          isCompleted: isCompleted,
          completedAt: DateTime.now().toUtc(),
        );

        queue.removeWhere((rawJson) {
          try {
            final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
            return decoded['task_id'] == taskId;
          } catch (_) {
            return false;
          }
        });

        queue.add(jsonEncode(item.toJson()));
      }

      // First toggle: task 1 -> completed
      queueTask(1, true);
      expect(queue.length, 1);

      // Second toggle: task 2 -> completed
      queueTask(2, true);
      expect(queue.length, 2);

      // Third toggle: task 1 -> uncompleted (should replace previous task 1)
      queueTask(1, false);
      expect(queue.length, 2);

      final task1Data = jsonDecode(queue.firstWhere((q) => q.contains('"task_id":1')));
      expect(task1Data['is_completed'], false);
    });
  });
}
