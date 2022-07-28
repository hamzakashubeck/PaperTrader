import csv
from yahooquery import Ticker
    
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
    inv = []
    with open('CurrentPortfolio.csv','r') as infile:
        file_reader = csv.reader(infile)
        for entry in file_reader:
            inv.append(entry)
        acct_balance = float(inv[0][0])
        inv.pop(0)
                
#returns the price of the given security
def get_price(ticker):
    try:
        stock = Ticker(ticker)
        return stock.price[ticker.upper()]['regularMarketPrice']
    except:
        print('Invalid ticker symbol.\n')

#determines if a stock can be purchased, and then passes the operation to process_buy
def buy(ticker,qty):
    #DEAL WITH BUY CONSTRAINTS HERE - enough money, valid ticker, etc
    global acct_balance
    
    price = get_price(ticker)
    cost = price*qty

    if cost < acct_balance:
        process_buy(ticker,qty,cost)
        print('\nBought '+str(qty)+ ' '+ticker+ ' for $' +str(price)+ ' each, for a total of $'+str(cost)+'.')
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
    
    price = get_price(ticker)
    total_cost = price*qty
    
    print('Sold '+str(qty)+ ' '+ticker+ ' for $' +str(price)+ ' each, for a total of $'+str(total_cost)+'.')
    acct_balance += total_cost
    for entry in inv:
        if ticker in entry and not found:
            index = inv.index(entry)
            old_entry = inv.pop(index)
            qty = int(old_entry[1])-qty
            total_cost = float(old_entry[2])-total_cost
            found = True
    if qty != 0:
        inv.append([ticker,qty,round(total_cost,2)])
    
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

#POSSIBLE INPUTS: "buy", "sell", "balance", "inventory"
def handle_input(command):
    global acct_balance
    global inv
    
    print('\n')
    if command.lower() in 'buy':
        ticker = input("Type in the ticker symbol to purchase: ").upper()
        price = get_price(ticker)
        if not price:
            return
        qty = int(input(ticker+'\'s current price is $'+str(price) + ". How many would you like to buy?"))
        buy(ticker,qty)
    elif command.lower() in 'sell':
        ticker = input("Type in the ticker symbol to sell: ").upper()
        qty = int(input(ticker+'\'s current price is $'+str(get_price(ticker)) + ". How many would you like to sell?"))
        sell(ticker,qty)
    elif command.lower() in 'inv':
        print('Current portfolio: '+str(inv))
    elif command.lower() in 'balance':
        print('Cash balance: $'+str(round(acct_balance,2)))
    else:
        print('Invalid command.')
    print('\n')
        
def get_command():
    command = input('Type \"balance\" to view your overall currency balance.\nType \"inv\" to view your stock portfolio broken down by ticker, quantity, and total cost.\nType \"buy\" to purchase a new stock.\nType \"sell\" to sell an owned stock.\n')
    return command

import_existing_csv()
while True:
    cmd = get_command()
    handle_input(cmd)
