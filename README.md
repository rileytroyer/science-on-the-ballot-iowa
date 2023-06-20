# Read Me File for Science on the Ballot Iowa

See document-struture.md for a layout of the project structure and where files are located.

I don't include all of the directories in this particular project.

Make sure to run any .py files from the base project directory and not within a subdirectory.



### PDF Reader

Running this requires Java to be installed on your computer. 

Install via `sudo apt install default-jre`

This python script is located at src/features/candidate-info-to-excel.py

- The script takes a pdf created by the Iowa SoS with candidate information and writes this out to an excel spreadsheet organized by contested and not contested races.

- This works for the 2022 election cycle and no guaranty that the pdf format will remain the same.



### Mapping

You can find the 2021 redistricted boundaries here: https://www.legis.iowa.gov/legislators/redistricting

You can find a shape file for the entire state of iowa here: https://iowageodata2.s3.us-east-2.amazonaws.com/boundaries/iowa_border.zip

- This is through the following website: https://geodata.iowa.gov/documents/4d033695b9c142e2b7f899129da3b692/about

The raw shape files need some more processing to be used in the visualization. This is done with the script located at src/features/add-identifiers-to-shapefiles.py.

- Converts to .json files and adds identifiers to each shape for the race it represents.





### Visualization




