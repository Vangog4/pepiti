class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic details;

  ApiException({
    required this.message,
    this.statusCode,
    this.details,
  });

  @override
  String toString() => 'ApiException(statusCode: $statusCode, message: $message)';
}

class UnauthorizedException extends ApiException {
  UnauthorizedException({String message = 'Требуется авторизация'})
      : super(message: message, statusCode: 401);
}

class NetworkException extends ApiException {
  NetworkException({String message = 'Нет подключения к интернету'})
      : super(message: message, statusCode: null);
}

class ServerException extends ApiException {
  ServerException({String message = 'Ошибка сервера. Попробуйте позже'})
      : super(message: message, statusCode: 500);
}

class RateLimitException extends ApiException {
  RateLimitException({String message = 'Дневной лимит бесплатных запросов исчерпан'})
      : super(message: message, statusCode: 429);
}
