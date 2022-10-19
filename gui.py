import PySimpleGUI as sg
from scraper import AmazonProductReviewScraper
import time

def gui():
    sg.theme("BluePurple")
    layout = [
        [sg.Text("Please input product's url:")],
        [sg.InputText("",expand_x=True,key="-URL-")],
        [sg.Text("")],
        [sg.Column(justification="c",layout = [
            [sg.Button("Scrape Reviews",key="-SCRAPE-",size=(13,2),button_color=("white","orange")),
            sg.Frame(element_justification="c",title="",layout=[[sg.Button("Export",key="-EXPORT-",button_color=("white","green"),disabled_button_color=("white","gray"),disabled=True)],[sg.Radio("json","file_fmt",key="-JSON-"),sg.Radio("csv","file_fmt",key="-CSV-")]])]
            ])],
        [sg.Text("")],
        [sg.Button("Exit",key="-EXIT-",size=(5,1),button_color=("white","red"))]
        ]

    window = sg.Window("Amazon product review scraper", layout = layout)

    while True:
        event,values = window.read()
        if event in [sg.WIN_CLOSED,"-EXIT-"]:
            break
        if event == "-SCRAPE-":
            if not len(values["-URL-"]):
                sg.popup("Please input url.")
                continue

            instance = AmazonProductReviewScraper(values["-URL-"])
            instance.scrape_all_pages_concurrent()
            sg.popup("Scraping complete!")
            window["-EXPORT-"].update(disabled=False)
        
        if event == "-EXPORT-":

            if values["-JSON-"]:
                instance.to_json(f"scraping_output_{int(time.time())}.json")
                continue

            instance.to_csv(f"scraping_output_{int(time.time())}.csv")

if __name__ == "__main__":
    gui()