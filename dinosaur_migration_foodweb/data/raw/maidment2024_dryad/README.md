# Data and code for: Diversity through space and time in the Upper Jurassic Morrison Formation, western USA

[https://doi.org/10.5061/dryad.6m905qg77](https://doi.org/10.5061/dryad.6m905qg77)

This dataset provides raw data and code for all analyses carried out in the above paper. There are eight .xlsx files that contain raw data, and four scripts that implement the analyses carried out in R.

The R script 'Diversity_analysis_code.R' plots raw generic occurrences, tetrapod-bearing collections and abundance against latitude and systems tract, and carries out correlation tests to examine whether these are statistically correlated with each other. It uses the data files "Genera_with_latitude.xlsx", "Collections with time.xlsx", "Corrected abundance with time.xlsx", "Collections_with_latitude.xlsx" and "Corrected abundance with latitude.xlsx".

The R script 'iNext_code.R' sample standardizes the raw generic occurrence data for each degree of latitude and for each systems tract using the iNEXT package and quorum levels from 0.3 to 0.7 and at a confidence interval of 0.95, and plots the results against time and latitude. It uses the data files "Genera_with_latitude.xslx".

The R script 'Dino_data_code.R' calculates the proportions of different dinosaurs across the whole Morrison Formation and by systems tract and plots the results as a proportional bar graph. It uses the data file "Occurrence data with STs_dinos.xlsx". The same plots could be produced for all tetrapod occurrences in the Morrison Formation and thus the data file "Occurrence data with STs.xlsx" which contains this information, is also included in the data package.

The R script 'Collector_curve_code.R' plots collector curves for different systems tracts in the Morrison Formation and uses the data file "Collector_curve_data.xlsx".

## Description of the data and file structure

The data package is divided into raw data and R scripts. The data files are referred to in the instructions in the R scripts.

"Collections with time.xlsx" comprises two columns, one titled 'coll', and which comprises all tetrapod-bearing collections for the Morrison Formation in the Paleobiology Database as of December 2022. The column titled "ST" comprises the systems tract that these collections are found in. Blank cells in column "ST" indicate that the systems tract is unknown.

"Collections_with_latitude.xlsx" comprises two columns. 'lat' is the degrees of latitude north rounded to 1 decimal place. 'coll' is the number of collections found within that degree of latitude in the Morrison Formation. These data are derived from a Paleobiology Database download in December 2022.

"Collector_curve_data.xlsx" comprises four columns. 'taxon' is an occurrence list of tetrapods from the Morrison Formation. 'pubyr' is the year that occurrence was published. 'collection' is the location where the occurrence was collected, and 'st' is the systems tract the occurrence (and collection) is found in. Blank cells indicate the systems tract is unknown. Data in the first three columns are from a Paleobiology Database download in December 2022.

"Corrected abundance with latitude.xlsx" has two columns. 'lat' is degrees latitude rounded to 1 decimal place. 'abun' is the number of tetrapod specimens found in the Morrison Formation. These data are derived from a Paleobiology Database download in December 2022 and are shown in the data sheet "Genera_with_latitude".

"Corrected abundance with time.xlsx" has two columns. 'ST' is systems tract. 'abun' is the number of tetrapod specimens found in the Morrison Formation. Abun data is derived from a Paleobiology Database download in December 2022, and is shown in the data sheet "Genera_with_latitude"

"Genera_with_latitude.xlsx" comprises four columns. 'accepted_name' is a list of tetrapod bearing occurrences to generic level known in the Morrison Formation. 'lat' is the latitude at which the occurrence was found. 'abund_va' is the number of specimens of that taxon that were found at the same site. 'ST' is systems tract. Blank cells indicate unknown values. Data in the first three columns are from a Paleobiology Database download made in December 2022.

"Occurrence data with STs.xlsx" is the Palaeobiology Database download made in December 2022 from which other data sheets are derived. It shows all tetrapod occurrences in the Morrison Formation recorded in the database at that time. Added to that is the column 'Systems tract', which gives the systems tract in which each occurrence is found. Blank cells in the Systems tract column indicate that the systems tract is unknown. Blank cells elsewhere in the data sheet indicate inapplicable values.

"Occurrence data with STs_dinos.xlsx" is as above but with only dinosaur occurrences (rather than all tetrapods).

## Sharing/Access information

Data was derived from The Paleobiology Database.

## Code/Software

This data package contains R scripts, which were written in R version 4.0.4. Their function and the data they use is described above. The scripts require the following packages to run correctly: Tidyverse, nlme, ggfortify, iNEXT, ggplot2, patchwork. This information is included in the individual scripts.
