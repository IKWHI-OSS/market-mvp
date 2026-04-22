import 'package:flutter/material.dart';

import 'status_badge.dart';

class ListCard extends StatelessWidget {
  const ListCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.price,
    required this.status,
    this.onTap,
    this.onAction,
    this.actionLabel,
  });

  final String title;
  final String subtitle;
  final String price;
  final String status;
  final VoidCallback? onTap;
  final VoidCallback? onAction;
  final String? actionLabel;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFFFDFBF5),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  StatusBadge(
                    label: status,
                    backgroundColor: const Color(0xFFD4E8BA),
                    textColor: const Color(0xFF2F5710),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(subtitle, style: const TextStyle(fontSize: 13, color: Color(0xFF625E55))),
              const SizedBox(height: 6),
              Text(price, style: const TextStyle(fontSize: 15, color: Color(0xFF2F5710), fontWeight: FontWeight.w700)),
              if (actionLabel != null) ...[
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: FilledButton.tonal(onPressed: onAction, child: Text(actionLabel!)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
