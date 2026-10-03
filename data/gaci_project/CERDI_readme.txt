

Database updates CERDI-seadistance_V1.1 

Selected distance choice

Version 1.1 selects the distance between two ports calculated from the projection whose Prime Meridian is closer to the longitude of the mid-point between the two ports. This choice ensures that we minimize the distortion produced by the projection. Version 1.0 was retaining the shortest distance, which was not necessarily the least distorted.
 
 
Countries 'unlandlocked' via Russia
 
Armenia and Azerbaijan are two landlocked countries whose relevant port is in Russia (more precisely, the Russian west port). This port is always retained in Version 1.1 to compute the distance between Russia and all other countries in the world that are relevant for Armenia and Azerbaijan, i.e., we do not use the Russian Eastern port, as we do when computing a part of the sea distances for Russia and as we did in Version 1.0 also for Armenia and Azerbaijan.

 
References
Bertoli S., M. Goujon and O. Santoni (2016), “The CERDI-seadistance database”, Working Paper, No. 2016/7, CERDI. 

Corresponding author: Olivier Santoni - olivier.santoni@ferdi.fr
