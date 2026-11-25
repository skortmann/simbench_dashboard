"""German translations: power flow, diagnostics, thresholds (group B)."""

DE = {
    # --- utils: threshold controls --------------------------------------
    "No network loaded yet. Please select and load a SimBench network "
    "on the **Home** page first.":
        "Es ist noch kein Netz geladen. Bitte wählen Sie zunächst auf der "
        "Seite **Start** ein SimBench-Netz aus und laden Sie es.",
    "Assessment thresholds": "Bewertungsgrenzen",
    "Voltage band preset": "Spannungsband-Voreinstellung",
    "Normative or planning-based voltage band. Pick *Custom* to "
    "set your own limits.":
        "Normatives oder planerisches Spannungsband. Wählen Sie "
        "*Benutzerdefiniert*, um eigene Grenzen festzulegen.",
    "Minimum voltage [p.u.]": "Minimale Spannung [p.u.]",
    "Buses below this magnitude are flagged as undervoltage.":
        "Knoten mit einem Spannungsbetrag unterhalb dieses Wertes werden als "
        "Unterspannung gekennzeichnet.",
    "Maximum voltage [p.u.]": "Maximale Spannung [p.u.]",
    "Buses above this magnitude are flagged as overvoltage.":
        "Knoten mit einem Spannungsbetrag oberhalb dieses Wertes werden als "
        "Überspannung gekennzeichnet.",
    "Maximum loading [%]": "Maximale Auslastung [%]",
    "Lines/transformers above this loading are flagged as "
    "overloaded.":
        "Leitungen/Transformatoren oberhalb dieser Auslastung werden als "
        "überlastet gekennzeichnet.",
    "Max. voltage rise by generation [%]":
        "Max. Spannungsanhebung durch Einspeisung [%]",
    "Limit for the voltage rise caused by all generators compared "
    "with the same case without generation (orientation: 3 % in LV, "
    "VDE-AR-N 4105).":
        "Grenzwert für die Spannungsanhebung durch alle Erzeugungsanlagen im "
        "Vergleich zum selben Fall ohne Einspeisung (Orientierung: 3 % in "
        "der Niederspannung, VDE-AR-N 4105).",

    # --- config: voltage band presets (constants) -----------------------
    "EN 50160 (±10 %)": "DIN EN 50160 (±10 %)",
    "Normative tolerance of the supply voltage at the connection point "
    "(DIN EN 50160, 10-min mean values, 95 % of a week).":
        "Normative Toleranz der Versorgungsspannung am Netzanschlusspunkt "
        "(DIN EN 50160, 10-Minuten-Mittelwerte, 95 % einer Woche).",
    "Planning band (±5 %)": "Planungsband (±5 %)",
    "Conservative band leaving headroom for the other network levels - "
    "a typical starting point for planning; use your own DSO's allocation.":
        "Konservatives Band, das Spielraum für die übrigen Netzebenen lässt "
        "- ein typischer Ausgangspunkt für die Netzplanung; verwenden Sie "
        "die Aufteilung Ihres eigenen Netzbetreibers.",
    "Custom": "Benutzerdefiniert",
    "Set the limits manually below.":
        "Legen Sie die Grenzen unten manuell fest.",

    # --- powerflow: constants -------------------------------------------
    "Newton-Raphson (default, robust)": "Newton-Raphson (Standard, robust)",
    "Backward/forward sweep (radial networks)":
        "Rückwärts-/Vorwärtsiteration (Strahlennetze)",
    "Gauss-Seidel (slow, didactic)": "Gauß-Seidel (langsam, didaktisch)",
    "Fast-decoupled (BX)": "Schnelle entkoppelte Lösung (BX)",
    "Fast-decoupled (XB)": "Schnelle entkoppelte Lösung (XB)",
    "lightsim2grid (C++, fast; Newton-Raphson only)":
        "lightsim2grid (C++, schnell; nur Newton-Raphson)",
    "pandapower native (all algorithms)":
        "pandapower nativ (alle Algorithmen)",

    # --- powerflow: results ---------------------------------------------
    "lightsim2grid not applicable: {exc}":
        "lightsim2grid nicht anwendbar: {exc}",
    "lightsim2grid is not installed": "lightsim2grid ist nicht installiert",
    "Min [p.u.]": "Min [p.u.]",
    "Mean [p.u.]": "Mittel [p.u.]",
    "Max [p.u.]": "Max [p.u.]",
    "Buses": "Knoten",
    "Voltage level [kV]": "Spannungsebene [kV]",
    "Elements": "Betriebsmittel",
    "Mean loading": "Mittlere Auslastung",
    "Median loading": "Median der Auslastung",
    "Maximum loading": "Maximale Auslastung",
    "Elements above 80 %": "Betriebsmittel über 80 %",
    "Quantity": "Größe",
    "Value": "Wert",
    "Unit": "Einheit",
    "Component": "Komponente",
    "External grid infeed": "Einspeisung aus dem vorgelagerten Netz",
    "Generation (gen)": "Erzeugung (gen)",
    "Static generation (sgen)": "Statische Erzeugung (sgen)",
    "Load demand": "Lastbedarf",
    "Storage (positive = charging)": "Speicher (positiv = Laden)",
    "Network losses (lines + transformers)":
        "Netzverluste (Leitungen + Transformatoren)",

    # --- page 04 --------------------------------------------------------
    "Compute the static AC operating point of the loaded network. The solver "
    "determines all bus voltages and branch flows from the specified loads, "
    "generation and the slack (external grid).":
        "Berechnet den statischen Wechselstrom-Arbeitspunkt des geladenen "
        "Netzes. Der Löser bestimmt alle Knotenspannungen und Zweigflüsse aus "
        "den vorgegebenen Lasten, der Einspeisung und dem Slack-Knoten "
        "(vorgelagertes Netz).",
    "Why convergence matters": "Warum Konvergenz wichtig ist",
    "Solver options": "Löseroptionen",
    "Solver backend": "Löser-Backend",
    "lightsim2grid runs Newton-Raphson in C++. Unsupported cases "
    "(other algorithms, voltage-dependent loads, ...) fall back to "
    "pandapower automatically.":
        "lightsim2grid führt das Newton-Raphson-Verfahren in C++ aus. Nicht "
        "unterstützte Fälle (andere Algorithmen, spannungsabhängige Lasten, "
        "...) werden automatisch mit pandapower gerechnet.",
    "Algorithm": "Algorithmus",
    "Initialisation": "Initialisierung",
    "'auto' picks a suitable start vector; 'dc' starts from a DC power "
    "flow; 'results' continues from previous results (warm start).":
        "'auto' wählt einen geeigneten Startvektor; 'dc' startet von einem "
        "Gleichstrom-Lastfluss; 'results' setzt bei den vorherigen "
        "Ergebnissen auf (Warmstart).",
    "Enforce generator Q limits": "Blindleistungsgrenzen der Generatoren einhalten",
    "Converts generators to PQ nodes when their reactive-power limits "
    "are hit, as in real operation.":
        "Wandelt Generatoren in PQ-Knoten um, sobald ihre "
        "Blindleistungsgrenzen erreicht sind, wie im realen Betrieb.",
    "Max. iterations (0 = auto)": "Max. Iterationen (0 = automatisch)",
    "Run power flow": "Lastfluss berechnen",
    "No power flow has been run for this network yet.":
        "Für dieses Netz wurde noch kein Lastfluss berechnet.",
    "Power flow **converged** in {runtime:.3f} s "
    "({algorithm}, backend: {backend}, run at {timestamp}).":
        "Der Lastfluss ist in {runtime:.3f} s **konvergiert** "
        "({algorithm}, Backend: {backend}, Berechnung am {timestamp}).",
    "Fell back to pandapower: {note}":
        "Rückfall auf pandapower: {note}",
    "Power flow **did not converge**. Solver message: {error}\n\n"
    "Typical causes: an infeasible operating point (overloaded feeder, "
    "voltage collapse), isolated subnetworks without slack, or "
    "inconsistent element data. Check the *Diagnostics* page; the result "
    "tables below are not meaningful.":
        "Der Lastfluss ist **nicht konvergiert**. Meldung des Lösers: "
        "{error}\n\n"
        "Typische Ursachen: ein nicht realisierbarer Arbeitspunkt (überlasteter "
        "Abgang, Spannungskollaps), isolierte Teilnetze ohne Slack-Knoten oder "
        "inkonsistente Betriebsmitteldaten. Prüfen Sie die Seite "
        "*Diagnose*; die Ergebnistabellen unten sind nicht aussagekräftig.",
    "The result tables are empty — re-run the power flow "
    "(the network may have been reloaded or modified).":
        "Die Ergebnistabellen sind leer — bitte den Lastfluss erneut "
        "berechnen (das Netz wurde möglicherweise neu geladen oder "
        "verändert).",
    "Voltage profile": "Spannungsprofil",
    "Voltage magnitude [p.u.]": "Spannungsbetrag [p.u.]",
    "What does voltage in p.u. mean?": "Was bedeutet Spannung in p.u.?",
    "Where does the voltage band come from?":
        "Woher stammt das Spannungsband?",
    "Voltage rise caused by generation":
        "Spannungsanhebung durch Einspeisung",
    "This network has no static generators (sgen).":
        "Dieses Netz enthält keine statischen Erzeugungsanlagen (sgen).",
    "Compute voltage rise with vs. without generation":
        "Spannungsanhebung mit und ohne Einspeisung berechnen",
    "Runs one additional power flow with all sgen switched off.":
        "Führt einen zusätzlichen Lastfluss mit abgeschalteten sgen durch.",
    "Not available: no active generation or a run did not "
    "converge.":
        "Nicht verfügbar: keine aktive Einspeisung oder eine Berechnung ist "
        "nicht konvergiert.",
    "Min [%]": "Min [%]",
    "Mean [%]": "Mittel [%]",
    "Max [%]": "Max [%]",
    "{n} bus(es) exceed the limit of {limit} % voltage rise.":
        "{n} Knoten überschreiten den Grenzwert von {limit} % "
        "Spannungsanhebung.",
    "All buses stay within the {limit} % limit.":
        "Alle Knoten bleiben innerhalb des Grenzwerts von {limit} %.",
    "How to read this": "So lesen Sie das Ergebnis",
    "Branch loading": "Auslastung der Zweige",
    "Lines": "Leitungen",
    "Transformers": "Transformatoren",
    "No line results.": "Keine Leitungsergebnisse.",
    "No transformer results.": "Keine Transformatorergebnisse.",
    "What does loading percent mean?": "Was bedeutet die Auslastung in Prozent?",
    "Power balance": "Leistungsbilanz",
    "How to read the power balance": "So lesen Sie die Leistungsbilanz",
    "Limit violations": "Grenzwertverletzungen",
    "Assessed against the sidebar thresholds: voltage band "
    "**[{vm_min}, {vm_max}] p.u.**, "
    "maximum loading **{max_loading} %**.":
        "Bewertet gegen die Grenzen der Seitenleiste: Spannungsband "
        "**[{vm_min}, {vm_max}] p.u.**, "
        "maximale Auslastung **{max_loading} %**.",
    "No violations — all voltages and loadings are within the "
    "configured limits.":
        "Keine Verletzungen — alle Spannungen und Auslastungen liegen "
        "innerhalb der eingestellten Grenzen.",
    "Undervoltage buses": "Knoten mit Unterspannung",
    "Overvoltage buses": "Knoten mit Überspannung",
    "Overloaded lines": "Überlastete Leitungen",
    "Overloaded transformers": "Überlastete Transformatoren",
    "What do violations imply?": "Was bedeuten Verletzungen?",

    # --- page 05 --------------------------------------------------------
    "Automated checks of the loaded network and — once a power flow has been "
    "run — of its results. Each finding carries a severity and a plain-"
    "language explanation.":
        "Automatische Prüfungen des geladenen Netzes und — sobald ein Lastfluss "
        "berechnet wurde — seiner Ergebnisse. Jeder Befund enthält eine "
        "Schwere und eine allgemeinverständliche Erläuterung.",
    "How severities are assigned": "Wie die Schwere vergeben wird",
    "Critical": "Kritisch",
    "Warnings": "Warnungen",
    "Info": "Hinweis",
    "Run a power flow on the *Power Flow Analysis* page to "
    "enable voltage-band and loading checks.":
        "Berechnen Sie auf der Seite *Lastflussanalyse* einen Lastfluss, um "
        "die Prüfungen von Spannungsband und Auslastung zu aktivieren.",
    "Model limitations to keep in mind":
        "Zu beachtende Modellgrenzen",

    # --- validation -----------------------------------------------------
    "No slack source": "Keine Slack-Quelle",
    "The network has neither an external grid nor a slack generator. "
    "A power flow cannot balance the system without a slack bus.":
        "Das Netz enthält weder ein vorgelagertes Netz noch einen "
        "Slack-Generator. Ohne Slack-Knoten kann ein Lastfluss das System "
        "nicht bilanzieren.",
    "{n} unsupplied bus(es)": "{n} nicht versorgte(r) Knoten",
    "These buses have no electrical path to a slack source "
    "(considering switch states and in-service flags): "
    "{buses}. "
    "Power flow treats them as isolated.":
        "Diese Knoten haben keinen elektrischen Pfad zu einer Slack-Quelle "
        "(unter Berücksichtigung der Schaltzustände und des "
        "Betriebszustands): {buses}. "
        "Der Lastfluss behandelt sie als isoliert.",
    "All buses are supplied": "Alle Knoten sind versorgt",
    "Every in-service bus is topologically connected to a slack source.":
        "Jeder in Betrieb befindliche Knoten ist topologisch mit einer "
        "Slack-Quelle verbunden.",
    "Network splits into {n} islands": "Das Netz zerfällt in {n} Inseln",
    "With the current switch states the network graph is not a "
    "single connected component. Islands without their own slack "
    "source cannot be solved.":
        "Bei den aktuellen Schaltzuständen ist der Netzgraph nicht "
        "zusammenhängend. Inseln ohne eigene Slack-Quelle können nicht "
        "berechnet werden.",
    "Elements out of service": "Betriebsmittel außer Betrieb",
    "The following elements are switched off and ignored by "
    "analyses: {elements}.":
        "Die folgenden Betriebsmittel sind abgeschaltet und werden bei den "
        "Analysen ignoriert: {elements}.",
    "Missing values in {table}.{col}": "Fehlende Werte in {table}.{col}",
    "{n} of {total} entries are NaN. "
    "This parameter is required for power-flow modelling.":
        "{n} von {total} Einträgen sind NaN. "
        "Dieser Parameter wird für die Lastflussmodellierung benötigt.",
    "{n} line(s) with non-positive length":
        "{n} Leitung(en) mit nicht positiver Länge",
    "Zero or negative lengths usually indicate data errors and "
    "distort impedances.":
        "Null oder negative Längen deuten meist auf Datenfehler hin und "
        "verfälschen die Impedanzen.",
    "No geographic coordinates": "Keine Geokoordinaten",
    "The bus table has no geodata; the topology page falls back to "
    "an automatically computed layout.":
        "Die Knotentabelle enthält keine Geodaten; die Topologieseite "
        "verwendet ersatzweise ein automatisch berechnetes Layout.",
    "Partial geographic coordinates": "Unvollständige Geokoordinaten",
    "Only {n} of {total} buses carry geodata.":
        "Nur {n} von {total} Knoten besitzen Geodaten.",
    "Last power flow did not converge":
        "Der letzte Lastfluss ist nicht konvergiert",
    "Solver message: {error}. All result-based "
    "checks are skipped; the result tables are not meaningful.":
        "Meldung des Lösers: {error}. Alle ergebnisbasierten Prüfungen "
        "entfallen; die Ergebnistabellen sind nicht aussagekräftig.",
    "unknown": "unbekannt",
    "No power-flow results yet": "Noch keine Lastflussergebnisse",
    "Run a power flow on the *Power Flow Analysis* page to enable "
    "voltage and loading checks.":
        "Berechnen Sie auf der Seite *Lastflussanalyse* einen Lastfluss, um "
        "die Prüfungen von Spannung und Auslastung zu aktivieren.",
    "{n} buses below {limit} p.u. "
    "(worst: {worst:.4f} p.u.)":
        "{n} Knoten unter {limit} p.u. "
        "(schlechtester Wert: {worst:.4f} p.u.)",
    "{n} buses above {limit} p.u. "
    "(worst: {worst:.4f} p.u.)":
        "{n} Knoten über {limit} p.u. "
        "(schlechtester Wert: {worst:.4f} p.u.)",
    "Voltage-band violations": "Verletzungen des Spannungsbands",
    "All bus voltages within the configured band":
        "Alle Knotenspannungen innerhalb des eingestellten Bands",
    "{n} overloaded lines": "{n} überlastete Leitungen",
    "{n} overloaded transformers": "{n} überlastete Transformatoren",
    "Loading above {limit} % "
    "(worst: {worst:.1f} %). Sustained overloading accelerates "
    "ageing and may trip protection.":
        "Auslastung über {limit} % "
        "(Maximum: {worst:.1f} %). Dauerhafte Überlastung beschleunigt die "
        "Alterung und kann den Schutz auslösen.",
    "No overloaded lines": "Keine überlasteten Leitungen",
    "No overloaded transformers": "Keine überlasteten Transformatoren",
    "All lines are at or below {limit} % loading.":
        "Alle Leitungen liegen bei höchstens {limit} % Auslastung.",
    "All transformers are at or below {limit} % loading.":
        "Alle Transformatoren liegen bei höchstens {limit} % Auslastung.",
}
