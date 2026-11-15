import json
import argparse
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DEFAULT = "rapport_red_team.pdf"

COLOR_DARK = colors.HexColor("#172554")
COLOR_BLUE = colors.HexColor("#2563EB")
COLOR_LIGHT = colors.HexColor("#EFF6FF")
COLOR_GREY = colors.HexColor("#64748B")
COLOR_RED = colors.HexColor("#DC2626")
COLOR_ORANGE = colors.HexColor("#D97706")
COLOR_GREEN = colors.HexColor("#15803D")
COLOR_BORDER = colors.HexColor("#CBD5E1")


def get_value(data, *keys, default=None):
    """Safely retrieve a nested JSON value."""
    current = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


LEVEL_FR = {
    "CRITICAL": "CRITICAL (Critique)",
    "HIGH": "HIGH (Élevé)",
    "MEDIUM": "MEDIUM (Moyen)",
    "LOW": "LOW (Faible)",
}


def level_fr(value):
    return LEVEL_FR.get(str(value).upper(), value)


def get_test(data, name):
    """Return a conventional test of the attacker agent by name."""
    tests = get_value(data, "agents", "2_attacker", "evidence", "tests", default=[])
    return next((t for t in tests if t.get("name") == name), {})


def split_findings(findings):
    """Separate real vulnerabilities from controls that were validated."""
    vulns = [f for f in findings if f.get("type") != "validated_control"]
    controls = [f for f in findings if f.get("type") == "validated_control"]
    return vulns, controls


def display(value):
    """Display only values actually present in the JSON."""
    if value is None or value == "":
        return "Non renseigné dans les résultats"

    if isinstance(value, bool):
        return "Oui" if value else "Non"

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def safe(value):
    """Escape content before inserting it into a ReportLab Paragraph."""
    return escape(display(value))


def make_paragraph(text, style):
    return Paragraph(text, style)


def add_paragraph(story, text, style):
    story.append(make_paragraph(text, style))
    story.append(Spacer(1, 6))


def add_bullet(story, text, styles):
    add_paragraph(
        story,
        "• " + safe(text),
        styles["Body"]
    )


def add_section(story, number, title, styles):
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f"{number}. {escape(title)}",
            styles["Section"]
        )
    )
    story.append(Spacer(1, 8))


def add_subsection(story, title, styles):
    story.append(Spacer(1, 7))
    story.append(
        Paragraph(
            escape(title),
            styles["Subsection"]
        )
    )
    story.append(Spacer(1, 5))


def add_table(story, headers, rows, widths=None):
    """Create a table with consistent formatting."""

    data = [
        [Paragraph(f"<b>{safe(h)}</b>", get_styles()["TableHeader"])
         for h in headers]
    ]

    for row in rows:
        data.append([
            Paragraph(safe(cell), get_styles()["TableCell"])
            for cell in row
        ])

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT"
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, COLOR_LIGHT]),
    ]))

    story.append(table)
    story.append(Spacer(1, 10))


# ============================================================
# STYLES
# ============================================================

_STYLES = None


def get_styles():
    global _STYLES

    if _STYLES:
        return _STYLES

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=29,
        textColor=COLOR_DARK,
        alignment=TA_CENTER,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=COLOR_GREY,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=15,
        leading=20,
        textColor=COLOR_DARK,
        spaceBefore=10,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontSize=11,
        leading=15,
        textColor=COLOR_BLUE,
        spaceBefore=6,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=COLOR_GREY
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=10
    ))

    styles.add(ParagraphStyle(
        name="RiskScore",
        parent=styles["Title"],
        fontSize=30,
        leading=35,
        alignment=TA_CENTER,
        textColor=COLOR_DARK
    ))

    _STYLES = styles
    return styles


# ============================================================
# COVER PAGE AND RISK SCORE
# ============================================================

def build_cover(story, data):
    styles = get_styles()

    project = display(data.get("project"))
    generated_at = display(data.get("generated_at"))
    scope = display(data.get("scope"))

    story.append(Spacer(1, 3 * cm))

    story.append(Paragraph(
        "RAPPORT D'ANALYSE<br/>RED TEAM",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        safe(project),
        styles["Subtitle"]
    ))

    story.append(Spacer(1, 2 * cm))

    risk = data.get("final_risk", {})
    score = risk.get("score")
    severity = risk.get("severity")

    if score is not None:
        story.append(Paragraph(
            f"{float(score):.3f} / 1.000",
            styles["RiskScore"]
        ))

        story.append(Paragraph(
            f"Niveau de risque : {safe(severity)}",
            styles["Subtitle"]
        ))
    else:
        story.append(Paragraph(
            "Score de risque non renseigné",
            styles["RiskScore"]
        ))

    story.append(Spacer(1, 2 * cm))

    add_table(
        story,
        ["Information", "Valeur"],
        [
            ["Projet", project],
            ["Date de génération", generated_at],
            ["Périmètre", scope],
        ],
        [5 * cm, 11 * cm]
    )

    story.append(Spacer(1, 2 * cm))

    story.append(Paragraph(
        "Epitalab © 2026",
        styles["Subtitle"]
    ))

    story.append(PageBreak())


