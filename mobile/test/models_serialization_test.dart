import 'package:flutter_test/flutter_test.dart';
import 'package:pepito_mobile/data/models/coach_thread.dart';
import 'package:pepito_mobile/data/models/pet.dart';
import 'package:pepito_mobile/data/models/product.dart';
import 'package:pepito_mobile/data/models/sync_payload.dart';
import 'package:pepito_mobile/data/models/training_plan.dart';
import 'package:pepito_mobile/data/models/training_task.dart';
import 'package:pepito_mobile/data/models/user_profile.dart';

void main() {
  group('Models Serialization Tests', () {
    test('UserProfile JSON serialization', () {
      final json = {
        'id': 42,
        'telegram_id': 12345678,
        'username': 'doglover',
        'first_name': 'Алексей',
        'is_premium': true,
        'training_days': 15,
        'reminder_time': '18:30',
        'timezone': 'Europe/Moscow',
        'language_code': 'ru',
      };

      final profile = UserProfile.fromJson(json);

      expect(profile.id, 42);
      expect(profile.telegramId, 12345678);
      expect(profile.isTelegramLinked, true);
      expect(profile.isPremium, true);
      expect(profile.trainingDays, 15);
      expect(profile.reminderTime, '18:30');

      final serialized = profile.toJson();
      expect(serialized['id'], 42);
      expect(serialized['telegram_id'], 12345678);
    });

    test('PetModel puppy and small breed helpers', () {
      final puppy = PetModel(
        id: 1,
        userId: 10,
        name: 'Арчи',
        breed: 'Корги',
        ageCategory: 'Щенок (до 4 мес)',
        weightKg: 4.5,
      );

      expect(puppy.isPuppy, true);
      expect(puppy.isSmallBreed, true);

      final adult = PetModel(
        id: 2,
        userId: 10,
        name: 'Рекс',
        breed: 'Овчарка',
        ageCategory: 'Взрослый (3–7 лет)',
        weightKg: 35.0,
      );

      expect(adult.isPuppy, false);
      expect(adult.isSmallBreed, false);
    });

    test('TrainingPlanModel task day filtering', () {
      final tasks = [
        TrainingTaskModel(id: 1, dayOfWeek: 1, title: 'Сидеть', isCompleted: true),
        TrainingTaskModel(id: 2, dayOfWeek: 1, title: 'Лежать', isCompleted: false),
        TrainingTaskModel(id: 3, dayOfWeek: 2, title: 'Ко мне', isCompleted: false),
      ];

      final plan = TrainingPlanModel(
        id: 100,
        userId: 5,
        petId: 1,
        title: 'Недельный план',
        weekNumber: 42,
        tasks: tasks,
      );

      expect(plan.isWeeklyPlan, true);
      expect(plan.getTasksForDay(1).length, 2);
      expect(plan.getTasksForDay(2).length, 1);
      expect(plan.completedCount(1), 1);
    });

    test('SyncPullResponse deserialization', () {
      final json = {
        'profile': {
          'id': 1,
          'telegram_id': 999,
          'is_premium': false,
          'training_days': 3,
        },
        'pets': [
          {'id': 10, 'user_id': 1, 'name': 'Бруно', 'breed': 'Лабрадор'}
        ],
        'today_tasks': [
          {'id': 501, 'title': 'Выдержка', 'is_completed': false, 'duration_minutes': 5}
        ],
        'subscription': {'is_premium': false, 'days_left': 0},
        'coach_threads': [],
      };

      final pull = SyncPullResponse.fromJson(json);

      expect(pull.user.id, 1);
      expect(pull.pets.first.name, 'Бруно');
      expect(pull.todayTasks.first.title, 'Выдержка');
      expect(pull.subscription.isPremium, false);
    });

    test('ProductModel price formatting', () {
      final product = ProductModel(
        id: 1,
        name: 'Утка для дрессировки',
        category: 'training',
        price: 390,
        weightGrams: 80,
        description: '100% мясо',
        imageUrl: '',
      );

      expect(product.priceFormatted, '390 ₽');
      expect(product.weightFormatted, '80 г');
    });
  });
}
