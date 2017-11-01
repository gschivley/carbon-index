# Index-variability
This repository contains the data analysis and figure generation code for *Assessing the evolution of power sector carbon intensity in the United States* (submitted). The methods and code borrow heavily from the Power Sector Carbon Index ([EmissionsIndex.org](emissionsindex.org)).

## Organization
Most analysis is done with a series of Jupyter notebooks in the `Notebooks` folder. Commonly used functions are included as scripts in the `src` folder. Most necessary data is downloaded automatically with scripts, but you will need to download and extract [EIA's bulk electricity data file](https://www.eia.gov/opendata/bulkfiles.php) (or use this direct link: [ELEC.zip](http://api.eia.gov/bulk/ELEC.zip)). We use EIA's bulk data file rather than the EIA-923 Excel files because it is an easy way to access all of the generation and fuel consumption data in one place. The datafile also includes lat/lon data for each plant, which would otherwise have to be accessed through EIA-860.

Data files are located in the `Data storage` folder. Some files aren't included in this repo - they either need to be downloaded manually (e.g. the ELEC.txt file) or using code in one of the notebooks (e.g. EPA emissions data). A single file (`Data storage/Facility labels/Facility locations.csv', which gives the state, lat/lon, and NERC region of each plant) was compiled without the use of Python scripts. We used QGIS to perform the spatial join, because GeoPandas assigned a handful of power plants to multiple NERC regions.

## Recreating results
Producing monthly generation by fuel type, adjusted fossil CO<sub>2</sub> emissions, and CO<sub>2</sub> intensity at state, regional, and national levels is not yet fully automated. As mentioned above, a few data files need to be obtained or created manually. Otherwise, the steps are as follows:

### Download and extract EPA emissions
1. Run the `Download EPA emissions data` notebook. This will download zip files for selected years from the AMPD ftp server, extract the hourly data, change column names to make them consistent over time, and combine everything into .csv files for each year.
2. Run the `Group EPA emissions data by month` notebook. This will read in the .csv files that were just created, group emissions for each facility to the monthly level, and export a single .csv file.

Code for these two notebooks could be combined without too much trouble.

### Extract data from EIA bulk file
1. Run the `EIA Bulk Download - extract facility generation` notebook. This reads in data from `ELEC.txt`, extracts generation and fuel consumption data, calculates CO<sub>2</sub> emissions from the fuel consumption using emission factors, and exports the results as a .csv file.
2. Run the `EIA bulk download - non-facility (distributed PV & state-level)` notebook. This reads in the `ELEC.txt` file again, but extracts state-level total generation and fuel consumption. As above, calculate CO<sub>2</sub> emissions using emission factors. Export both national and state-level results to .csv files.

### Calculate generation by fuel, total CO<sub>2</sub>, and CO<sub>2</sub> intensity
1. For national and NERC regions, run the `Calculate national and NERC gen and emissions` notebook. This reads in facility data, EIA state-level data (at national level), EPA emissions, and emission factors. It calculates the historical fraction of generation/fuel consumption from annual reporting facilities in each NERC region within a states, and uses the results to allocate state-level estimates in recent years to NERC regions. We have to do this because a subset of power plants only have to report EIA-923 at the end of the year. EIA estimates their generation/fuel consumption throughout the year, reporting it as part of the state-level totals. Actual facility data is included in the final 923 release the following fall. **Note** This notebook produces final national results, but only *extra* generation/fuel consumption for NERC regions.
2. Since the notebook above doesn't actually calculate final NERC results, open up the `Calculate NERC results` notebook (*these should probably be combined at some point*). Start by loading in the extra gen/fuel consumption calculated above, and calculate CO<sub>2</sub> emissions using emission factors. Facility data are grouped into NERC regions, and combined with the extra data to create total generation (including by fuel) and emissions.
3. Finally, run the `Compile state index & gen files` notebook.

### Generate figures and top-line numbers
1. For NERC and national figures, run the `Paper figures` notebook.
2. For state-level barbell and SI figures, run the `State figures` notebook.
