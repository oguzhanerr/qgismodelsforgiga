# QGIS model for Giga 

## About ITU

The International Telecommunication Union (ITU) is the United Nations specialized agency for information and communication technologies. ITU is committed to connecting all the world's people – wherever they live and whatever their means. Through our work, we protect and support everyone's right to communicate.

## About Giga

[Giga](https://gigaconnect.org/), an initiative launched by UNICEF and ITU in September 2019 to connect every school to the Internet and every young person to information, opportunity and choice, is supporting the immediate response to COVID19, as well as looking at how connectivity can create stronger infrastructures of hope and opportunity in the "time after COVID."

## About Model

This model runs a series of spatial analyzes to support the understanding of school connectivity and was created with the help of the QGIS graphical modeler. It uses school, telecom infrastructure (fiber nodes, base stations, mobile coverages), and census data as inputs. It provides distance information for each school on possible Internet provisioning options and population statistics with the preset distances around schools.

YO CAN MODİFY THE FİELDS OF İNPUTS İN THE REFACTORİNG STEP
BURAYA ÇIKTILARI TEK TEK AÇIKLAYARAK VE BİR GÖRSEL İLE EKLE!
TÜM FİELDLARI GÖZDEN GEÇİR!


### Dependencies

* QGIS3>=3.0 Girona (available on Windows, macOS, Linux and Android) - [Download Page](https://qgis.org/en/site/forusers/download.html)
* The graphical modeler is built into QGIS, so you don't have to download any other sofware. Further information about graphical modeler can be found [here](https://docs.qgis.org/3.16/en/docs/user_manual/processing/modeler.html).

### Executing Model

* Open QGIS - Click on Processing tab and select Graphical Modeler - Select the folder icon  ![folder](https://svgshare.com/i/_Zw.svg)  and specify where you downloaded the model - Specify the inputs and run by clicking play icon ![play](https://i.ibb.co/dP6B46M/Play.png)

### Inputs  GİRDİ ATTRİBUTELARINI VER

  * Fiber Nodes 
      * Point - vector
      * Unique id = "ID"
  * School Data
      * Point - vector
      * Unique id = "id"
  * Cell Towers
      * Point - vector
      * Model creates auto incremented field and uses it as an id so, you don't need to indicate another for cell tower
  * 2G Mobile Coverage
      * Raster
  * 3G Mobile Coverage
      * Raster
  * 4G Mobile Coverage
      * Raster
  * 5G Mobile Coverage
      * Raster
  * Population
      * Raster

### Be careful!!
  * ...About the projection of the project and inputs!! Model transform the raster inputs from any CRS to EPSG:4326, but you need to transform if the CRS of your vector files different
  * ...If you want to change the buffer zone you need to give the unit in degrees!! It depends upon location on earth. Near the equator, 1 km ≅ 0.008°
  * ...About the unique id of fiber nodes and school data. If they different than the above you need to check each step of the model.
  * ...About the fields and the data type of them if you modify any of the indicator of vector datasets

## License

This project is licensed under the MIT License.
