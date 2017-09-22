# -*- coding: utf-8 -*-
"""
/***************************************************************************
 STeAMM
                                 A QGIS plugin
 Stream Temperature Automated Modeler using MODIS
                             -------------------
        begin                : 2016-09-08
        copyright            : (C) 2016 by South Fork Research, Inc.
        email                : jesse@southforkresearch.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load STeAMM class from file STeAMM.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .steamm import STeAMM
    return STeAMM(iface)
