"""
Model exported as python.
Name : School2Fiber & School2School & School2CellTower & School2MobileCoverage & Population Stats Model
Group : 
With QGIS : 32000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class School2fiberSchool2schoolSchool2celltowerSchool2mobilecoveragePopulationStatsModel(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('School', 'School Data', optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('CellTowers', 'Cell Towers', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Nodes', 'Fiber Nodes', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('PopulationRaster', 'Population', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('2G', '2G Mobile Coverage', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('2G (2)', '3G Mobile Coverage', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('2G (3)', '4G Mobile Coverage', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('2G (4)', '5G Mobile Coverage', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFileDestination('OutputXlsx', 'output (xlsx)', fileFilter='Microsoft Excel (*.xlsx);;Open Document Spreadsheet (*.ods)', createByDefault=True, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('_school_processed', '_school_processed', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(37, model_feedback)
        results = {}
        outputs = {}

        # Add autoincremental field
        alg_params = {
            'FIELD_NAME': 'HubName',
            'GROUP_FIELDS': [''],
            'INPUT': parameters['CellTowers'],
            'SORT_ASCENDING': True,
            'SORT_EXPRESSION': '',
            'SORT_NULLS_FIRST': False,
            'START': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddAutoincrementalField'] = processing.run('native:addautoincrementalfield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Distance to nearest fiber(km)
        alg_params = {
            'FIELD': 'ID',
            'HUBS': parameters['Nodes'],
            'INPUT': parameters['School'],
            'UNIT': 3,  # Kilometers
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestFiberkm'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Join fiber distance attributes by unique id to school dataset
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['HubDist'],
            'FIELD_2': 'id',
            'INPUT': parameters['School'],
            'INPUT_2': outputs['DistanceToNearestFiberkm']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'fiber_node_distance',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinFiberDistanceAttributesByUniqueIdToSchoolDataset'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Create spatial index (celltower)
        alg_params = {
            'INPUT': outputs['AddAutoincrementalField']['OUTPUT']
        }
        outputs['CreateSpatialIndexCelltower'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Distance to nearest school by unique id (m)
        alg_params = {
            'INPUT': outputs['JoinFiberDistanceAttributesByUniqueIdToSchoolDataset']['OUTPUT'],
            'INPUT_FIELD': 'id',
            'MATRIX_TYPE': 0,  # Linear (N*k x 3) distance matrix
            'NEAREST_POINTS': 1,
            'TARGET': outputs['JoinFiberDistanceAttributesByUniqueIdToSchoolDataset']['OUTPUT'],
            'TARGET_FIELD': 'id',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestSchoolByUniqueIdM'] = processing.run('qgis:distancematrix', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Refactor fields (id data type)
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"radio\"','length': 0,'name': 'radio','precision': 0,'type': 10},{'expression': '\"mcc\"','length': 0,'name': 'mcc','precision': 0,'type': 2},{'expression': '\"net\"','length': 0,'name': 'net','precision': 0,'type': 2},{'expression': '\"area\"','length': 0,'name': 'area','precision': 0,'type': 2},{'expression': '\"cell\"','length': 0,'name': 'cell','precision': 0,'type': 2},{'expression': '\"unit\"','length': 0,'name': 'unit','precision': 0,'type': 2},{'expression': '\"lon\"','length': 0,'name': 'lon','precision': 0,'type': 6},{'expression': '\"lat\"','length': 0,'name': 'lat','precision': 0,'type': 6},{'expression': '\"range\"','length': 0,'name': 'range','precision': 0,'type': 2},{'expression': '\"samples\"','length': 0,'name': 'samples','precision': 0,'type': 2},{'expression': '\"changeable\"','length': 0,'name': 'changeable','precision': 0,'type': 2},{'expression': '\"created\"','length': 0,'name': 'created','precision': 0,'type': 2},{'expression': '\"updated\"','length': 0,'name': 'updated','precision': 0,'type': 2},{'expression': '\"averageSignal\"','length': 0,'name': 'averageSignal','precision': 0,'type': 2},{'expression': '\"HubName\"','length': 0,'name': 'HubName','precision': 0,'type': 10}],
            'INPUT': outputs['CreateSpatialIndexCelltower']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorFieldsIdDataType'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by cell tower type (UMTS)
        alg_params = {
            'FIELD': 'radio',
            'INPUT': outputs['RefactorFieldsIdDataType']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': 'UMTS',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByCellTowerTypeUmts'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract by cell tower type (LTE)
        alg_params = {
            'FIELD': 'radio',
            'INPUT': outputs['RefactorFieldsIdDataType']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': 'LTE',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByCellTowerTypeLte'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Distance',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '\"Distance\" / 1000',
            'INPUT': outputs['DistanceToNearestSchoolByUniqueIdM']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Extract by cell tower type (GSM)
        alg_params = {
            'FIELD': 'radio',
            'INPUT': outputs['RefactorFieldsIdDataType']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': 'GSM',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByCellTowerTypeGsm'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Join school distances to school dataset by unique id
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Distance'],
            'FIELD_2': 'InputID',
            'INPUT': outputs['JoinFiberDistanceAttributesByUniqueIdToSchoolDataset']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculator']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'nearest_school_distance',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinSchoolDistancesToSchoolDatasetByUniqueId'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Create spatial index (school data)
        alg_params = {
            'INPUT': outputs['JoinSchoolDistancesToSchoolDatasetByUniqueId']['OUTPUT']
        }
        outputs['CreateSpatialIndexSchoolData'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # 10km buffer (school data)
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.09,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBufferSchoolData'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Count schools in 10km distance
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'Schools within 10km',
            'POINTS': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'POLYGONS': outputs['KmBufferSchoolData']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountSchoolsIn10kmDistance'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # 7km buffer (school data)
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.063,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBufferSchoolData'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # 1km buffer (school data)
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.009,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBufferSchoolData'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # 3km buffer (school data)
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.027,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBufferSchoolData'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Count schools in 1km distance
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'Schools within 1km',
            'POINTS': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'POLYGONS': outputs['KmBufferSchoolData']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountSchoolsIn1kmDistance'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Count schools in 3km distance
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'Schools within 3km',
            'POINTS': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'POLYGONS': outputs['KmBufferSchoolData']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountSchoolsIn3kmDistance'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Join 1km distanced schools as a column by specifying unique id
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Schools within 1km'],
            'FIELD_2': 'id',
            'INPUT': outputs['CreateSpatialIndexSchoolData']['OUTPUT'],
            'INPUT_2': outputs['CountSchoolsIn1kmDistance']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Join1kmDistancedSchoolsAsAColumnBySpecifyingUniqueId'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Join 3km distanced schools as a column by specifying unique id
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Schools within 3km'],
            'FIELD_2': 'id',
            'INPUT': outputs['Join1kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'INPUT_2': outputs['CountSchoolsIn3kmDistance']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Join3kmDistancedSchoolsAsAColumnBySpecifyingUniqueId'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Join 10km distanced schools as a column by specifying unique id
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Schools within 10km'],
            'FIELD_2': 'id',
            'INPUT': outputs['Join3kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'INPUT_2': outputs['CountSchoolsIn10kmDistance']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Join10kmDistancedSchoolsAsAColumnBySpecifyingUniqueId'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Distance2nearestCelltower GSM (km)
        alg_params = {
            'FIELD': 'HubName',
            'HUBS': outputs['ExtractByCellTowerTypeGsm']['OUTPUT'],
            'INPUT': outputs['Join10kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'UNIT': 3,  # Kilometers
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Distance2nearestcelltowerGsmKm'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Distance2nearestCelltower UMTS (km)
        alg_params = {
            'FIELD': 'HubName',
            'HUBS': outputs['ExtractByCellTowerTypeUmts']['OUTPUT'],
            'INPUT': outputs['Join10kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'UNIT': 3,  # Kilometers
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Distance2nearestcelltowerUmtsKm'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Distance2nearestCelltower LTE (km)
        alg_params = {
            'FIELD': 'HubName',
            'HUBS': outputs['ExtractByCellTowerTypeLte']['OUTPUT'],
            'INPUT': outputs['Join10kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'UNIT': 3,  # Kilometers
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Distance2nearestcelltowerLteKm'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Join LTE celltower distance attributes by school_id records to school dataset
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'giga_schoo',
            'FIELDS_TO_COPY': ['HubName','HubDist'],
            'FIELD_2': 'giga_schoo',
            'INPUT': outputs['Join10kmDistancedSchoolsAsAColumnBySpecifyingUniqueId']['OUTPUT'],
            'INPUT_2': outputs['Distance2nearestcelltowerLteKm']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinLteCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Join UMTS celltower distance attributes by school_id records to school dataset
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'giga_schoo',
            'FIELDS_TO_COPY': ['HubName','HubDist'],
            'FIELD_2': 'giga_schoo',
            'INPUT': outputs['JoinLteCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset']['OUTPUT'],
            'INPUT_2': outputs['Distance2nearestcelltowerUmtsKm']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinUmtsCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Join GSM celltower distance attributes by school_id records to school dataset
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'giga_schoo',
            'FIELDS_TO_COPY': ['HubName','HubDist'],
            'FIELD_2': 'giga_schoo',
            'INPUT': outputs['JoinUmtsCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset']['OUTPUT'],
            'INPUT_2': outputs['Distance2nearestcelltowerGsmKm']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinGsmCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Refactor fields (Celltower)
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"uuid\"','length': 254,'name': 'uuid','precision': 0,'type': 10},{'expression': '\"country\"','length': 254,'name': 'country','precision': 0,'type': 10},{'expression': '\"source\"','length': 254,'name': 'source','precision': 0,'type': 10},{'expression': '\"giga_schoo\"','length': 254,'name': 'giga_school_id','precision': 0,'type': 10},{'expression': '\"source_sch\"','length': 50,'name': 'source_school_id','precision': 0,'type': 4},{'expression': '\"school_nam\"','length': 254,'name': 'school_name','precision': 0,'type': 10},{'expression': '\"latitude\"','length': 23,'name': 'latitude','precision': 15,'type': 6},{'expression': '\"longitude\"','length': 23,'name': 'longitude','precision': 15,'type': 6},{'expression': '\"hex8\"','length': 254,'name': 'hex8','precision': 0,'type': 10},{'expression': '\"source_tim\"','length': 35,'name': 'source_timestamp','precision': 0,'type': 10},{'expression': '\"master_tim\"','length': 254,'name': 'master_timestamp','precision': 0,'type': 6},{'expression': '\"school_arc\"','length': 254,'name': 'school_archive','precision': 0,'type': 10},{'expression': '\"district_c\"','length': 254,'name': 'district_code','precision': 0,'type': 4},{'expression': '\"student_co\"','length': 10,'name': 'student_count','precision': 0,'type': 4},{'expression': '\"computer_a\"','length': 10,'name': 'computer_availability','precision': 0,'type': 10},{'expression': '\"school_typ\"','length': 254,'name': 'school_type','precision': 0,'type': 10},{'expression': '\"school_reg\"','length': 254,'name': 'school_region','precision': 0,'type': 10},{'expression': '\"internet_a\"','length': 254,'name': 'internet_availability','precision': 0,'type': 10},{'expression': '\"internet_s\"','length': 0,'name': 'internet_speed','precision': 0,'type': 2},{'expression': '\"fiber_node_distanceHubDist\"','length': 0,'name': 'fiber_node_distanceHubDist','precision': 0,'type': 6},{'expression': '\"nearest_school_distanceDistance\"','length': 0,'name': 'nearest_school_distanceDistance','precision': 0,'type': 6},{'expression': '\"Schools within 1km\"','length': 0,'name': 'Schools within 1km','precision': 0,'type': 6},{'expression': '\"Schools within 3km\"','length': 0,'name': 'Schools within 3km','precision': 0,'type': 6},{'expression': '\"Schools within 10km\"','length': 0,'name': 'Schools within 10km','precision': 0,'type': 6},{'expression': '\"HubName\"','length': 0,'name': 'nearest_LTE_id','precision': 0,'type': 10},{'expression': '\"HubDist\"','length': 0,'name': 'nearest_LTE_distance','precision': 0,'type': 6},{'expression': '\"HubName_2\"','length': 0,'name': 'nearest_UMTS_id','precision': 0,'type': 10},{'expression': '\"HubDist_2\"','length': 0,'name': 'nearest_UMTS_distance','precision': 0,'type': 6},{'expression': '\"HubName_3\"','length': 0,'name': 'nearest_GSM_id','precision': 0,'type': 10},{'expression': '\"HubDist_3\"','length': 0,'name': 'nearest_GSM_distance','precision': 0,'type': 6}],
            'INPUT': outputs['JoinGsmCelltowerDistanceAttributesBySchool_idRecordsToSchoolDataset']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorFieldsCelltower'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Sampling for 2G
        alg_params = {
            'COLUMN_PREFIX': '2G',
            'INPUT': outputs['RefactorFieldsCelltower']['OUTPUT'],
            'RASTERCOPY': parameters['2G'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SamplingFor2g'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Reproject 2G (crs:4326)
        alg_params = {
            'INPUT': outputs['SamplingFor2g']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Reproject2gCrs4326'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(31)
        if feedback.isCanceled():
            return {}

        # Sampling for 3G
        alg_params = {
            'COLUMN_PREFIX': '3G',
            'INPUT': outputs['Reproject2gCrs4326']['OUTPUT'],
            'RASTERCOPY': parameters['2G (2)'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SamplingFor3g'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(32)
        if feedback.isCanceled():
            return {}

        # Reproject 3G (crs:4326)
        alg_params = {
            'INPUT': outputs['SamplingFor3g']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Reproject3gCrs4326'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(33)
        if feedback.isCanceled():
            return {}

        # Sampling for 4G
        alg_params = {
            'COLUMN_PREFIX': '4G',
            'INPUT': outputs['Reproject3gCrs4326']['OUTPUT'],
            'RASTERCOPY': parameters['2G (3)'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SamplingFor4g'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(34)
        if feedback.isCanceled():
            return {}

        # Reproject 4G (crs:4326)
        alg_params = {
            'INPUT': outputs['SamplingFor4g']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Reproject4gCrs4326'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(35)
        if feedback.isCanceled():
            return {}

        # Refactor fields last
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"uuid\"','length': 254,'name': 'uuid','precision': 0,'type': 10},{'expression': '\"country\"','length': 254,'name': 'country','precision': 0,'type': 10},{'expression': '\"source\"','length': 254,'name': 'source','precision': 0,'type': 10},{'expression': '\"giga_school_id\"','length': 254,'name': 'giga_school_id','precision': 0,'type': 10},{'expression': '\"source_school_id\"','length': 50,'name': 'source_school_id','precision': 0,'type': 4},{'expression': '\"school_name\"','length': 254,'name': 'school_name','precision': 0,'type': 10},{'expression': '\"latitude\"','length': 23,'name': 'latitude','precision': 15,'type': 6},{'expression': '\"longitude\"','length': 23,'name': 'longitude','precision': 15,'type': 6},{'expression': '\"hex8\"','length': 254,'name': 'hex8','precision': 0,'type': 10},{'expression': '\"source_timestamp\"','length': 35,'name': 'source_timestamp','precision': 0,'type': 10},{'expression': '\"master_timestamp\"','length': 254,'name': 'master_timestamp','precision': 0,'type': 6},{'expression': '\"school_archive\"','length': 254,'name': 'school_archive','precision': 0,'type': 10},{'expression': '\"district_code\"','length': 254,'name': 'district_code','precision': 0,'type': 4},{'expression': '\"student_count\"','length': 10,'name': 'student_count','precision': 0,'type': 4},{'expression': '\"computer_availability\"','length': 10,'name': 'computer_availability','precision': 0,'type': 10},{'expression': '\"school_type\"','length': 254,'name': 'school_type','precision': 0,'type': 10},{'expression': '\"school_region\"','length': 254,'name': 'school_region','precision': 0,'type': 10},{'expression': '\"internet_availability\"','length': 254,'name': 'internet_availability','precision': 0,'type': 10},{'expression': '\"internet_speed\"','length': 0,'name': 'internet_speed','precision': 0,'type': 2},{'expression': '\"fiber_node_distanceHubDist\"','length': 0,'name': 'fiber_node_distance','precision': 0,'type': 6},{'expression': '\"nearest_school_distanceDistance\"','length': 0,'name': 'nearest_school_distance','precision': 0,'type': 6},{'expression': '\"Schools within 1km\"','length': 0,'name': 'Schools_within_1km','precision': 0,'type': 6},{'expression': '\"Schools within 3km\"','length': 0,'name': 'Schools_within_3km','precision': 0,'type': 6},{'expression': '\"Schools within 10km\"','length': 0,'name': 'Schools_within_10km','precision': 0,'type': 6},{'expression': '\"nearest_LTE_id\"','length': 0,'name': 'nearest_LTE_id','precision': 0,'type': 10},{'expression': '\"nearest_LTE_distance\"','length': 0,'name': 'nearest_LTE_distance','precision': 0,'type': 6},{'expression': '\"nearest_UMTS_id\"','length': 0,'name': 'nearest_UMTS_id','precision': 0,'type': 10},{'expression': '\"nearest_UMTS_distance\"','length': 0,'name': 'nearest_UMTS_distance','precision': 0,'type': 6},{'expression': '\"nearest_GSM_id\"','length': 0,'name': 'nearest_GSM_id','precision': 0,'type': 10},{'expression': '\"nearest_GSM_distance\"','length': 0,'name': 'nearest_GSM_distance','precision': 0,'type': 6},{'expression': 'if(\"2G1\" is null, 0, \"2G1\")','length': 0,'name': '2G','precision': 0,'type': 2},{'expression': 'if(\"3G1\" is null, 0, \"3G1\")','length': 0,'name': '3G','precision': 0,'type': 2},{'expression': 'if(\"4G1\" is null, 0, \"4G1\")','length': 0,'name': '4G','precision': 0,'type': 2},{'expression': '\"pop within 1kmsum\"','length': 0,'name': 'pop_within_1km','precision': 0,'type': 4},{'expression': '\"pop within 3kmsum\"','length': 0,'name': 'pop_within_3km','precision': 0,'type': 4},{'expression': '\"pop within 7kmsum\"','length': 0,'name': 'pop_within_7km','precision': 0,'type': 4}],
            'INPUT': outputs['Reproject4gCrs4326']['OUTPUT'],
            'OUTPUT': parameters['_school_processed']
        }
        outputs['RefactorFieldsLast'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['_school_processed'] = outputs['RefactorFieldsLast']['OUTPUT']

        feedback.setCurrentStep(36)
        if feedback.isCanceled():
            return {}

        # Export to spreadsheet
        alg_params = {
            'FORMATTED_VALUES': False,
            'LAYERS': outputs['RefactorFieldsLast']['OUTPUT'],
            'OVERWRITE': True,
            'USE_ALIAS': False,
            'OUTPUT': parameters['OutputXlsx']
        }
        outputs['ExportToSpreadsheet'] = processing.run('native:exporttospreadsheet', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OutputXlsx'] = outputs['ExportToSpreadsheet']['OUTPUT']
        return results

    def name(self):
        return 'School2Fiber & School2School & School2CellTower & School2MobileCoverage & Population Stats Model'

    def displayName(self):
        return 'School2Fiber & School2School & School2CellTower & School2MobileCoverage & Population Stats Model'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return School2fiberSchool2schoolSchool2celltowerSchool2mobilecoveragePopulationStatsModel()