# ============================================================
# RISK ASSESSMENT
# ============================================================

def build_risk(story, data):
    styles = get_styles()
    risk = data.get("final_risk", {})

    add_section(story, "0", "Résultat global et score de risque", styles)

    score = risk.get("score")
    severity = risk.get("severity")

    if score is not None:
        add_paragraph(
            story,
            f"<b>Score de risque :</b> {float(score):.3f} / 1.000",
            styles["Body"]
        )
    else:
        add_paragraph(
            story,
            "<b>Score de risque :</b> Non renseigné dans les résultats",
            styles["Body"]
        )

    add_paragraph(
        story,
        f"<b>Niveau :</b> {safe(severity)}",
        styles["Body"]
    )

    add_paragraph(
        story,
        f"<b>Échelle :</b> {safe(risk.get('scale'))}",
        styles["Body"]
    )

    add_paragraph(
        story,
        f"<b>Formule :</b> {safe(risk.get('formula'))}",
        styles["Body"]
    )

    factors = risk.get("factors", {})

    if factors:
        add_subsection(story, "Facteurs du score", styles)

        rows = [
            [key, value]
            for key, value in factors.items()
        ]

        add_table(
            story,
            ["Facteur", "Valeur"],
            rows,
            [9 * cm, 7 * cm]
        )

    findings, validated_controls = split_findings(risk.get("findings", []))

    add_subsection(story, "Hiérarchisation des vulnérabilités", styles)

    if findings:
        priority_order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3
        }

        findings = sorted(
            findings,
            key=lambda item: priority_order.get(
                str(item.get("priority", "")).upper(),
                4
            )
        )

        rows = []

        for rank, finding in enumerate(findings, start=1):
            rows.append([
                rank,
                finding.get("id"),
                finding.get("title"),
                level_fr(finding.get("priority")),
                finding.get("evidence")
            ])

        add_table(
            story,
            [
                "Rang",
                "ID",
                "Vulnérabilité / constat",
                "Niveau",
                "Preuve"
            ],
            rows,
            [
                1.2 * cm,
                2.3 * cm,
                5.5 * cm,
                2.7 * cm,
                4.3 * cm
            ]
        )
    else:
        add_paragraph(
            story,
            "Aucun finding détaillé n'est renseigné dans le JSON.",
            styles["Body"]
        )

    if validated_controls:
        add_subsection(story, "Contrôles validés (non classés comme vulnérabilités)", styles)

        for control in validated_controls:
            add_bullet(
                story,
                f"{control.get('id')} - {control.get('title')} : "
                f"{control.get('evidence')}",
                styles
            )

    add_paragraph(
        story,
        "<b>Portée :</b> ces constats concernent uniquement le simulateur "
        "local et des données synthétiques ; ils ne prouvent pas une faille "
        "sur un système bancaire en production.",
        styles["Small"]
    )

    limitations = risk.get("limitations", [])

    if limitations:
        add_subsection(story, "Limites du score", styles)

        for item in limitations:
            add_bullet(story, item, styles)


# ============================================================
# 1. TARGET
# ============================================================

