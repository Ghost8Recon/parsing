import csv
import requests
import ast
import re
import time
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url)

    return r.text


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find('div', class_='search-pagination-list-container')

    try:
        pages = divs.find_all('a')[-2].get('href')
        total_pages = pages.split('=')[3]

    except BaseException as e:
        print(e)
        total_pages = 1

    return int(total_pages)


def get_product(html):

    soup = BeautifulSoup(html, 'lxml')

    try:
        divs = soup.find('div', class_='search-main')
        pages_1 = divs.find_all('a', class_='search-result-product-url')  # For product_url and product_name
        pages_2 = divs.find_all('div', class_='product-codes')  # For product_codes

        product_codes = []
        products = []

        for page in pages_2:
            spans = page.find_all('span')
            product_codes.append([spans[0].text.split(':')[1].strip(), spans[1].text.split(':')[1].strip()])

        for page, codes in zip(pages_1, product_codes):
            product = {}
            product.update(dict({"name": page.text, "MFG": codes[0], "CDW": codes[1]}))
            products.append(product)

        return products


    except BaseException as e:
        print(e)
        print("This category contains only one product")
        # If category contains only one product the site makes redirect to this product-page. Parsing product-page

        try:
            codes = []
            base_url = "https://www.cdw.ca"
            div = soup.find_all('script', type='text/javascript')[-3].text.strip()
            new_url = div.split('"')[1]
            new_html = get_html(base_url + new_url)
            soup = BeautifulSoup(new_html, 'lxml')
            divs = soup.find('div', class_='productRight')
            codes.append(divs.find('span', class_='mpn').text.strip())
            codes.append(divs.find('span', class_='edc').text.strip())
            product = {}
            product.update(dict({"name": divs.find('h1', id='primaryProductName').text.strip(), "MFG": codes[0], "CDW": codes[1]}))
            return [product]

        except BaseException as e:
            print(e)


def get_product_categories(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find('table')
    pages = divs.find_all('div', class_='viewbulletedHyperlink SecondLevelInner')
    categories = {}

    for page in pages:
        url = page.find('a').get('href')

        if '?' in url and '&' in url:
            url = url.split('?')[1]
        else:
            continue

        category_name = page.text.strip()
        if 'Software' not in category_name and 'Delivered Services' not in category_name and 'CDW BTOs' not in category_name:
            categories.update(dict({category_name: url}))

    return categories


def write_csv(data, category_name, mod):
    if mod == 'add':
        use_mod = 'a'
    else:
        use_mod = 'w'
    with open('/parsing/update_data.csv', use_mod, newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['reference#'],
                         data['cost_price'],
                         data['price_tax_excluded'],
                         data['quantity'],
                         data['shipping_weight'],
                         data['active'],
                         data['available_for_order'],))



def get_json(url):
    try:
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        soup = soup.text
        soup = soup.replace("null", "None")
        specifications = ast.literal_eval(soup)
    except BaseException as e:
        print(e)
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        soup.replace('<html><body><p>', '')
        soup.replace('</p></body></html>', '')
        soup.replace('<br/>', '')
        specifications = ast.literal_eval(soup)


    return specifications


