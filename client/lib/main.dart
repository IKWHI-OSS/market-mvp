import 'package:flutter/material.dart';

import 'app/app.dart';
import 'core/repositories/market_repository.dart';
import 'core/repositories/repository_provider.dart';

void main() {
  runApp(
    AppRepositoryProvider(
      marketRepository: MarketRepository(),
      child: const MarketInfoApp(),
    ),
  );
}