def build_target(story, data):
    styles = get_styles()

    add_section(story, "1", "La cible", styles)

    recon = get_value(
        data, "agents", "1_reconnaissance", "evidence",
        default={}
    )

    add_subsection(story, "1.1 Systèmes visés", styles)

    add_paragraph(
        story,
        f"<b>Cible :</b> {safe(recon.get('target'))}",
        styles["Body"]
    )

    add_paragraph(
        story,
        f"<b>URL :</b> {safe(recon.get('base_url'))}",
        styles["Body"]
    )

    health = recon.get("health", {})

    if health:
        add_paragraph(
            story,
            f"<b>État du service :</b> {safe(health.get('status'))}",
            styles["Body"]
        )

    endpoints = recon.get("endpoints", [])

    add_subsection(story, "1.2 Interfaces API observées", styles)

    if endpoints:
        rows = [
            [
                endpoint.get("method"),
                endpoint.get("path"),
                endpoint.get("summary")
            ]
            for endpoint in endpoints
        ]

        add_table(
            story,
            ["Méthode", "Endpoint", "Description"],
            rows,
            [3 * cm, 7 * cm, 6 * cm]
        )
    else:
        add_paragraph(
            story,
            "Aucun endpoint renseigné.",
            styles["Body"]
        )

    add_subsection(story, "1.3 Flux de données", styles)

    incoming = []
    outgoing = []

    for endpoint in endpoints:
        method = str(endpoint.get("method", "")).upper()
        path = endpoint.get("path", "")

        if method in ("POST", "PUT", "PATCH"):
            incoming.append(f"{method} {path}")

        elif method == "GET":
            outgoing.append(f"{method} {path}")

    add_paragraph(
        story,
        "<b>Flux entrants (classification basée sur la méthode HTTP) :</b>",
        styles["Body"]
    )

    for item in incoming:
        add_bullet(story, item, styles)

    add_paragraph(
        story,
        "<b>Flux sortants (classification basée sur la méthode HTTP) :</b>",
        styles["Body"]
    )

    for item in outgoing:
        add_bullet(story, item, styles)

    if not incoming and not outgoing:
        add_paragraph(
            story,
            "Les flux ne sont pas renseignés.",
            styles["Body"]
        )

    add_subsection(story, "1.4 Architecture interne et flux internes", styles)

    architecture = get_value(data, "manual_context", "architecture", default={})

    if architecture.get("components") or architecture.get("internal_flows"):
        for item in architecture.get("components", []):
            add_bullet(story, item, styles)

        for item in architecture.get("internal_flows", []):
            add_bullet(story, item, styles)
    else:
        add_paragraph(
            story,
            "Non documenté : l'architecture interne (API, base de données, "
            "modèle IA) n'est pas décrite dans le JSON "
            "(manual_context.architecture).",
            styles["Body"]
        )

    add_subsection(story, "1.5 Périmètre et limites", styles)

    add_paragraph(
        story,
        f"<b>Périmètre :</b> {safe(data.get('scope'))}",
        styles["Body"]
    )

    for limitation in recon.get("limitations", []):
        add_bullet(story, limitation, styles)

    dependencies = recon.get("observed_dependencies", [])

    if dependencies:
        add_subsection(story, "Dépendances observées", styles)

        add_paragraph(
            story,
            ", ".join(escape(str(item)) for item in dependencies),
            styles["Small"]
        )


# ============================================================
# 2. AGENTS
# ============================================================

def build_agents(story, data):
    styles = get_styles()

    add_section(story, "2", "L'équipe : les agents", styles)

    agents = data.get("agents", {})

    agent_descriptions = {
        "1_reconnaissance": (
            "Agent de reconnaissance",
            "Inventaire de la cible, de l'état du service, "
            "des endpoints API et des dépendances observées."
        ),
        "2_attacker": (
            "Agent attaquant",
            "Exécution des tests de soumission de transactions "
            "synthétiques et de validation des entrées."
        ),
        "3_ai_adversary": (
            "Agent adversaire IA",
            "Perturbation contrôlée des caractéristiques des "
            "transactions et observation des changements de score."
        ),
        "4_compliance_breaker": (
            "Agent conformité",
            "Examen préliminaire des contrôles DORA, MiCA, "
            "GDPR et EU AI Act à partir des éléments fournis."
        ),
        "5_impact_risk_scoring": (
            "Agent évaluation des risques",
            "Calcul du score de risque et hiérarchisation "
            "des constats."
        )
    }

    rows = []

    for key, agent_data in agents.items():
        name, role = agent_descriptions.get(
            key,
            (key, "Rôle détaillé non renseigné dans les résultats.")
        )

        rows.append([
            name,
            role,
            "Présent" if isinstance(agent_data, dict) else "Non renseigné"
        ])

    add_table(
        story,
        ["Agent", "Rôle identifié", "Données"],
        rows,
        [4 * cm, 9 * cm, 3 * cm]
    )

    add_subsection(story, "2.1 Interactions entre les agents", styles)

    log = data.get("interaction_log", [])

    if log:
        add_paragraph(
            story,
            "L'orchestrateur exécute les agents dans l'ordre ci-dessous et "
            "transmet les preuves d'un agent aux suivants (colonne « Reçoit de »).",
            styles["Body"]
        )

        rows = []

        for entry in log:
            rows.append([
                entry.get("step"),
                entry.get("started_at"),
                f"{entry.get('duration_ms')} ms",
                entry.get("status"),
                ", ".join(entry.get("inputs_from", [])) or "-"
            ])

        add_table(
            story,
            ["Étape", "Début (UTC)", "Durée", "Statut", "Reçoit de"],
            rows,
            [4 * cm, 4.5 * cm, 2 * cm, 1.5 * cm, 4 * cm]
        )

        add_paragraph(
            story,
            "<b>Limite :</b> les agents ne s'échangent pas de messages "
            "directs ; seuls la séquence, les durées et les dépendances "
            "de données sont tracées.",
            styles["Small"]
        )
    else:
        add_paragraph(
            story,
            "Les résultats sont organisés en cinq blocs : reconnaissance, "
            "tests conventionnels, tests adversariaux IA, conformité et "
            "évaluation du risque.",
            styles["Body"]
        )

        add_paragraph(
            story,
            "<b>Limite :</b> le JSON ne contient pas de journal "
            "d'exécution (interaction_log).",
            styles["Body"]
        )


