#Morrison diversity analyses_subsampling using iNext
#January 2024
#Susannah Maidment
###########################################################
###########################################################

library(tidyverse)
library(ggplot2)
library(iNEXT)

#############################################################
#Diversity through time
############################################################
#Import 'genera with latitude'
DivTime<-select(Genera_with_latitude, accepted_name, ST)

DivTime<-DivTime%>%
  group_by(ST)%>%
  count(accepted_name)


#Extract from DivTime the abundance data for each genus and each systems tract
Abun_Data<-list()

x<-c(2:6)

for (val in x) {
  Abun_Data[[val]]<-filter(DivTime, ST==val)
}

#Calculate SQS value at a quorum level of 0.3 with a confidence interval of 0.95 for each systems tract

Results0.3<-list()

for (val in x) {
  Results0.3[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.3, conf = 0.95)
}

#Repeat for quorum levels to 0.7

Results0.4<-list()
for (val in x) {
  Results0.4[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.4, conf = 0.95)
}

Results0.5<-list()
for (val in x) {
  Results0.5[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.5, conf = 0.95)
}

Results0.6<-list()
for (val in x) {
  Results0.6[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.6, conf = 0.95)
}

Results0.7<-list()
for (val in x) {
  Results0.7[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.7, conf = 0.95)
}


#Extract qD values for each systems tract from Results0.3

q0.3<-vector()

for(val in x){

ST_matrix<-as.matrix(Results0.3[[val]])
q0.3[[val]]<-as.numeric(ST_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.3

LCL0.3<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.3[[val]])
  LCL0.3[[val]]<-as.numeric(ST_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.3

UCL0.3<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.3[[val]])
  UCL0.3[[val]]<-as.numeric(ST_matrix[1, 7])
}

#Make a matrix for plotting data

iNEXT_Time<-matrix(data = NA, nrow = 6, ncol=16)
iNEXT_Time[,1]<-q0.3
iNEXT_Time[,2]<-LCL0.3
iNEXT_Time[,3]<-UCL0.3
colnames(iNEXT_Time)<-c("qD0.3", "LCL0.3", "UCL0.3", "qD0.4", "LCL0.4", "UCL0.4", "qD0.5", "LCL0.5", "UCL0.5", "qD0.6", "LCL0.6", "UCL0.6", "qD0.7", "LCL0.7", "UCL0.7", "ST")


#Repeat for each quorum level

q0.4<-vector()

for(val in x){
  
  ST_matrix<-as.matrix(Results0.4[[val]])
  q0.4[[val]]<-as.numeric(ST_matrix[1, 5])
}

LCL0.4<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.4[[val]])
  LCL0.4[[val]]<-as.numeric(ST_matrix[1, 6])
}

UCL0.4<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.4[[val]])
  UCL0.4[[val]]<-as.numeric(ST_matrix[1, 7])
}


iNEXT_Time[,4]<-q0.4
iNEXT_Time[,5]<-LCL0.4
iNEXT_Time[,6]<-UCL0.4


##q0.5
q0.5<-vector()

for(val in x){
  
  ST_matrix<-as.matrix(Results0.5[[val]])
  q0.5[[val]]<-as.numeric(ST_matrix[1, 5])
}

LCL0.5<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.5[[val]])
  LCL0.5[[val]]<-as.numeric(ST_matrix[1, 6])
}

UCL0.5<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.5[[val]])
  UCL0.5[[val]]<-as.numeric(ST_matrix[1, 7])
}


iNEXT_Time[,7]<-q0.5
iNEXT_Time[,8]<-LCL0.5
iNEXT_Time[,9]<-UCL0.5


#q0.6
q0.6<-vector()

for(val in x){
  
  ST_matrix<-as.matrix(Results0.6[[val]])
  q0.6[[val]]<-as.numeric(ST_matrix[1, 5])
}

LCL0.6<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.6[[val]])
  LCL0.6[[val]]<-as.numeric(ST_matrix[1, 6])
}

UCL0.6<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.6[[val]])
  UCL0.6[[val]]<-as.numeric(ST_matrix[1, 7])
}

iNEXT_Time[,10]<-q0.6
iNEXT_Time[,11]<-LCL0.6
iNEXT_Time[,12]<-UCL0.6


