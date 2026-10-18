import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import '../../data/models/product.dart';
import '../home/home_controller.dart';
import 'shop_controller.dart';
import 'widgets/cart_sheet.dart';

class ShopScreen extends ConsumerWidget {
  const ShopScreen({super.key});

  void _openCart(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => const CartSheet(),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(shopControllerProvider);
    final homeState = ref.watch(homeControllerProvider);
    final pet = homeState.activePet;

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    final filteredProducts = ref.read(shopControllerProvider.notifier).state.getFilteredProducts(pet);

    return Scaffold(
      appBar: AppBar(
        title: Text('Лакомства Pepito', style: AppTypography.titleLarge(textPrimary)),
        actions: [
          // Cart Button with Badge
          Stack(
            alignment: Alignment.center,
            children: [
              IconButton(
                icon: const Icon(Icons.shopping_bag_outlined),
                onPressed: () => _openCart(context),
              ),
              if (state.totalCartCount > 0)
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppColors.primary,
                    ),
                    constraints: const BoxConstraints(minWidth: 18, minHeight: 18),
                    child: Text(
                      '${state.totalCartCount}',
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          const SizedBox(height: 12),

          // Categories Filter Row
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _buildCategoryChip(
                  label: pet != null ? '🐾 Для ${pet.name}' : '🐾 Рекомендовано',
                  categoryKey: 'recommended',
                  isSelected: state.selectedCategory == 'recommended',
                  ref: ref,
                ),
                _buildCategoryChip(
                  label: '🥩 Для тренировок',
                  categoryKey: 'training',
                  isSelected: state.selectedCategory == 'training',
                  ref: ref,
                ),
                _buildCategoryChip(
                  label: '🦴 Долгоиграющие',
                  categoryKey: 'longplay',
                  isSelected: state.selectedCategory == 'longplay',
                  ref: ref,
                ),
                _buildCategoryChip(
                  label: '🐶 Для щенков',
                  categoryKey: 'puppy',
                  isSelected: state.selectedCategory == 'puppy',
                  ref: ref,
                ),
                _buildCategoryChip(
                  label: 'Все товары',
                  categoryKey: 'all',
                  isSelected: state.selectedCategory == 'all',
                  ref: ref,
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Product Grid
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 14,
                mainAxisSpacing: 14,
                childAspectRatio: 0.68,
              ),
              itemCount: filteredProducts.length,
              itemBuilder: (context, index) {
                final product = filteredProducts[index];
                return _buildProductCard(context, ref, product, isDark, textPrimary, textSecondary);
              },
            ),
          ),

          // Bottom Cart Bar when items in cart
          if (state.totalCartCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              decoration: BoxDecoration(
                color: isDark ? AppColors.surfaceDark : Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 15, offset: const Offset(0, -4)),
                ],
              ),
              child: SafeArea(
                top: false,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('В корзине ${state.totalCartCount} шт', style: AppTypography.bodySmall(textSecondary)),
                        Text('${state.totalCartPrice} ₽', style: AppTypography.titleLarge(textPrimary)),
                      ],
                    ),
                    ElevatedButton(
                      onPressed: () => _openCart(context),
                      style: ElevatedButton.styleFrom(minimumSize: const Size(160, 48)),
                      child: const Text('Оформить заказ'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCategoryChip({
    required String label,
    required String categoryKey,
    required bool isSelected,
    required WidgetRef ref,
  }) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        selectedColor: AppColors.primary.withOpacity(0.15),
        labelStyle: TextStyle(
          color: isSelected ? AppColors.primary : AppColors.textSecondaryLight,
          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        ),
        onSelected: (_) => ref.read(shopControllerProvider.notifier).selectCategory(categoryKey),
      ),
    );
  }

  Widget _buildProductCard(
    BuildContext context,
    WidgetRef ref,
    ProductModel product,
    bool isDark,
    Color textPrimary,
    Color textSecondary,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Meat Percentage Badge & Image container
            Expanded(
              child: Stack(
                children: [
                  Container(
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Center(child: Text('🥩', style: TextStyle(fontSize: 48))),
                  ),
                  Positioned(
                    top: 6,
                    left: 6,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppColors.successGreen,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        '${product.meatPercentage}% мясо',
                        style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),

            // Product Title & Weight
            Text(
              product.name,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: AppTypography.titleMedium(textPrimary).copyWith(fontSize: 14),
            ),
            const SizedBox(height: 2),
            Text(product.weightFormatted, style: AppTypography.bodySmall(textSecondary)),
            const SizedBox(height: 8),

            // Price & Add to Cart button
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(product.priceFormatted, style: AppTypography.titleLarge(AppColors.primary).copyWith(fontSize: 17)),
                InkWell(
                  onTap: () {
                    ref.read(shopControllerProvider.notifier).addToCart(product);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('«${product.name}» добавлено в корзину'),
                        duration: const Duration(seconds: 1),
                        behavior: SnackBarBehavior.floating,
                      ),
                    );
                  },
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.add, color: Colors.white, size: 20),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
