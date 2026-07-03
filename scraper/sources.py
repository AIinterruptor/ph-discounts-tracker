from functools import partial

from scraper.parsers import aggregator, bank, ecommerce, food, retail

SOURCES = [
    {
        "name": "SM Sale Events",
        "url": "https://www.smsupermalls.com/mall-sale-events",
        "category": "retail",
        "parser": retail.parse_sm_sale_events,
    },
    {
        "name": "SM Malls Online",
        "url": "https://www.smmallsonline.com/promos-2/",
        "category": "retail",
        "parser": retail.parse_sm_malls_online,
    },
    {
        "name": "Robinsons Malls",
        "url": "https://robinsonsmalls.com/promos-events",
        "category": "retail",
        "parser": retail.parse_robinsons,
    },
    {
        "name": "iPrice Lazada",
        "url": "https://iprice.ph/coupons/lazada/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Lazada"),
    },
    {
        "name": "iPrice Shopee",
        "url": "https://iprice.ph/coupons/shopee/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Shopee"),
    },
    {
        "name": "iPrice Zalora",
        "url": "https://iprice.ph/coupons/zalora/",
        "category": "ecommerce",
        "parser": partial(ecommerce.parse_iprice, store_name="iPrice Zalora"),
    },
    {
        "name": "Rappler Coupons",
        "url": "https://coupons.rappler.com",
        "category": "ecommerce",
        "parser": ecommerce.parse_rappler,
    },
    {
        "name": "VoucherCodes.ph",
        "url": "https://vouchercodes.ph",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="VoucherCodes.ph",
            container_selector="article._1ve99md1",
        ),
    },
    {
        "name": "RewardPay Shopee",
        "url": "https://rewardpay.com/ph/shopee",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="RewardPay Shopee",
            container_selector="article.xffhp0",
        ),
    },
    {
        "name": "Picodi PH",
        "url": "https://picodi.com/ph",
        "category": "ecommerce",
        "parser": ecommerce.parse_picodi,
    },
    {
        "name": "Yummy.ph Coupons",
        "url": "https://coupons.yummy.ph",
        "category": "ecommerce",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="Yummy.ph Coupons",
            container_selector="article._1ve99md1",
        ),
    },
    {
        "name": "Jollibee Promos",
        "url": "https://www.jollibee.com.ph/promos",
        "category": "food",
        "parser": food.parse_jollibee,
    },
    {
        "name": "Chowking Promos",
        "url": "https://chowking.ph/promos",
        "category": "food",
        "parser": food.parse_chowking,
    },
    {
        "name": "Spot.ph Coupons",
        "url": "https://coupons.spot.ph",
        "category": "food",
        "parser": partial(
            ecommerce.parse_hashed_card_platform,
            source_name="Spot.ph Coupons",
            container_selector="article._1ve99md1",
            category="food",
        ),
    },
    {
        "name": "BPI Promos",
        "url": "https://www.bpi.com.ph/personal/rewards-and-promotions/promos",
        "category": "bank",
        "parser": bank.parse_bpi,
    },
    {
        "name": "RCBC Credit Promos",
        "url": "https://www.rcbccredit.com/promos",
        "category": "bank",
        "parser": bank.parse_rcbc,
    },
    {
        "name": "EastWest Promos",
        "url": "https://www.eastwestbanker.com/promos",
        "category": "bank",
        "parser": bank.parse_eastwest,
    },
    {
        "name": "Moneymax Metrobank",
        "url": "https://www.moneymax.ph/credit-card/partners/metrobank",
        "category": "bank",
        "parser": bank.parse_moneymax_metrobank,
    },
    {
        "name": "CollectOffers PH",
        "url": "https://collectoffers.com/ph",
        "category": "aggregator",
        "parser": aggregator.parse_collectoffers,
    },
]