# ============================================================
# 3. ATTACK SCENARIOS
# ============================================================

def build_scenarios(story, data):
    styles = get_styles()

    add_section(story, "3", "Les scénarios d'attaque", styles)

    agents = data.get("agents", {})

    # --------------------------------------------------------
    # Scenario 1: conventional cyber attack
    # --------------------------------------------------------

    add_subsection(
        story,
        "3.1 Attaque cyber conventionnelle",
        styles
    )

    attacker = get_value(
        data, "agents", "2_attacker", "evidence",
        default={}
    )

    tests = attacker.get("tests", [])

    if tests:
        for test in tests:
            name = test.get("name", "Test non nommé")

            if name == "detection_and_audit_trail_check":
                continue  # présenté dans la section 4 (réaction et détection)

            add_paragraph(
                story,
                f"<b>Test :</b> {safe(name)}",
                styles["Body"]
            )

            if "http_status" in test:
                add_paragraph(
                    story,
                    f"<b>Statut HTTP :</b> {safe(test.get('http_status'))}",
                    styles["Body"]
                )

            if "accepted" in test:
                add_paragraph(
                    story,
                    f"<b>Transaction acceptée :</b> {safe(test.get('accepted'))}",
                    styles["Body"]
                )

            if "authorization_header_sent" in test:
                add_paragraph(
                    story,
                    "<b>En-tête Authorization envoyé :</b> "
                    + safe(test.get("authorization_header_sent")),
                    styles["Body"]
                )

            if "rejected_as_expected" in test:
                add_paragraph(
                    story,
                    "<b>Rejet attendu :</b> "
                    + safe(test.get("rejected_as_expected")),
                    styles["Body"]
                )

            response = test.get("response", {})
            transaction = response.get("transaction", {})

            if transaction:
                add_table(
                    story,
                    ["Élément", "Valeur observée"],
                    [
                        ["Transaction ID", transaction.get("id")],
                        ["Référence", transaction.get("transaction_ref")],
                        ["Montant", transaction.get("amount")],
                        ["Devise", transaction.get("currency")],
                        ["Classification", transaction.get("classification")],
                        ["Risk score", transaction.get("risk_score")],
                        ["Anomaly score", transaction.get("anomaly_score")]
                    ],
                    [6 * cm, 10 * cm]
                )

            explanation = response.get("explanation", [])

            if explanation:
                add_paragraph(
                    story,
                    "<b>Signaux de détection :</b>",
                    styles["Body"]
                )

                for item in explanation:
                    add_bullet(story, item, styles)

            if test.get("interpretation"):
                add_paragraph(
                    story,
                    f"<b>Interprétation fournie :</b> "
                    f"{safe(test.get('interpretation'))}",
                    styles["Body"]
                )

    else:
        add_paragraph(
            story,
            "Aucun test conventionnel détaillé dans le JSON.",
            styles["Body"]
        )

    submission = get_test(data, "synthetic_transaction_submission")

    if submission.get("accepted"):
        add_paragraph(
            story,
            "<b>Point de rupture :</b> la transaction synthétique a été "
            "acceptée (HTTP 200) sans en-tête d'authentification. "
            "Observation sur le simulateur local, pas une preuve de "
            "faille en production.",
            styles["Body"]
        )

    # --------------------------------------------------------
    # Scenario 2: AI / data attack
    # --------------------------------------------------------

    add_subsection(
        story,
        "3.2 Attaque ciblant l'IA et les données",
        styles
    )

    ai = get_value(
        data, "agents", "3_ai_adversary", "evidence",
        default={}
    )

    ai_tests = ai.get("tests", [])

    if ai_tests:
        for test in ai_tests:
            add_paragraph(
                story,
                f"<b>Test :</b> {safe(test.get('test'))}",
                styles["Body"]
            )

            baseline = test.get("baseline", {})
            perturbed = test.get("perturbed", {})

            add_table(
                story,
                ["Indicateur", "Baseline", "Perturbé"],
                [
                    [
                        "Risk score",
                        baseline.get("risk_score"),
                        perturbed.get("risk_score")
                    ],
                    [
                        "Classification",
                        baseline.get("classification"),
                        perturbed.get("classification")
                    ]
                ],
                [5 * cm, 5.5 * cm, 5.5 * cm]
            )

            add_paragraph(
                story,
                "<b>Variation du score :</b> "
                + safe(test.get("risk_score_delta")),
                styles["Body"]
            )

            add_paragraph(
                story,
                "<b>Changement de classification :</b> "
                + safe(test.get("classification_changed")),
                styles["Body"]
            )

    else:
        add_paragraph(
            story,
            "Aucun test de perturbation IA détaillé dans le JSON.",
            styles["Body"]
        )

    ai_deltas = [
        abs(float(t.get("risk_score_delta", 0))) for t in ai_tests
    ]

    if ai_tests:
        add_paragraph(
            story,
            "<b>Point de faiblesse :</b> variation maximale du score de "
            f"{max(ai_deltas):.2f} pour une petite modification des données, "
            "sans changement de classification. C'est une sensibilité du "
            "modèle, pas une évasion démontrée. Il s'agit d'une perturbation "
            "des entrées, pas d'un empoisonnement de données.",
            styles["Body"]
        )

        saturated = [
            v for t in ai_tests
            for v in (
                t.get("baseline", {}).get("anomaly_score"),
                t.get("perturbed", {}).get("anomaly_score")
            ) if v is not None and v >= 0.999
        ]

        if saturated:
            add_paragraph(
                story,
                f"<b>À vérifier :</b> le score d'anomalie Isolation Forest "
                f"vaut 1.0 dans {len(saturated)} cas sur "
                f"{2 * len(ai_tests)}, y compris pour des transactions de "
                "référence sans règle déclenchée.",
                styles["Body"]
            )

    if ai.get("interpretation_note"):
        add_paragraph(
            story,
            "<b>Limite d'interprétation :</b> "
            + safe(ai.get("interpretation_note")),
            styles["Body"]
        )

    # --------------------------------------------------------
    # Robustness evaluation
    # --------------------------------------------------------

    robustness = get_value(
        data, "stage", "robustness", default={}
    )

    add_subsection(
        story,
        "3.3 Résultats des tests de robustesse",
        styles
    )

    if robustness:
        add_table(
            story,
            ["Indicateur", "Résultat"],
            [
                ["Version du modèle", robustness.get("model_version")],
                ["Taille de la cohorte", robustness.get("cohort_size")],
                ["Cas réussis", robustness.get("passed_cases")],
                ["Taux de réussite", robustness.get("scenario_pass_rate")],
                ["Précision synthétique", robustness.get("synthetic_precision")],
                ["Rappel synthétique", robustness.get("synthetic_recall")]
            ],
            [8 * cm, 8 * cm]
        )

        cases = robustness.get("cases", [])

        if cases:
            add_subsection(
                story,
                "Détail des cas évalués",
                styles
            )

            rows = []

            for case in cases:
                rows.append([
                    case.get("case_id"),
                    case.get("expected"),
                    case.get("actual"),
                    case.get("risk_score"),
                    case.get("passed")
                ])

            add_table(
                story,
                ["Cas", "Attendu", "Obtenu", "Score", "Réussi"],
                rows,
                [4 * cm, 3 * cm, 3 * cm, 2.5 * cm, 3.5 * cm]
            )

        counts = robustness.get("confusion_counts", {})

        if counts:
            add_subsection(
                story,
                "Matrice de confusion",
                styles
            )

            add_table(
                story,
                ["Indicateur", "Valeur"],
                [[key.upper(), value] for key, value in counts.items()],
                [8 * cm, 8 * cm]
            )

    else:
        add_paragraph(
            story,
            "Aucun résultat de robustesse disponible.",
            styles["Body"]
        )


