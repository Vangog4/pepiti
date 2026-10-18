import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/api_constants.dart';
import '../../core/network/api_client.dart';
import '../../core/providers.dart';
import '../../data/models/pet.dart';
import '../../data/models/product.dart';
import '../home/home_controller.dart';

class ShopState {
  final List<ProductModel> allProducts;
  final String selectedCategory; // 'all', 'recommended', 'training', 'longplay', 'puppy'
  final List<CartItemModel> cartItems;
  final bool isLoading;
  final bool isOrderProcessing;
  final String? successOrderMessage;

  ShopState({
    this.allProducts = const [],
    this.selectedCategory = 'recommended',
    this.cartItems = const [],
    this.isLoading = false,
    this.isOrderProcessing = false,
    this.successOrderMessage,
  });

  int get totalCartPrice => cartItems.fold(0, (sum, item) => sum + item.totalPrice);
  int get totalCartCount => cartItems.fold(0, (sum, item) => sum + item.quantity);

  List<ProductModel> getFilteredProducts(PetModel? activePet) {
    if (selectedCategory == 'recommended') {
      if (activePet != null && activePet.isPuppy) {
        return allProducts.where((p) => p.isPuppy).toList();
      } else if (activePet != null && activePet.isSmallBreed) {
        return allProducts.where((p) => p.isSmallBreed).toList();
      }
      return allProducts.where((p) => p.category == 'training').toList();
    } else if (selectedCategory == 'training') {
      return allProducts.where((p) => p.category == 'training').toList();
    } else if (selectedCategory == 'longplay') {
      return allProducts.where((p) => p.category == 'longplay').toList();
    } else if (selectedCategory == 'puppy') {
      return allProducts.where((p) => p.isPuppy).toList();
    }
    return allProducts;
  }

  ShopState copyWith({
    List<ProductModel>? allProducts,
    String? selectedCategory,
    List<CartItemModel>? cartItems,
    bool? isLoading,
    bool? isOrderProcessing,
    String? successOrderMessage,
  }) {
    return ShopState(
      allProducts: allProducts ?? this.allProducts,
      selectedCategory: selectedCategory ?? this.selectedCategory,
      cartItems: cartItems ?? this.cartItems,
      isLoading: isLoading ?? this.isLoading,
      isOrderProcessing: isOrderProcessing ?? this.isOrderProcessing,
      successOrderMessage: successOrderMessage,
    );
  }
}

class ShopController extends StateNotifier<ShopState> {
  final ApiClient _apiClient;

  ShopController(this._apiClient) : super(ShopState(isLoading: true)) {
    loadProducts();
  }

  Future<void> loadProducts() async {
    // Populate with default catalog of natural Pepito treats matching Odoo 19 tags
    final defaultCatalog = [
      ProductModel(
        id: 1,
        name: 'Кусочки утки для дрессировки',
        category: 'training',
        price: 390,
        weightGrams: 80,
        description: 'Идеальный размер для быстрой похвалы. Не крошатся в кармане, 100% мясо.',
        imageUrl: 'https://pepitopet.ru/web/image/product.template/1/image_1024',
        meatPercentage: 100,
        isPuppy: true,
      ),
      ProductModel(
        id: 2,
        name: 'Говяжье легкое сушеное',
        category: 'training',
        price: 340,
        weightGrams: 70,
        description: 'Воздушные кусочки, гипоаллергенно. Легко ломаются на мелкие части.',
        imageUrl: 'https://pepitopet.ru/web/image/product.template/2/image_1024',
        meatPercentage: 100,
        isSmallBreed: true,
        isPuppy: true,
      ),
      ProductModel(
        id: 3,
        name: 'Бычий корень долгоиграющий',
        category: 'longplay',
        price: 590,
        weightGrams: 120,
        description: 'Натуральная погрызушка на 30–60 минут. Очищает зубной камень и снимает стресс.',
        imageUrl: 'https://pepitopet.ru/web/image/product.template/3/image_1024',
        meatPercentage: 100,
      ),
      ProductModel(
        id: 4,
        name: 'Трахея говяжья хрустящая',
        category: 'longplay',
        price: 450,
        weightGrams: 100,
        description: 'Источник натурального хондроитина и коллагена для суставов щенков и взрослых собак.',
        imageUrl: 'https://pepitopet.ru/web/image/product.template/4/image_1024',
        meatPercentage: 100,
        isPuppy: true,
      ),
      ProductModel(
        id: 5,
        name: 'Индейка кубиками для мини-пород',
        category: 'by_size',
        price: 380,
        weightGrams: 90,
        description: 'Миниатюрные кубики для шпицев, йорков, корги и мелких щенков.',
        imageUrl: 'https://pepitopet.ru/web/image/product.template/5/image_1024',
        meatPercentage: 100,
        isSmallBreed: true,
        isPuppy: true,
      ),
    ];

    state = state.copyWith(allProducts: defaultCatalog, isLoading: false);
  }

  void selectCategory(String cat) {
    state = state.copyWith(selectedCategory: cat);
  }

  void addToCart(ProductModel product) {
    final current = List<CartItemModel>.from(state.cartItems);
    final idx = current.indexWhere((item) => item.product.id == product.id);

    if (idx != -1) {
      current[idx].quantity += 1;
    } else {
      current.add(CartItemModel(product: product, quantity: 1));
    }

    state = state.copyWith(cartItems: current);
  }

  void removeFromCart(ProductModel product) {
    final current = List<CartItemModel>.from(state.cartItems);
    final idx = current.indexWhere((item) => item.product.id == product.id);

    if (idx != -1) {
      if (current[idx].quantity > 1) {
        current[idx].quantity -= 1;
      } else {
        current.removeAt(idx);
      }
      state = state.copyWith(cartItems: current);
    }
  }

  void clearCart() {
    state = state.copyWith(cartItems: []);
  }

  // Tinkoff Checkout integration
  Future<bool> checkoutTinkoff(String deliveryAddress) async {
    if (state.cartItems.isEmpty) return false;

    state = state.copyWith(isOrderProcessing: true);
    await Future.delayed(const Duration(seconds: 2)); // Simulate payment initiation

    state = state.copyWith(
      isOrderProcessing: false,
      cartItems: [],
      successOrderMessage: 'Заказ успешно оформлен! Чек и трек-номер отправлены.',
    );
    return true;
  }
}

final shopControllerProvider =
    StateNotifierProvider<ShopController, ShopState>((ref) {
  final api = ref.watch(apiClientProvider);
  return ShopController(api);
});
