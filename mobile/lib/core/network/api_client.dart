import 'dart:io';
import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../storage/storage_service.dart';
import 'api_exceptions.dart';
import 'auth_interceptor.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient(StorageService storageService, {Dio? customDio}) {
    _dio = customDio ??
        Dio(
          BaseOptions(
            baseUrl: ApiConstants.baseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 25),
          ),
        );

    _dio.interceptors.add(AuthInterceptor(storageService));
  }

  // Generic request handler with error wrapping
  Future<dynamic> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> post(String path, {dynamic data, Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.post(path, data: data, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> patch(String path, {dynamic data}) async {
    try {
      final response = await _dio.patch(path, data: data);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> delete(String path) async {
    try {
      final response = await _dio.delete(path);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Upload multipart media (voice audio, photo, video)
  Future<dynamic> uploadFile(
    String path, {
    required File file,
    required String fieldName,
    Map<String, dynamic>? extraData,
  }) async {
    try {
      final fileName = file.path.split('/').last;
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(file.path, filename: fileName),
        if (extraData != null) ...extraData,
      });

      final response = await _dio.post(
        path,
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Download binary data (e.g. PDF training plan)
  Future<List<int>> downloadBytes(String path) async {
    try {
      final response = await _dio.get<List<int>>(
        path,
        options: Options(responseType: ResponseType.bytes),
      );
      return response.data ?? [];
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  ApiException _handleDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return NetworkException();
    }

    final statusCode = error.response?.statusCode;
    final data = error.response?.data;

    String message = 'Произошла ошибка при обращении к серверу';
    if (data is Map && data.containsKey('detail')) {
      message = data['detail'].toString();
    } else if (data is Map && data.containsKey('error')) {
      message = data['error'].toString();
    }

    if (statusCode == 401) {
      return UnauthorizedException(message: message);
    } else if (statusCode == 429) {
      return RateLimitException(message: message);
    } else if (statusCode != null && statusCode >= 500) {
      return ServerException(message: message);
    }

    return ApiException(message: message, statusCode: statusCode, details: data);
  }
}
