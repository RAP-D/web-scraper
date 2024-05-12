from os import environ as env

from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from orm import Table
from datetime import date


load_dotenv()

Table.connect(config_dict={
    'host': env['HOST'],
    'port': int(env['PORT']),
    'user': env['USER'],
    'password': env['PASSWORD'],
    'database': env['DATABASE']
})


class Products(Table):
    table_name = 'Products'


class Product:
    def __init__(self, product_name, min_price, max_price):
        self.product_name = product_name
        self.max_price = max_price
        self.min_price = min_price

    def __eq__(self, other):
        return self.product_name == other.product_name

    def __hash__(self):
        return hash(('product_name', self.product_name))


url = "https://idealz.lk/product-category/smartphones-tablets/smartphones/"

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

products_list = []

products = soup.find_all('div', class_="product")
for product in products:
    product_name = product.find(
        'h2', class_='woocommerce-loop-product__title').get_text()
    product_prices = product.find_all('span', class_="amount")

    if (len(product_prices) > 2):
        low = product_prices[1].get_text()
        high = product_prices[2].get_text()
    else:
        low = product_prices[0].get_text()
        high = product_prices[1].get_text()

    products_list.append(Product(product_name, low, high))

# remove duplicates
products_list = list(set(products_list))


for product in products_list:
    new_product = Products(product_name=product.product_name,
                           date_=date.today(), min_price=product.min_price, max_price=product.max_price)
    new_product.save()
