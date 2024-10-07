wits<-read.csv("extra-data/wits-tariffs/DataJobID-2702382_2702382_2018ISIC.csv")

#is it balanced panel?
length(levels(factor(wits$Reporter.Name)))*length(levels(factor(wits$Partner.Name)))*length(levels(factor(wits$Product.Name)))
#no

#merge in sectors
concordance<-read.csv("extra-data/manual-correspondance.csv")
concordance$ourcat[concordance$ourcat=="3"]<-"03"
names(concordance)<-c("sector", "sectorname", "Product")

library(dplyr)
wits<-left_join(wits, concordance, by="Product")

#merge in countries
library(countrycode)
wits$row_country<-countrycode(wits$Partner.Name, "country.name", "iso3c")
#Partner has EU countries
wits$col_country<-countrycode(wits$Reporter.Name, "country.name", "iso3c")
#EU not matched - what to do with it?

#ADJUST ROW
ROWcountries<-c("Albania","Angola","Armenia","Bahrain","Bangladesh","Barbados",
                  "Belize","Benin","Bolivia","Botswana","Burkina Faso","Burundi",
                  "Cameroon","Cape Verde","Central African Republic","Chad",
                  "Comoros","Congo, Dem. Rep.","Congo, Rep.",
                  "Cote d'Ivoire","Cuba","Dominican Republic",
                  "Ecuador","Egypt, Arab Rep.","El Salvador","Eswatini",
                  "European Union","Fiji","Gabon","Gambia, The","Georgia","Ghana","Guatemala","Guinea",
                  "Guinea-Bissau","Guyana","Haiti","Honduras",
                  "Jordan","Kenya","Kyrgyz Republic","Lesotho","Liberia","Macao","Madagascar","Malaysia","Maldives",
                  "Mali","Mauritania","Mauritius","Moldova","Mongolia","Montenegro","Mozambique",         
                  "Namibia","Nepal","Nicaragua","Niger","Nigeria","North Macedonia",
                  "Oman","Pakistan","Panama","Papua New Guinea",
                  "Paraguay","Qatar","Rwanda","Samoa",
                  "Senegal","Seychelles","Sierra Leone","St. Lucia","St. Vincent and the Grenadines","Suriname",
                  "Tajikistan","Tanzania","Togo","Tonga","Trinidad and Tobago",
                  "Uganda","Ukraine","United Arab Emirates","Uruguay","Vanuatu","Zimbabwe")

wits$col_country<-ifelse(wits$Reporter.Name %in% ROWcountries,"ROW",
                         wits$col_country)
wits$row_country<-ifelse(wits$Partner.Name %in% ROWcountries,"ROW",
                         wits$row_country)

wits2<-wits %>% group_by(sector, sectorname, row_country, col_country) %>% 
  summarise(tariff=mean(Weighted.Average, na.rm = T))

length(levels(factor(wits$row_country)))*length(levels(factor(wits$col_country)))*length(levels(factor(wits$sector)))

eu<-wits[wits$Reporter.Name=="European Union",]
#replicate this for each EU country, then append to wits
eu$col_country<-NA
e<-data.frame()
eucountries<-c('AUT', 'BEL', 'CYP','BGR','CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 
               'GRC', 'HRV', 'HUN', 'IRL', 'ITA', 'LTU', 'LVA', 'MLT', 'NLD', 'POL', 'PRT', 
               'ROU', 'SVK', 'SVN', 'SWE') #one or two missing

for (country in eucountries) {
  a<-eu
  a$col_country<-country
  e<-rbind(e,a)
}

eu2<-left_join(e, concordance, by=c("Product", "sector", "sectorname"))
# eu2<-e[("sector", "sectorname", "row_country", "col_country", "tariff"))

eu2<-eu2 %>% group_by(sector, sectorname, row_country, col_country) %>% 
  summarise(tariff=mean(Weighted.Average, na.rm = T))

witseu<-rbind(wits2, eu2)
length(levels(factor(witseu$sector)))*length(levels(factor(witseu$row_country)))*length(levels(factor(witseu$col_country)))
#there are no services sectors
#row_country and col_country have quite different numbers

#Now merge in our countries
ourdata<-read.csv("data/yearly_CSV_agg_treated/datas2018/consumption_2018.csv")
ourdata$value<-NULL
names(ourdata)<-c("row_country", "sector", "col_country")
ourdata<-left_join(ourdata, witseu, by=c("sector", "row_country", "col_country"))
summary(ourdata$tariff)
ourdata$tariff[is.na(ourdata$tariff)]<-0
ourdata$tariff<-ourdata$tariff/100 #originially, this is in percentage points

ourdata$sectorname<-NULL
names(ourdata)<-c("row_country",
                  "row_sector",
                  "col_country",
                  "tariff" )
write.csv(ourdata, "extra-data/tariffs2018.csv", row.names = F)

#are NAs now only in services sector?
natariffs<-ourdata[is.na(ourdata$tariff),]
#not only services sectors, but also.