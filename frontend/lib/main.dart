import 'package:flutter/material.dart';
import 'package:frontend/screens/login_screen.dart';
import 'package:frontend/screens/signup_screen.dart';
import 'package:frontend/screens/dashboard_screen.dart';
import 'package:frontend/screens/upload_screen.dart';
import 'package:frontend/screens/review_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Questionnaire AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      initialRoute: '/login',
      routes: {
        '/login': (_) => const LoginScreen(),
        '/signup': (_) => const SignupScreen(),
        '/dashboard': (_) => const DashboardScreen(),
        '/upload': (_) => const UploadScreen(),
      },
      onGenerateRoute: (settings) {
        // Handle review route with arguments
        if (settings.name == '/review') {
          final questionnaireId = settings.arguments as int;
          return MaterialPageRoute(
            builder: (_) => ReviewScreen(questionnaireId: questionnaireId),
          );
        }
        return null;
      },
    );
  }
}
