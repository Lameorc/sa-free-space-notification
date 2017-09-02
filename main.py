import argparse
import ctypes
import logging
import time
from tkinter import *

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DESTINATION_URLS = {
    "zlin": "https://jizdenky.regiojet.cz/Booking/from/10204002/to/17655001/tarif/CZECH_STUDENT_PASS_26/departure/{}/retdep/{}/return/false",
    "brno": "https://jizdenky.regiojet.cz/Booking/from/17655001/to/10204002/tarif/CZECH_STUDENT_PASS_26/departure/{}/retdep/{}/return/false"
}

logger = logging.getLogger('main')
fh = logging.FileHandler('last_run.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(ch)


def mBox(title, text, style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def tkiner_mbox(title, msg):
    root = Tk()
    label = Label(root, text=msg, padx=5, pady=5)
    label.pack()

    button = Button(root, text="ok", command=lambda: root.destroy())
    button.pack()

    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    root.wm_title("SA scraping")
    root.mainloop()


class Renderer():
    def __init__(self, url):
        self.url = url
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.__driver = webdriver.Chrome(executable_path="e:\\Data\\selenium\\chromedriver.exe",
                                         chrome_options=chrome_options)

    def html(self):
        self.__driver.get(self.url)
        return self.__driver.page_source

    def __del__(self):
        self.__driver.close()


class Connection():
    def __init__(self, departure_time: str, free_spaces: int, url: str):
        self.departure_time = departure_time
        self.free_spaces = free_spaces
        self.search_url = url


def retrieve_connections(date, destination):
    """
    date: str in format YYYYMMDD
    """
    connections = []
    url = DESTINATION_URLS[destination.lower()].format(date, date)
    r = Renderer(url)
    soup = bs(r.html(), "html.parser")
    connection_elements = soup.find_all("div", class_="routeSummary")
    for tag in connection_elements:
        departure_time = tag.contents[3].get_text()  # The indexes are kind of magical
        free_spaces = tag.contents[9].get_text()
        connections.append(Connection(departure_time, int(free_spaces), url))
    return connections


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, type=str, default="n",
                        help="date of outbound journey")
    parser.add_argument("--destination", required=True, type=str, default="n",
                        help="Destination of your journey")
    parser.add_argument("--time", type=str, default="n",
                        help="Time for which you would like to make a reservation")
    args = parser.parse_args()

    if args.date == "n" or args.destination == "n":
        print("One of the required arguments is missing")
    elif args.time == "n":
        connections = retrieve_connections(
            date=args.date,
            destination=args.destination
        )
        search_result = "Found connections:"
        for connection in connections:
            search_result += "\nTime: {}\tFree spaces: {}".format(connection.departure_time, connection.free_spaces)
        tkiner_mbox(title="Search results", msg=search_result)
    else:
        while True:
            connections = retrieve_connections(
                date=args.date,
                destination=args.destination
            )
            try:
                departure_times
            except:
                departure_times = None
            if departure_times is None:  # first run only
                departure_times = []
                for connection in connections:
                    departure_times.append(connection.departure_time)
                if args.time not in departure_times:
                    tkiner_mbox("Error", "Failed to find the time specified on this day. Double check input")
                    sys.exit(1)
            for connection in connections:
                if connection.departure_time == args.time and connection.free_spaces > 0:
                    tkiner_mbox(title="Found empty space",
                                msg="Empty space at {} found. Go to website for reservation".format(args.time))
                    sys.exit(0)
                else:
                    logger.info('No free spaces found')
            time.sleep(60)
