import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'router.dart';

class MarketInfoApp extends StatelessWidget {
  const MarketInfoApp({super.key});

  @override
  Widget build(BuildContext context) {
    final baseTextTheme = ThemeData.light(useMaterial3: true).textTheme;
    final notoTextTheme = GoogleFonts.notoSansTextTheme(baseTextTheme);
    final juaFamily = GoogleFonts.jua().fontFamily;

    return MaterialApp(
      title: '돗개비',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF4A7D1A),
          onPrimary: Color(0xFFF2F7EC),
          secondary: Color(0xFFD4663A),
          surface: Color(0xFFFDFBF5),
          onSurface: Color(0xFF1E1D18),
        ),
        scaffoldBackgroundColor: const Color(0xFFF2F7EC),
        cardColor: const Color(0xFFFDFBF5),
        fontFamily: GoogleFonts.notoSans().fontFamily,
        textTheme: notoTextTheme.copyWith(
          displayLarge: notoTextTheme.displayLarge?.copyWith(fontFamily: juaFamily, fontWeight: FontWeight.w700),
          displayMedium: notoTextTheme.displayMedium?.copyWith(fontFamily: juaFamily, fontWeight: FontWeight.w700),
          displaySmall: notoTextTheme.displaySmall?.copyWith(fontFamily: juaFamily, fontWeight: FontWeight.w700),
          headlineLarge: notoTextTheme.headlineLarge?.copyWith(fontFamily: juaFamily, fontWeight: FontWeight.w700),
          headlineMedium: notoTextTheme.headlineMedium?.copyWith(fontFamily: juaFamily, fontWeight: FontWeight.w700),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: const Color(0xFF2F5710),
          titleTextStyle: notoTextTheme.titleLarge?.copyWith(
            color: const Color(0xFF2F5710),
            fontWeight: FontWeight.w700,
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF4A7D1A),
            foregroundColor: const Color(0xFFF2F7EC),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            minimumSize: const Size(44, 44),
            textStyle: notoTextTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF2F5710),
            side: const BorderSide(color: Color(0xFF4A7D1A), width: 1.2),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            minimumSize: const Size(44, 44),
            textStyle: notoTextTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
          ),
        ),
        useMaterial3: true,
      ),
      initialRoute: AppRoutes.login,
      onGenerateRoute: AppRouter.onGenerateRoute,
    );
  }
}
