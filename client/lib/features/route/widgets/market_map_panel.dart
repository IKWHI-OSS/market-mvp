import 'package:flutter/material.dart';

import 'market_map_panel_stub.dart'
    if (dart.library.html) 'market_map_panel_web.dart' as impl;

class MarketMapPanel extends StatelessWidget {
  const MarketMapPanel({
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
    return impl.MarketMapPanelImpl(
      centerLat: centerLat,
      centerLng: centerLng,
      radiusMeters: radiusMeters,
    );
  }
}