#q0.7
q0.7<-vector()

for(val in x){
  
  ST_matrix<-as.matrix(Results0.7[[val]])
  q0.7[[val]]<-as.numeric(ST_matrix[1, 5])
}

LCL0.7<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.7[[val]])
  LCL0.7[[val]]<-as.numeric(ST_matrix[1, 6])
}

UCL0.7<-vector()

for(val in x){
  ST_matrix<-as.matrix(Results0.7[[val]])
  UCL0.7[[val]]<-as.numeric(ST_matrix[1, 7])
}


iNEXT_Time[,13]<-q0.7
iNEXT_Time[,14]<-LCL0.7
iNEXT_Time[,15]<-UCL0.7

#Remove the first row because there's no data in it, and add in systems tracts

x<-1:6
iNEXT_Time[,16]<-x
iNEXT_Time<-iNEXT_Time[-c(1),]

#Change to a tibble for plotting and saving

iNEXT_Time_Results<-as_tibble(iNEXT_Time)
write_csv(iNEXT_Time_Results, file ="iNEXT time results.csv")

#Due to large error bars and inconclusive results for ST2, remove that column and replot

iNEXT_Time_Results_minusST2<-iNEXT_Time[-c(1),]
iNEXT_Time_Results_minusST2<-as_tibble(iNEXT_Time_Results_minusST2)


#Plot data

#Plot the results 
iNEXT_plot<-ggplot(iNEXT_Time_Results_minusST2)+
  geom_point(aes(x=ST, y=qD0.3, colour="Quorum=0.3"), size=2)+
  geom_path(aes(x=ST, y=qD0.3, colour="Quorum=0.3"), size=1)+
  geom_errorbar(aes(x=ST, y=qD0.3,xmin=0, xmax=0, ymin=LCL0.3, ymax=UCL0.3, colour="Quorum=0.3"), size = 0.5, width=0.05)+
  geom_point(aes(x=ST, y=qD0.4, colour="Quorum=0.4"), size=2)+
  geom_path(aes(x=ST, y=qD0.4, colour="Quorum=0.4"), size=1)+
  geom_errorbar(aes(x=ST, y=qD0.4,xmin=0, xmax=0, ymin=LCL0.4, ymax=UCL0.4, colour="Quorum=0.4"), size = 0.5, width=0.05)+
  geom_point(aes(x=ST, y=qD0.5, colour="Quorum=0.5"), size=2)+
  geom_path(aes(x=ST, y=qD0.5, colour="Quorum=0.5"), size=1)+
  geom_errorbar(aes(x=ST, y=qD0.5,xmin=0, xmax=0, ymin=LCL0.5, ymax=UCL0.5, colour="Quorum=0.5"), size = 0.5, width=0.05)+
  geom_point(aes(x=ST, y=qD0.6, colour="Quorum=0.6"), size=2)+
  geom_path(aes(x=ST, y=qD0.6, colour="Quorum=0.6"), size=1)+
  geom_errorbar(aes(x=ST, y=qD0.6,xmin=0, xmax=0, ymin=LCL0.6, ymax=UCL0.6, colour="Quorum=0.6"), size = 0.5, width=0.05)+
  geom_point(aes(x=ST, y=qD0.7, colour="Quorum=0.7"), size=2)+
  geom_path(aes(x=ST, y=qD0.7, colour="Quorum=0.7"), size=1)+
  geom_errorbar(aes(x=ST, y=qD0.7,xmin=0, xmax=0, ymin=LCL0.7, ymax=UCL0.7, colour="Quorum=0.7"), size = 0.5, width=0.05)+
  scale_colour_manual(values=c("cornflowerblue", "dark green", "yellow", "orange", "maroon"))+
  theme_bw(base_size=14)+
  theme(legend.title = element_blank())+
  theme(legend.position = c(0.15, 0.8))+
  xlab("Systems tract")+
  ylab("Subsampled diversity")

iNEXT_plot

#save the plot
ggsave("Subsampled_diversity_with_time.png", width = 6, height = 4)


###########################################################################################
#Diversity with latitude
###########################################################################################

