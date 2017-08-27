import argparse
import ctypes
import sys
import time

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DESTINATION_URLS = {
    "zlin": "https://jizdenky.regiojet.cz/Booking/from/10204002/to/17655001/tarif/CZECH_STUDENT_PASS_26/departure/{}/retdep/{}/return/false",
    "brno": "https://jizdenky.regiojet.cz/Booking/from/17655001/to/10204002/tarif/CZECH_STUDENT_PASS_26/departure/{}/retdep/{}/return/false"
}


def Mbox(title, text, style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


class Renderer():
    def __init__(self, url):
        self.url = url
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="e:\\Data\\selenium\\chromedriver.exe",
                                       chrome_options=chrome_options)
        self.driver.get(url=url)
        self.html = self.driver.page_source

    def html(self):
        self.driver.close()
        return self.html


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
    r = Renderer(url).html
    soup = bs(r, "html.parser")
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
        Mbox("Search results", search_result)
    else:
        while True:
            connections = retrieve_connections(
                date=args.date,
                destination=args.destination
            )
            departure_times = []
            for connection in connections:
                departure_times.append(connection.departure_time)
                if args.time not in departure_times:
                    Mbox("Error", "Failed to find the time specified on this day. Double check input")
                if connection.departure_time == args.time and connection.free_spaces > 0:
                    Mbox("Found empty space",
                         "Empty space at {} found. Go to website for reservation".format(args.time))
                    sys.exit(0)
            time.sleep(120)
