"""
Hannah McGoran
05/16/2023
1. Substitutes incorrect 02/23/2023 concentration data in the main N2O data
with correct data by indexing with sample ID
2. Merges metadata with updates N2O data (377 samples to 375 samples)
2. Calculates potential density using GSW and adds it on to the merged dataframe
3. Merges updated N2O data+density data+metadata with with water mass percentages (375 samples to 318 samples)
"""
import pandas as pd
import numpy as np
import gsw as gsw


def convert_column(dataframe, column_name):  # Converts a column in a dataframe to a 1-D array
    prelim_list = list(dataframe[column_name])
    variable_array = [float(i) for i in prelim_list]
    return variable_array


def main():
    n2o = pd.read_csv("Final GP16 Regression Model - GP16 N2O Data (Pre-merge).csv")
    new_conc = pd.read_csv("Final GP16 Regression Model - New Concentrations.csv")
    metadata = pd.read_csv("Final GP16 Regression Model - GP16 Metadata.csv")
    water_mass = pd.read_csv("Final GP16 Regression Model - Water Mass Data (Pre-merge).csv")

    # Switch out old N2O concentrations with new N2O concentrations
    for i in range(len(new_conc["conc"])):
        samp_id = new_conc.at[i, "samp_num"]  # Identifies the sample ID to be replaced
        index = np.where(n2o["Sample ID"] == samp_id)[0][0]  # Identifies the index of the sample that needs to be replaced
        n2o.at[index, "N2O_avg"] = new_conc.at[i, "conc"]  # Replaces the conc at the index of interest with the updated conc
        n2o.at[index, "N2O_std"] = new_conc.at[i, "stdev"]

    # Merge metadata with N2O data
    isotope_merge = pd.merge(metadata, n2o, on='Sample ID')  # Merges the new isotope data with the metadata

    # Calculate Potential Density
    salinity = convert_column(isotope_merge, "SALNTY")
    pressure = convert_column(isotope_merge, "CTDPRS")
    longitude = convert_column(isotope_merge, "LONGITUDE")
    latitude = convert_column(isotope_merge, "LATITUDE")
    temperature = convert_column(isotope_merge, "CTDTMP")
    abs_salinity = gsw.conversions.SA_from_SP(salinity, pressure, longitude, latitude)
    cons_temp = gsw.conversions.CT_from_t(abs_salinity, temperature, pressure)
    density = list(gsw.density.sigma0(abs_salinity, cons_temp))
    isotope_merge["Potdens"] = density  # Adds density as a column to the isotope + metadata dataframe

    # Merge N2O data + metadata with water mass data
    water_mass_merge = pd.merge(isotope_merge, water_mass, on='Sample ID')

    print(isotope_merge)
    print(water_mass_merge)

    isotope_merge.to_csv(
            r'/Users/hannahmcgoran/Documents/Research/Latest GP16 Multiple Regression/merge_isotope.csv', index=False)
    water_mass_merge.to_csv(
           r'/Users/hannahmcgoran/Documents/Research/Latest GP16 Multiple Regression/merge_water_mass.csv', index=False)


if __name__ == "__main__":
    main()