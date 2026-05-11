import 'package:flutter/material.dart';

class MarketMapPanelImpl extends StatelessWidget {
  const MarketMapPanelImpl({
    super.key,
    required this.centerLat,
    required this.centerLng,
    required this.radiusMeters,
  });

  final double centerLat;
  final double centerLng;
  final double radiusMeters;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFFCBD5C0),
      alignment: Alignment.center,
      child: const Text(
        '지도는 웹에서 활성화됩니다.',
        style: TextStyle(
          color: Color(0xFF3C4739),
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

