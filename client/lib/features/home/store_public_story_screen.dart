import 'package:flutter/material.dart';

import '../../shared/widgets/market_logo_title.dart';
import '../../core/repositories/repository_provider.dart';

class StorePublicStoryScreen extends StatefulWidget {
  const StorePublicStoryScreen({super.key, required this.storeId});

  final String storeId;

  @override
  State<StorePublicStoryScreen> createState() => _StorePublicStoryScreenState();
}

class _StorePublicStoryScreenState extends State<StorePublicStoryScreen> {
  late Future<Map<String, dynamic>?> _future;

  @override
  void initState() {
    super.initState();
    _future = context.marketRepository.getPublishedStoryForStore(widget.storeId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(title: const MarketLogoTitle()),
      body: FutureBuilder<Map<String, dynamic>?>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('스토리 조회 실패: ${snapshot.error}'));
          }
          final item = snapshot.data;
          if (item == null || item.isEmpty) {
            return const Center(child: Text('게시된 스토리가 없습니다.'));
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                item['store_name'] as String? ?? '점포 스토리',
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF2F5710)),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFDDE8D4)),
                ),
                child: Text(
                  item['story'] as String? ?? '',
                  style: const TextStyle(fontSize: 15, height: 1.5),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
