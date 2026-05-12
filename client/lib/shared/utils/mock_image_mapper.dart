class MockImageMapper {
  static String? productAssetByName(String name) {
    final n = _norm(name);
    if (n.contains('고등어') && n.contains('1손')) return 'assets/images/mock/products/prod_mackerel_1son.jpeg';
    if (n.contains('딸기') && n.contains('500g')) return 'assets/images/mock/products/prod_strawberry_500g.jpeg';
    if (n.contains('멸치') && n.contains('500g')) return 'assets/images/mock/products/prod_anchovy_500g.jpeg';
    if (n.contains('삼겹살') && n.contains('600g')) return 'assets/images/mock/products/prod_porkbelly_600g.jpeg';
    if (n.contains('시금치') && n.contains('200g')) return 'assets/images/mock/products/prod_spinach_200g.jpeg';
    if (n.contains('대파') && n.contains('1단')) return 'assets/images/mock/products/prod_greenonion_1dan.jpeg';
    if (n.contains('갈치') && n.contains('1마리')) return 'assets/images/mock/products/prod_hairtail_1.jpeg';
    if ((n.contains('샤인머스켓') || n.contains('샤인머스캣')) && n.contains('500g')) {
      return 'assets/images/mock/products/prod_shine_500g.jpeg';
    }
    if (n.contains('감귤') && n.contains('3kg')) return 'assets/images/mock/products/prod_tangerine_3kg.jpeg';
    if (n.contains('한라봉') && n.contains('3kg')) return 'assets/images/mock/products/prod_hallabong_3kg.jpeg';
    if (n.contains('청양고추') && n.contains('500g')) return 'assets/images/mock/products/prod_hotpepper_500g.jpeg';
    if (n.contains('애호박') && n.contains('1개')) return 'assets/images/mock/products/prod_zucchini_1.jpeg';
    if (n.contains('불고기용') && n.contains('300g')) return 'assets/images/mock/products/prod_hanwoo_300g.jpeg';
    if (n.contains('광어') && n.contains('300g')) return 'assets/images/mock/products/prod_flatfish_300g.jpeg';
    return null;
  }

  static String? storeAssetByName(String name) {
    final n = _norm(name);
    if (n.contains('망원신선야채')) return 'assets/images/mock/stores/store_mangwon_fresh_veg.jpeg';
    if (n.contains('망원채소마트')) return 'assets/images/mock/stores/store_mangwon_vegmart.jpeg';
    if (n.contains('망원과일나라')) return 'assets/images/mock/stores/store_mangwon_fruitnara.jpeg';
    if (n.contains('달콤과일')) return 'assets/images/mock/stores/store_dalkom_fruit.jpeg';
    if (n.contains('망원수산')) return 'assets/images/mock/stores/store_mangwon_fish.jpeg';
    if (n.contains('신선해산물')) return 'assets/images/mock/stores/store_fresh_seafood.jpeg';
    if (n.contains('망원정육')) return 'assets/images/mock/stores/store_mangwon_meat.jpeg';
    if (n.contains('망원반찬가게')) return 'assets/images/mock/stores/store_mangwon_banchan.jpeg';
    if (n.contains('망원생활잡화')) return 'assets/images/mock/stores/store_mangwon_goods.jpeg';
    if (n.contains('망원건어물')) return 'assets/images/mock/stores/store_mangwon_dryfish.jpeg';
    return null;
  }

  static String _norm(String s) => s.replaceAll(' ', '').replaceAll('(', '').replaceAll(')', '').toLowerCase();
}
