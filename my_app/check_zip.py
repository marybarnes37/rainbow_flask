import pandas as pd

class checkZip(object):
    def __init__(self):
        self.data = pd.read_csv('data/zip_code_database.csv')
        self.supported_counties = {'WA': 'King County', 'CO': 'Denver County', 'TX': 'Travis County'}
        self.seattle_zips = self.get_city_zips('WA', 'King County')
        self.denver_zips = self.get_city_zips('CO', 'Denver County')
        self.austin_zips = self.get_city_zips('TX', 'Travis County')

    def get_city_zips(self, state, county):
        return list(self.data[(self.data['state'] == state) & (self.data['county'] == county)]['zip'])

    def check_zip(self, zip_code):
        if zip_code in self.seattle_zips:
            return "You've been added to Seattle rainbow alerts."
        elif zip_code in self.denver_zips:
            return "You've been added to Denver rainbow alerts."
        elif zip_code in self.austin_zips:
            return "You've been added to Austin rainbow alerts."
        else:
            return "We don't currently have rainbow results for your zip code."

    def get_supported_counties(self):
        return self.supported_counties
