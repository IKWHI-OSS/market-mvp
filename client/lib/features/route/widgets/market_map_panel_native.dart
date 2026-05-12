import 'package:flutter/material.dart';
import 'package:flutter_naver_map/flutter_naver_map.dart';

class MarketMapPanelImpl extends StatefulWidget {
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
  State<MarketMapPanelImpl> createState() => _MarketMapPanelImplState();
}

class _MarketMapPanelImplState extends State<MarketMapPanelImpl> {
  static const _marketPins = <_NativeMarketPin>[
    _NativeMarketPin(
      id: 'mangwon-fresh-veg',
      label: '망원 신선야채',
      latOffset: 0.00034,
      lngOffset: -0.00042,
      color: Color(0xFF4A7D1A),
    ),
    _NativeMarketPin(
      id: 'mangwon-fish',
      label: '망원 수산',
      latOffset: -0.00010,
      lngOffset: 0.00044,
      color: Color(0xFFD4663A),
    ),
    _NativeMarketPin(
      id: 'dalkom-fruit',
      label: '달콤 과일',
      latOffset: -0.00036,
      lngOffset: -0.00004,
      color: Color(0xFF7A9A38),
    ),
  ];

  NLatLng get _center => NLatLng(widget.centerLat, widget.centerLng);

  NLatLngBounds get _extent {
    const latDelta = 0.0012;
    const lngDelta = 0.0014;
    return NLatLngBounds(
      southWest: NLatLng(widget.centerLat - latDelta, widget.centerLng - lngDelta),
      northEast: NLatLng(widget.centerLat + latDelta, widget.centerLng + lngDelta),
    );
  }

  Future<void> _onMapReady(NaverMapController controller) async {
    final overlays = <NAddableOverlay>{
      NCircleOverlay(
        id: 'mangwon-market-radius',
        center: _center,
        radius: widget.radiusMeters,
        color: const Color(0x334A7D1A),
        outlineColor: const Color(0xFF4A7D1A),
        outlineWidth: 2,
      ),
      ..._marketPins.map(
        (pin) => NMarker(
          id: pin.id,
          position: NLatLng(
            widget.centerLat + pin.latOffset,
            widget.centerLng + pin.lngOffset,
          ),
          iconTintColor: pin.color,
          caption: NOverlayCaption(
            text: pin.label,
            textSize: 12,
            color: const Color(0xFF2F5710),
            haloColor: const Color(0xFFFDFBF5),
          ),
        ),
      ),
    };
    await controller.addOverlayAll(overlays);
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(0),
      child: Stack(
        fit: StackFit.expand,
        children: [
          NaverMap(
            forceGesture: true,
            options: NaverMapViewOptions(
              initialCameraPosition: NCameraPosition(
                target: _center,
                zoom: 17,
              ),
              extent: _extent,
              minZoom: 16,
              maxZoom: 19,
              rotationGesturesEnable: false,
              tiltGesturesEnable: false,
              locationButtonEnable: false,
              compassEnable: false,
              scaleBarEnable: false,
              indoorEnable: false,
              logoMargin: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            ),
            onMapReady: _onMapReady,
          ),
          Positioned(
            left: 12,
            top: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
              decoration: BoxDecoration(
                color: const Color(0xF2FDFBF5),
                borderRadius: BorderRadius.circular(12),
                boxShadow: const [
                  BoxShadow(color: Color(0x1A000000), blurRadius: 10, offset: Offset(0, 4)),
                ],
              ),
              child: Text(
                '망원시장 반경 ${widget.radiusMeters.round()}m',
                style: const TextStyle(
                  color: Color(0xFF2F5710),
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NativeMarketPin {
  const _NativeMarketPin({
    required this.id,
    required this.label,
    required this.latOffset,
    required this.lngOffset,
    required this.color,
  });

  final String id;
  final String label;
  final double latOffset;
  final double lngOffset;
  final Color color;
}
