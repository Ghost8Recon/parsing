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
            pass


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


def get_main_category(string):
    computer_accessories = ['Computer Components', 'Computer Security Locks', 'Computer Speakers',
                            'Joysticks & Game Controllers', 'Keyboards & Keypads', 'Mice & Trackballs',
                            'Notebook Accessories', 'Notebook Carrying Cases & Accessories',
                            'Notebook Docks & Port Replicators', 'Signature Pads & Accessories', 'Tablet Accessories',
                            'Tools', 'Video Cards & Imaging', 'Webcams']
    computers = ['Desktop Computers', 'Notebook Computers', 'Point of Sale Computers', 'Tablets & Tablet PCs',
                 'Thin Clients', 'Workstations']
    data_storage_products = ['CD, DVD & Blu-Ray Drives', 'Disc Duplicators', 'Drive Arrays', 'Flash Memory',
                             'Floppy Disk Drives', 'Hard Drives', 'Interfaces / Controllers', 'Media & Accessories',
                             'Networked Attached Storage (NAS)', 'Storage Area Networking (SAN)',
                             'Tape Automation & Drives']
    electronics = ['2-Way Radios & Accessories', 'Audio/Stereo Equipment', 'Automation & Control Systems',
                   'Cell/Smart Phones & Accessories', 'Digital Cameras & Accessories', 'Drones & Accessories',
                   'GPS Devices & Accessories', 'Handheld Devices & Accessories', 'Headphones/Earphones & Accessories',
                   'Microphones & Accessories', 'MP3 Players & Accessories', 'Photographic Accessories',
                   'Speaker Systems & Accessories', 'Televisions & Video Equipment', 'Video Camcorders & Accessories',
                   'Virtual Reality & Accessories']
    memories = ['Cache Memory', 'Network Device Memory', 'Printer Memory', 'Server Memory', 'System Memory (RAM)']
    monitors_projectors = ['CRT Monitors', 'Interactive Whiteboards & Accessories', 'Large-Format Displays',
                           'LCD / LED Monitors', 'Medical Displays & Accessories', 'Monitor, Display & TV Accessories',
                           'Projector Accessories', 'Projectors', 'Touchscreen Displays & Accessories']
    networking_products = ['Communication Boards', 'Ethernet Switches', 'Modems', 'Network Interface Adapters (NIC)',
                           'Network Optimization Appliances', 'Network Security', 'Network Test Equipment',
                           'PBX/Multi-User Telephony Systems', 'Routers', 'Wireless Networking']
    office_equipment = ['Books', 'Calculators & Accessories', 'Cleaning Supplies', 'Furniture', 'Mounts & Carts',
                        'Office Supplies', 'Paper Shredders & Accessories', 'Toys', 'Typewriters/Word Processors']
    phones_video_conferencing = ['Headsets', 'Phone System Architecture', 'Phones', 'Video Conferencing']
    power_cooling_racks = ['Batteries', 'Power Adapters', 'Power Inverters', 'Rack Mounting Equipment',
                           'Surge Suppressors', 'UPS/Battery Backup Products']
    printers_scanners = ['3D Printers & Accessories', 'Barcode & Handheld Scanners', 'Business Inkjet Printers',
                         'CD/DVD Media Printers', 'Copy Machines & Accessories', 'Document Scanners',
                         'Dot-Matrix Printers', 'FAX Machines', 'Ink, Toner & Print Supplies',
                         'Inkjet & Photo Printers', 'Laser Printers', 'Multifunction Printers', 'Print Servers',
                         'Printer & Scanner Accessories', 'Printer Hard Drives', 'Printer Paper & Media',
                         'Thermal Printers', 'Wide-Format Printers/Plotters']
    servers_server = ['KVM Switches, Consoles & Accessories', 'Server Accessories & IO Accelerators', 'Servers']

    if 'Cable' in string[0]:
        return 'Cables'
    elif string[0] in computer_accessories:
        return 'Computer Accessories'
    elif string[0] in computers:
        return 'Computers'
    elif string[0] in data_storage_products:
        return 'Data Storage Products'
    elif string[0] in electronics:
        return 'Electronics'
    elif string[0] in memories:
        return 'Memory'
    elif string[0] in monitors_projectors:
        return 'Monitors & Projectors'
    elif string[0] in networking_products:
        return 'Networking Products'
    elif string[0] in office_equipment:
        return 'Office Equipment & Supplies'
    elif string[0] in phones_video_conferencing:
        return 'Phones & Video Conferencing'
    elif string[0] in power_cooling_racks:
        return 'Power, Cooling & Racks'
    elif string[0] in printers_scanners:
        return 'Printers, Scanners & Print Supplies'
    elif string[0] in servers_server:
        return 'Servers & Server Management'
    else:
        return 'Computer Accessories'


