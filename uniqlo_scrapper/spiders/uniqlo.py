import time
import scrapy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
from ..items import UniqloScrapperItem

FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall",
                "Mid-weight", "High-waisted", "Oversized"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]
OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear", "beach"]

LENGTH_KEYWORDS = ["mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]

LINKS_KEYWORDS = ["dress", "knitwear", "jacket", "top", "pant", "lingerie",
                  "jumpsuit", "beachwear", "shirt", "activewear", "denim",
                  "coat", "sweatshirt", "clothes", "innerwear",
                  "wear", "loungewear", "tees", "bottoms", "outwear", ""]

FABRICS_KEYWORDS = ["polyester", "cashmere", "viscose", "Machine wash cold",
                    "metallic", "silk", "rayon", "spandex",
                    "TENCEL", "cotton", "elastane", "lyocell",
                    "LENZING", "LYCRA", "%"]

DISALLOWED_CATEGORIES = ["shoes", "accessories", "joggers", "accessories", "heels", "socks", "gloves", "All"]
CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit', 'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}
CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}

WEBSITE_NAME = "uniqlo"
urls = ['https://www.uniqlo.com/us/en/women/tops/all-tops',
        'https://www.uniqlo.com/us/en/search?q=crop%20tops&path=22210%2C23295',
        'https://www.uniqlo.com/us/en/women/bottoms/all-bottoms',
        'https://www.uniqlo.com/us/en/women/dresses-and-jumpsuits/all-dresses-and-jumpsuits',
        'https://www.uniqlo.com/us/en/women/outerwear-and-blazers/all-outerwear',
        'https://www.uniqlo.com/us/en/women/innerwear/all-innerwear',
        'https://www.uniqlo.com/us/en/women/loungewear-and-home/all-loungewear-and-home',
        'https://www.uniqlo.com/us/en/women/sport-utility-wear/all-sport-utility-wear',
        'https://www.uniqlo.com/us/en/women/innerwear/airism']


