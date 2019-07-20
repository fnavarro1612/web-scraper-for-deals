import os
import requests
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage

def site_data():
    """Return the relevant data form the website."""
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'}

    web_data = []

    for page in range(1, 4):
        r = requests.get('https://us.carhartt-wip.com/collections/men-sale-jackets?page={}'.format(page), headers=headers).text
        web_data.append(r.replace('\n', '').replace('\t', ''))

    web_data_str = str(web_data)

    soup = BeautifulSoup(web_data_str, 'html.parser')

    all_site_items = {}

    for item in soup.find_all('div', class_='collection-basic__product'):
        item_name = item.p.text
        item_price = item.span.text
        item_link = item.a.get('href')
        item_color = item['data-variant']
        all_site_items[item_name + ' - ' + item_color] = {'price': item_price.strip('$'), 'link': item_link}

    price_point = 100

    below_price_items = {}

    url = 'https://us.carhartt-wip.com'

    for key, value in all_site_items.items():
        if int(value['price']) <= price_point:
            below_price_items[key] = {'price': value['price'], 'url': url + value['link']}
    return(below_price_items)

def send_email(deals_data):
    """Send an email if there are items at or below the price point."""
    EMAIL = os.environ.get('EMAIL')
    PASSWORD = os.environ.get('PASSWORD')
    msg = EmailMessage()
    msg['Subject'] = 'There are the deals for $100 or less!'
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg.set_content('Content will be the msg alternative.')

    items = ["\n <li> {} : <a href = '{}'>${}</a></li>".format(k, v['url'], v['price']) for k, v in deals_data.items()]
    items = "".join(items)
    msg.add_alternative("""
        <!DOCTYPE html>
        <html>
          <body> 
            <h2>These are the deals:</h2>
            <p>{0}</p>
          </body>
        </html>
    """.format(items), subtype = 'html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

def main():
    """Pass dictionary into a variable to then pass to send the email."""
    deals_data = site_data()

    send_email(deals_data)

if __name__ == '__main__':
    main()
