import os
from datetime import datetime
import pandas as pd
import ccxt
import statistics
import matplotlib.pyplot as plt

def enter_crypto_data():
    crypto_data = []
    while True:
        name = input("Enter cryptocurrency name (or 'q' to quit): ")
        if name.lower() == "q":
            break

        symbol = input("Enter symbol: ")
        polygon_address = input("Enter Polygon address: ")

        crypto_data.append({"name": name, "symbol": symbol, "polygon_address": polygon_address})

    df = pd.DataFrame(crypto_data, columns=["name", "symbol", "polygon_address"])
    filename = "crypto_data.csv"
    df.to_csv(filename, index=False)

    print(f"CSV file '{filename}' has been generated successfully.")

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def save_price_update(symbol, median_price):
    folder_name = "coin_logs"
    create_folder(folder_name)

    file_path = os.path.join(folder_name, f"{symbol}.csv")
    current_time = datetime.now().strftime("%H:%Mh / %Y-%m-%d")
    performance = calculate_performance(symbol, median_price)

    new_row = {"time": current_time, "price": median_price, "performance": performance}
    df = pd.DataFrame([new_row])

    if os.path.isfile(file_path):
        existing_df = pd.read_csv(file_path)
        existing_df = pd.concat([existing_df, df], ignore_index=True)
        existing_df["performance"] = existing_df["price"].pct_change() * 100
        existing_df["performance"] = existing_df["performance"].cumsum()
        existing_df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)

def calculate_performance(symbol, median_price):
    folder_name = "coin_logs"
    file_path = os.path.join(folder_name, f"{symbol}.csv")

    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        last_price = df.iloc[-1]["price"]
        performance = ((median_price - last_price) / last_price) * 100
        return performance

    return 0

def get_prices():
    filename = "crypto_data.csv"
    try:
        df = pd.read_csv(filename)
        symbols = df["symbol"].tolist()

        exchanges = [ccxt.binance(), ccxt.cryptocom(), ccxt.gateio(), ccxt.okex(), ccxt.gateio(), ccxt.coinex()]
        supported_symbols = []
        prices = []

        for symbol in symbols:
            ticker_symbols = [f"{symbol}/USDT" for exchange in exchanges]
            symbol_prices = []

            for i, exchange in enumerate(exchanges):
                markets = exchange.load_markets()
                if ticker_symbols[i] in markets:
                    supported_symbols.append(ticker_symbols[i])
                    ticker = exchange.fetch_ticker(ticker_symbols[i])
                    symbol_prices.append(ticker['close'])
                else:
                    print(f"Symbol '{symbol}' is not supported by {exchange.id}.")

            if len(symbol_prices) > 0:
                median_price = statistics.median(symbol_prices)
                prices.append({"symbol": symbol, "price": median_price})
                save_price_update(symbol, median_price)

        if len(prices) > 0:
            prices_df = pd.DataFrame(prices, columns=["symbol", "price"])
            prices_filename = "crypto_prices.csv"
            prices_df.to_csv(prices_filename, index=False)
            print(f"CSV file '{prices_filename}' with median prices has been generated successfully.")

    except FileNotFoundError:
        print(f"CSVfile '{filename}' not found. Please enter the cryptocurrency data first.")

def best_performance_coin():
    folder_name = "coin_logs"
    if not os.path.exists(folder_name):
        print("No coin logs found.")
        return

    coin_files = os.listdir(folder_name)
    if len(coin_files) == 0:
        print("No coin logs found.")
        return

    performance_dict = {}
    for coin_file in coin_files:
        file_path = os.path.join(folder_name, coin_file)
        df = pd.read_csv(file_path)
        last_performance = df.iloc[-1]["performance"]
        performance_dict[coin_file[:-4]] = last_performance

    sorted_coins = sorted(performance_dict, key=performance_dict.get, reverse=True)
    top_3_coins = sorted_coins[:3]

    print("Top 3 Coins with the Best Performance:")
    for coin in top_3_coins:
        performance = performance_dict[coin]
        print("")
        print(f"{coin}: {performance:.3f}%")
        print("")

    output_file = "top_coins_performance.csv"
    output_data = pd.DataFrame({'Coin': top_3_coins, 'Performance': [performance_dict[coin] for coin in top_3_coins]})
    output_data.to_csv(output_file, index=False)
    print(f"\nTop 3 coins and their performance saved to {output_file}.")