def get_page_data(html, products_id, products, category_name):
    try:
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find('div', class_='search-results')
        products_pages = divs.find_all('div', class_='search-result coupon-check')

        for page, id, product in zip(products_pages, products_id, products):
            try:
                div = page.find('div', class_='search-result-price')

                if div.find('div', class_='price-msrp single'):
                    price = ''
                else:
                    price = div.find('div', class_='price-type-price').text.strip()
            except:
                price = ''

            try:
                div = page.find('div', class_='is-available').find_all('span')[1].text.split()
                availability = ''

                for i in range(1, len(div)):
                    availability += div[i] + ' '
                    availability.strip()
            except:
                availability = ''

            try:
                specifications_url = 'https://www.cdw.ca/api/product/1/data/technicalspecifications/' + id
                specifications = get_json(specifications_url)
                weight = ''

                for param in specifications["AttributeGroups"]:
                    attributes = param["Attributes"]
                    if 'weight' in param['FolderName'].lower():
                        for attribute in attributes:
                            if 'weight' in attribute["Key"].lower():
                                value = attribute["Value"]

                                if 'kg' not in value:
                                    weight = re.sub("[^0-9.]", "", value)
                                    weight = int(weight) / 1000
                                    weight = str(weight)
                                else:
                                    weight = re.sub("[^0-9.]", "", value)

            except:
                weight = ''

            if 'In Stock' in availability and price != '':
                active = 1
                quantity = 100
                available_for_order = 1
            else:
                active = 0
                quantity = 0
                available_for_order = 0

            price = re.sub("[^0-9.]", "", price)

            data = {'reference#': product.get("MFG"),
                    'quantity': quantity,
                    'cost_price': price,
                    'price_tax_excluded': str(round(float(price)*1.12, 2)),
                    'active': active,
                    'shipping_weight': weight,
                    'available_for_order': available_for_order
                    }

            write_csv(data, category_name, mod='add')

    except AttributeError:  # If category contains only one product the site makes redirect to this product-page. Parsing product-page
        base_url = "https://www.cdw.ca/product/any/"
        new_url = base_url + products_id[0] + '?enkwrd='
        new_html = get_html(new_url)
        soup = BeautifulSoup(new_html, 'lxml')
        product = soup.find('div', class_='productMain')

        try:
            div = product.find('div', class_='price-type-single').find('span', class_='price-type-selected')
            if div is None:
                price = ''
            else:
                price = div.text.strip()
        except:
            price = ''

        try:
            span = product.find('span', class_='short-message-block').text.strip()
            if span is not None:
                availability = span
            else:
                availability = ''
        except:
            availability = ''

        try:
            specifications_url = 'https://www.cdw.ca/api/product/1/data/technicalspecifications/' + id
            specifications = get_json(specifications_url)
            weight = ''

            for param in specifications["AttributeGroups"]:
                attributes = param["Attributes"]
                if 'weight' in param['FolderName'].lower():
                    for attribute in attributes:
                        if 'weight' in attribute["Key"].lower():
                            value = attribute["Value"]

                            if 'kg' not in value:
                                weight = re.sub("[^0-9.]", "", value)
                                weight = int(weight) / 1000
                                weight = str(weight)
                            else:
                                weight = re.sub("[^0-9.]", "", value)

        except:
            weight = ''

        if 'In Stock' in availability and price != '':
            active = 1
            quantity = 100
            available_for_order = 1
        else:
            active = 0
            quantity = 0
            available_for_order = 0

        price = re.sub("[^0-9.]", "", price)

        data = {'reference#': product.get("MFG"),
                'quantity': quantity,
                'cost_price': price,
                'price_tax_excluded': str(round(float(price)*1.12, 2)),
                'active': active,
                'shipping_weight': weight,
                'available_for_order': available_for_order
                }
        write_csv(data, category_name, mod='add')


def main():
    url = "https://www.cdw.ca/search/?"
    start_url = "https://www.cdw.ca/shop/search/browse.aspx"
    page_part = "&pCurrent="

    html = get_html(start_url)
    categories = get_product_categories(html)

    data = {'reference#': 'reference#',
            'quantity': 'quantity',
            'cost_price': 'cost_price',
            'price_tax_excluded': 'price_tax_excluded',
            'active': 'active',
            'shipping_weight': 'shipping_weight',
            'available_for_order': 'available_for_order'
            }
    write_csv(data, 'all_data', mod='w')

    for category in categories.items():  # 135 categories
        try:
            category_url = category[1]
            url_gen = url + category_url
            total_pages = get_total_pages(get_html(url_gen))
            for i in range(1, total_pages + 1):
                print(category[0], ': ', i, '/', total_pages)
                time.sleep(0.2)
                url_gen = url + category_url + page_part + str(i)
                html = get_html(url_gen)
                products = get_product(html)
                # Search for products codes
                products_id = []

                for product in products:
                    element = product.get("CDW")
                    products_id.append(element)

                get_page_data(html, products_id, products, category[0])

        except BaseException as e:
            print(e)
            continue


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
