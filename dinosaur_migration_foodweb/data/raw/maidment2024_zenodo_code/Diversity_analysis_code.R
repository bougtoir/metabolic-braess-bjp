#Morrison raw diversity analyses 
#December 2022
#Susannah Maidment
###########################################################################

library(tidyverse)

#########################################################################
#CALCULATE RAW DIVERSITY, ABUNDANCE AND COLLECTIONS THROUGH TIME
#Import dataset Genera with latitude.xlsx

DivTime<-select(Genera_with_latitude, accepted_name, ST)

#Group by systems tract and give uncorrected abundance of each genus
DivTime<-DivTime%>%
  group_by(ST)%>%
  count(accepted_name)

#Calculate the number of unique taxa in each systems tract
x<-c(2:6)

DivByST<-list()

for (val in x) {
  
  y<-filter(DivTime, ST == val)
  DivByST[[val]]<-summarise(y, length(accepted_name))
}

DivByST1<-as_tibble_col(DivByST)
DivByST1<-unnest(DivByST1, value)

#DivByST1 is the diversity in terms of numbers of unique genera in each systems tract

#Import Corrected abundance with time
abun<-Corrected_abundance_with_time$abun

#Import Collections with time

CollTime<-select(Collections_with_time, coll, ST)

#Group by systems tract
CollTime<-CollTime%>%
  group_by(ST)%>%
  count(coll)

#Calculate number of collections in each systems tract

x<-c(2:6)

CollbyST<-list()

for (val in x) {
  y<-filter(CollTime, ST == val)
  CollbyST[[val]]<-summarise(y, length(coll))
}

CollbyST1<-as_tibble_col(CollbyST)
CollbyST1<-unnest(CollbyST1, value)

#Build a table for plotting

div<-DivByST1$`length(accepted_name)`
coll<-CollbyST1$`length(coll)`
st<-x

DivTimeData<-tibble(st, div, abun, coll)

DivTimePlot<-ggplot(DivTimeData)+
  geom_point(aes(x=st, y=div, colour="Diversity"), size=2)+
  geom_path(aes(x=st, y=div, group=1, colour="Diversity"), size=1)+
  geom_point(aes(x=st, y=coll, colour="Collections"), size=2)+
  geom_path(aes(x=st, y=coll, group=1, colour="Collections"), size=1)+
  geom_point(aes(x=st, y=abun, colour="Abundance"), size=2)+
  geom_path(aes(x=st, y=abun, group=1, colour="Abundance"), size=1)+
  scale_colour_manual(values=c("cornflowerblue", "maroon4", "darkgreen"))+
  scale_y_log10()+
  theme_bw(base_size=14)+
  theme(legend.title = element_blank())+
  theme(legend.text = element_text(size=12))+
  theme(legend.position = c(0.2, 0.8))+
  xlab("Systems tract")+
  ylab("Count")

DivTimePlot

ggsave("Diversity_with_ST.png", width = 6, height = 5)




####################################################################################################
####################################################################################################

#CALCULATE RAW DIVERSITY, ABUNDANCE AND COLLECTIONS WITH LATITUDE
#Import dataset Genera with latitude.xlsx

DivLat<-select(Genera_with_latitude, accepted_name, lat, ST)

#Round latitude to nearest degree

DivLat<- DivLat %>% 
  mutate_at(2, round, 0)

#Filter on systems tract required

DivLatC6<-filter(DivLat, ST == 6)


#Group by degrees latitide and sum the total in each column

DivByLatC6<-DivLatC6%>%
  group_by(lat)%>%
  count(accepted_name)

#Calculate the number of unique taxa at each degree of latitude
x<-c(34:47)

DivByDegC6<-list()

for (val in x) {
  
  y<-filter(DivByLatC6, lat == val)
  DivByDegC6[[val]]<-summarise(y, length(accepted_name))
}

DivByDegC6<-as_tibble_col(DivByDegC6)
DivByDegC6<-unnest(DivByDegC6, value)

#DivByDeg1 is diversity in terms of generic richness per degree of latitude. 


####Import dataset Corrected abundance with latitude (if required unhash)
  
AbunByDeg<-select(Corrected_abundance_with_latitude, lat, abun)



####Import dataset collections with latitude (if required unhash)

CollByDeg<-select(Collections_with_latitude, lat, coll)

####Build a dataset to plot
lat<-c(34:47)
div<-DivByDeg1$`length(accepted_name)`
abun<-AbunByDeg$abun
coll<-CollByDeg$coll

DivByDegA2<-c(0, 1, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0)
DivByDegB3<-c(0, 0, 0, 0, 5, 21, 4, 0, 0, 0, 0, 0, 0, 0)
DivByDegB4<-c(0, 3, 4, 9, 10, 45, 17,  2, 5, 0,  0,  6,  5,  0)
DivByDegC5<-c(0, 0, 0, 9, 0, 10, 10, 18, 12, 3, 17, 14, 0, 0)
DivByDegC6<-c(0, 0, 0, 0, 0, 0, 0, 0, 53, 4, 22, 3, 0, 0)


