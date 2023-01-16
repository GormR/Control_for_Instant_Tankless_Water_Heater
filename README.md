(für Deutsch bitte runterscrollen)

# Controller for Instant or Tankless Water Heater

# Safety Warning

This project deals with mains voltage. Make sure you understand what you are doing. Please read the safety warning below carefully.

![pic](warning.webp)

![pic](documentation/control_unit.jpg?raw=true)

[Link to EasyEDA project](https://oshwlab.com/goronb/imu-for-agopengps_copy_copy_copy)

Housing:

![pic](mechanical_data/sonoff_IP66_housing.png?raw=true)

e. g.: https://de.aliexpress.com/item/1005004819429222.html

Flow meter and temperature sensor:

![pic](mechanical_data/flow_meter.png?raw=true)

e. g.: https://de.aliexpress.com/item/1005004532077576.html

Suitable triac: BTA40-600

https://www.st.com/resource/en/datasheet/btb41.pdf

Suitable instant / tankless water heater:

e. g. CLAGE MPH6 5,7 kW 230V (e. g. via Amazon)

* to be translated 


# Elektronische Regelung für einen Durchlauferhitzer

Warnung! Nicht nachbauen - dieses Projekt verwendet Netzspannung und Wasser. Bei unsachgemäßem Umgang besteht Lebensgefahr! Ferner kann hoher Sachschaden entstehen!

![pic](documentation/control_unit.jpg?raw=true)

Die Elektronik regelt zusammen mit einem oder zwei externen Triacs und einem Durchflussmesser/Temperatursensor die Wassertemperatur eines elektrischen Durchlauferhitzers. Diese Durchlauferhitzer gibt es sowohl einphasig (dann oft als "Klein-Durchlauferhitzer" bezeichnet), als auch dreiphasig. Der Anschluss ist dementsprechend zweipolig oder dreipolig (dreiphasige Durchlauferhitzer sind als Dreieck geschaltet und benötigen keinen Nullleiter), und zur Regelung benötigt entweder einen oder zwei extern zu montierende Triacs.

Solange Triacs und Durchfluss-/Temperaturmesser nicht im Durchlauferhitzer eingebaut werden sollen, ist kein Eingriff in das Gerät notwendig.

Sicherheitseinrichtungen des Durchlauferhitzers dürfen in keinem Fall außer Kraft gesetzt werden!

Aufbau:
Am Kaltwasserzulauf wird ein Durchfluss-/Temperaturmesser angebracht. Dessen Gehäuse kann gleichzeitig zur Kühlung des oder der Triacs dienen. Hier auf perfekten Wärmeübergang achten! Ein Strom von 1A verursacht eine Verlustleistung von ca. 1.2W im Triac. Diese Leistung dient zwar auch der Aufheizung des Wassers, aber bei 40A müssen rund 50W abgeführt werden. 

Es muss eine Messingplatte angelötet werden, die den oder die Triacs isoliert aufnehmen kann. Diese Messingplatte muss mit PE verbunden sein mit einem 4mm²-Draht. Zum Anlöten der Platte muss natürlich die Turbine im Inneren sowie der Hallsensor und der Temperatursensor demontiert werden.

Nach erfolgtem Aufbau sollte die Funktion zunächst mit Hilfe einer klassischen Glühlampe anstelle des Heizelementes überprüft werden.

Regelung:
Die notwendige elektrische Energie ist direkt proportional zum Durchfluss und zur Temperaturdifferenz zwischen der Temperatur des einströmenden Wassers und der Wunschtemperatur:

Power = p x Wasserdurchfluss x deltaT

Die Proportionalitätskonstante (in Python-Script auch "p") muss empirisch ermittelt werden, solange nicht exakt dieselben Teile verwendet werden, wie in diesem Versuchsaufbau. Auf den Temperatursensor am Ausgang kann für die Temperaturregeleung komplett verzichtet werden, er ist aber zum Finden der Proportionalitätskonstante sehr hilfreich, und die Ausgangstemperatur kann auf dem Display angezeigt werden. 

Auch muss die Formel zur Berechnung der Temperatur händisch ermittelt werden. Dazu wird der Sensor in ein Wasserbad gehängt und die Rohdaten des ADCs über Temperatur ermittelt. In einer Tabellenkalkulation kann man dann die optimale Formel ausprobieren. Eine geeignete Kalkulationstabelle befindet sich im Ordner "documentation". Ggf. die drei Konstanten k0, k1 und k2 im Python-Script anpassen.

Gehäuse:

![pic](mechanical_data/sonoff_IP66_housing.png?raw=true)

z. B.: https://de.aliexpress.com/item/1005004819429222.html

Durchflussmesser und Temperatursensor:

![pic](mechanical_data/flow_meter.png?raw=true)

z. B.: https://de.aliexpress.com/item/1005004532077576.html

Geeigneter Triac: BTA40-600
https://www.st.com/resource/en/datasheet/btb41.pdf

Durchlauferhitzer:
z. B. CLAGE MPH6 Klein-Durchlauferhitzer 5,7 kW 230V, druckfest, Untertisch (z. B. bei Amazon)