# ============================================================
# 4. ARMS REACTION AND DETECTION
# ============================================================

def build_reaction(story, data):
    styles = get_styles()

    add_section(story, "4", "La réaction du système ARMS", styles)

    attacker = get_value(
        data, "agents", "2_attacker", "evidence",
        default={}
    )

    tests = attacker.get("tests", [])

    add_subsection(
        story,
        "4.1 Réaction aux tests conventionnels",
        styles
    )

    if tests:
        rows = []

        for test in tests:
            if test.get("name") == "detection_and_audit_trail_check":
                continue  # détaillé en 4.2

            rows.append([
                test.get("name"),
                test.get("http_status"),
                test.get("accepted", test.get("rejected_as_expected"))
            ])

        add_table(
            story,
            ["Test", "HTTP", "Résultat observé"],
            rows,
            [7 * cm, 3 * cm, 6 * cm]
        )

    # Detection result
    add_subsection(
        story,
        "4.2 Détection des transactions",
        styles
    )

    transaction = None

    for test in tests:
        transaction = get_value(
            test, "response", "transaction"
        )

        if transaction:
            break

    if transaction:
        add_table(
            story,
            ["Indicateur", "Résultat"],
            [
                ["Classification", transaction.get("classification")],
                ["Risk score", transaction.get("risk_score")],
                ["Anomaly score", transaction.get("anomaly_score")],
                ["Statut", transaction.get("status")],
                ["Version du modèle", transaction.get("model_version")]
            ],
            [7 * cm, 9 * cm]
        )
    else:
        add_paragraph(
            story,
            "Aucune réponse de transaction contenant un résultat "
            "de classification n'est disponible.",
            styles["Body"]
        )

    trail = get_test(data, "detection_and_audit_trail_check")

    if trail:
        detected = (
            transaction or {}
        ).get("classification") == "SUSPICIOUS" and trail.get("listed_in_alerts")

        add_paragraph(
            story,
            "<b>Détection :</b> "
            + ("Oui. La transaction a été classée SUSPICIOUS et apparaît "
               "dans /alerts." if detected else
               "Non confirmée pour la transaction de test.")
            + (" ARMS n'a pas bloqué la transaction (détection sans blocage)."
               if not trail.get("attack_blocked") else ""),
            styles["Body"]
        )

        alert = trail.get("matching_alert") or {}

        add_table(
            story,
            ["Élément", "Valeur observée"],
            [
                ["Référence de la transaction", trail.get("transaction_ref")],
                ["Présente dans /alerts", trail.get("listed_in_alerts")],
                ["Alerte (id)", alert.get("id")],
                ["Score de l'alerte", alert.get("risk_score")],
                ["Délai de détection (borne haute)",
                 f"{trail.get('detection_latency_ms_upper_bound')} ms"],
                ["Événements d'audit",
                 ", ".join(trail.get("audit_events_for_transaction", []))],
                ["Attaque bloquée", trail.get("attack_blocked")],
                ["Mécanisme de notification", trail.get("notification_mechanism")]
            ],
            [6 * cm, 10 * cm]
        )

        add_paragraph(
            story,
            "Le délai mesuré inclut les appels API (borne haute). "
            "La corrélation attaque / alerte porte sur la transaction de "
            "test principale uniquement.",
            styles["Small"]
        )

    # AI robustness
    robustness = get_value(
        data, "stage", "robustness", default={}
    )

    if robustness:
        add_subsection(
            story,
            "4.3 Détection des scénarios synthétiques",
            styles
        )

        add_paragraph(
            story,
            f"<b>Cas réussis :</b> "
            f"{safe(robustness.get('passed_cases'))} / "
            f"{safe(robustness.get('cohort_size'))}",
            styles["Body"]
        )

        add_paragraph(
            story,
            f"<b>Taux de réussite :</b> "
            f"{safe(robustness.get('scenario_pass_rate'))}",
            styles["Body"]
        )

        counts = robustness.get("confusion_counts", {})

        if counts:
            add_paragraph(
                story,
                f"<b>Faux négatifs (FN) :</b> {safe(counts.get('fn'))}",
                styles["Body"]
            )

    false_negatives = [
        c for c in robustness.get("cases", [])
        if c.get("expected") == "SUSPICIOUS" and c.get("actual") != "SUSPICIOUS"
    ]

    if false_negatives:
        add_subsection(story, "4.4 Causes des faux négatifs", styles)

        add_table(
            story,
            ["Cas", "Score", "Écart au seuil", "Règles déclenchées", "Cause"],
            [
                [
                    c.get("case_id"),
                    c.get("risk_score"),
                    c.get("gap_to_threshold"),
                    "; ".join(c.get("triggered_rules", [])),
                    c.get("cause")
                ]
                for c in false_negatives
            ],
            [3 * cm, 1.5 * cm, 2 * cm, 4.5 * cm, 5 * cm]
        )

    add_paragraph(
        story,
        "<b>Limite :</b> les résultats concernent le simulateur local "
        "et des transactions synthétiques. Ils ne démontrent pas "
        "le comportement d'un système de production.",
        styles["Body"]
    )