DivData<-tibble(lat, div, coll, abun)
DivDataST<-tibble(lat, DivByDegA2, DivByDegB3, DivByDegB4, DivByDegC5, DivByDegC6)


#Plot

DivLatPlot<-ggplot(DivData)+
  geom_point(aes(x=lat, y=div, colour="Diversity"), size=2)+
  geom_path(aes(x=lat, y=div, colour="Diversity"), size=1)+
  geom_point(aes(x=lat, y=coll, colour="Collections"), size=2)+
  geom_path(aes(x=lat, y=coll, colour="Collections"), size=1)+
  geom_point(aes(x=lat, y=abun, colour="Abundance"), size=2)+
  geom_path(aes(x=lat, y=abun, colour="Abundance"), size=1)+
  scale_colour_manual(values=c("maroon", "cornflowerblue", "seagreen"))+
  scale_y_log10()+
  theme_bw(base_size=12)+
  theme(legend.title = element_blank())+
  theme(legend.text = element_text(size=12))+
  theme(legend.position = c(0.87, 0.25))+
  xlab("Latitude (degrees north)")+
  ylab("Count")+
  coord_flip()
DivLatPlot


DivLatSTPlot<-ggplot(DivData)+
  geom_point(aes(x=lat, y=DivByDegA2, colour="A2"), size=2)+
  geom_path(aes(x=lat, y=DivByDegA2, group=1, colour="A2"), size=1)+
  geom_point(aes(x=lat, y=DivByDegB3, colour="B3"), size=2)+
  geom_path(aes(x=lat, y=DivByDegB3, group=1, colour="B3"), size=1)+
  geom_point(aes(x=lat, y=DivByDegB4, colour="B4"), size=2)+
  geom_path(aes(x=lat, y=DivByDegB4, group=1, colour="B4"), size=1)+
  geom_point(aes(x=lat, y=DivByDegC5, colour="C5"), size=2)+
  geom_path(aes(x=lat, y=DivByDegC5, group=1, colour="C5"), size=1)+
  geom_point(aes(x=lat, y=DivByDegC6, colour="C6"), size=2)+
  geom_path(aes(x=lat, y=DivByDegC6, group=1, colour="C6"), size=1)+
  scale_colour_manual(values=c("red", "orange", "yellow", "lightgreen", "cornflowerblue"))+
  theme_bw(base_size=14)+
  theme(legend.title = element_blank())+
  theme(legend.text = element_text(size=12))+
  theme(legend.position = c(0.87, 0.8))+
  xlab("Latitude (degrees north)")+
  ylab("Diversity")+
  coord_flip()
DivLatSTPlot

ggsave("Diversity_with_Latitude_per_ST.png", width = 6, height = 5)

#to add in the abundance data add these lines
#geom_point(aes(x=lat, y=abun, colour="Abundance"), size=1)+
#geom_path(aes(x=lat, y=abun, group=1, colour="Abundance"), size=0.5)+

#correlation tests

cor.test(div, coll, method="kendall")
cor.test(div, coll, method="spearman")

cor.test(div, abun, method="kendall")
cor.test(div, abun, method="spearman")

cor.test(abun, coll, method="kendall")
cor.test(abun, coll, method="spearman")

#apply a generalised linear model to account for autocorrelation

library (nlme)
CorData<-tibble (div, coll)

#examine data
ggplot(CorData, aes(x=div, y=coll))+
  geom_point(size=2, colour="cornflowerblue")+
  theme_bw(base_size=14)+
  labs(x="diversity", y="collections")

#calculate lm
mod1_CorData<-lm(div ~ coll, data=CorData)

#examine assumptions

library(ggfortify)

autoplot(mod1_CorData)

#assumptions dodgy, particularly scale location and residuals vs. fitted: 
#log data. But coll has a 0 value so add 1 to all datapoints

CorData<-mutate(CorData, coll=coll+1)
coll<-CorData$coll

logDiv<-log(div)
logColl<-log(coll)

logCorData<-tibble (logDiv, logColl)

ggplot(logCorData, aes(x=logColl, y=logDiv))+
  geom_point(size=2, colour="cornflowerblue")+
  geom_smooth(method=lm, se=FALSE, colour="cornflowerblue")+
  theme_bw(base_size=14)+
  labs(x="Collections", y="Diversity")

mod1_logCorData<-lm(logColl ~ logDiv, data=logCorData)
autoplot(mod1_logCorData)

#assumptions look better. Residuals vs. fitted is nearly flat. 
#Scale-location not a hockey stick anymore 
#Normal Q-Q fine in both cases. 

anova(mod1_logCorData)
summary(mod1_logCorData)

#div and coll are correlated.
#now use GLS to account for autocorrelation due to latitude

mod2_logCorData<-gls(logColl ~ logDiv, logCorData, method = "ML", correlation = corARMA(p=1))
summary(mod2_logCorData)



