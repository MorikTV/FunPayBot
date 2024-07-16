import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import os

init()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_settings(filename='settings.txt'):
    settings = {}
    try:
        with open(f"{filename}", 'r', encoding='utf-8') as file:
            for line in file:
                if '--' not in line and ':' in line:
                    key, value = map(str.strip, line.split(':', 1))
                    settings[key] = value
    except FileNotFoundError:
        print(f"Settings file {filename} not found.")
        input("Нажмите ENTER, чтобы выйти...")
        exit()
    return settings

def get_user_data(session, api_url):
    url = f"{api_url}/orders/trade"
    session.get(url + "?setlocale=ru")
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    total_earnings = 0
    total_orders = 0
    sale = 0
    order_ids = set()
    order_id = ""
    data = {"continue": order_id}
    clear_console()
    print("Загрузка...")

    while True:
        items = soup.select(".tc-item")
        if not items: break
        for item in items:
            order_id = item.select_one(".tc-order").text.replace("#", "").strip()
            if order_id in order_ids:
                continue
            order_ids.add(order_id)
            status = item.select_one(".tc-status").text
            if status == "Закрыт":
                price_text = item.select_one(".tc-price").contents[0].replace(" ", "")
                try: price = float(price_text)
                except ValueError: continue
                if price > sale: sale = price
                total_earnings += price
                total_orders += 1
        try: 
            last_order_id = items[-1].select_one(".tc-order").text.replace("#", "").strip()
            data["continue"] = last_order_id
            response = session.post(url, data=data)
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception as _ex:
            pass

    if total_orders > 0: average_check = round(total_earnings / total_orders, 2)
    else: average_check = 0

    total_earnings = round(total_earnings, 2)
    clear_console()
    text_data = (f"Продажи: {Fore.BLUE + Style.BRIGHT + str(total_orders) + Fore.RESET + Style.RESET_ALL}. "
                 f"Заработок: {Fore.GREEN + Style.BRIGHT + str(total_earnings) + Fore.RESET} {Style.RESET_ALL}₽. "
                 f"Средний чек: {Fore.LIGHTGREEN_EX + Style.BRIGHT + str(average_check) + Fore.RESET} ₽{Style.RESET_ALL}. "
                 f"Самая крупная продажа: {Fore.LIGHTGREEN_EX + Style.BRIGHT + str(sale) + Fore.RESET} ₽{Style.RESET_ALL}.")

    print(text_data)
    return total_orders, total_earnings, average_check

def save_to_file(filename, data):
    with open(f"{filename}", 'w', encoding='utf-8') as f:
        f.write(data)

def main():
    save_data = input("Сохранить данные в файл? (Y/N): ").strip().lower() == 'y'

    settings = load_settings()
    GOLDEN_KEY = settings.get("GOLDEN_KEY")
    USER_AGENT = settings.get("USER_AGENT")

    if not GOLDEN_KEY:
        GOLDEN_KEY = input("Получите golden_key из cookie FunPay. Вы можете использовать расширение Edit This Cookie.\nhttps://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg\nВведите GOLDEN_KEY: ")

    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    session.cookies.update({'golden_key': GOLDEN_KEY})

    api_url = 'https://funpay.com'

    response = session.get(api_url)
    if response.status_code != 200:
        print(f"Ошибка при получении данных со страницы: {response.status_code}")
        input("Нажмите ENTER, чтобы выйти...")
        return

    total_orders, total_earnings, average_check = get_user_data(session, api_url)
    if save_data:
        text_data = f"Продажи: {total_orders}. Заработок: {total_earnings} ₽. Средний чек: {average_check} ₽."
        save_to_file("data.txt", text_data)

    input("\nНажмите ENTER, чтобы выйти...")

if __name__ == "__main__":
    main()