def write_csv(data, category_name, mod):
    if mod == 'add':
        use_mod = 'a'
    else:
        use_mod = 'w'
    with open('/parsing/all_data.csv', use_mod, newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['name'],
                         data['reference#'],
                         data['supplier_reference#'],
                         data['cost_price'],
                         data['price_tax_excluded'],
                         data['label_in_stock'],
                         data['quantity'],
                         data['img_url'],
                         data['features'],
                         data['active'],
                         data['description'],
                         data['available_for_order'],
                         data['category']))


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
                div = page.find('div', class_='column-1')
                img_url = div.find('img').get('src')
            except:
                img_url = ''

            try:
                specifications_url = 'https://www.cdw.ca/api/product/1/data/technicalspecifications/' + id
                specifications = get_json(specifications_url)
                all_specifications = ""

                for param in specifications["AttributeGroups"]:
                    attributes = param["Attributes"]
                    for attribute in attributes:
                        all_specifications += '{0}:{1}:::{2}, '.format(attribute["Key"], attribute["Value"],
                                                                       param["FolderName"])

            except:
                all_specifications = ''
            try:
                description_url = 'https://www.cdw.ca/api/product/1/data/overview/' + id
                description = get_json(description_url)
                description = description["MarketText"]

            except:
                description = ''

            if 'In Stock' in availability:
                active = 1
                quantity = 100
                available_for_order = 1
            else:
                active = 0
                quantity = 0
                available_for_order = 0

            price = re.sub("[^0-9.]", "", price)
            data = {'name': product.get("name"),
                    'category': 'Home/'+get_main_category(category_name)+'/'+(category_name.replace('/', '-')),
                    'reference#': product.get("MFG"),
                    'supplier_reference#': product.get("CDW"),
                    'label_in_stock': 'In Stock',
                    'quantity': quantity,
                    'cost_price': price,
                    'price_tax_excluded': str(round(float(price)*1.12, 2)),
                    'img_url': img_url.replace("CDW//", "CDW/"),
                    'features': all_specifications,
                    'active': active,
                    'description': description,
                    'available_for_order': available_for_order
                    }

            if price == '':
                pass
            else:
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
            div = product.find('div', class_='main-image')
            img_url = div.find('img').get('src')
        except:
            img_url = ''

        try:
            specifications_url = 'https://www.cdw.ca/api/product/1/data/technicalspecifications/' + products_id[0]
            specifications = get_json(specifications_url)
            all_specifications = ""

            for param in specifications["AttributeGroups"]:
                    attributes = param["Attributes"]
                    for attribute in attributes:
                        all_specifications += '{0}:{1}:::{2}, '.format(attribute["Key"], attribute["Value"], param["FolderName"])

        except:
            all_specifications = ''

        try:
            description_url = 'https://www.cdw.ca/api/product/1/data/overview/' + products_id[0]
            description = get_json(description_url)
            description = description["MarketText"]
            description = description.replace('<br/>', '')

        except:
            description = ''

        if 'In Stock' in availability:
            active = 1
            quantity = 100
            available_for_order = 1
        else:
            active = 0
            quantity = 0
            available_for_order = 0

        price = re.sub("[^0-9.]", "", price)

        data = {'name': product.get("name"),
                'category': 'Home/'+get_main_category(category_name)+'/'+(category_name.replace('/', '-')),
                'reference#': product.get("MFG"),
                'supplier_reference#': product.get("CDW"),
                'label_in_stock': 'In Stock',
                'quantity': quantity,
                'cost_price': price,
                'price_tax_excluded': str(round(float(price)*1.12, 2)),
                'img_url': img_url.replace("CDW//", "CDW/"),
                'features': all_specifications,
                'active': active,
                'description': description,
                'available_for_order': available_for_order
                }

        # print(data)
        if price == '':
            pass
        else:
            write_csv(data, category_name, mod='add')


def main():
    url = "https://www.cdw.ca/search/?"
    start_url = "https://www.cdw.ca/shop/search/browse.aspx"
    page_part = "&pCurrent="

    html = get_html(start_url)
    categories = get_product_categories(html)
    data = {'name': 'name',
            'category': 'category',
            'reference#': 'reference#',
            'supplier_reference#': 'supplier_reference#',
            'label_in_stock': 'label_in_stock',
            'quantity': 'quantity',
            'cost_price': 'cost_price',
            'price_tax_excluded': 'price_tax_excluded',
            'img_url': 'img_url',
            'features': 'features',
            'active': 'active',
            'description': 'description',
            'available_for_order': 'available_for_order'
            }
    write_csv(data, 'all_data', mod='w')

    for category in categories.items():  # 135 categories
        try:
            category_url = category[1]
            url_gen = url + category_url
            total_pages = get_total_pages(get_html(url_gen))
            for i in range(1, total_pages + 1):
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
