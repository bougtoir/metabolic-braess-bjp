##Code to plot proprotional data on Morrison dinosaurs ##
## Susie Maidment, Jan 2023 ##


library(tidyverse)

#Import spreadsheet "Occurrence data with STs_ dinos" #

dinos<-select(Occurrence_data_with_STs_dinos, genus, class, Systems_tract)

#use this line if timeslicing. If not, move on
dinos<-filter(dinos, Systems_tract=="6")

#Find number of occurrences of each dinosaur genus
hist<-dinos %>%
  group_by(genus) %>%
  summarise(length(genus))

colnames(hist)[2] = "freq"

hist<-mutate(hist, prop=(freq/sum(freq)))

#Find number of occurrences of each sauropod genus

pods<-dinos %>%
  filter(class == "Sauropoda") %>%
  group_by(genus) %>%
  summarise(length(genus))

colnames(pods) [2] = "freq"

pods<-mutate(pods, prop=(freq/sum(freq)))

#Find number of occurrence of each theropod genus

thero<-dinos%>%
  filter(class == "Theropoda") %>%
  group_by(genus)%>%
  summarise(length(genus))

colnames(thero) [2] = "freq"

thero<-mutate(thero, prop=(freq/sum(freq)))

#Find number of occurrences of each ornithischian genus

ornith<-dinos %>%
  filter(class == "Ornithischia") %>%
  group_by(genus) %>%
  summarise(length(genus))

colnames(ornith) [2] = "freq"

ornith<-mutate(ornith, prop=(freq/sum(freq)))

#Plot data for each one

theroplot<-ggplot(thero, aes(x="", y=prop, fill=genus))+
  geom_bar(width = 1, stat = "identity", colour = "grey")+
  theme_bw(base_size=14)+
  xlab("Theropods")+
  ylab("Proportion")+
  theme(legend.title=element_blank())+
  theme(legend.text=element_text(face = "italic"))
theroplot

podplot<-ggplot(pods, aes(x="", y=prop, fill=genus))+
  geom_bar(width = 1, stat = "identity", colour = "grey")+
  theme_bw(base_size=14)+
  xlab("Sauropods")+
  ylab("Proportion")+
  theme(legend.title=element_blank())+
  theme(legend.text=element_text(face = "italic"))
podplot

ornithplot<-ggplot(ornith, aes(x="", y=prop, fill=genus))+
  geom_bar(width = 1, stat = "identity", colour = "grey")+
  theme_bw(base_size=14)+
  xlab("Ornithischians")+
  ylab("Proportion")+
  theme(legend.title=element_blank())+
  theme(legend.text=element_text(face = "italic"))
ornithplot

#Plot next to each otehr

library(patchwork)  
podplot+theroplot+ornithplot


