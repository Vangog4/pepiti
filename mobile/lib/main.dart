import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/providers.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/auth_controller.dart';
import 'features/auth/welcome_screen.dart';
import 'features/home/home_controller.dart';
import 'features/navigation/main_nav_shell.dart';
import 'features/onboarding/pet_onboarding_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final sharedPreferences = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(sharedPreferences),
      ],
      child: const PepitoApp(),
    ),
  );
}

class PepitoApp extends StatelessWidget {
  const PepitoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pepito — AI-кинолог',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const AppRouterWidget(),
    );
  }
}

class AppRouterWidget extends ConsumerStatefulWidget {
  const AppRouterWidget({super.key});

  @override
  ConsumerState<AppRouterWidget> createState() => _AppRouterWidgetState();
}

class _AppRouterWidgetState extends ConsumerState<AppRouterWidget> {
  bool _forceOnboarding = false;

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final homeState = ref.watch(homeControllerProvider);

    // Initial Splash / Loading
    if (authState.status == AuthStatus.initial || authState.status == AuthStatus.loading) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('🐕', style: TextStyle(fontSize: 64)),
              SizedBox(height: 16),
              CircularProgressIndicator(),
            ],
          ),
        ),
      );
    }

    // Unauthenticated -> Show Welcome Screen
    if (authState.status == AuthStatus.unauthenticated) {
      return WelcomeScreen(
        onContinueToOnboarding: () {
          setState(() => _forceOnboarding = true);
        },
        onAuthenticated: () {
          setState(() => _forceOnboarding = false);
        },
      );
    }

    // If newly created guest or no pet registered yet -> Show Onboarding Wizard
    final hasPet = homeState.activePet != null;
    if (_forceOnboarding || (!hasPet && !homeState.isLoading)) {
      return PetOnboardingScreen(
        onCompleted: () {
          setState(() => _forceOnboarding = false);
          ref.read(homeControllerProvider.notifier).refresh();
        },
      );
    }

    // Authenticated & Pet Exists -> Main 5-Tab App Shell
    return const MainNavShell();
  }
}