# ============================================================
# 5. REGULATORY GAP
# ============================================================

def build_compliance(story, data):
    styles = get_styles()

    add_section(
        story,
        "5",
        "Le problème réglementaire : Gap réglementaire",
        styles
    )

    matrix = get_value(
        data, "stage", "regulatory_matrix", default={}
    )

    controls = matrix.get("controls", [])

    compliance_agent = get_value(
        data, "agents", "4_compliance_breaker", "evidence",
        default={}
    )

    if controls:
        rows = []

        for control in controls:
            framework = control.get("framework")

            # The expected framework is DORA or MiCA.
            if framework not in ("DORA", "MiCA"):
                continue

            rows.append([
                framework,
                control.get("reference"),
                control.get("theme"),
                control.get("status_rule"),
                control.get("note")
            ])

        if rows:
            add_table(
                story,
                [
                    "Cadre",
                    "Référence",
                    "Thème",
                    "Statut",
                    "Éléments observés"
                ],
                rows,
                [
                    2 * cm,
                    2.5 * cm,
                    3 * cm,
                    2.5 * cm,
                    6.5 * cm
                ]
            )
        else:
            add_paragraph(
                story,
                "Aucun contrôle DORA ou MiCA n'est renseigné.",
                styles["Body"]
            )

    else:
        # Fallback to compliance agent controls
        controls = compliance_agent.get("controls", [])

        if controls:
            rows = []

            for control in controls:
                if control.get("framework") not in ("DORA", "MiCA"):
                    continue

                rows.append([
                    control.get("framework"),
                    control.get("control"),
                    control.get("status"),
                    control.get("evidence")
                ])

            if rows:
                add_table(
                    story,
                    ["Cadre", "Contrôle", "Statut", "Preuve"],
                    rows,
                    [2 * cm, 5 * cm, 3 * cm, 6.5 * cm]
                )
        else:
            add_paragraph(
                story,
                "Aucune donnée réglementaire disponible.",
                styles["Body"]
            )

    add_subsection(story, "Où le système a-t-il failli ?", styles)

    submission = get_test(data, "synthetic_transaction_submission")
    robustness = get_value(data, "stage", "robustness", default={})
    trail = get_test(data, "detection_and_audit_trail_check")
    dora = {c.get("reference"): c for c in controls if c.get("framework") == "DORA"}

    if "Article 9" in dora:
        add_bullet(
            story,
            "DORA Article 9 (protection et prévention) : statut "
            f"{dora['Article 9'].get('status_rule')}. "
            + ("Une transaction synthétique a été acceptée sans "
               "authentification (HTTP 200) ; le contrôle d'accès est à "
               "revoir." if submission.get("accepted") else
               "Aucune acceptation sans authentification observée."),
            styles
        )

    if "Article 10" in dora:
        add_bullet(
            story,
            "DORA Article 10 (détection) : statut "
            f"{dora['Article 10'].get('status_rule')}. "
            f"Rappel synthétique {robustness.get('synthetic_recall')} "
            f"({get_value(robustness, 'confusion_counts', 'fn')} faux "
            "négatifs) : la détection est partielle.",
            styles
        )

    if "Article 17" in dora:
        add_bullet(
            story,
            "DORA Article 17 (incidents) : statut "
            f"{dora['Article 17'].get('status_rule')}. "
            + ("Des événements d'audit existent ("
               + ", ".join(trail.get("audit_events_for_transaction", []))
               + ") ; " if trail else "")
            + "conservation, intégrité et escalade non testées.",
            styles
        )

    mica_scope = get_value(
        data, "manual_context", "mica", "crypto_asset_services_in_scope"
    )

    add_bullet(
        story,
        "MiCA : aucune conclusion possible. "
        + ("L'applicabilité n'est pas documentée (services sur "
           "crypto-actifs non confirmés)." if mica_scope is None else
           f"Services sur crypto-actifs dans le périmètre : "
           f"{display(mica_scope)}."),
        styles
    )

    if matrix.get("disclaimer"):
        add_paragraph(
            story,
            "<b>Réserve :</b> " + safe(matrix.get("disclaimer")),
            styles["Small"]
        )

    scope = compliance_agent.get("assessment_scope")

    if scope:
        add_paragraph(
            story,
            "<b>Périmètre de l'évaluation :</b> " + safe(scope),
            styles["Body"]
        )

    # not_tested = compliance_agent.get("not_tested", [])

    # if not_tested:
    #     add_subsection(
    #         story,
    #         "Contrôles non testés",
    #         styles
    #     )

    #     for item in not_tested:
    #         add_bullet(story, item, styles)

    # add_paragraph(
    #     story,
    #     "<b>Interprétation :</b> un statut REVIEW_REQUIRED ou "
    #     "NOT_ASSESSED ne constitue pas, à lui seul, une preuve "
    #     "de non-conformité réglementaire. Les résultats fournis "
    #     "sont des observations préliminaires sur un simulateur.",
    #     styles["Body"]
    # )


