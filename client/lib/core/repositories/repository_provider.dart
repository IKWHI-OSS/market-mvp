import 'package:flutter/material.dart';

import 'market_repository.dart';

class AppRepositoryProvider extends InheritedWidget {
  const AppRepositoryProvider({
    super.key,
    required this.marketRepository,
    required super.child,
  });

  final MarketRepository marketRepository;

  static AppRepositoryProvider of(BuildContext context) {
    final provider = context
        .getElementForInheritedWidgetOfExactType<AppRepositoryProvider>()
        ?.widget as AppRepositoryProvider?;
    assert(provider != null, 'AppRepositoryProvider not found in widget tree');
    return provider!;
  }

  @override
  bool updateShouldNotify(AppRepositoryProvider oldWidget) {
    return oldWidget.marketRepository != marketRepository;
  }
}

extension RepositoryX on BuildContext {
  MarketRepository get marketRepository => AppRepositoryProvider.of(this).marketRepository;
}
