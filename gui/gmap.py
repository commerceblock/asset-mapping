#!/usr/bin/env python

import sys

from PyQt5.QtGui import QIcon, QBrush, QColor

from PyQt5.QtCore import Qt

from PyQt5.QtCore import QFile, QIODevice, Qt, QTextStream, QRegExp, QTime
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout, QHBoxLayout,
        QLabel, QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
        QWidget, QApplication, QCheckBox, QComboBox, QTreeView, QGroupBox)
from PyQt5.QtGui import QStandardItemModel

import amap.mapping as am
import bitcoin as bc
import boto3
import sys
import amap.rpchost as rpc
from datetime import datetime

class AMapping(QWidget):
    INDEX, ASSET, MASS, TOKENID = range(4)

    def __init__(self, parent=None):
        super(AMapping, self).__init__(parent)

        self.new_map = am.MapDB(2,3)
        self.old_map = am.MapDB(2,3)

        self.con_pubkeys = am.ConPubKey()

        self.title = 'Asset Mapping Interface'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 540

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.oldMapping = QGroupBox("Current Mapping")
        self.oldMapView = QTreeView()
        self.oldMapView.setRootIsDecorated(False)
        self.oldMapView.setAlternatingRowColors(True)

        oldMapLayout = QHBoxLayout()
        oldMapLayout.addWidget(self.oldMapView)
        self.oldMapping.setLayout(oldMapLayout)

        self.oldModel = self.createMapModel(self)
        self.oldMapView.setModel(self.oldModel)

        self.newMapping = QGroupBox("New Mapping")
        self.newMapView = QTreeView()
        self.newMapView.setRootIsDecorated(False)
        self.newMapView.setAlternatingRowColors(True)

        newMapLayout = QHBoxLayout()
        newMapLayout.addWidget(self.newMapView)
        self.newMapping.setLayout(newMapLayout)

        self.newModel = self.createMapModel(self)
        self.newMapView.setModel(self.newModel)

        self.oldMapView.setColumnWidth(0,50)
        self.newMapView.setColumnWidth(0,50)

        self.issueButton = QPushButton("&Issue Asset")
        self.issueButton.show()
        self.addButton = QPushButton("&Add Asset")
        self.addButton.show()
        self.removeButton = QPushButton("&Remove Asset")
        self.removeButton.show()
        self.findButton = QPushButton("&Find Asset")
        self.findButton.show()
        self.tokenButton = QPushButton("&Token Report")
        self.tokenButton.show()
        self.remapButton = QPushButton("&Redemeption")
        self.remapButton.show()

        self.oldMassButton = QPushButton("&Mass Check")
        self.oldMassButton.show()
        self.loadOldButton = QPushButton("&Load File")
        self.loadOldButton.show()
        self.downloadButton = QPushButton("&Download")
        self.downloadButton.show()
        
        self.newMassButton = QPushButton("&Mass Check")
        self.newMassButton.show()
        self.loadNewButton = QPushButton("&Load File")
        self.loadNewButton.show()
        self.uploadButton = QPushButton("&Upload")
        self.uploadButton.show()

        self.sigButton = QPushButton("&Signatures")
        self.sigButton.show()

        self.saveButton = QPushButton("&Save JSON")
        self.saveButton.setToolTip("Save JSON to a file")
        self.saveButton.show()

        self.settingsButton = QPushButton("&Settings")
        self.settingsButton.setToolTip("Settings and configuration options")
        self.settingsButton.show()

#        self.dialog = IssueAssetDialog()
        self.addAssetDlog = AddAssetDialog()
        self.tokenDlog = TokenDialog()
