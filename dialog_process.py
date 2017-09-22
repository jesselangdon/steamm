# -*- coding: utf-8 -*-
"""
/***************************************************************************
 STeAMMDialog
                                 A QGIS plugin
 Stream Temperature Automated Modeler using MODIS
                             -------------------
        begin                : 2016-09-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by South Fork Research, Inc.
        email                : jesse@southforkresearch.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import datetime
import steamm

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog_process.ui'))


class ProcessDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProcessDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # self.cbo_ProductID()
        # self.cbo_SwathID()
        # self.cbo_ProcessYear()
        # self.lineEdit_DoYStart()
        # self.lineEdit_DoYEnd()
        # self.checkBox_HDFConvert()
        # self.lineEdit_DataDir()
        #
        # self.text_StatusConsole()

    def load_product_id(self):
        product_list = ['MOD11A1.005''MOD11A2.005']
        self.cbo_ProductID.clear()
        self.cbo_ProductID.addItems(product_list)

    def load_swath_id(self):
        swath_list = ['h08v04', 'h08v05',
                      'h09v03', 'h09v04', 'h09v05', 'h09v06'
                      'h10v03', 'h10v04', 'h10v05', 'h10v06'
                      'h11v03', 'h11v04', 'h11v05', 'h11v06']
        self.cbo_SwathID.clear()
        self.cbo_SwathID.addItems(swath_list)

    def load_years(self):
        now = datetime.datetime.now()
        year_list = []
        for yr in range(2000, now.year, 1):
            year_list.append(yr)

        self.cbo_ProcessYear.clear()
        self.cbo_ProcessYear.addItems(year_list)

    def exec(self):


if __name__ == "__main__":
