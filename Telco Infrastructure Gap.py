"""
Model exported as python.
Name : Telco Infrastructure Gap
Group : 
With QGIS : 32000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class TelcoInfrastructureGap(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('4GCoverageRaster (2)', '2G Coverage (Raster)', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('4GCoverageRaster (2) (2)', '3G Coverage (Raster)', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('4GCoverageRaster', '4G Coverage (Raster)', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Admin0Vector', 'Admin0 (Vector)', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('FinerNodes', 'Fiber Nodes (Vector)', optional=True, types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('PopulationRaster', 'Population (Raster)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('GCoveredPopulationStatistics', '4G covered population statistics', type=QgsProcessing.TypeVector, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('GCoveredPopulationStatistics', '3G covered population statistics', type=QgsProcessing.TypeVector, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('GCoveredPopulationStatistics', '2G covered population statistics', type=QgsProcessing.TypeVector, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Fiberaway10', 'Fiberaway10', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Fiberaway25', 'Fiberaway25', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(16, model_feedback)
        results = {}
        outputs = {}

        # 3G (reproject)
        alg_params = {
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': parameters['4GCoverageRaster (2) (2)'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'RESAMPLING': 0,  # Nearest Neighbour
            'SOURCE_CRS': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GReproject'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 2G (reproject)
        alg_params = {
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': parameters['4GCoverageRaster (2)'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'RESAMPLING': 0,  # Nearest Neighbour
            'SOURCE_CRS': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GReproject'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 2G Coverage statistics
        alg_params = {
            'BAND': 1,
            'INPUT': parameters['PopulationRaster'],
            'REF_LAYER': 0,  # Input layer
            'ZONES': outputs['GReproject']['OUTPUT'],
            'ZONES_BAND': 1,
            'OUTPUT_TABLE': parameters['GCoveredPopulationStatistics']
        }
        outputs['GCoverageStatistics'] = processing.run('native:rasterlayerzonalstats', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['GCoveredPopulationStatistics'] = outputs['GCoverageStatistics']['OUTPUT_TABLE']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 10 km Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.09,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['FinerNodes'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBuffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 4G (reproject)
        alg_params = {
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': parameters['4GCoverageRaster'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'RESAMPLING': 0,  # Nearest Neighbour
            'SOURCE_CRS': None,
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'TARGET_EXTENT': None,
            'TARGET_EXTENT_CRS': None,
            'TARGET_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GReproject'] = processing.run('gdal:warpreproject', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 25 km Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 0.225,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['FinerNodes'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmBuffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 3G Coverage statistics
        alg_params = {
            'BAND': 1,
            'INPUT': parameters['PopulationRaster'],
            'REF_LAYER': 0,  # Input layer
            'ZONES': outputs['GReproject']['OUTPUT'],
            'ZONES_BAND': 1,
            'OUTPUT_TABLE': parameters['GCoveredPopulationStatistics']
        }
        outputs['GCoverageStatistics'] = processing.run('native:rasterlayerzonalstats', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['GCoveredPopulationStatistics'] = outputs['GCoverageStatistics']['OUTPUT_TABLE']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 10km Dissolve
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['KmBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmDissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # 4G Coverage statistics
        alg_params = {
            'BAND': 1,
            'INPUT': parameters['PopulationRaster'],
            'REF_LAYER': 0,  # Input layer
            'ZONES': outputs['GReproject']['OUTPUT'],
            'ZONES_BAND': 1,
            'OUTPUT_TABLE': parameters['GCoveredPopulationStatistics']
        }
        outputs['GCoverageStatistics'] = processing.run('native:rasterlayerzonalstats', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['GCoveredPopulationStatistics'] = outputs['GCoverageStatistics']['OUTPUT_TABLE']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # 25km Dissolve
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['KmBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmDissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # 10 km Difference
        alg_params = {
            'INPUT': parameters['Admin0Vector'],
            'OVERLAY': outputs['KmDissolve']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmDifference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # 25 km Difference
        alg_params = {
            'INPUT': parameters['Admin0Vector'],
            'OVERLAY': outputs['KmDissolve']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmDifference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Fix geometries 25km
        alg_params = {
            'INPUT': outputs['KmDifference']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries25km'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Fix geometries 10km
        alg_params = {
            'INPUT': outputs['KmDifference']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries10km'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Zonal statistics 25km
        alg_params = {
            'COLUMN_PREFIX': 'f25_',
            'INPUT': outputs['FixGeometries25km']['OUTPUT'],
            'INPUT_RASTER': parameters['PopulationRaster'],
            'RASTER_BAND': 1,
            'STATISTICS': [1,4],  # Sum,St dev
            'OUTPUT': parameters['Fiberaway25']
        }
        outputs['ZonalStatistics25km'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Fiberaway25'] = outputs['ZonalStatistics25km']['OUTPUT']

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Zonal statistics 10km
        alg_params = {
            'COLUMN_PREFIX': 'f10_',
            'INPUT': outputs['FixGeometries10km']['OUTPUT'],
            'INPUT_RASTER': parameters['PopulationRaster'],
            'RASTER_BAND': 1,
            'STATISTICS': [1,4],  # Sum,St dev
            'OUTPUT': parameters['Fiberaway10']
        }
        outputs['ZonalStatistics10km'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Fiberaway10'] = outputs['ZonalStatistics10km']['OUTPUT']
        return results

    def name(self):
        return 'Telco Infrastructure Gap'

    def displayName(self):
        return 'Telco Infrastructure Gap'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return TelcoInfrastructureGap()
