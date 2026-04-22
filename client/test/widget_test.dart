import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:market_info_client/app/app.dart';

void main() {
  testWidgets('App boots and renders MaterialApp', (WidgetTester tester) async {
    await tester.pumpWidget(const MarketInfoApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
