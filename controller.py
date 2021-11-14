import requests
import json
import xmltodict

class Controller:
    def __init__(self):
        self.nbp_site = "http://api.nbp.pl/api/exchangerates/tables/A?format=json"
        self.agh_meteo_api = "http://meteo2.ftj.agh.edu.pl/meteo/meteo.xml"

    def get_weather(self):
        r = requests.get(self.agh_meteo_api)
        r.encoding = 'utf-8'
        dic = xmltodict.parse(r.text)['meteo']
        result = "                                                              "
        result += dic['miasto'] + " " + dic['nazwa_stacji'] + " " + dic['szerokosc_geograficzna'] + " " + dic['dlugosc_geograficzna'] + " " * 31
        curr_data = dic['dane_aktualne']
        result += ("temperatura: " + curr_data['ta']).ljust(79)
        result += ("wilgotność: " + curr_data['ua']).ljust(80)
        result += ("średnia prędkość wiatru: " + curr_data['sm']).ljust(80)
        result += ("ciśnienie barometryczne: " + curr_data['barosealevel']).ljust(79)
        
        return result 

    def get_currency_table(self):
        table = json.loads(requests.get(self.nbp_site).text)[0]
        result = "                                                              "
        for row in table['rates']:
            if row['code'] in {'USD', 'AUD', 'CAD', 'EUR', 'CHF', 'GBP', 'CZK', 'HRK', 'UAH', 'SEK'}:
                result += f"[({row['code']}) : ({str(row['mid']).ljust(6)})]" + " " * 62 
        return result