# ============================================================
# 6. RECOMMENDATIONS
# ============================================================

def build_recommendations(story, data):
    styles = get_styles()

    add_section(
        story,
        "6",
        "Les solutions : recommandations",
        styles
    )

    findings, validated_controls = split_findings(
        get_value(data, "final_risk", "findings", default=[])
    )

    if findings:
        priority_order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3
        }

        findings = sorted(
            findings,
            key=lambda item: priority_order.get(
                str(item.get("priority", "")).upper(),
                4
            )
        )

        for finding in findings:
            title = finding.get("title", "Constat non nommé")
            priority = finding.get("priority")
            remediation = finding.get("remediation")
            evidence = finding.get("evidence")

            add_subsection(
                story,
                f"{finding.get('id', '')} - {title} ({level_fr(priority)})",
                styles
            )

            add_paragraph(
                story,
                f"<b>Preuve :</b> {safe(evidence)}",
                styles["Body"]
            )

            add_paragraph(
                story,
                f"<b>Action corrective :</b> {safe(remediation)}",
                styles["Body"]
            )

    else:
        add_paragraph(
            story,
            "Aucune recommandation détaillée n'est disponible "
            "dans final_risk.findings.",
            styles["Body"]
        )

    if validated_controls:
        add_subsection(story, "Contrôles à maintenir", styles)

        for control in validated_controls:
            add_bullet(
                story,
                f"{control.get('id')} - {control.get('title')} : "
                f"{control.get('remediation')}",
                styles
            )

    # add_subsection(story, "Suivi des corrections", styles)

    # tracking = get_value(data, "manual_context", "remediation_tracking", default=[])

    # if tracking:
    #     add_table(
    #         story,
    #         ["Constat", "Responsable", "Échéance", "Statut", "Validé par"],
    #         [
    #             [
    #                 t.get("finding_id"),
    #                 t.get("owner") or "Non documenté",
    #                 t.get("due_date") or "Non documenté",
    #                 t.get("status") or "Non documenté",
    #                 t.get("validated_by") or "Non documenté"
    #             ]
    #             for t in tracking
    #         ],
    #         [3 * cm, 3.5 * cm, 3 * cm, 3.5 * cm, 3 * cm]
    #     )
    # else:
    #     add_paragraph(
    #         story,
    #         "Non documenté : responsables, échéances et validation des "
    #         "corrections ne sont pas fournis dans le JSON "
    #         "(manual_context.remediation_tracking).",
    #         styles["Body"]
    #     )

    add_subsection(
        story,
        "Observations réglementaires associées (DORA, MiCA)",
        styles
    )

    # These are taken from the remediation fields of the JSON.
    compliance_controls = get_value(
        data,
        "agents",
        "4_compliance_breaker",
        "evidence",
        "controls",
        default=[]
    )

    for control in compliance_controls:
        if control.get("framework") not in ("DORA", "MiCA"):
            continue

        evidence = control.get("evidence")

        if evidence:
            add_paragraph(
                story,
                f"<b>{safe(control.get('framework'))} - "
                f"{safe(control.get('control'))} :</b> "
                f"{safe(evidence)}",
                styles["Body"]
            )
 

 

