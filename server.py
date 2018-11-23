import re
from bs4 import BeautifulSoup
from flask import Flask, render_template
import requests
import json



app = Flask(__name__)

parent_url = "https://fr.openfoodfacts.org/"

class Product:
  def __init__(self, nom, photo, score):
    self.nom = nom
    self.photo = photo
    self.score = score

def calcul_nova_score(product):
    nova = product.find_all("a", {"href": "/nova"})
    nova_score = None
    if nova is not None:
        nova_score = nova[1].find("img")['alt'][0]
    if nova_score == '1':
        result = 4
    elif nova_score == '2':
        result = 3
    elif nova_score == '3':
        result = 2
    elif nova_score == '4':
        result = 1
    else:
        result = None
    return result


def calcul_nutri_score(product):
    nutri = product.find_all("a", {"href": "/nutriscore"})
    nutri_score = None
    if nutri is not None and nutri != []:
        nutri_score = nutri[1].find("img")['alt'][-1:]
    if nutri_score == 'A':
        result = 5
    elif nutri_score == 'B':
        result = 4
    elif nutri_score == 'C':
        result = 3
    elif nutri_score == 'D':
        result = 2
    elif nutri_score == 'E':
        result = 1
    else:
        result = None
    return result


def calcul_score(product):
    bio = product.find("a", {"href": "/label/bio"})
    if bio is not None:
        bio = 1
    else:
        bio = 0
    #print("bio : ", bio)
    nova_score = calcul_nova_score(product)
    #print("nova score : ", nova_score)
    nutri_score = calcul_nutri_score(product)
    #print("nutri score : ", nutri_score)
    score = None
    if nutri_score is not None and nova_score is not None:
        score = ((0.6 * int(nutri_score)/5) + (0.3 * int(nova_score)/4) + (0.1 * int(bio)))*100
        #print("SCOOOOOOOOOOOORE : ", score)
    return score


def get_product(product):
    nom = product.find("a")['title']
    #print(nom)
    photo = product.find("noscript").find("img")['src']
    #print(photo)
    href = product.find("a")['href']
    #print(href)
    product_get = requests.get(parent_url + href)
    product = product_get.text
    soup = BeautifulSoup(product, "html.parser")
    score = calcul_score(soup)
    result = None
    if score is not None :
        result = Product(nom, photo, score)
    return result


def get_all_product():
    url = parent_url
    next_page = True
    page_suivante = ''
    productsList = list()
    productsJson = '{ "products": ['
    while next_page:
        r = requests.get(url + page_suivante)
        html = r.content
        soup = BeautifulSoup(html, "html.parser")
        pagination = soup.find('ul', {"class": "pagination"})
        page_suivante = pagination.find('a', text=re.compile(".*Suivante.*"))['href']
        products = soup.find("ul", {"class": "products"}).find_all("li")
        for product in products:
            product_result = get_product(product)
            if product_result is not None:
                productsList.append(product_result)
                #print(product_result.nom, " - ", product_result.photo, " - ", product_result.score)
        if page_suivante is None or page_suivante == "/3":
            next_page = False
    for product in productsList:
        productsJson = productsJson + '{"nom": "' + product.nom + '", "photo": "' + product.photo + '", "score": "' + str(product.score) + '"},'

    productsJson = productsJson[:-1] + ']}'
    n = json.dumps(productsJson)
    o = json.loads(n)
    return o


@app.route('/')
def home():
    return render_template('index.html', products=get_all_product())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)




