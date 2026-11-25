"""German translations: Network Overview, Element Inspector, Topology
Visualization, Modify Network and their helper modules."""

DE = {
    # --- Netzübersicht -------------------------------------------------------
    "Summary of **`{code}`** — {level} grid, {kind}, scenario {scenario}.":
        "Zusammenfassung von **`{code}`** — Netzebene {level}, {kind}, Szenario {scenario}.",
    "Element inventory": "Betriebsmittelbestand",
    "Voltage levels and installed capacities": "Spannungsebenen und installierte Leistungen",
    "Lines and transformers": "Leitungen und Transformatoren",
    "Data completeness and consistency": "Datenvollständigkeit und Konsistenz",
    "What does this network represent?": "Was bildet dieses Netz ab?",
    "What do these element types mean?": "Was bedeuten diese Betriebsmitteltypen?",
    "**Buses per voltage level**": "**Knoten je Spannungsebene**",
    "**Installed capacities**": "**Installierte Leistungen**",
    "**Static generation by technology**": "**Statische Erzeugung nach Technologie**",
    "No missing values in any element table.":
        "In keiner Betriebsmitteltabelle fehlen Werte.",
    "How to read SimBench bus names": "So sind die SimBench-Knotennamen aufgebaut",
    "**Not present in this network:**": "**In diesem Netz nicht vorhanden:**",
    "**Generation-to-demand ratio:** installed generation covers **{ratio:.0%}** of peak active demand. Values near or above 100 % indicate that reverse power flow towards the upstream grid can occur at times of high generation and low demand — a typical driver of voltage-rise problems in distribution grids.":
        "**Verhältnis von Erzeugung zu Last:** Die installierte Erzeugungsleistung deckt **{ratio:.0%}** der maximalen Wirkleistungsnachfrage. Werte nahe oder über 100 % deuten darauf hin, dass es bei hoher Einspeisung und geringer Last zu einer Rückspeisung in das überlagerte Netz kommen kann — eine typische Ursache für Spannungsanhebungen in Verteilnetzen.",
    "**Line statistics**": "**Leitungsstatistik**",
    "This network contains no lines.": "Dieses Netz enthält keine Leitungen.",
    "**Transformer statistics**": "**Transformatorstatistik**",
    "This network contains no 2-winding transformers.":
        "Dieses Netz enthält keine Zweiwicklungstransformatoren.",
    "Columns with missing values ({n})": "Spalten mit fehlenden Werten ({n})",
    "Many pandapower columns are optional and legitimately unset (e.g. capability limits). Missing values only matter when a parameter is required by an analysis — see the Diagnostics page.":
        "Viele pandapower-Spalten sind optional und dürfen unbelegt bleiben (z. B. Leistungsgrenzen). Fehlende Werte sind nur relevant, wenn eine Analyse den Parameter benötigt — siehe Seite „Ergebnisdiagnose“.",
    # Spaltenköpfe / Zeilenbezeichnungen
    "Element": "Betriebsmittel",
    "Technology": "Technologie",
    "Nominal voltage [kV]": "Nennspannung [kV]",
    "Buses": "Knoten",
    "Table": "Tabelle",
    "Column": "Spalte",
    "Missing values": "Fehlende Werte",
    "Share": "Anteil",
    "Count": "Anzahl",
    "In service": "In Betrieb",
    "Units": "Anzahl",
    "Installed_MW": "Installiert [MW]",
    "Quantity": "Größe",
    "Unit": "Einheit",
    "unspecified": "nicht spezifiziert",
    # network_analysis: Zeilenbezeichnungen
    "Total active load demand": "Summe Wirklastbedarf",
    "Total reactive load demand": "Summe Blindlastbedarf",
    "Installed static generation (sgen)": "Installierte statische Erzeugung (sgen)",
    "Installed controllable generation (gen)": "Installierte regelbare Erzeugung (gen)",
    "Storage rated power": "Speicher-Bemessungsleistung",
    "Storage energy capacity": "Speicher-Energiekapazität",
    "Number of lines": "Anzahl Leitungen",
    "Total route length": "Gesamte Trassenlänge",
    "Mean line length": "Mittlere Leitungslänge",
    "Median line length": "Median der Leitungslänge",
    "Longest line": "Längste Leitung",
    "Distinct standard types": "Verschiedene Standardtypen",
    "Cables (type 'cs')": "Kabel (Typ 'cs')",
    "Overhead lines (type 'ol')": "Freileitungen (Typ 'ol')",
    "Number of transformers": "Anzahl Transformatoren",
    "Total rated power": "Gesamte Bemessungsleistung",
    "Smallest unit": "Kleinste Einheit",
    "Largest unit": "Größte Einheit",
    "Units {hv:g} kV → {lv:g} kV": "Einheiten {hv:g} kV → {lv:g} kV",
    "A slack source (external grid or slack generator) exists":
        "Eine Slack-Quelle (externes Netz oder Slack-Generator) ist vorhanden",
    "All lines have a positive length": "Alle Leitungen haben eine positive Länge",
    "All line endpoints reference existing buses":
        "Alle Leitungsenden verweisen auf vorhandene Knoten",
    "No loads are connected to out-of-service buses ({n_bad} affected)":
        "Keine Lasten sind an außer Betrieb befindliche Knoten angeschlossen ({n_bad} betroffen)",
    "No loads are connected to out-of-service buses":
        "Keine Lasten sind an außer Betrieb befindliche Knoten angeschlossen",
    "Bus names are unique ({n_dup} duplicates)":
        "Knotennamen sind eindeutig ({n_dup} Duplikate)",
    "Bus names are unique": "Knotennamen sind eindeutig",
    # Betriebsmittelarten (na.ELEMENTS)
    "Lines": "Leitungen",
    "Transformers": "Transformatoren",
    "Transformers (2-winding)": "Transformatoren (2-Wicklungen)",
    "Transformers (3-winding)": "Transformatoren (3-Wicklungen)",
    "Loads": "Lasten",
    "Static generators": "Statische Erzeuger",
    "Generators": "Generatoren",
    "Generators (voltage-controlled)": "Generatoren (spannungsgeregelt)",
    "Storage": "Speicher",
    "Storage units": "Speichereinheiten",
    "Switches": "Schalter",
    "External grids": "Externe Netze",
    "Shunts": "Querglieder (Shunts)",
    "Measurements": "Messungen",

    # --- Elementinspektor / tables -------------------------------------------
    "Inspect the raw pandapower element tables of the loaded network. Filters narrow the rows; the column preset keeps tables readable. Every filtered view can be downloaded as CSV.":
        "Hier lassen sich die rohen pandapower-Betriebsmitteltabellen des geladenen Netzes einsehen. Filter schränken die Zeilen ein; die Spaltenvorauswahl hält die Tabellen übersichtlich. Jede gefilterte Ansicht kann als CSV heruntergeladen werden.",
    "Element table": "Betriebsmitteltabelle",
    "Filters": "Filter",
    "{n} of {total} rows match the current filters.":
        "{n} von {total} Zeilen entsprechen den aktuellen Filtern.",
    "Columns": "Spalten",
    "Essential": "Wesentliche",
    "All": "Alle",
    "Download filtered table (CSV)": "Gefilterte Tabelle herunterladen (CSV)",
    "The network contains no element tables.": "Das Netz enthält keine Betriebsmitteltabellen.",
    "The essential preset hides rarely needed parameter columns.":
        "Die Vorauswahl „Wesentliche“ blendet selten benötigte Parameterspalten aus.",
    "{label} ({n})": "{label} ({n})",
    "Power-flow results for this table (res_{choice})":
        "Lastflussergebnisse für diese Tabelle (res_{choice})",
    "Download result table (CSV)": "Ergebnistabelle herunterladen (CSV)",
    "Name contains": "Name enthält",
    "Yes": "Ja",
    "No": "Nein",
    "Voltage level (SimBench voltLvl)": "Spannungsebene (SimBench voltLvl)",
    "Numeric range filter": "Filter für Zahlenbereich",
    "{col} range": "Bereich {col}",

    # --- Topologie-Visualisierung --------------------------------------------
    "Bus neighbourhood": "Knotenumgebung",
    "Select a bus to list every element electrically attached to it.":
        "Knoten auswählen, um alle elektrisch angeschlossenen Betriebsmittel aufzulisten.",
    "Bus": "Knoten",
    "Bus positions use the **geographic coordinates** shipped with the SimBench dataset (schematic, not surveyed).":
        "Die Knotenpositionen verwenden die **geografischen Koordinaten** des SimBench-Datensatzes (schematisch, nicht vermessen).",
    "This network carries no geodata — bus positions are a **computed topological layout** (force-directed, deterministic). Distances on screen carry no physical meaning.":
        "Dieses Netz enthält keine Geodaten — die Knotenpositionen sind ein **berechnetes topologisches Layout** (kraftbasiert, deterministisch). Abstände auf dem Bildschirm haben keine physikalische Bedeutung.",
    "Nominal voltage level": "Nennspannungsebene",
    "Uniform": "Einheitlich",
    "Voltage magnitude (vm, p.u.)": "Spannungsbetrag (vm, p.u.)",
    "Colour buses by": "Knoten einfärben nach",
    "Loading (% of thermal limit)": "Auslastung (% der thermischen Grenze)",
    "Colour lines by": "Leitungen einfärben nach",
    "Show loads / generation / storage": "Lasten / Erzeugung / Speicher anzeigen",
    "Overlays markers at the connection buses of injections.":
        "Blendet Markierungen an den Anschlussknoten der Einspeiser und Lasten ein.",
    "Result-based colouring (voltage magnitude, line loading) becomes available after running a power flow on the *Power Flow Analysis* page.":
        "Die ergebnisbasierte Einfärbung (Spannungsbetrag, Leitungsauslastung) steht zur Verfügung, sobald auf der Seite *Lastflussanalyse* ein Lastfluss berechnet wurde.",
    "Large network ({n} lines): rendering switches to WebGL and per-line hover labels are disabled to stay responsive.":
        "Großes Netz ({n} Leitungen): Die Darstellung wechselt zu WebGL, und die Hover-Beschriftungen je Leitung sind deaktiviert, damit die Anzeige flüssig bleibt.",
    "How to read this figure": "So ist die Abbildung zu lesen",
    "- **Dots** are buses (electrical nodes); **solid grey or coloured segments** are lines; **dotted dark segments** are transformers coupling two voltage levels.\n- Hover over buses (and, for moderate network sizes, line midpoints) for names, nominal voltages and — after a power flow — result values.\n- Line colours follow the loading bins green < 50 %, yellow 50–80 %, orange 80–100 %, red > 100 % of the thermal rating.":
        "- **Punkte** sind Knoten (elektrische Netzknoten); **durchgezogene graue oder farbige Strecken** sind Leitungen; **gepunktete dunkle Strecken** sind Transformatoren, die zwei Spannungsebenen koppeln.\n- Beim Überfahren der Knoten (und bei mittelgroßen Netzen der Leitungsmitten) erscheinen Namen, Nennspannungen und — nach einem Lastfluss — Ergebniswerte.\n- Die Leitungsfarben folgen den Auslastungsklassen grün < 50 %, gelb 50–80 %, orange 80–100 %, rot > 100 % der thermischen Bemessungsgrenze.",
    "No elements are attached to this bus.": "An diesem Knoten sind keine Betriebsmittel angeschlossen.",
    "**{label} ({n})**": "**{label} ({n})**",
    # visualization.py
    "Bus {idx}: {name}<br>{vn:g} kV": "Knoten {idx}: {name}<br>{vn:g} kV",
    "Line {idx}: {name}<br>{length:.3f} km, {std_type}":
        "Leitung {idx}: {name}<br>{length:.3f} km, {std_type}",
    "<br>vm = {value:.4f} p.u.": "<br>vm = {value:.4f} p.u.",
    "<br>loading: {value:.1f} %": "<br>Auslastung: {value:.1f} %",
    "Load": "Last",
    "Static generator": "Statischer Erzeuger",
    "Storage unit": "Speichereinheit",
    "Line info": "Leitungsinfo",
    "Lines {label}": "Leitungen {label}",
    "{level:g} kV buses": "Knoten {level:g} kV",
    "{kind} {i}: {name}<br>p = {p:.3f} MW": "{kind} {i}: {name}<br>p = {p:.3f} MW",

    # --- Netz verändern --------------------------------------------------------
    "Apply controlled modifications to the **session working copy** of the network for what-if studies. The cached original is untouched — reload the network to discard all changes. Power-flow results are invalidated by every modification; re-run the power flow afterwards.":
        "Hier lassen sich kontrollierte Änderungen an der **Arbeitskopie der Sitzung** für Was-wäre-wenn-Untersuchungen vornehmen. Das zwischengespeicherte Original bleibt unverändert — durch erneutes Laden des Netzes werden alle Änderungen verworfen. Jede Änderung macht die Lastflussergebnisse ungültig; der Lastfluss ist anschließend erneut zu berechnen.",
    "Scale loads": "Lasten skalieren",
    "Load scale factor": "Lastskalierungsfaktor",
    "Multiplies active and reactive power of every load. Useful to emulate demand growth or stress-test the feeder.":
        "Multipliziert Wirk- und Blindleistung jeder Last. Geeignet, um Lastwachstum nachzubilden oder den Abgang unter Last zu prüfen.",
    "Apply scaling": "Skalierung anwenden",
    "Scaled all loads by factor {scale}": "Alle Lasten mit dem Faktor {scale} skaliert",
    "Scaled {n} loads by {scale}× (active and reactive power).":
        "{n} Lasten um den Faktor {scale} skaliert (Wirk- und Blindleistung).",
    "Add a storage unit": "Speichereinheit hinzufügen",
    "Name": "Name",
    "Power [MW] (positive = charging)": "Leistung [MW] (positiv = Laden)",
    "Energy capacity [MWh]": "Energiekapazität [MWh]",
    "Connection bus": "Anschlussknoten",
    "Add storage": "Speicher hinzufügen",
    "Added storage '{name}' ({power} MW / {capacity} MWh) at bus {bus}":
        "Speicher '{name}' ({power} MW / {capacity} MWh) an Knoten {bus} hinzugefügt",
    "Storage '{name}' added with index {idx}.":
        "Speicher '{name}' mit Index {idx} hinzugefügt.",
    "Adding the storage failed: {exc}": "Das Hinzufügen des Speichers ist fehlgeschlagen: {exc}",
    "Modification log": "Änderungsprotokoll",
    "Modifications are recorded in the analysis report on the *Export & Report* page for reproducibility.":
        "Änderungen werden zur Nachvollziehbarkeit im Analysebericht auf der Seite *Export & Bericht* festgehalten.",
    "No modifications applied in this session.": "In dieser Sitzung wurden keine Änderungen vorgenommen.",
    "Discard modifications and reload original network":
        "Änderungen verwerfen und Originalnetz neu laden",
    "Reloaded original network `{code}`.": "Originalnetz `{code}` neu geladen.",
}
