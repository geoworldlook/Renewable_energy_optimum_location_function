#1
processing.run("gdal:polygonize"
               , {'INPUT':'D:/GEOWORLDLOOK/OZE/PILOT/PRZYCIETE_PILOT_SURFACE_RADIATION_1991_2020/MAPA_STYCZEN_PRZYCIETE.tif'
                   ,'BAND':1,'FIELD':'Solar_surface_radiation_[Wm2]'
                   ,'EIGHT_CONNECTEDNESS':False
                   ,'EXTRA':''
                   ,'OUTPUT':'D:/GEOWORLDLOOK/OZE/PILOT/Step_3_solar_radiation/solar_radiation_vector_january.shp'})