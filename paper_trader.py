import csv
import requests
from bs4 import BeautifulSoup
    
acct_balance = 10000.0
inv = []
#inv = list of entries in the form: [Ticker, Quantity, Total Cost]    

#a simple test program, added for my convenience
def run_test():
    global acct_balance
    global inv
    
    print('buy 5 tesla \n')
    buy("TSLA",5)
    print(inv)
    print(acct_balance)
    
    print('buy 10 twitter \n')
    buy("TWTR",10)
    print(inv)
    print(acct_balance)
    
    print('\n\n import the csv \n')
    import_existing_csv()
    print(inv)
    print(acct_balance)
    
    print('\n\n sell 1 tesla \n')
    sell("TSLA",1)
    print(inv)
    print(acct_balance)
    
    print('\n\n sell 4 teslas \n')
    sell("TSLA",4)
    print(inv)
    print(acct_balance)
    
# imports current account balance and inventory
def import_existing_csv():
    global acct_balance
    global inv
    acct_balance = -40.0
    inv = []
    with open('CurrentPortfolio.csv','r') as infile:
        file_reader = csv.reader(infile)
        for entry in file_reader:
            inv.append(entry)
        acct_balance = float(inv[0][0])
        inv.pop(0)
                
#returns the price of the given security
def get_price(ticker):    
    count = 3
    while True and count>0:
        try:
            rh_html = requests.get('https://robinhood.com/stocks/'+ticker.upper()).text
            rh_soup = BeautifulSoup(rh_html, 'lxml')
            return round(float(rh_soup.find('span', class_ = 'up')['aria-label'][1:]),2)
        except TypeError:
            #if the request fails, try again!
            print("Pricing request failed. Trying again...")
            count -=1
    print("Something went wrong.")

#determines if a stock can be purchased, and then passes the operation to process_buy
def buy(ticker,qty):
    #DEAL WITH BUY CONSTRAINTS HERE - enough money, valid ticker, etc
    global acct_balance
    
    try:
        cost = get_price(ticker)*qty
    except TypeError:
            print("Ticker symbol appears to be invalid. The buy order for \'" +ticker+ "\' will not be executed.")
            return
    if cost < acct_balance:
        process_buy(ticker,qty,cost)
    else:
        print("You do not have enough cash on hand to purchase this security. The buy order for \'" +ticker+ "\' will not be executed.")

#executes a market buy order
def process_buy(ticker,qty,cost):
    global inv
    global acct_balance
    acct_balance -= cost
    for entry in inv:
        if ticker in entry:
            old_entry = inv.pop(inv.index(entry))
            cost+= float(old_entry[2])
            qty+= old_entry[1]
    inv.append([ticker,qty,round(cost,2)])
    update_csv()

#determines if a stock can be sold, and then passes the operation to process_sell
def sell(ticker,qty):
    global acct_balance
    global inv
    #DEAL WITH SELL CONSTRAINTS HERE - stock is in inv, qty <= held qty, etc
    for entry in inv:
        if ticker in entry and qty <= int(entry[1]):
            process_sell(ticker,qty)
            return

#executes a market sell order
def process_sell(ticker,qty):
    global inv
    global acct_balance
    found = False
    
    price = get_price(ticker)*qty
    
    acct_balance += price
    for entry in inv:
        if ticker in entry and not found:
            index = inv.index(entry)
            old_entry = inv.pop(index)
            qty = int(old_entry[1])-qty
            price = float(old_entry[2])-price
            found = True
    if qty != 0:
        inv.append([ticker,qty,round(price,2)])
    update_csv()

#pushes the inventory and current balance into the csv file
def update_csv():
    global acct_balance
    global inv
    
    with open('CurrentPortfolio.csv','w', newline="") as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow([acct_balance])
        for entry in inv:
            csvwriter.writerow(entry)


run_test()
