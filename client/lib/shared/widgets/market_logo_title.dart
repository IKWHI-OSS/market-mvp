import 'package:flutter/material.dart';

enum MarketLogoVariant { black, color }

class MarketLogoTitle extends StatelessWidget {
  const MarketLogoTitle({
    super.key,
    this.variant = MarketLogoVariant.black,
    this.height,
  });

  final MarketLogoVariant variant;
  final double? height;

  String get _assetPath {
    switch (variant) {
      case MarketLogoVariant.color:
        return 'assets/images/new_logo/typo_logo_eng_color.png';
      case MarketLogoVariant.black:
        return 'assets/images/new_logo/typo_logo_eng_black.png';
    }
  }

  @override
  Widget build(BuildContext context) {
    final resolvedHeight = height ??
        (variant == MarketLogoVariant.color ? 24.0 : 36.0);
    return Image.asset(
      _assetPath,
      height: resolvedHeight,
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) => const Text(
        '돗개비',
        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
      ),
    );
  }
}
