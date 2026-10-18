class ProductModel {
  final int id;
  final String name;
  final String category; // 'training', 'longplay', 'by_size'
  final int price;
  final int weightGrams;
  final String description;
  final String imageUrl;
  final int meatPercentage; // e.g. 100% мясо
  final bool isPuppy;
  final bool isSmallBreed;

  ProductModel({
    required this.id,
    required this.name,
    required this.category,
    required this.price,
    required this.weightGrams,
    required this.description,
    required this.imageUrl,
    this.meatPercentage = 100,
    this.isPuppy = false,
    this.isSmallBreed = false,
  });

  String get weightFormatted => '$weightGrams г';
  String get priceFormatted => '$price ₽';

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    return ProductModel(
      id: json['id'] as int? ?? 0,
      name: json['name'] as String? ?? 'Лакомство Pepito',
      category: json['category'] as String? ?? 'training',
      price: json['price'] as int? ?? 390,
      weightGrams: json['weight_grams'] as int? ?? 100,
      description: json['description'] as String? ?? 'Натуральное гипоаллергенное лакомство для собак',
      imageUrl: json['image_url'] as String? ?? '',
      meatPercentage: json['meat_percentage'] as int? ?? 100,
      isPuppy: json['is_puppy'] as bool? ?? false,
      isSmallBreed: json['is_small_breed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'category': category,
      'price': price,
      'weight_grams': weightGrams,
      'description': description,
      'image_url': imageUrl,
      'meat_percentage': meatPercentage,
      'is_puppy': isPuppy,
      'is_small_breed': isSmallBreed,
    };
  }
}

class CartItemModel {
  final ProductModel product;
  int quantity;

  CartItemModel({
    required this.product,
    this.quantity = 1,
  });

  int get totalPrice => product.price * quantity;
}
