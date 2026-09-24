##Code for plotting a collector curve##
##Susie Maidment, Jan 2023##
#######################################
######################################

library(tidyverse)

#Import dataset Collector_curve_data #

#First find number of collections each year, and then make a cumulative total

colls<-select(Collector_curve_data, collection, pubyr, st)

#filter for desired ST
colls<-filter(colls, st == 4)

#filter for year required
colls1<-filter(colls, pubyr==1901)

#find number of unique collections for that year
colls2<-distinct(colls1, collection)

#summarise the number of unique collections that year
colls3<-summarise(colls2, length(collection))

#loop this for all years
hist<-list()

dates<-c(1877:2022)

for (val in dates) {
  colls1<-filter(colls, pubyr==val)
  colls2<-distinct(colls1, collection)
  hist[val]<-summarise(colls2, length(collection))
}


hist1<-pluck(hist[dates])

#make a tibble
collsperyearB4<-tibble(dates, hist1)
collsperyearB4<-mutate(collsperyearB4, cumsum(hist1))
collsperyearB4<-rename(collsperyearB4, "cumulcolls"="cumsum(hist1)")

#collsperyear now shows the cumulative number of unique collections in the specified ST from years 1877 to 2022.


#Now find when new taxa are named

taxa<-select(Collector_curve_data, taxon, pubyr, st)
taxa<-filter(taxa, st == 4)


test<-unique(taxa$taxon)
test

taxa1<-list()

a<-c(1:50)

for (val in a) {
  dino<-filter(taxa, taxon == test[val])
  dino<-sort(dino$pubyr)
  dino1<-pluck(dino[1])
  taxa1[[val]]<-dino1
}


taxa2<-tibble(test, taxa1)
taxa2<-rename(taxa2, "taxon"="test")
taxa2<-rename(taxa2, "pubyr"="taxa1")

#taxa2 is the year each unique taxon was recognised in the specified ST

hist<-list()

dates<-c(1877:2022)

for (val in dates) {
  y<-filter(taxa2, pubyr==val)
  hist[val]<-summarise(y, length(taxon))
}


hist1<-pluck(hist[dates])

taxaperyearB4<-tibble(dates, hist1)
taxaperyearB4<-mutate(taxaperyearB4, cumsum(hist1))
taxaperyearB4<-rename(taxaperyearB4, "cumultaxa"="cumsum(hist1)")

#taxaperyear shows the cumulative number of new taxa published in the specified ST

#########################repeat for a different systems tract but rename files!#################

#First find number of collections each year, and then make a cumulative total

colls<-select(Collector_curve_data, collection, pubyr, st)

#filter for desired ST
colls<-filter(colls, st == 6)

hist<-list()

dates<-c(1877:2022)

for (val in dates) {
  colls1<-filter(colls, pubyr==val)
  colls2<-distinct(colls1, collection)
  hist[val]<-summarise(colls2, length(collection))
}


hist1<-pluck(hist[dates])

#make a tibble
collsperyearC6<-tibble(dates, hist1)
collsperyearC6<-mutate(collsperyearC6, cumsum(hist1))
collsperyearC6<-rename(collsperyearC6, "cumulcolls"="cumsum(hist1)")


#Now find when new taxa are named

taxa<-select(Collector_curve_data, taxon, pubyr, st)
taxa<-filter(taxa, st == 6)


test<-unique(taxa$taxon)
test

taxa1<-list()

a<-c(1:58)

for (val in a) {
  dino<-filter(taxa, taxon == test[val])
  dino<-sort(dino$pubyr)
  dino1<-pluck(dino[1])
  taxa1[[val]]<-dino1
}


taxa2<-tibble(test, taxa1)
taxa2<-rename(taxa2, "taxon"="test")
taxa2<-rename(taxa2, "pubyr"="taxa1")

#taxa2 is the year each unique taxon was recognised in the specified ST

hist<-list()

dates<-c(1877:2022)

for (val in dates) {
  y<-filter(taxa2, pubyr==val)
  hist[val]<-summarise(y, length(taxon))
}


hist1<-pluck(hist[dates])

taxaperyearC6<-tibble(dates, hist1)
taxaperyearC6<-mutate(taxaperyearC6, cumsum(hist1))
taxaperyearC6<-rename(taxaperyearC6, "cumultaxa"="cumsum(hist1)")

#taxaperyear shows the cumulative number of new taxa published in the specified ST



#Make a dataset with cumulative colls per year and cumulative taxa per year

collcurve<-tibble(collsperyearB4$cumulcolls, taxaperyearB4$cumultaxa, collsperyearC6$cumulcolls, taxaperyearC6$cumultaxa)
collcurve<-rename(collcurve, "B4colls"="collsperyearB4$cumulcolls", "B4taxa"="taxaperyearB4$cumultaxa", "C6colls"="collsperyearC6$cumulcolls", "C6taxa"="taxaperyearC6$cumultaxa")

## plot curve

collcurveplot<-ggplot(collcurve)+
  geom_point(aes(x=B4colls, y=B4taxa, colour="B4"), size = 2)+
  geom_path(aes(x=B4colls, y=B4taxa, colour="B4"), size=1)+
  geom_point(aes(x=C6colls, y=C6taxa, colour="C6"), size = 2)+
  geom_path(aes(x=C6colls, y=C6taxa, colour="C6"), size=1)+
  scale_colour_manual(values=c("cornflowerblue", "maroon4"))+
  xlab("Cumulative collections per year")+
  ylab("Cumulative new taxa identified")+
  theme_bw(base_size=14)+
  theme(legend.title = element_blank())+
  theme(legend.text = element_text(size=12))+
  theme(legend.position = c(0.2, 0.8))
collcurveplot



ggsave("C6 Collector curve.png", width = 6, height = 5)

library(patchwork)
B4collcurveplot/C6collcurveplot

ggsave("Collector curves.png", width=6, height = 10)
