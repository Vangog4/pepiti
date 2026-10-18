class ApiConstants {
  ApiConstants._();

  static const String baseUrl = 'https://bot.pepitopet.ru/api/v1';
  static const String webappUrl = 'https://bot.pepitopet.ru/webapp';
  static const String shopBaseUrl = 'https://pepitopet.ru/shop';
  static const String botUsername = 'pepitopetbot';

  // Auth endpoints
  static const String authGuest = '/auth/guest';
  static const String authTelegramSession = '/auth/telegram/session';
  static const String authTelegramCheck = '/auth/telegram/check';
  static const String authTelegramCode = '/auth/telegram/code';
  static const String authVk = '/auth/vk';
  static const String authLink = '/auth/link';

  // Sync endpoints
  static const String syncPull = '/sync/pull';
  static const String syncPush = '/sync/push';

  // Profile endpoints
  static const String profile = '/profile';

  // Pets endpoints
  static const String pets = '/pets';
  static String petById(int id) => '/pets/$id';

  // Training endpoints
  static const String trainingPlan = '/training/plan';
  static const String trainingToday = '/training/today';
  static String trainingTaskToggle(int taskId) => '/training/tasks/$taskId/toggle';
  static const String trainingPdf = '/training/pdf';

  // Coach endpoints
  static const String coachThreads = '/coach/threads';
  static String coachThreadMessages(int threadId) => '/coach/threads/$threadId/messages';
  static String coachThreadArchive(int threadId) => '/coach/threads/$threadId/archive';

  // Subscription endpoints
  static const String subscriptionStatus = '/subscription/status';
  static const String subscriptionPlans = '/subscription/plans';

  // Push endpoints
  static const String pushRegister = '/push/register';
}
