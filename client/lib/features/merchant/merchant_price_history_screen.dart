import 'package:flutter/material.dart';

import '../../core/network/api_client.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantPriceHistoryScreen extends StatefulWidget {
  const MerchantPriceHistoryScreen({super.key, required this.productId});

  final String productId;

  @override
  State<MerchantPriceHistoryScreen> createState() => _MerchantPriceHistoryScreenState();
}

class _MerchantPriceHistoryScreenState extends State<MerchantPriceHistoryScreen> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = ApiClient.instance.getProductPriceHistory(widget.productId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(title: const MarketLogoTitle()),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('가격 이력 조회 실패: ${snapshot.error}'));
          }

          final items = snapshot.data ?? const <Map<String, dynamic>>[];
          if (items.isEmpty) {
            return const Center(child: Text('가격 이력이 없습니다.'));
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                '최근 가격 이력',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Color(0xFF2F5710)),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFDDE8D4)),
                ),
                child: Column(
                  children: items.map((e) {
                    final date = e['recorded_at'] as String? ?? '-';
                    final price = e['price']?.toString() ?? '-';
                    final source = e['source'] as String? ?? 'manual';
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        children: [
                          Expanded(child: Text(date, style: const TextStyle(fontSize: 12, color: Color(0xFF666666)))),
                          Text('₩$price', style: const TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF2F5710))),
                          const SizedBox(width: 8),
                          Text(source, style: const TextStyle(fontSize: 11, color: Color(0xFF888888))),
                        ],
                      ),
                    );
                  }).toList(growable: false),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