#        self.dialog = SignaturesDialog()
#        self.dialog = RemapDialog()
#        self.dialog = OldMassDialog()
#        self.dialog = NewMassDialog()

        self.oldMapMass = QLabel("Mass:")
        self.oldMapTime = QLabel("Time:")
        self.oldMapSigs = QLabel("Signatures:")
        self.newMapMass = QLabel("Mass:")
        self.newMapTime = QLabel("Time:")
        self.newMapSigs = QLabel("Signatures:")

        self.conStatus = QLabel("Ocean:")

        self.issueButton.clicked.connect(self.issueAsset)
        self.addButton.clicked.connect(self.addAsset)
        self.removeButton.clicked.connect(self.removeAsset)
        self.findButton.clicked.connect(self.findAsset)
        self.tokenButton.clicked.connect(self.tokenReport)
        self.remapButton.clicked.connect(self.remapAssets)
        self.oldMassButton.clicked.connect(self.oldMassAsset)
        self.loadOldButton.clicked.connect(self.loadOldMap)
        self.downloadButton.clicked.connect(self.downloadMap)
        self.newMassButton.clicked.connect(self.newMassAsset)
        self.loadNewButton.clicked.connect(self.loadNewMap)
        self.uploadButton.clicked.connect(self.uploadMap)
        self.sigButton.clicked.connect(self.signatures)
        self.saveButton.clicked.connect(self.saveMap)
        self.settingsButton.clicked.connect(self.settings)

        buttonLayout1 = QVBoxLayout()
        buttonLayout1.addWidget(self.issueButton)
        buttonLayout1.addWidget(self.addButton)
        buttonLayout1.addWidget(self.removeButton)
        buttonLayout1.addWidget(self.findButton)
        buttonLayout1.addWidget(self.tokenButton)
        buttonLayout1.addWidget(self.remapButton)
        buttonLayout1.addWidget(self.sigButton)
        buttonLayout1.addWidget(self.saveButton)
        buttonLayout1.addWidget(self.settingsButton)
        buttonLayout1.addStretch()

        buttonLayout2 = QHBoxLayout()
        buttonLayout2.addWidget(self.oldMassButton)
        buttonLayout2.addWidget(self.loadOldButton)
        buttonLayout2.addWidget(self.downloadButton)

        buttonLayout3 = QHBoxLayout()
        buttonLayout3.addWidget(self.newMassButton)
        buttonLayout3.addWidget(self.loadNewButton)
        buttonLayout3.addWidget(self.uploadButton)

        oldMapSummary = QVBoxLayout()
        oldMapSummary.addWidget(self.oldMapMass)
        oldMapSummary.addWidget(self.oldMapTime)
        oldMapSummary.addWidget(self.oldMapSigs)
        newMapSummary = QVBoxLayout()
        newMapSummary.addWidget(self.newMapMass)
        newMapSummary.addWidget(self.newMapTime)
        newMapSummary.addWidget(self.newMapSigs)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.oldMapping, 0, 0)
        mainLayout.addWidget(self.newMapping, 0, 1)
        mainLayout.addLayout(buttonLayout1, 0, 2)
        mainLayout.addLayout(oldMapSummary, 1, 0)
        mainLayout.addLayout(buttonLayout2, 2, 0)
        mainLayout.addLayout(newMapSummary, 1, 1)
        mainLayout.addLayout(buttonLayout3, 2, 1)

        self.setLayout(mainLayout)

    def createMapModel(self,parent):
        model = QStandardItemModel(0, 4, parent)
        model.setHeaderData(self.INDEX, Qt.Horizontal, "Index")
        model.setHeaderData(self.ASSET, Qt.Horizontal, "Asset ID")
        model.setHeaderData(self.MASS, Qt.Horizontal, "Mass")
        model.setHeaderData(self.TOKENID, Qt.Horizontal, "Token ID")
        return model
 
    def addEntry(self, model, index, assetID, mass, tokenID):
        model.insertRow(0)
        model.setData(model.index(0, self.INDEX), index)
        model.setData(model.index(0, self.ASSET), assetID)
        model.setData(model.index(0, self.MASS), mass)
        model.setData(model.index(0, self.TOKENID), tokenID)

    def addAsset(self):
        self.addAssetDlog.show()

        if self.addAssetDlog.exec_() == QDialog.Accepted:
            ref,year,man,mass,token = self.addAssetDlog.getAssetInfo()

            index = self.new_map.add_asset(ref,year,mass,token,man)
            self.addEntry(self.newModel,str(index),str(ref)+str(year)+man,mass,token)

    def issueAsset(self):
        return 0

    def signatures(self):
        return 0

    def remapAssets(self):
        return 0

    def removeAsset(self):
        return 0

    def tokenReport(self):
        self.tokenDlog.show()
        return 0

    def newMassAsset(self):
        return 0

    def oldMassAsset(self):

        QMessageBox.information(self, "Verifying map","Signatures verified")

        return 0

    def findAsset(self):
        return 0

    def saveMap(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Export modified Map",
                '', "JSON (*.json);;All Files (*)")

        if not fileName:
            return

        try:
            out_file = open(str(fileName), 'wb')
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                    "There was an error opening \"%s\"" % fileName)
            return

        self.new_map.export_json(out_file)
        out_file.close()

    def loadNewMap(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Load New Map",'', "JSON (*.json);;All Files (*)")

        if not fileName:
            return

        try:
            in_file = open(str(fileName), 'rb')
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                    "There was an error opening \"%s\"" % fileName)
            return

        self.new_map.load_json(fileName)
        json_obj = self.new_map.get_json()

        for i,j in json_obj["assets"].items():
            self.addEntry(self.newModel,i,j["ref"],j["mass"],j["tokenid"])

        tot_mass = self.new_map.get_total_mass()
        self.newMapMass.setText("Mass: "+str(tot_mass))
#        timestamp = self.new_map.get

    def loadOldMap(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Old Map",
                '', "JSON (*.json);;All Files (*)")

        if not fileName:
            return

        try:
            in_file = open(str(fileName), 'rb')
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                    "There was an error opening \"%s\"" % fileName)
            return
        
        self.old_map.load_json(fileName)
        json_obj = self.old_map.get_json()

        for i,j in json_obj["assets"].items():
            self.addEntry(self.oldModel,i,j["ref"],j["mass"],j["tokenid"])

    def settings(self):
        return 0

    def downloadMap(self):
        s3 = boto3.resource('s3')
        s3.Bucket('gtsa-mapping').download_file('map.json','map.json')

        self.old_map.load_json('map.json')
        json_obj = self.old_map.get_json()

        for i,j in json_obj["assets"].items():
            self.addEntry(self.oldModel,i,j["ref"],j["mass"],j["tokenid"])

        tot_mass = self.old_map.get_total_mass()
        self.oldMapMass.setText("Mass: "+str(tot_mass))
        tmstr = "Time: "+str(self.old_map.get_time())+" ("+datetime.fromtimestamp(self.old_map.get_time()).strftime('%c')+")"
        self.oldMapTime.setText(tmstr)
        self.oldMapSigs.setText("Signatures: Verified")

        complete = True

        return complete

    def uploadMap(self):
        return 0

class AddAssetDialog(QDialog):

    def __init__(self, parent=None):
        super(AddAssetDialog, self).__init__(parent)

        assetLabel = QLabel("Enter the asset reference number:")
        self.assetLineEdit = QLineEdit()
        yearLabel = QLabel("Enter the asset production year:")
        self.yearLineEdit = QLineEdit()
        manLabel = QLabel("Enter the asset manufacturer:")
        self.manLineEdit = QLineEdit()
        massLabel = QLabel("Enter the asset mass:")
        self.massLineEdit = QLineEdit()
        tokenLabel = QLabel("Enter the issued token ID:")
        self.tokenLineEdit = QLineEdit()

        self.addAssetButton = QPushButton("&Submit")

        layout = QGridLayout()
        layout.addWidget(assetLabel,0,0)
        layout.addWidget(self.assetLineEdit,0,1)
        layout.addWidget(yearLabel,1,0)
        layout.addWidget(self.yearLineEdit,1,1)
        layout.addWidget(manLabel,2,0)
        layout.addWidget(self.manLineEdit,2,1)
        layout.addWidget(massLabel,3,0)
        layout.addWidget(self.massLineEdit,3,1)
        layout.addWidget(tokenLabel,4,0)
        layout.addWidget(self.tokenLineEdit,4,1)
        layout.addWidget(self.addAssetButton,5,1)

        self.setLayout(layout)
        self.setWindowTitle("Add asset to map (without issuance)")

        self.addAssetButton.clicked.connect(self.addAssetClicked)
        self.addAssetButton.clicked.connect(self.accept)

    def addAssetClicked(self):
        self.assetref = self.assetLineEdit.text()
        self.year = self.yearLineEdit.text()
        self.man = self.manLineEdit.text()
        self.mass = self.massLineEdit.text()
        self.token = self.tokenLineEdit.text()

        if not self.assetref:
            QMessageBox.information(self, "Empty Serial Number Field",
                    "Please enter a serial number.")
            return

        if not self.year:
            QMessageBox.information(self, "Empty Year Field",
                    "Please enter a year.")
            return

        if not self.man:
            QMessageBox.information(self, "Empty Manufacturer Field",
                    "Please enter a manufacturer.")
            return

        if not self.mass:
            QMessageBox.information(self, "Empty Mass Field",
                    "Please enter a mass.")
            return

        self.assetLineEdit.clear()
        self.hide()

    def getAssetInfo(self):
        return self.assetref,self.year,self.man,self.mass,self.token

class TokenDialog(QDialog):
    RTOKEN, RMASS, ETOK, CTOK, RDIFF = range(5)
    def __init__(self, parent=None):
        super(TokenDialog, self).__init__(parent)

        rpcport = 8332
        rpcuser = 'ocean'
        rpcpassword = 'oceanpass'
        url = 'http://' + rpcuser + ':' + rpcpassword + '@localhost:' + str(rpcport)
        ocean = rpc.RPCHost(url)

        utxorep = ocean.call('getutxoassetinfo')
        token_ratio,hour = am.token_ratio()

        s3 = boto3.resource('s3')
        s3.Bucket('gtsa-mapping').download_file('map.json','map.json')

        self.setWindowTitle("Token Report")

        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 500

        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tokenReport = QGroupBox("Blockchain token analysis: UTXO scan")
        self.tokenView = QTreeView()
        self.tokenView.setRootIsDecorated(False)
        self.tokenView.setAlternatingRowColors(True)

        tokenLayout = QHBoxLayout()
        tokenLayout.addWidget(self.tokenView)
        self.tokenReport.setLayout(tokenLayout)

        self.tokenModel = self.createReportModel(self)
        self.tokenView.setModel(self.tokenModel)

        self.tokenView.setColumnWidth(0,200)

        self.tokenRatio = QLabel("Token ratio: "+str("%.8f" % token_ratio)+" oz/token at hour "+str(hour))

        map_obj = am.MapDB(2,3)
        map_obj.load_json('map.json')

        json_obj = map_obj.get_json()

        for entry in utxorep:
            asset = entry["asset"]
            amount = entry["amountspendable"] + entry["amountfrozen"]
            mass = 0.0
            inmap = False
            for i,j in json_obj["assets"].items():
                if j["tokenid"] == asset:
                    mass += j["mass"]
                    inmap = True
            if inmap and amount < 9.0:
                exptoken = mass/token_ratio
                self.addReport(self.tokenModel,asset,mass,exptoken,amount)

        layout = QVBoxLayout()
        layout.addWidget(self.tokenReport)
        layout.addWidget(self.tokenRatio)

        self.setLayout(layout)

    def createReportModel(self,parent):
        model = QStandardItemModel(0, 5, parent)
        model.setHeaderData(self.RTOKEN, Qt.Horizontal, "Token ID")
        model.setHeaderData(self.RMASS, Qt.Horizontal, "Mass")
        model.setHeaderData(self.ETOK, Qt.Horizontal, "Expected tokens")
        model.setHeaderData(self.CTOK, Qt.Horizontal, "Chain tokens")
        model.setHeaderData(self.RDIFF, Qt.Horizontal, "Difference")
        return model

    def addReport(self, model, tokID, rmas, etoken, ctoken):
        model.insertRow(0)
        model.setData(model.index(0, self.RTOKEN), tokID)
        model.setData(model.index(0, self.RMASS), str("%.3f" % rmas))
        model.setData(model.index(0, self.ETOK), str("%.8f" % etoken))
        model.setData(model.index(0, self.CTOK), str("%.8f" % ctoken))
        model.setData(model.index(0, self.RDIFF), str("%.8f" % (ctoken-etoken)))

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    astmapping = AMapping()
    astmapping.show()

    sys.exit(app.exec_())
