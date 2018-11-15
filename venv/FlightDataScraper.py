# This file scrapes data from Expedia about flights

## Josh Dombal
## November 15th, 2018





import json
import requests
from lxml import html
from collections import OrderedDict
import argparse


def parse(source, destination, date):
    for i in range(5):
        try:
            #https://www.expedia.com/Flights-Search?flight-type=on&starDate=11%2F16%2F2018&endDate=11%2F22%2F2018&mode=search&trip=roundtrip&leg1=from%3ASeattle%2C+WA+%28SEA-Seattle+-+Tacoma+Intl.%29%2Cto%3AMiami%2C+FL+%28MIA-All+Airports%29%2Cdeparture%3A11%2F16%2F2018TANYT&leg2=from%3AMiami%2C+FL+%28MIA-All+Airports%29%2Cto%3ASeattle%2C+WA+%28SEA-Seattle+-+Tacoma+Intl.%29%2Cdeparture%3A11%2F22%2F2018TANYT&passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY
            # https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:SEA,to:MIA,starDate:11/20/2018,endDate:11/28/2018TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com
            url = "https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:{0},to:{1},starDate:{2},endDate:{3}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,departureDate,returnDate)
            #url2 = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com"

            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
            response = requests.get(url, headers=headers, verify=False)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
            raw_json = json.loads(json_data_xpath[0] if json_data_xpath else '')
            flight_data = json.loads(raw_json["content"])

            flight_info = OrderedDict()
            lists = []


            for i in flight_data['legs'].keys():
                total_distance = flight_data['legs'][i].get("formattedDistance", '')
                exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal', '')

                departure_location_airport = flight_data['legs'][i].get('departureLocation', {}).get('airportLongName', '')
                departure_location_city = flight_data['legs'][i].get('departureLocation', {}).get('airportCity', '')
                departure_location_airport_code = flight_data['legs'][i].get('departureLocation', {}).get('airportCode', '')

                arrival_location_airport = flight_data['legs'][i].get('arrivalLocation', {}).get('airportLongName', '')
                arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation', {}).get('airportCode', '')
                arrival_location_city = flight_data['legs'][i].get('arrivalLocation', {}).get('airportCity', '')
                airline_name = flight_data['legs'][i].get('carrierSummary', {}).get('airlineName', '')

                no_of_stops = flight_data['legs'][i].get("stops", "")
                flight_duration = flight_data['legs'][i].get('duration', {})
                flight_hour = flight_duration.get('hours', '')
                flight_minutes = flight_duration.get('minutes', '')
                flight_days = flight_duration.get('numOfDays', '')

                if no_of_stops == 0:
                    stop = "Nonstop"
                else:
                    stop = str(no_of_stops) + ' Stop'

                total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days, flight_hour, flight_minutes)
                departure = departure_location_airport + ", " + departure_location_city
                arrival = arrival_location_airport + ", " + arrival_location_city
                carrier = flight_data['legs'][i].get('timeline', [])[0].get('carrier', {})
                plane = carrier.get('plane', '')
                plane_code = carrier.get('planeCode', '')
                formatted_price = "{0:.2f}".format(exact_price)

                if not airline_name:
                    airline_name = carrier.get('operatedBy', '')

                timings = []
                for timeline in flight_data['legs'][i].get('timeline', {}):
                    if 'departureAirport' in timeline.keys():
                        departure_airport = timeline['departureAirport'].get('longName', '')
                        departure_time = timeline['departureTime'].get('time', '')
                        arrival_airport = timeline.get('arrivalAirport', {}).get('longName', '')
                        arrival_time = timeline.get('arrivalTime', {}).get('time', '')
                        flight_timing = {
                            'departure_airport': departure_airport,
                            'departure_time': departure_time,
                            'arrival_airport': arrival_airport,
                            'arrival_time': arrival_time
                        }
                        timings.append(flight_timing)

                flight_info = {'stops': stop,
                               'ticket price': formatted_price,
                               'departure': departure,
                               'arrival': arrival,
                               'flight duration': total_flight_duration,
                               'airline': airline_name,
                               'plane': plane,
                               'timings': timings,
                               'plane code': plane_code
                }
                lists.append(flight_info)
            sortedlist = sorted(lists, key=lambda k: k['ticket price'], reverse=False)
            return sortedlist

        except ValueError:
            print ("Rerying...")

        return {"error":"failed to process the page",}




    if __name__=="__main__":
        argparse = argparse.ArgumentParser()
        argparser.add_argument('source', help = 'Source airport code. Ex: SEA')
        argparser.add_argument('destination', help = 'Destination airport code. Ex: MIA')
        argparser.add_argument('departureDate', help = 'MM/DD/YYYY')
        argparser.add_argument('returnDate', help='MM/DD/YYYY')


        args = argparser.parse_args()
        source = args.source
        destination = args.destination
        departureDate = args.departureDate
        returnDate = args.returnDate

        print("Fetching flight details")

        scraped_data = parse(source, destination, departureDate, returnDate)

        print ("Writing data to output file")

        with open('%s-%s-flight-results.json'%(source,destination), 'w') as fp:
            json.dump(scraped_data, fp, indent = 4)
















