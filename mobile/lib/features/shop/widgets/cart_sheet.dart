import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../shop_controller.dart';

class CartSheet extends ConsumerStatefulWidget {
  const CartSheet({super.key});

  @override
  ConsumerState<CartSheet> createState() => _CartSheetState();
}

class _CartSheetState extends ConsumerState<CartSheet> {
  final TextEditingController _addressController = TextEditingController(text: 'Москва, ул. Ленина, д. 10, кв. 42');

  @override
  void dispose() {
    _addressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(shopControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.surfaceDark : AppColors.surfaceLight;
    final textPrimary = isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight;
    final textSecondary = isDark ? AppColors.textSecondaryDark : AppColors.textSecondaryLight;

    return Container(
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: state.cartItems.isEmpty
          ? Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 12),
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: textSecondary.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                const Text('🛍', style: TextStyle(fontSize: 48)),
                const SizedBox(height: 16),
                Text('Корзина пуста', style: AppTypography.titleLarge(textPrimary)),
                const SizedBox(height: 8),
                Text(
                  'Добавьте натуральные лакомства для тренировок и погрызушки',
                  textAlign: TextAlign.center,
                  style: AppTypography.bodyMedium(textSecondary),
                ),
                const SizedBox(height: 32),
              ],
            )
          : SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: textSecondary.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Корзина', style: AppTypography.titleLarge(textPrimary)),
                      TextButton(
                        onPressed: () => ref.read(shopControllerProvider.notifier).clearCart(),
                        child: const Text('Очистить', style: TextStyle(color: AppColors.errorRed)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Cart Items
                  ...state.cartItems.map((item) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: AppColors.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Center(child: Text('🥩', style: TextStyle(fontSize: 24))),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(item.product.name, style: AppTypography.titleMedium(textPrimary)),
                                Text('${item.product.price} ₽ × ${item.quantity}', style: AppTypography.bodySmall(textSecondary)),
                              ],
                            ),
                          ),
                          // Plus / Minus
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.remove_circle_outline, size: 22),
                                onPressed: () => ref.read(shopControllerProvider.notifier).removeFromCart(item.product),
                              ),
                              Text('${item.quantity}', style: AppTypography.titleMedium(textPrimary)),
                              IconButton(
                                icon: const Icon(Icons.add_circle_outline, size: 22),
                                onPressed: () => ref.read(shopControllerProvider.notifier).addToCart(item.product),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }),
                  const Divider(),
                  const SizedBox(height: 10),

                  // Delivery Address
                  Text('Адрес доставки (СДЭК / Курьер)', style: AppTypography.bodySmall(textSecondary)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _addressController,
                    decoration: const InputDecoration(
                      prefixIcon: Icon(Icons.location_on_outlined),
                      contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Total
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Итого к оплате:', style: AppTypography.titleMedium(textPrimary)),
                      Text('${state.totalCartPrice} ₽', style: AppTypography.titleLarge(AppColors.primary)),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Tinkoff Pay CTA
                  ElevatedButton.icon(
                    onPressed: state.isOrderProcessing
                        ? null
                        : () async {
                            final success = await ref
                                .read(shopControllerProvider.notifier)
                                .checkoutTinkoff(_addressController.text);
                            if (success && context.mounted) {
                              Navigator.of(context).pop();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Заказ успешно оплачен через Т-Банк! 🎉'),
                                  backgroundColor: AppColors.successGreen,
                                ),
                              );
                            }
                          },
                    icon: const Text('💳 ', style: TextStyle(fontSize: 18)),
                    label: state.isOrderProcessing
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Text('Оплатить через Т-Банк (СБП / T-Pay)'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFFDD2D), // T-Bank Yellow
                      foregroundColor: Colors.black,
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
              ),
            ),
    );
  }
}
