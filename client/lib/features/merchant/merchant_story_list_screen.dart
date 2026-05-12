import 'package:flutter/material.dart';

import '../../shared/widgets/market_logo_title.dart';
import '../../core/repositories/repository_provider.dart';

class MerchantStoryListScreen extends StatefulWidget {
  const MerchantStoryListScreen({super.key});

  @override
  State<MerchantStoryListScreen> createState() => _MerchantStoryListScreenState();
}

class _MerchantStoryListScreenState extends State<MerchantStoryListScreen> {
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();
    _future = context.marketRepository.listMyStories();
  }

  Future<void> _togglePublish(Map<String, dynamic> story, bool value) async {
    final storyId = story['story_id'] as String?;
    if (storyId == null || storyId.isEmpty) return;
    await context.marketRepository.publishStory(storyId, publish: value);
    if (!mounted) return;
    setState(() {
      _future = context.marketRepository.listMyStories();
    });
  }

  Future<void> _deleteStory(String storyId) async {
    await context.marketRepository.deleteStory(storyId);
    if (!mounted) return;
    setState(() {
      _future = context.marketRepository.listMyStories();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
        title: const MarketLogoTitle(),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('스토리 목록 조회 실패: ${snapshot.error}'));
          }
          final items = snapshot.data ?? const <Map<String, dynamic>>[];
          if (items.isEmpty) {
            return const Center(child: Text('생성된 스토리가 없습니다.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = items[index];
              final title = item['store_name'] as String? ?? '점포';
              final text = item['story'] as String? ?? '';
              final isPublished = item['is_published'] as bool? ?? false;
              final storyId = item['story_id'] as String? ?? '';

              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFDCE8D1)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: const TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF2F5710)),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: isPublished ? const Color(0xFFD7F2C8) : const Color(0xFFEAEAEA),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(isPublished ? '게시중' : '비공개'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      text,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Text('게시 상태'),
                        Switch(
                          value: isPublished,
                          onChanged: (v) => _togglePublish(item, v),
                        ),
                        const Spacer(),
                        IconButton(
                          icon: const Icon(Icons.delete_outline),
                          onPressed: storyId.isEmpty ? null : () => _deleteStory(storyId),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