# ============================================================
# PDF FOOTER
# ============================================================

def add_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setStrokeColor(COLOR_BORDER)
    canvas.line(
        2 * cm,
        1.5 * cm,
        width - 2 * cm,
        1.5 * cm
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLOR_GREY)

    canvas.drawString(
        2 * cm,
        1 * cm,
        "Epitalab © 2026 - Rapport Red Team"
    )

    canvas.drawRightString(
        width - 2 * cm,
        1 * cm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report(json_path, output_path):
    json_path = Path(json_path)
    output_path = Path(output_path)

    if not json_path.exists():
        raise FileNotFoundError(
            f"Fichier JSON introuvable : {json_path}"
        )

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Le fichier JSON doit contenir un objet JSON."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title="Rapport Agentic Red Team - ARMS",
        author="Epitalab"
    )

    story = []

    # Cover
    build_cover(story, data)

    # Requested analysis framework
    build_risk(story, data)
    build_target(story, data)
    build_agents(story, data)
    build_scenarios(story, data)
    build_reaction(story, data)
    build_compliance(story, data)
    build_recommendations(story, data)
 

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    print(f"Rapport généré : {output_path.resolve()}")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Génération du rapport Red Team ARMS depuis JSON."
    )

    parser.add_argument(
        "json_file",
        nargs="?",
        default="report.json",
        help="Chemin du fichier JSON source."
    )

    parser.add_argument(
        "--output",
        default=OUTPUT_DEFAULT,
        help="Chemin du PDF de sortie."
    )

    args = parser.parse_args()

    try:
        generate_report(
            args.json_file,
            args.output
        )

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"Erreur : {error}")
        raise SystemExit(1)