import 'package:flutter/material.dart';

import '../features/auth/login_screen.dart';
import '../features/common/consumer_shell_screen.dart';
import '../features/common/error_state_screen.dart';
import '../features/drop/drop_list_screen.dart';
import '../features/home/home_screen.dart';
import '../features/merchant/merchant_dashboard_screen.dart';
import '../features/merchant/merchant_product_form_screen.dart';
import '../features/merchant/merchant_product_review_screen.dart';
import '../features/merchant/merchant_story_screen.dart';
import '../features/notification/notification_screen.dart';
import '../features/route/route_screen.dart';
import '../features/search/product_detail_screen.dart';
import '../features/search/search_screen.dart';
import '../features/shopping/agent_screen.dart';
import '../features/shopping/shopping_list_screen.dart';
import '../features/home/event_screen.dart';
import '../features/home/spotlight_screen.dart';

class AppRoutes {
  static const login = '/login';
  static const consumerShell = '/consumer-shell';
  static const home = '/home';
  static const search = '/search';
  static const productDetail = '/product-detail';
  static const drop = '/drop';
  static const agent = '/agent';
  static const shoppingList = '/shopping-list';
  static const route = '/route';
  static const notification = '/notification';
  static const event = '/event';
  static const spotlight = '/spotlight';
  static const merchantDashboard = '/merchant-dashboard';
  static const merchantProductForm = '/merchant-product-form';
  static const merchantProductReview = '/merchant-product-review';
  static const merchantStory = '/merchant-story';
  static const errorState = '/error-state';
}

class AppRouter {
  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.login:
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      case AppRoutes.consumerShell:
        return MaterialPageRoute(builder: (_) => const ConsumerShellScreen());
      case AppRoutes.home:
        return MaterialPageRoute(builder: (_) => const HomeScreen());
      case AppRoutes.search:
        return MaterialPageRoute(builder: (_) => const SearchScreen());
      case AppRoutes.productDetail:
        final args = settings.arguments;
        final detailArgs = args is ProductDetailArgs ? args : const ProductDetailArgs(productId: 'product_001');
        return MaterialPageRoute(builder: (_) => ProductDetailScreen(args: detailArgs));
      case AppRoutes.drop:
        return MaterialPageRoute(builder: (_) => const DropListScreen());
      case AppRoutes.agent:
        return MaterialPageRoute(builder: (_) => const AgentScreen());
      case AppRoutes.shoppingList:
        return MaterialPageRoute(builder: (_) => const ShoppingListScreen());
      case AppRoutes.route:
        return MaterialPageRoute(builder: (_) => const RouteScreen());
      case AppRoutes.notification:
        return MaterialPageRoute(builder: (_) => const NotificationScreen());
      case AppRoutes.event:
        return MaterialPageRoute(builder: (_) => const EventScreen());
      case AppRoutes.spotlight:
        return MaterialPageRoute(builder: (_) => const SpotlightScreen());
      case AppRoutes.merchantDashboard:
        return MaterialPageRoute(builder: (_) => const MerchantDashboardScreen());
      case AppRoutes.merchantProductForm:
        return MaterialPageRoute(builder: (_) => const MerchantProductFormScreen());
      case AppRoutes.merchantProductReview:
        return MaterialPageRoute(builder: (_) => const MerchantProductReviewScreen());
      case AppRoutes.merchantStory:
        return MaterialPageRoute(builder: (_) => const MerchantStoryScreen());
      case AppRoutes.errorState:
        return MaterialPageRoute(builder: (_) => const ErrorStateScreen());
      default:
        return MaterialPageRoute(builder: (_) => const ErrorStateScreen());
    }
  }
}
