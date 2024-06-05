#!/usr/bin/env python3

import pandas as pd 
from pathlib import Path

DIR = Path("/home/haxor/Documents/Competitions/Shell/dataset/")

class Constraint:
    def __init__(self):
        print("Contraint Class!")
        pass 

    def Size(self):
        # Size used must equal vehicle size
        pass

    def Distance(self):
        # Distance travelled must be <= than vehicle 
        # distance (D1, D2, etc..)
        pass

    def CarbonEmissions(self):
        # Vehicle Carbon =  For SUM(fueltype) in vehicle:
        #                       Distance traveled *
        #                       Consumption Rate (fuel type) *
        #                       Carbon Emissions (type) *
        #                       Number of Vehicles with that fuel type
        #
        # Total Carbon = For vehicle in Fleet:
        #                   SUM(Vehicle Carbon)

        pass

    def Targets(self):
        # Must reach size and distance targets per vehicle per year
        pass

    def PurchaseYear(self):
        # Vehicle can only be bought in year of manufacture 
        pass

    def Age(self):
        # Vehicle must be sold at latest, the end of it's tenth year
        pass

    def BuyOrSellDate(self):
        # Vehicle must be sold dec 31st and bought jan 1st
        pass

    def MaxFleetSold(self):
        # Must sell <= 20% of fleet
        pass

def main():
    Constraint() 
    return 0

if __name__ == '__main__':
    main()

