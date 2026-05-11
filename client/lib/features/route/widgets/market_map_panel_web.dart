import 'dart:async';
import 'dart:html' as html;
import 'dart:js' as js;
import 'dart:ui_web' as ui_web;

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
  late final String _viewType;
  late final String _mapId;
  static int _seq = 0;
  bool _mapInitRequested = false;

  @override
  void initState() {
    super.initState();
    _seq += 1;
    _mapId = 'market-naver-map-$_seq';
    _viewType = 'market-naver-map-view-$_seq';

    ui_web.platformViewRegistry.registerViewFactory(_viewType, (int viewId) {
      final div = html.DivElement()
        ..id = _mapId
        ..style.width = '100%'
        ..style.height = '100%'
        ..style.border = '0'
        ..style.backgroundColor = '#dbe3d3';

      // 맵 스크립트 로딩 지연을 고려해 재시도하며 초기화
      scheduleMicrotask(_initMapWithRetry);
      return div;
    });
  }

  void _initMapWithRetry() {
    if (_mapInitRequested) return;
    _mapInitRequested = true;
    var attempts = 0;
    Timer.periodic(const Duration(milliseconds: 300), (timer) {
      attempts += 1;
      try {
        final hasInit = js.context.hasProperty('initRouteNaverMap');
        if (hasInit) {
          js.context.callMethod('initRouteNaverMap', <dynamic>[
            _mapId,
            widget.centerLat,
            widget.centerLng,
            widget.radiusMeters,
          ]);
          timer.cancel();
          return;
        }
      } catch (_) {
        // retry
      }
      if (attempts >= 20) {
        timer.cancel();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return HtmlElementView(viewType: _viewType);
  }
}
