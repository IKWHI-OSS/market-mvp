import 'package:flutter/material.dart';

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
  static const _pins = <_MarketPin>[
    _MarketPin(label: '망원 신선야채', alignment: Alignment(-0.45, -0.28), color: Color(0xFF4A7D1A)),
    _MarketPin(label: '망원 수산', alignment: Alignment(0.28, -0.06), color: Color(0xFFD4663A)),
    _MarketPin(label: '달콤 과일', alignment: Alignment(-0.08, 0.38), color: Color(0xFF7A9A38)),
  ];

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFDDE8D4), Color(0xFFF2F7EC)],
        ),
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          const _MarketGrid(),
          Center(
            child: Container(
              width: 190,
              height: 132,
              decoration: BoxDecoration(
                color: const Color(0xFFEAF3E2).withValues(alpha: 0.82),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: const Color(0xFF8BB66B), width: 2),
              ),
            ),
          ),
          ..._pins.map((pin) => Align(
                alignment: pin.alignment,
                child: _PinBadge(pin: pin),
              )),
          Positioned(
            left: 12,
            top: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
              decoration: BoxDecoration(
                color: const Color(0xFFFDFBF5).withValues(alpha: 0.92),
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
          Positioned(
            right: 12,
            bottom: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFF2F5710).withValues(alpha: 0.9),
                borderRadius: BorderRadius.circular(999),
              ),
              child: const Text(
                '방문 핀 3곳',
                style: TextStyle(color: Color(0xFFF2F7EC), fontSize: 11, fontWeight: FontWeight.w700),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MarketGrid extends StatelessWidget {
  const _MarketGrid();

  @override
  Widget build(BuildContext context) {
    return CustomPaint(painter: _MarketGridPainter());
  }
}

class _MarketGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final roadPaint = Paint()
      ..color = const Color(0xFFFFFFFF).withValues(alpha: 0.72)
      ..strokeWidth = 13
      ..strokeCap = StrokeCap.round;
    final subRoadPaint = Paint()
      ..color = const Color(0xFFFFFFFF).withValues(alpha: 0.46)
      ..strokeWidth = 7
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(Offset(size.width * 0.08, size.height * 0.28), Offset(size.width * 0.92, size.height * 0.18), roadPaint);
    canvas.drawLine(Offset(size.width * 0.14, size.height * 0.74), Offset(size.width * 0.88, size.height * 0.56), roadPaint);
    canvas.drawLine(Offset(size.width * 0.24, size.height * 0.10), Offset(size.width * 0.36, size.height * 0.92), subRoadPaint);
    canvas.drawLine(Offset(size.width * 0.62, size.height * 0.06), Offset(size.width * 0.54, size.height * 0.94), subRoadPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _PinBadge extends StatelessWidget {
  const _PinBadge({required this.pin});

  final _MarketPin pin;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: pin.label,
      child: Container(
        width: 30,
        height: 30,
        decoration: BoxDecoration(
          color: pin.color,
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0xFFFDFBF5), width: 3),
          boxShadow: const [
            BoxShadow(color: Color(0x33000000), blurRadius: 10, offset: Offset(0, 4)),
          ],
        ),
        child: const Icon(Icons.storefront_rounded, color: Color(0xFFFDFBF5), size: 15),
      ),
    );
  }
}

class _MarketPin {
  const _MarketPin({
    required this.label,
    required this.alignment,
    required this.color,
  });

  final String label;
  final Alignment alignment;
  final Color color;
}