class UniqloSpider(scrapy.Spider):
    name = 'uniqlo'
    allowed_domains = ['www.uniqlo.com']

    # initializes selenium
    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.action = ActionChains(self.driver)
        super().__init__(*a, **kw)

    def start_requests(self):
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse_products_links)

        url = "https://www.uniqlo.com/us/en/products/E445259-000/00"
        yield scrapy.Request(url=url, callback=self.parse_product)

    # This function parses product links for each category
    def parse_products_links(self, response):
        self.driver.maximize_window()
        self.driver.get(response.url)
        time.sleep(5)
        product_links = []
        while True:
            try:
                show_more = self.driver.find_element(by=By.CSS_SELECTOR,
                                                     value=".uq-ec-content-alignment >.uq-ec-show-more")
                if show_more:
                    self.action.move_to_element(show_more).perform()
                    self.driver.implicitly_wait(10)
                    self.action.click(show_more).perform()
                else:
                    break
            except NoSuchElementException:
                time.sleep(5)
                product_links_raw = self.driver.find_elements(by=By.CSS_SELECTOR,
                                                              value=".uq-ec-product-collection>.uq-ec-product-tile-resize-wrapper> a")
                for link in product_links_raw:
                    product_links.append(link.get_attribute('href'))
                break
                pass
        for link in product_links:
            yield scrapy.Request(url=link, callback=self.parse_product)

    # This function parses product details
    def parse_product(self, response):
        self.driver.get(response.url)
        self.driver.maximize_window()
        time.sleep(3)
        images = []
        colors = []
        external_id = self.driver.find_element(by=By.CSS_SELECTOR, value=".uq-ec-header-section__extra>p").text.replace(
            "Product ID", "").strip()

        name = self.driver.find_element(by=By.CSS_SELECTOR, value=".uq-ec-layout >.uq-ec-display").text
        url = response.request.url
        colors_raw = self.driver.find_elements(by=By.XPATH, value="//*[@id='product-color-picker']/div[2]/div/input")
        del colors_raw[:int(len(colors_raw) / 2)]
        for color in colors_raw:
            label = color.get_attribute('aria-label')
            value = color.get_attribute('value')
            colors.append(f"{value} {label}")

        plus_buttons = self.driver.find_elements(by=By.CSS_SELECTOR, value=".uq-ec-accordion__control")
        plus_buttons[0].click()
        price = self.driver.find_element(by=By.CSS_SELECTOR, value=".uq-ec-price").get_attribute('aria-label').replace(
            "price is ", "")

        detail1 = self.driver.find_element(by=By.XPATH, value="//*[@id='root']/div[2]/div/section/div[3]/p").text
        details2 = self.driver.find_element(by=By.XPATH, value="//*[@id='productLongDescription-content']/p").text

        details = [detail1.replace("\n", "") + str(details2).replace("\n", "")]

        images_raw = self.driver.find_elements(By.XPATH,
                                               '//div[@class="uq-ec-media-gallery__preview"] /div /div[@class="uq-ec-media-gallery__preview-chip-container-inner"] /div /img')
        for img in images_raw:
            images.append(img.get_attribute('src'))

        plus_buttons[1].click()
        time.sleep(1)
        fabrics = self.driver.find_elements(By.XPATH, "//div[@id='productMaterialDescription-content'] //dl /dd[1] /p")[0].text
        fabrics = (re.sub("Imported|imported", "", fabrics)).strip()
        categories = []
        categories_raw = self.driver.find_elements(By.CSS_SELECTOR, "ol.uq-ec-breadcrumb-group li a")
        scrapped_categories = [category.text for category in categories_raw]
        scrapped_categories = scrapped_categories[1:-1]
        if re.search("HEATTECH", ' '.join(scrapped_categories), re.IGNORECASE):
            scrapped_categories = [category for category in scrapped_categories if not re.search("HEATTECH", category, re.IGNORECASE)]
        if re.search("Best Sellers", ' '.join(scrapped_categories), re.IGNORECASE):
            scrapped_categories = [category for category in scrapped_categories if not re.search("Best Sellers", category, re.IGNORECASE)]
        if re.search("Featured", ' '.join(scrapped_categories), re.IGNORECASE):
            scrapped_categories = [category for category in scrapped_categories if not re.search("Featured", category, re.IGNORECASE)]
        if re.search("UT: Graphic Tees", ' '.join(scrapped_categories), re.IGNORECASE):
            scrapped_categories = [category for category in scrapped_categories if not re.search("UT: Graphic Tees", category, re.IGNORECASE)]

        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)

        sizes_raw = self.driver.find_elements(By.XPATH,
                                              '(//div[@class="uq-ec-chip-group__chips"])[last()] /div //label')
        sizes = [size.text for size in sizes_raw]
        neck_line = self.find_from_str(details, NECK_LINE_KEYWORDS)
        length = self.find_from_str(details, LENGTH_KEYWORDS)
        if length:
            length = ' '.join(length)
        else:
            length = ""

        occasions = self.find_from_str(details, OCCASIONS_KEYWORDS)
        style = self.find_from_str(details, STYLE_KEYWORDS)
        fit = self.find_from_str(details, FIT_KEYWORDS)
        if fit:
            fit = ' '.join(fit)
        else:
            fit = ""

        gender = "women"
        top_best_seller = ""
        review_description_raw = self.driver.find_elements(By.XPATH, '//section[@class="uq-ec-review"] /p[3]')
        review_description = [r.text for r in review_description_raw]
        number_of_reviews = str(len(review_description)) if review_description else ""
        # aesthetics = find_from_target_string_multiple(details, categories, AESTHETIC_KEYWORDS)

        item = UniqloScrapperItem()
        item["external_id"] = external_id
        item["url"] = response.url
        item["name"] = name
        item["categories"] = categories
        item["price"] = price
        item["colors"] = colors
        item["sizes"] = sizes
        item["fabric"] = fabrics
        item["fit"] = fit
        item["details"] = details
        item["images"] = images
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = review_description
        item["top_best_seller"] = top_best_seller
        item["style"] = style
        item["length"] = length
        item["neck_line"] = neck_line
        item["occasions"] = occasions
        item["meta"] = {}
        # item["aesthetics"] = aesthetics
        item["gender"] = gender
        item["website_name"] = WEBSITE_NAME
        if categories and (not self.in_disallowed_categories(categories)):
            yield item

    def find_from_string_return_array(self, data, tarkget_keywords):
        myarray = []
        for word in tarkget_keywords:
            if word in data:
                myarray.append(word)
        return myarray

    def find_from_target_string_single(self, source_data, target_keywords):
        for each_element in source_data:
            if any(keyword.lower() in each_element.lower() for keyword in target_keywords):
                return each_element
        return " "

    def find_from_string(self, data, target_keywords):
        for word in target_keywords:
            if word in data:
                return word
        return ""

    def find_from_target_multiple_list(self, details, categories, target_keywords):
        target_list = []
        details = ' '.join([str(item) for item in details])
        categories_list = ' '.join([str(item) for item in categories])
        target_list.append(details)
        target_list.append(categories_list)
        final_list = []
        for each_element in target_list:
            if any(keyword.lower() in each_element.lower() for keyword in target_keywords):
                final_list.append(each_element)

        return final_list

    def find_from_target_string_multiple(self, details, categories, target_keywords):
        target_list = []
        details = ' '.join([str(item) for item in details])
        categories_list = ' '.join([str(item) for item in categories])
        target_list.append(details)
        target_list.append(categories_list)

        for element in target_list:
            if any(keyword.lower() in element.lower() for keyword in target_keywords):
                return element
            return " "

    # This helper finds fabric from details and returns it
    def find_fabric_from_details(self, details):
        product_details = ' '.join(details)
        fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b)\)?""", product_details,
                                     flags=re.IGNORECASE | re.MULTILINE)

        fabrics = re.sub("\(|\)", "", ' '.join([''.join(tups) for tups in fabrics_founded]))
        if fabrics:
            fabrics = list(set(fabrics.split(" ")))
            return ' '.join(fabrics)
        else:
            return ""


    def find_from_str(self, details, keywords):
        details = ' '.join(details)
        finals = []
        for keyword in keywords:
            if re.search(keyword.lower(), details.lower(), re.IGNORECASE):
                finals.append(keyword)

        return finals

    def in_disallowed_categories(self, categories):
        categories = ','.join(categories)
        for keyword in DISALLOWED_CATEGORIES:
            if re.search(keyword.lower(), categories, re.IGNORECASE):
                return True
        return False


# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)

    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)

    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats
