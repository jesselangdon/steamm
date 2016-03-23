# steamm
## Stream Temperature Automated Modeling with MODIS

STeAMM (Stream Temperature Automated Modeler using MODIS) will eventually be QGIS Plugin 
that automates the process of modeling stream temperature using the methodology described
in McNyset, et al. 2015. STeAMM is written in Python, and relies on several external
libraries, including gdal, numpy, matplotlib, and PyQT.

STeAMM is in an early stage of development.  For testing purposes, the interface
is currently implemented as a command line interface, accessible through the OSGeo4W
shell.

### Environment
* This tool is currently built using Python 2.7, GDAL 1.11.
* STeAMM can be run in an 64-bit processing environment.

### References
McNyset, Kristina M., Carol J. Volk, and Chris E. Jordan. "Developing an Effective Model for Predicting Spatially and Temporally Continuous Stream Temperatures from Remotely Sensed Land Surface Temperatures." Water 7.12 (2015): 6827-6846.

### Acknowledgements
STeAMM is being developed by Jesse Langdon, in consultation with Kris McNyset.