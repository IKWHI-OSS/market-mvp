import 'package:flutter/material.dart';

class MarketLogoTitle extends StatelessWidget {
  const MarketLogoTitle({super.key});

  static const _assetPath = 'assets/images/branding/typo logo.png';

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      _assetPath,
      height: 24,
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) => const Text(
        'Market Info',
        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
      ),
    );
  }
}
