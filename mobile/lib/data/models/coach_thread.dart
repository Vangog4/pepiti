class CoachMessageModel {
  final String role; // 'user' or 'coach'
  final String content;
  final int timestamp;
  final String? mediaType; // 'text', 'voice', 'photo', 'video'
  final String? mediaUrl;

  CoachMessageModel({
    required this.role,
    required this.content,
    required this.timestamp,
    this.mediaType = 'text',
    this.mediaUrl,
  });

  bool get isUser => role == 'user';
  bool get isCoach => role == 'coach';

  DateTime get dateTime => DateTime.fromMillisecondsSinceEpoch(timestamp * 1000);

  factory CoachMessageModel.fromJson(Map<String, dynamic> json) {
    return CoachMessageModel(
      role: json['role'] as String? ?? 'user',
      content: json['content'] as String? ?? '',
      timestamp: json['ts'] as int? ?? (DateTime.now().millisecondsSinceEpoch ~/ 1000),
      mediaType: json['media_type'] as String? ?? 'text',
      mediaUrl: json['media_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'role': role,
      'content': content,
      'ts': timestamp,
      'media_type': mediaType,
      'media_url': mediaUrl,
    };
  }
}

class CoachThreadModel {
  final int id;
  final int userId;
  final String? title;
  final String status; // 'active' or 'archived'
  final String? summary;
  final int messageCount;
  final List<CoachMessageModel> messages;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final bool isActive;

  CoachThreadModel({
    required this.id,
    required this.userId,
    this.title,
    this.status = 'active',
    this.summary,
    this.messageCount = 0,
    this.messages = const [],
    this.createdAt,
    this.updatedAt,
    this.isActive = false,
  });

  String get displayTitle => title ?? 'Консультация с кинологом';

  factory CoachThreadModel.fromJson(Map<String, dynamic> json) {
    var rawMsgs = json['messages_json'] as List? ?? json['messages'] as List? ?? [];
    List<CoachMessageModel> parsedMsgs =
        rawMsgs.map((m) => CoachMessageModel.fromJson(m as Map<String, dynamic>)).toList();

    return CoachThreadModel(
      id: json['id'] as int? ?? 0,
      userId: json['user_id'] as int? ?? 0,
      title: json['title'] as String?,
      status: json['status'] as String? ?? 'active',
      summary: json['summary'] as String?,
      messageCount: json['message_count'] as int? ?? parsedMsgs.length,
      messages: parsedMsgs,
      createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'].toString()) : null,
      updatedAt: json['updated_at'] != null ? DateTime.tryParse(json['updated_at'].toString()) : null,
      isActive: json['is_active'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'status': status,
      'summary': summary,
      'message_count': messageCount,
      'messages_json': messages.map((m) => m.toJson()).toList(),
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'is_active': isActive,
    };
  }
}