def make_graphic():
    folder_name = "coin_logs"
    if not os.path.exists(folder_name):
        print("No coin logs found.")
        return

    coin_files = os.listdir(folder_name)
    if len(coin_files) == 0:
        print("No coin logs found.")
        return

    plt.figure(figsize=(17, 8))

    for coin_file in coin_files:
        file_path = os.path.join(folder_name, coin_file)
        df = pd.read_csv(file_path)
        df['time'] = pd.to_datetime(df['time'], format="%H:%Mh / %Y-%m-%d")
        df.sort_values('time', inplace=True)  # Sort DataFrame by 'time'
        plt.plot(df["time"], df["performance"], label=coin_file[:-4])

        last_performance = df.iloc[-1]["performance"]
        last_time = df.iloc[-1]["time"]
        plt.annotate(f'{coin_file[:-4]}: {last_performance:.3f}', xy=(last_time, last_performance),
                     xytext=(5, 0), textcoords='offset points', ha='left', va='center')

    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel("Time")
    plt.ylabel("Performance")
    plt.title("Performance Graph")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def check_positive_performance():
    folder_name = "coin_logs"
    if not os.path.exists(folder_name):
        print("No coin logs found.")
        exit()

    coin_files = os.listdir(folder_name)
    if len(coin_files) == 0:
        print("No coin logs found.")
        exit()

    positive_coins = []

    for coin_file in coin_files:
        file_path = os.path.join(folder_name, coin_file)
        df = pd.read_csv(file_path)

        if len(df) < 2:
            continue

        last_performance = df.iloc[-1]["performance"]
        current_performance = df.iloc[-2]["performance"]

        if current_performance > last_performance:
            coin_name = coin_file[:-4]
            positive_coins.append(coin_name)

    if len(positive_coins) > 0:
        df_positive = pd.DataFrame({"Coin Name": positive_coins})

        output_file = "positive_coins.csv"
        df_positive.to_csv(output_file, index=False)
        print(f"Positive coins saved to {output_file}")
    else:
        print("No coins with positive performance found.")


def check_coin_performance():
    positive_coins_file = 'positive_coins.csv'
    top_coins_performance_file = 'top_coins_performance.csv'

    positive_coins_df = pd.read_csv(positive_coins_file)
    top_coins_performance_df = pd.read_csv(top_coins_performance_file)

    positive_coins = set(positive_coins_df['Coin Name'])

    matching_coins = top_coins_performance_df[top_coins_performance_df['Coin'].isin(positive_coins)]

    if not matching_coins.empty:
        print("------------------------------------------------------------")
        print("Coins with positive performance:")
        print(matching_coins)
        print("------------------------------------------------------------")
    else:
        print("-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!")
        print("NO COIN ON BEST PERFORMANCE")
        print("-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!-!")

def reset():
    folder_path = "coin_logs"
    confirmation = input("Are you sure you want to delete the contents of the 'coin_logs' folder? This action cannot be undone. Please type 'DELETE' to confirm: ")

    if confirmation == "DELETE":
        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"The contents of the folder '{folder_path}' have been deleted.")
        except FileNotFoundError:
            print(f"The folder '{folder_path}' does not exist.")
        except Exception as e:
            print(f"An error occurred while deleting the contents of the folder '{folder_path}': {str(e)}")
    else:
        print("Deletion canceled.")

def run_general_code():
    best_performance_coin()
    check_positive_performance()
    check_coin_performance()

def menu():
    print("Menu:")
    print("1. Enter cryptocurrency data")
    print("2. Get prices")
    print("3. Best performance coin")
    print("4. Make graphic")
    print("r. Reset")
    print("x. Exit")

while True:
    menu()
    choice = input("Select an option: ")
    if choice == "1":
        enter_crypto_data()
    elif choice == "2":
        get_prices()
        print("")
        run_general_code()
    elif choice == "3":
        run_general_code()
    elif choice == "4":
        make_graphic()
    elif choice == "r":
        reset()
    elif choice.lower() == "x":
        break
    else:
        print("Invalid option. Please try again.")

print("Program exited.")
