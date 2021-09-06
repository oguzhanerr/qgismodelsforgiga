# QGIS model for Giga 

## About ITU

The International Telecommunication Union (ITU) is the United Nations specialized agency for information and communication technologies. ITU is committed to connecting all the world's people – wherever they live and whatever their means. Through our work, we protect and support everyone's right to communicate.

## About Giga

[Giga](https://gigaconnect.org/), an initiative launched by UNICEF and ITU in September 2019 to connect every school to the Internet and every young person to information, opportunity and choice, is supporting the immediate response to COVID19, as well as looking at how connectivity can create stronger infrastructures of hope and opportunity in the "time after COVID."

### Dependencies

* QGIS3>=3.0 Girona (available on Windows, macOS, Linux and Android) - [Download Page](https://qgis.org/en/site/forusers/download.html)
* The graphical modeler is built into QGIS, so you don't have to download other software. Further information about graphical modeler can be found [here](https://docs.qgis.org/3.16/en/docs/user_manual/processing/modeler.html).

### Executing Models

* Open QGIS - Click on Processing tab and select Graphical Modeler - Select the folder icon  ![folder](https://svgshare.com/i/_Zw.svg)  and indicate where you downloaded the model - Specify the inputs and run by clicking play icon ![play](https://i.ibb.co/dP6B46M/Play.png)

## About School Connectivity Model

This model ran a series of spatial analyzes to support the understanding of school connectivity and was created with the help of the QGIS graphical modeler. It uses school, telecom infrastructure (fiber nodes, base stations, mobile coverages), and census data as inputs. It provides distance information for each school on possible Internet provisioning options and population statistics with the preset distances around schools.

### Inputs

 
| Input        | Type   | Comment  |
| ------------ | ------ | ------------ |
| Fiber Nodes  | vector | point data, unique id = "ID"  |
| School Data  | vector | point data, unique id = "id"  |
| Cell Towers  | vector | point data, model creates auto incremented field and uses it as an id so, no need to indicate another.  |
| 2G Coverage  | raster | -  |
| 3G Coverage  | raster | -  |
| 4G Coverage  | raster | -  |
| 5G Coverage  | raster | -  |
| Population   | raster | -  |

### Be careful!!
  * ...about the CRS (Coordinate Reference System) of the project and inputs!! Model transform the raster inputs from any CRS to EPSG:4326, but you need to transform if the CRS of your vector files different
  * ...if you want to change the buffer zone, you need to give the unit in degrees!! It depends upon the location on earth. Near the equator, 1 km ≅ 0.008°
  * ...about the unique id of fiber nodes and school data. If they are different than the above, you need to check each step of the model.
  * ...about the fields and the data type of them if you modify any of the indicator of vector datasets
  * ...that, there are two school connectivity models available. One is based on school data collected by the Giga team ("schoolconnectivitygiga.model3"), and the other based on data from OpenStreetMap ("schoolconnectivityosm.model3").


### Output

The model creates a new vector point data based on the school input and adds the analyzes as new columns to the attributes table;

| Attribute               | Description  |
| ----------------------- | ------------ | 
| fiber_node_distance     |  the distance of each school to the nearest fiber node in km |
| nearest_school_distance   | the distance of each school to the nearest school node in km  |
| Schools_within_1km   | number of schools in a circle with a radius of one km centering a school point  |
| Schools_within_3km   | number of schools in a circle with a radius of three km centering a school point  |
| Schools_within_10km   | number of schools in a circle with a radius of ten km centering a school point  |
| nearest_LTE_id   | unique id automatically assigned to each base station by the model  |
| nearest_LTE_distance   |  the distance of each school to the nearest LTE cell tower node in km |
| nearest_UMTS_id   | unique id automatically assigned to each base station by the model  |
| nearest_UMTS_distance   | the distance of each school to the nearest UMTS cell tower node in km  |
| nearest_GSM_id   |  unique id automatically assigned to each base station by the model |
| nearest_GSM_distance   |  the distance of each school to the nearest GSM cell tower node in km |
| 2G   | Returns a boolean result based on the condition that the school point stays within the 2G coverage raster image; "0"=no, "1"=strong "2"=variable |
| 3G   | Returns a boolean result based on the condition that the school point stays within the 3G coverage raster image; "0"=no, "1"=strong "2"=variable |
| 4G   | Returns a boolean result based on the condition that the school point stays within the 4G coverage raster image; "0"=no, "1"=strong "2"=variable |
| pop_within_1km   | number of total population in a circle with a radius of one km centering a school point  |
| pop_within_3km   | number of total population in a circle with a radius of three km centering a school point  |
| pop_within_7km   | number of total population in a circle with a radius of seven km centering a school point  |
																

## License

This project is licensed under the MIT License.
