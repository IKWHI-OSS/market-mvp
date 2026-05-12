import 'package:flutter/material.dart';
import 'package:flutter_naver_map/flutter_naver_map.dart';

import 'app/app.dart';
import 'core/repositories/market_repository.dart';
import 'core/repositories/repository_provider.dart';

const _naverMapClientId = String.fromEnvironment(
  'NAVER_MAP_CLIENT_ID',
  defaultValue: 'vfkjxwfl5n',
);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await FlutterNaverMap().init(
    clientId: _naverMapClientId,
    onAuthFailed: (_) {},
  );

  runApp(
    AppRepositoryProvider(
      marketRepository: MarketRepository(),
      child: const MarketInfoApp(),
    ),
  );
}
