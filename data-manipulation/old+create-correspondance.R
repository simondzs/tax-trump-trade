correspondance<-read.delim("extra-data/ISIC31_ISIC4.txt", sep = ",",
                           colClasses = "character")
correspondance$isic3short<-substr(correspondance$ISIC31code, 1, 2)
correspondance$isic4short<-substr(correspondance$ISIC4code, 1, 2)

#a lot of subcategories are under different headings..

# our categories
d<-read.csv("data/yearly_CSV_agg_treated/datas2018/co2_intensity_prod_2018.csv")
ourcat<-unique(d$sector)
ournames<-c('Agriculture', 'Fishing', 'Mining, energy', 'Mining, non-energy', 
'Food products', 'Textiles', 'Wood','Paper', 'Coke, petroleum', 
'Chemicals', 'Pharmaceuticals', 'Plastics', 'Non-metallic minerals', 
'Basic metals', 'Fabricated metals', 'Electronics','Electrical equipment',
'Machinery', 'Transport equipment', 'Manufacturing nec', 'Energy', 
'Water supply', 'Construction','Wholesale, retail', 'Land transport', 
'Water transport', 'Air transport', 'Warehousing', 'Post', 'Tourism', 
'Media', 'Telecom', 'IT', 'Finance, insurance', 'Real estate', 'R&D',
'Administration', 'Public sector', 'Education', 'Health',
'Entertainment', 'Other service')
o<-data.frame(ourcat, ournames)
#easier to map wits categories to ourcat
wits<-read.csv("extra-data/wits-tariffs/DataJobID-2702358_2702358_2018ISIC.csv")
witscatname<-unique(wits$Product.Name)
witscat<-unique(wits$Product)
w<-data.frame(witscat, witscatname)
