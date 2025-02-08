This project allows to analyze BGP events, tailored of rshort-lived MOAS events. 
Here are the brief explanation of the scripts you can find. Some of them are not neccessarily needed but included for further improvement or inspiration
## Main.py
gather data and write it in a log file

## Fullstream.py
depricated
used for testing purposes

## Combinedgraphs.py
make 2 graphs to visualize the count and ratio of MOAS events

## Maketable.py
read log files and find which is seen in multiple files or not

## Moasperyear.py
output a file showing prefixes with moas events
sorts from more moas events to less

## Durationcounter.py
for each prefix show the first and last seen
write it in respective log

## Makegraph.py
show the ratio and relations of BGP announcements and MOAS events

## find_onesession_yearly.py
find the MOAS events seen only in 1 case and put them in a respective yearly log file

## sus_asn_detection.py
for each AS involved in a MOAS event analyze attribute using RIPE STAT api
write it to a log file

## read_analysis.py
test script for analyzing the attributes of ASes

## suspicionscorer.py
refined versoin of read_analysis that grades the attribute of ASes using RPKI, RIS, and RIR data

## moasaverageduration.py
makes a table showing the duration of moas events