GenLat<-select(Genera_with_latitude, accepted_name, lat, abund_value, ST)

#round latitude to 1dp
GenLat<- GenLat %>% mutate_at(2, round, 0)


Abun_Data<-list()

x<-c(35:45)

for (val in x) {
  y<-filter(GenLat, lat==val)
  Abun_Data[[val]]<-y%>%count(accepted_name)
}

#Calculate SQS value at a quorum level of 0.3 with a confidence interval of 0.95 for each degree of latitude
Lat0.3<-list()

for (val in x) {
 Lat0.3[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.3, conf = 0.95)
}

#Repeat for other quorum levels
#0.4
Lat0.4<-list()

for (val in x) {
  Lat0.4[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.4, conf = 0.95)
}

#0.5
Lat0.5<-list()

for (val in x) {
  Lat0.5[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.5, conf = 0.95)
}
 
#0.6
Lat0.6<-list()

for (val in x) {
  Lat0.6[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.6, conf = 0.95)
}

#0.7
Lat0.7<-list()

for (val in x) {
  Lat0.7[[val]]<-estimateD(Abun_Data[[val]]$n, datatype = "abundance", base="coverage", level = 0.7, conf = 0.95)
}


#Extract qD values for each systems tract from Results0.3

q0.3<-vector()

for(val in x){
  
  Lat_matrix<-as.matrix(Lat0.3[[val]])
  q0.3[[val]]<-as.numeric(Lat_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.3

LCL0.3<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.3[[val]])
  LCL0.3[[val]]<-as.numeric(Lat_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.3

UCL0.3<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.3[[val]])
  UCL0.3[[val]]<-as.numeric(Lat_matrix[1, 7])
}

#Make a matrix for plotting data

iNEXT_Lat<-matrix(data = NA, nrow = 45, ncol=16)
iNEXT_Lat[,1]<-q0.3
iNEXT_Lat[,2]<-LCL0.3
iNEXT_Lat[,3]<-UCL0.3
colnames(iNEXT_Lat)<-c("qD0.3", "LCL0.3", "UCL0.3", "qD0.4", "LCL0.4", "UCL0.4", "qD0.5", "LCL0.5", "UCL0.5", "qD0.6", "LCL0.6", "UCL0.6", "qD0.7", "LCL0.7", "UCL0.7", "Deg")


#Repeat for each quorum level

#Extract qD values for each systems tract from Lat0.4

q0.4<-vector()

for(val in x){
  
  Lat_matrix<-as.matrix(Lat0.4[[val]])
  q0.4[[val]]<-as.numeric(Lat_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.4

LCL0.4<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.4[[val]])
  LCL0.4[[val]]<-as.numeric(Lat_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.4

UCL0.4<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.4[[val]])
  UCL0.4[[val]]<-as.numeric(Lat_matrix[1, 7])
}


#Extract qD values for each systems tract from Results0.5

q0.5<-vector()

for(val in x){
  
  Lat_matrix<-as.matrix(Lat0.5[[val]])
  q0.5[[val]]<-as.numeric(Lat_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.5

LCL0.5<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.5[[val]])
  LCL0.5[[val]]<-as.numeric(Lat_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.5

UCL0.5<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.5[[val]])
  UCL0.5[[val]]<-as.numeric(Lat_matrix[1, 7])
}


#Extract qD values for each systems tract from Results0.6

q0.6<-vector()

for(val in x){
  
  Lat_matrix<-as.matrix(Lat0.6[[val]])
  q0.6[[val]]<-as.numeric(Lat_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.6

LCL0.6<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.6[[val]])
  LCL0.6[[val]]<-as.numeric(Lat_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.6

UCL0.6<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.6[[val]])
  UCL0.6[[val]]<-as.numeric(Lat_matrix[1, 7])
}


#Extract qD values for each systems tract from Results0.7

q0.7<-vector()

for(val in x){
  
  Lat_matrix<-as.matrix(Lat0.7[[val]])
  q0.7[[val]]<-as.numeric(Lat_matrix[1, 5])
}

#Extract qD.LCL (lwr conf limit) values for each systems tract from Results0.7

LCL0.7<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.7[[val]])
  LCL0.7[[val]]<-as.numeric(Lat_matrix[1, 6])
}

