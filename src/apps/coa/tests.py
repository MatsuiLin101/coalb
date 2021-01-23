from django.test import TestCase


def test_query_produce_value_product():
    """
    from apps.coa.utils import *
    """
    print(query_produce_value_product('蓬萊', 105))
    print(query_produce_value_product('蓬萊', 105, '新北'))
    print(query_produce_value_product('小麥', 105))
    print(query_produce_value_product('大麥', 105, '新北'))
    print(query_produce_value_product('棉花', 105))
    print(query_produce_value_product('芝麻', 105, '新北'))
    # print(query_produce_value_product('甘蔗', 105))
    # print(query_produce_value_product('甘蔗', 105, '新北'))
    # print(query_produce_value_product('菸草', 105))
    # print(query_produce_value_product('菸草', 105, '新北'))
    print(query_produce_value_product('胡蘿蔔', 105))
    print(query_produce_value_product('牛蒡', 105, '新北'))
    print(query_produce_value_product('洋菇', 105))
    print(query_produce_value_product('香菇', 105, '新北'))
    print(query_produce_value_product('香蕉', 105))
    print(query_produce_value_product('鳳梨', 105, '新北'))
    print(query_produce_value_product('菊花', 105))
    print(query_produce_value_product('滿天星', 105, '新北'))
    print(query_produce_value_product('牛', 105))
    print(query_produce_value_product('豬', 105, '新北'))
    print(query_produce_value_product('鴨子', 105))
    print(query_produce_value_product('火雞', 105, '新北'))
    print(query_produce_value_product('牛乳', 105))
    print(query_produce_value_product('生皮', 105, '新北'))
    print(query_produce_value_product('蜂蜜', 105))
    print(query_produce_value_product('蠶', 105, '新北'))


def main():
    test_query_produce_value_product()


if "name" == "__main__":
    main()
