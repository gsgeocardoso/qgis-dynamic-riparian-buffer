# -*- coding: utf-8 -*-
"""
APP DINÂMICA | RIPARIAN BUFFER
"""

from qgis.core import *
from qgis.PyQt.QtCore import QVariant
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points, substring, unary_union


class APP_Dinamica(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    FIELD_ID = 'FIELD_ID'
    DIST = 'DIST'
    TOL = 'TOL'
    DISSOLVE_GENERAL = 'DISSOLVE_GENERAL'
    REMOVE_OVERLAP = 'REMOVE_OVERLAP'
    OUTPUT = 'OUTPUT'
    OUTPUT_POINTS = 'OUTPUT_POINTS'
    OUTPUT_CENTERLINE = 'OUTPUT_CENTERLINE'

    def shortHelpString(self):
        return """
APP DINÂMICA – GERAÇÃO AUTOMÁTICA DE APP
DYNAMIC RIPARIAN BUFFER – AUTOMATIC GENERATION

PORTUGUÊS
- Calcula largura do rio automaticamente
- Gera eixo central
- Gera pontos de largura
- Aplica APP conforme Código Florestal
- Gera APP completa (duas margens dissolvidas automaticamente)

ENTRADA:
- Camada de LINHAS com DUAS margens por rio
- Cada rio deve ter o MESMO ID nas duas margens

EXEMPLO:
id_arroio = 1 → margem esquerda
id_arroio = 1 → margem direita

OPÇÕES:
- Dissolver todas as APPs → une tudo em uma mancha
- Remover sobreposição → mantém apenas a maior APP

OBS:
- Linhas muito desalinhadas podem apresentar problemas
- Evite geometrias quebradas ou duplicadas
- Pontos de largura/distância podem ser utilizados para análise de perfil do rio

ENGLISH
- Automatically calculates river width
- Generates centerline
- Creates width sampling points
- Applies riparian buffer according to Brazilian Forest Code
- Generates full buffer (both banks merged automatically)

INPUT:
- Line layer with TWO riverbanks per river
- Each river must have the SAME ID for both banks

EXAMPLE:
id_arroio = 1 → left bank
id_arroio = 1 → right bank

OPTIONS:
- Dissolve all buffers → merges into a single polygon
- Remove overlap → keeps only the largest buffer

NOTES:
- Misaligned lines may cause issues
- Avoid broken or duplicated geometries
- Width/distance points can be used for river profile analysis

Author:
Guilherme Silveira Cardoso – GIS Specialist

Links:
https://github.com/gsgeocardoso
https://www.linkedin.com/in/gscardoso-bio
"""

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            'Margens do rio',
            [QgsProcessing.TypeVectorLine]
        ))

        self.addParameter(QgsProcessingParameterString(
            self.FIELD_ID,
            'Campo ID',
            defaultValue='id_arroio'
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.DIST,
            'Distância de amostragem',
            type=QgsProcessingParameterNumber.Double,
            defaultValue=2
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.TOL,
            'Tolerância',
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.DISSOLVE_GENERAL,
            'Dissolver tudo',
            defaultValue=False
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_OVERLAP,
            'Remover sobreposição',
            defaultValue=False
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, 'APP'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_POINTS, 'Pontos'))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_CENTERLINE, 'Eixo'))

    def geometry_to_line(self, geom):
        try:
            if geom.isMultipart():
                multi = geom.asMultiPolyline()
                return LineString(multi[0]) if multi else None
            return LineString(geom.asPolyline())
        except:
            return None

    def get_app_distance(self, width):
        if width <= 10: return 30
        elif width <= 50: return 50
        elif width <= 200: return 100
        elif width <= 600: return 200
        else: return 500

    def get_utm_crs(self, geom):
        centroid = geom.centroid().asPoint()
        lon = centroid.x()
        lat = centroid.y()

        zone = int((lon + 180) / 6) + 1

        if lat >= 0:
            epsg = 32600 + zone
        else:
            epsg = 32700 + zone

        return QgsCoordinateReferenceSystem(f"EPSG:{epsg}")

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)
        field_id = self.parameterAsString(parameters, self.FIELD_ID, context)
        step = self.parameterAsDouble(parameters, self.DIST, context)
        tolerance = self.parameterAsDouble(parameters, self.TOL, context)
        dissolve_all = self.parameterAsBool(parameters, self.DISSOLVE_GENERAL, context)
        remove_overlap = self.parameterAsBool(parameters, self.REMOVE_OVERLAP, context)

        fields_app = QgsFields()
        fields_app.append(QgsField('id', QVariant.String))
        fields_app.append(QgsField('APP_m', QVariant.Int))

        fields_pts = QgsFields()
        fields_pts.append(QgsField('id', QVariant.String))
        fields_pts.append(QgsField('dist', QVariant.Double))
        fields_pts.append(QgsField('width', QVariant.Double))

        (sink_app, out_app) = self.parameterAsSink(parameters, self.OUTPUT, context, fields_app, QgsWkbTypes.Polygon, source.sourceCrs())
        (sink_pts, out_pts) = self.parameterAsSink(parameters, self.OUTPUT_POINTS, context, fields_pts, QgsWkbTypes.Point, source.sourceCrs())
        (sink_center, out_center) = self.parameterAsSink(parameters, self.OUTPUT_CENTERLINE, context, fields_app, QgsWkbTypes.LineString, source.sourceCrs())

        # CRS único para todo o processamento
        first_feat = next(source.getFeatures())
        utm_crs = self.get_utm_crs(first_feat.geometry())

        transform = QgsCoordinateTransform(source.sourceCrs(), utm_crs, context.transformContext())
        reverse_transform = QgsCoordinateTransform(utm_crs, source.sourceCrs(), context.transformContext())

        all_geometries = []

        ids = set([f[field_id] for f in source.getFeatures()])

        for cid in ids:

            features = [f for f in source.getFeatures() if f[field_id] == cid]
            if len(features) != 2:
                continue

            geom1 = QgsGeometry(features[0].geometry())
            geom2 = QgsGeometry(features[1].geometry())

            geom1.transform(transform)
            geom2.transform(transform)

            line1 = self.geometry_to_line(geom1)
            line2 = self.geometry_to_line(geom2)

            if not line1 or not line2:
                continue

            ref_line, opp_line = (line1, line2) if line1.length >= line2.length else (line2, line1)

            distances = np.arange(0, ref_line.length, step)
            widths = []
            center_points = []

            for d in distances:
                pt = ref_line.interpolate(d)
                pt_opp = nearest_points(pt, opp_line)[1]

                width = pt.distance(pt_opp)
                widths.append(width)

                mid = Point((pt.x + pt_opp.x) / 2, (pt.y + pt_opp.y) / 2)
                center_points.append(mid)

                qpt = QgsGeometry.fromWkt(mid.wkt)
                qpt.transform(reverse_transform)

                feat_pt = QgsFeature()
                feat_pt.setGeometry(qpt)
                feat_pt.setAttributes([str(cid), float(d), float(width)])
                sink_pts.addFeature(feat_pt, QgsFeatureSink.FastInsert)

            if not widths:
                continue

            center_line = LineString(center_points)
            q_center = QgsGeometry.fromWkt(center_line.wkt)
            q_center.transform(reverse_transform)

            feat_center = QgsFeature()
            feat_center.setGeometry(q_center)
            feat_center.setAttributes([str(cid), 0])
            sink_center.addFeature(feat_center, QgsFeatureSink.FastInsert)

            zones = []
            current_app = self.get_app_distance(widths[0])
            current_width = widths[0]
            start_index = 0

            for i in range(1, len(widths)):
                width = widths[i]
                app_now = self.get_app_distance(width)
                diff = abs(width - current_width)

                if app_now != current_app and diff > tolerance:
                    zones.append((distances[start_index], distances[i], current_app))
                    start_index = i
                    current_app = app_now
                    current_width = width

            zones.append((distances[start_index], distances[-1], current_app))

            for start_d, end_d, app_dist in zones:

                if start_d == end_d:
                    continue

                try:
                    seg_ref = substring(ref_line, start_d, end_d)

                    p1 = nearest_points(Point(seg_ref.coords[0]), opp_line)[1]
                    p2 = nearest_points(Point(seg_ref.coords[-1]), opp_line)[1]

                    d1 = opp_line.project(p1)
                    d2 = opp_line.project(p2)

                    seg_opp = substring(opp_line, min(d1, d2), max(d1, d2))

                    buffer1 = seg_ref.buffer(app_dist)
                    buffer2 = seg_opp.buffer(app_dist)

                    big_buffer = unary_union([seg_ref, seg_opp]).buffer(app_dist)
                    outer_buffer = unary_union([buffer1, buffer2])
                    river_polygon = big_buffer.difference(outer_buffer).buffer(0)

                    merged = unary_union([buffer1, buffer2, river_polygon])

                except:
                    continue

                geometries = merged.geoms if hasattr(merged, 'geoms') else [merged]

                for geom in geometries:
                    if geom.is_empty:
                        continue
                    all_geometries.append((geom, cid, app_dist))

        for g, cid, app in all_geometries:
            feat = QgsFeature()
            qgs_geom = QgsGeometry.fromWkt(g.wkt)
            qgs_geom.transform(reverse_transform)

            feat.setGeometry(qgs_geom)
            feat.setAttributes([str(cid), app])
            sink_app.addFeature(feat, QgsFeatureSink.FastInsert)

        return {
            self.OUTPUT: out_app,
            self.OUTPUT_POINTS: out_pts,
            self.OUTPUT_CENTERLINE: out_center
        }

    def name(self): return 'app_dinamica'
    def displayName(self): return 'APP Dinâmica'
    def group(self): return 'APP'
    def groupId(self): return 'app'
    def createInstance(self): return APP_Dinamica()