#Extract qD.UCL (upr conf limit) values for each systems tract from Results0.7

UCL0.7<-vector()

for(val in x){
  Lat_matrix<-as.matrix(Lat0.7[[val]])
  UCL0.7[[val]]<-as.numeric(Lat_matrix[1, 7])
}

#Pop results into the matrix
iNEXT_Lat[,4]<-q0.4
iNEXT_Lat[,5]<-LCL0.4
iNEXT_Lat[,6]<-UCL0.4
iNEXT_Lat[,7]<-q0.5
iNEXT_Lat[,8]<-LCL0.5
iNEXT_Lat[,9]<-UCL0.5
iNEXT_Lat[,10]<-q0.6
iNEXT_Lat[,11]<-LCL0.6
iNEXT_Lat[,12]<-UCL0.6
iNEXT_Lat[,13]<-q0.7
iNEXT_Lat[,14]<-LCL0.7
iNEXT_Lat[,15]<-UCL0.7

#Delete rows 1- 34 in the matrix as there's no data in them

iNEXT_Lat<-iNEXT_Lat[-c(1:34),]

#Put degrees latitude in the final column
iNEXT_Lat[,16]<-x

#Convert to a tibble to save and plot

iNEXT_Lat_Results<-as_tibble(iNEXT_Lat)
write_csv(iNEXT_Lat_Results, file ="iNEXT lat results.csv")

#Plot the results 
iNext_Lat_Plot<-ggplot(iNEXT_Lat_Results)+
  geom_point(aes(x=Deg, y=qD0.3, colour="Quorum=0.3"), size=2)+
  geom_path(aes(x=Deg, y=qD0.3, colour="Quorum=0.3"), size=1)+
  geom_errorbar(aes(x=Deg, y=qD0.3,xmin=0, xmax=0, ymin=LCL0.3, ymax=UCL0.3, colour="Quorum=0.3"), size = 0.5, width=0.1)+
  geom_point(aes(x=Deg, y=qD0.4, colour="Quorum=0.4"), size=2)+
  geom_path(aes(x=Deg, y=qD0.4, colour="Quorum=0.4"), size=1)+
  geom_errorbar(aes(x=Deg, y=qD0.4,xmin=0, xmax=0, ymin=LCL0.4, ymax=UCL0.4, colour="Quorum=0.4"), size = 0.5, width=0.1, position=position_dodge(width=0.5))+
  geom_point(aes(x=Deg, y=qD0.5, colour="Quorum=0.5"), size=2)+
  geom_path(aes(x=Deg, y=qD0.5, colour="Quorum=0.5"), size=1)+
  geom_errorbar(aes(x=Deg, y=qD0.5,xmin=0, xmax=0, ymin=LCL0.5, ymax=UCL0.5, colour="Quorum=0.5"), size = 0.5, width=0.1, position=position_dodge(width=0.5))+
  geom_point(aes(x=Deg, y=qD0.6, colour="Quorum=0.6"), size=2)+
  geom_path(aes(x=Deg, y=qD0.6, colour="Quorum=0.6"), size=1)+
  geom_errorbar(aes(x=Deg, y=qD0.6,xmin=0, xmax=0, ymin=LCL0.6, ymax=UCL0.6, colour="Quorum=0.6"), size = 0.5, width=0.1, position=position_dodge(width=0.5))+
  geom_point(aes(x=Deg, y=qD0.7, colour="Quorum=0.7"), size=2)+
  geom_path(aes(x=Deg, y=qD0.7, colour="Quorum=0.7"), size=1)+
  geom_errorbar(aes(x=Deg, y=qD0.7,xmin=0, xmax=0, ymin=LCL0.7, ymax=UCL0.7, colour="Quorum=0.7"), size = 0.5, width=0.1, position=position_dodge(width=0.5))+
  scale_colour_manual(values=c("cornflowerblue", "maroon4", "seagreen", "orange", "red"))+
  theme_bw(base_size=14)+
  theme(legend.title = element_blank())+
  theme(legend.position = c(0.85, 0.85))+
  xlab("Latitude (degrees north)")+
  ylab("Subsampled diversity")+
  coord_flip()
iNext_Lat_Plot
