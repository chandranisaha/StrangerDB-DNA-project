#!/usr/bin/env python3

"""
HNL OPS-CONSOLE v4.2 — StrangerDB interactive terminal.
Implements the Phase-4 functional requirements on top of the Phase-3 schema.
"""

import sys
import time
import math
import textwrap
from getpass import getpass

import pymysql
from colorama import Fore, Style, init as colorama_init

DB_HOST = 'localhost'
DB_NAME = 'strangerdb'

colorama_init(autoreset=True)


def slow_print(message, delay=0.005, newline=True):
    """Lightweight typing animation for immersion."""
    for ch in message:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        sys.stdout.write("\n")


def header():
    print(Fore.CYAN + "=" * 70)
    print(Fore.YELLOW + "  HAWKINS NATIONAL LAB — OPS CONSOLE v4.2")
    print(Fore.GREEN + "  Interdimensional Anomaly Monitoring System — CLASSIFIED")
    print(Fore.CYAN + "=" * 70 + "\n")


def boot_sequence():
    header()
    slow_print(Fore.MAGENTA + "[BOOT] Initializing UpsideDown frequency scanner...")
    time.sleep(0.25)
    slow_print(Fore.MAGENTA + "[OK] Psychokinetic telemetry link stable.")
    slow_print(Fore.YELLOW + "[WARN] Portal C shows elevated distortion.")
    print()


def get_db_connection(user, password, host=DB_HOST, db=DB_NAME):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        # Set isolation level to READ COMMITTED to see latest changes from other connections
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        conn.commit()
        print(Fore.GREEN + "[DB] Connected to strangerdb.")
        return conn
    except pymysql.Error as exc:
        print(Fore.RED + f"[DB] Connection error: {exc}", file=sys.stderr)
        return None


# ----------------------- ANALYTIC (READ) MODULES ----------------------- #
def portal_stability_scanner(conn):
    conn.commit()  # Refresh to see latest data
    sql = """
        SELECT
            p.Portal_ID,
            p.Name,
            p.Status,
            origin.Name AS origin_name,
            dest.Name AS destination_name,
            COUNT(DISTINCT e.Event_ID) AS event_count,
            SUM(CASE WHEN e.Severity = 'Severe' THEN 1 ELSE 0 END) AS severe_count
        FROM Portal p
        LEFT JOIN Event e ON e.Portal_ID = p.Portal_ID
        LEFT JOIN Location origin ON origin.Location_ID = p.Has_Origin
        LEFT JOIN Location dest ON dest.Location_ID = p.Has_Destination
        GROUP BY p.Portal_ID, p.Name, p.Status, origin.Name, dest.Name
        ORDER BY p.Portal_ID;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    print(Fore.CYAN + "=== Portal Stability Scanner (all time) ===")
    for row in rows:
        event_count = int(row['event_count'] or 0)
        severe_count = int(row['severe_count'] or 0)
        risk_score = event_count + (severe_count * 3)
        if row['Status'] == 'Active':
            risk_score += 5
        if risk_score >= 10:
            color = Fore.RED
            level = "CRITICAL"
        elif risk_score >= 5:
            color = Fore.YELLOW
            level = "HIGH"
        else:
            color = Fore.GREEN
            level = "LOW"
        origin = row['origin_name'] or "Unknown"
        destination = row['destination_name'] or "Unknown"
        print(
            f"{color}[Portal {row['Portal_ID']}] {row['Name'] or 'N/A':18s} "
            f"| Status: {row['Status']:6s} "
            f"| Events: {event_count:2d} "
            f"| Severe: {severe_count:2d} "
            f"| Risk: {level}\n"
            f"    ↳ {origin}  ➜  {destination}"
        )
    print()


def entity_threat_analyzer(conn, entity_id_input):
    """Analyze threat for a specific entity, selected by Entity_ID (to avoid name collisions)."""
    conn.commit()  # Refresh to see latest data

    # Parse ID safely
    try:
        entity_id = int(entity_id_input)
    except ValueError:
        print(Fore.RED + f"Invalid Entity_ID '{entity_id_input}'. Must be an integer.")
        return

    with conn.cursor() as cur:
        cur.execute(
            "SELECT Entity_ID, Name, Threat_Level, Origin_World FROM Entity WHERE Entity_ID = %s",
            (entity_id,),
        )
        entity = cur.fetchone()

        if not entity:
            print(Fore.RED + f"No entity with ID {entity_id} found.")
            return

        print(Fore.MAGENTA + f"=== Entity Threat Analyzer — [{entity['Entity_ID']}] {entity['Name']} ===")
        threat_color = Fore.RED if entity['Threat_Level'] == 'Critical' else Fore.YELLOW
        print(f"Threat Level: {threat_color}{entity['Threat_Level']}")

        # Compute duration in minutes on the fly (schema stores start/end only)
        cur.execute(
            """
            SELECT ea.Appearance_ID,
                   ea.Event_ID,
                   ea.Start_Time,
                   ea.End_Time,
                   TIMESTAMPDIFF(MINUTE, ea.Start_Time, ea.End_Time) AS Duration,
                   l.Name AS LocationName
            FROM Entity_Appearance ea
            LEFT JOIN Event e ON ea.Event_ID = e.Event_ID
            LEFT JOIN Location l ON e.Location_ID = l.Location_ID
            WHERE ea.Entity_ID = %s
            """,
            (entity_id,),
        )
        sightings = cur.fetchall()

    total_duration = sum(row['Duration'] or 0 for row in sightings)
    print(f"Total Sightings: {len(sightings)}")
    print(f"Total Exposure Duration: {total_duration} minutes")

    hotzones = {}
    for row in sightings:
        loc = row['LocationName'] or "Unknown"
        hotzones[loc] = hotzones.get(loc, 0) + 1

    if hotzones:
        sorted_hotzones = sorted(hotzones.items(), key=lambda item: -item[1])
        print("Hotzones:", ", ".join(f"{name}({count})" for name, count in sorted_hotzones))
    else:
        print("Hotzones: None recorded.")

    threat_score = (len(sightings) * 3) + (10 if entity['Threat_Level'] == 'Critical' else 0)
    recommendation = "Dispatch Full Response" if threat_score >= 10 else "Hold Containment"
    print(Fore.CYAN + f"Recommended Response: {recommendation}\n")


def reality_disturbance_map(conn):
    """
    Shows disturbance bars using a pseudo-log scale and severity colors:
    🟥 Critical, 🟧 High, 🟨 Medium, 🟩 Normal
    """
    conn.commit()  # Refresh to see latest data
    sql = """
        SELECT
            l.Location_ID,
            l.Name,
            l.World_Type,
            COALESCE(ul.Distortion_Level, sl.Population_Density, l.Risk_Level) AS indicator
        FROM Location l
        LEFT JOIN UpsideDown_Location ul ON l.Location_ID = ul.Location_ID
        LEFT JOIN Surface_Location sl ON l.Location_ID = sl.Location_ID
        ORDER BY indicator DESC;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    # Step 1: compute a transformed "score" so huge population values don't crush the UpsideDown values
    scores = []
    for row in rows:
        raw = row['indicator'] or 1
        if raw <= 0:
            score = 1.0
        elif raw <= 10:
            # For distortion levels and simple risk 1–10 keep linear
            score = float(raw)
        else:
            # For big numbers (population density), compress using log scale
            score = math.log10(raw) * 10.0
        scores.append(score)

    min_score = min(scores) if scores else 1.0
    max_score = max(scores) if scores else 1.0
    span = max_score - min_score if max_score != min_score else 1.0

    print(Fore.CYAN + "=== Reality Disturbance Map ===")
    print("(🟥 Critical · 🟧 High · 🟨 Medium · 🟩 Normal)\n")

    for row, score in zip(rows, scores):
        # Normalize score to [0,1]
        norm = (score - min_score) / span if span > 0 else 0.5
        # Map to bar length 1–20
        bars = int(1 + norm * 19)

        # Severity buckets from normalized score
        if norm >= 0.75:
            sev_label = "🟥 CRITICAL"
            sev_color = Fore.RED
        elif norm >= 0.5:
            sev_label = "🟧 HIGH"
            sev_color = Fore.LIGHTRED_EX
        elif norm >= 0.25:
            sev_label = "🟨 MEDIUM"
            sev_color = Fore.YELLOW
        else:
            sev_label = "🟩 NORMAL"
            sev_color = Fore.GREEN

        # World type still shown at the end
        world_type = row['World_Type']
        name = row['Name']

        print(
            f"{sev_color}{sev_label:10s} "
            f"{name:25s} {'█' * bars:20s} ({world_type})"
        )
    print()




def psychic_activity_dashboard(conn):
    conn.commit()  # Refresh to see latest data
    sql_subjects = """
        SELECT p.Person_ID, p.Name, ps.Power_Level, ps.Control_Score, ps.Ability_Type
        FROM Person p
        JOIN Psychic_Subject ps ON p.Person_ID = ps.Person_ID
        ORDER BY ps.Power_Level DESC;
    """
    with conn.cursor() as cur:
        cur.execute(sql_subjects)
        subjects = cur.fetchall()

        print(Fore.CYAN + "=== Psychic Activity Dashboard ===")
        for subject in subjects:
            print(
                Fore.MAGENTA
                + f"[{subject['Person_ID']}] {subject['Name']} — Ability: {subject['Ability_Type']} "
                  f"| Power: {subject['Power_Level']} | Control: {subject['Control_Score']}"
            )

            cur.execute(
                "SELECT Exp_ID, Purpose, Date FROM Experiment WHERE Conducted_By = %s ORDER BY Date DESC LIMIT 3",
                (subject['Person_ID'],),
            )
            experiments = cur.fetchall()
            if experiments:
                print("  Recent Experiments:")
                for exp in experiments:
                    print(f"    - ({exp['Exp_ID']}) {exp['Date']}: {textwrap.shorten(exp['Purpose'], 60)}")

            cur.execute(
                """
                SELECT e.Event_ID, e.Date, e.Description
                FROM Event e
                JOIN Victim_Record vr ON vr.Hurt_In = e.Event_ID AND vr.Person_ID = %s
                ORDER BY e.Date DESC LIMIT 3
                """,
                (subject['Person_ID'],),
            )
            linked_events = cur.fetchall()
            if linked_events:
                print("  Linked Events:")
                for ev in linked_events:
                    print(f"    - ({ev['Event_ID']}) {ev['Date']}: {textwrap.shorten(ev['Description'], 60)}")
    print()


def dimensional_threat_score(conn):
    # Commit any pending transactions to see latest data
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS severe FROM Event WHERE Severity = 'Severe'")
        severe = cur.fetchone()['severe'] or 0
        cur.execute("SELECT COUNT(*) AS critical FROM Entity WHERE Threat_Level = 'Critical'")
        critical = cur.fetchone()['critical'] or 0
        cur.execute("SELECT COUNT(*) AS active FROM Portal WHERE Status = 'Active'")
        active = cur.fetchone()['active'] or 0

    score = (severe * 5) + (critical * 10) + (active * 4)
    if score >= 50:
        color = Fore.RED
        level = "EXTREME"
    elif score >= 20:
        color = Fore.YELLOW
        level = "ELEVATED"
    else:
        color = Fore.GREEN
        level = "NORMAL"

    print(Fore.CYAN + "=== Dimensional Threat Score (DTS) ===")
    print(f"DTS = (Severe:{severe} *5) + (Critical:{critical} *10) + (Active:{active} *4) = {score}")
    print(color + f"THREAT LEVEL: {level}\n")
    return score, level


def temporal_breach_timeline(conn):
    conn.commit()  # Refresh to see latest data
    with conn.cursor() as cur:
        cur.execute("SELECT Event_ID, Date, Time, Description, Severity FROM Event ORDER BY Date, Time")
        events = cur.fetchall()

    print(Fore.CYAN + "=== Temporal Breach Timeline ===")
    for event in events:
        if event['Severity'] == 'Severe':
            color = Fore.RED
        elif event['Severity'] == 'Moderate':
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        print(
            f"{color}{event['Date']} {event['Time']} - [{event['Severity']}] "
            f"{textwrap.shorten(event['Description'], 70)}"
        )
    print()


# ----------------------- WRITE OPERATIONS ----------------------- #
def insert_event(conn):
    print(Fore.CYAN + "Insert new Event (CREATE)")
    date = input("Date (YYYY-MM-DD): ").strip()
    time_str = input("Time (HH:MM:SS): ").strip()
    description = input("Description: ").strip()
    outcome = input("Outcome (Contained/Ongoing/Catastrophic) [Ongoing]: ").strip() or "Ongoing"
    severity = input("Severity (Minor/Moderate/Severe) [Moderate]: ").strip() or "Moderate"
    location_id = input("Location_ID (blank for NULL): ").strip()
    # Portal links are stored on Event.Portal_ID in this schema
    portal_id = input("(Optional) Portal_ID to set on event (blank for none): ").strip()

    # Helper to convert input to int or None
    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO Event (Date, Time, Description, Outcome, Severity, Location_ID, Portal_ID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    date,
                    time_str,
                    description,
                    outcome,
                    severity,
                    parse_id(location_id),
                    parse_id(portal_id),
                ),
            )
            event_id = cur.lastrowid

            conn.commit()
            print(Fore.GREEN + f"Inserted Event ID {event_id}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error inserting event: {exc}")


def update_portal_status(conn):
    print(Fore.CYAN + "Update Portal Status (UPDATE)")
    portal_id = input("Portal_ID: ").strip()
    status = input("New status (Active/Closed): ").strip()
    links_to = input("Links_To Portal_ID (blank to keep, NULL to clear): ").strip()
    coordinate_x = input("Coordinate_X (blank to keep): ").strip()
    coordinate_y = input("Coordinate_Y (blank to keep): ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Portal_ID, Name, Status, Links_To, Coordinate_X, Coordinate_Y FROM Portal WHERE Portal_ID = %s", (portal_id,))
            before = cur.fetchone()
            print("Before:", before)

            def parse_id(value, current):
                if not value or value.upper() == 'NULL':
                    return None
                if value == '':
                    return current
                try:
                    return int(value)
                except ValueError:
                    return current

            def parse_float(value, current):
                if value == '':
                    return current
                if not value or value.upper() == 'NULL':
                    return None
                try:
                    return float(value)
                except ValueError:
                    return current

            cur.execute(
                "UPDATE Portal SET Status = %s, Links_To = %s, Coordinate_X = %s, Coordinate_Y = %s WHERE Portal_ID = %s",
                (
                    status,
                    parse_id(links_to, before.get('Links_To') if before else None),
                    parse_float(coordinate_x, before.get('Coordinate_X') if before else None),
                    parse_float(coordinate_y, before.get('Coordinate_Y') if before else None),
                    portal_id,
                ),
            )
            conn.commit()
            print(Fore.GREEN + f"Portal {portal_id} updated to {status}. Rows affected: {cur.rowcount}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error updating portal: {exc}")


def delete_artifact(conn):
    print(Fore.CYAN + "Delete Artifact (DELETE)")
    artifact_id = input("Artifact_ID to delete: ").strip()
    confirmation = input("Confirm delete (type YES): ").strip()
    if confirmation != "YES":
        print("Deletion aborted.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Artifact_ID, Name FROM Artifact WHERE Artifact_ID = %s", (artifact_id,))
            row = cur.fetchone()
            print("Deleting:", row)

            cur.execute("DELETE FROM Artifact WHERE Artifact_ID = %s", (artifact_id,))
            conn.commit()
            print(Fore.GREEN + f"Artifact {artifact_id} deleted. Rows affected: {cur.rowcount}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error deleting artifact: {exc}")


def create_person(conn):
    """Create Person with optional subclass."""
    print(Fore.CYAN + "Create Person (CREATE)")
    name = input("Name: ").strip()
    role = input("Role (Researcher/Agent/Victim/Psychic_Subject): ").strip()
    age = input("Age (optional): ").strip()
    affiliation = input("Affiliation: ").strip()
    status = input("Status (Active/Deceased/Missing) [Active]: ").strip() or "Active"
    supervisor_id = input("Supervisor_ID (blank for NULL): ").strip()

    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    known_aliases = input("Known_Aliases (comma-separated, optional): ").strip()
    known_aliases = known_aliases if known_aliases else None

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Person (Name, Role, Age, Status, Affiliation, Supervisor_ID, Known_Aliases)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (name, role, int(age) if age else None, status, affiliation, parse_id(supervisor_id), known_aliases)
            )
            person_id = cur.lastrowid

            # Handle subclasses
            if role == 'Researcher':
                clearance = input("Clearance_Level: ").strip()
                cur.execute("INSERT INTO Researcher (Person_ID, Clearance_Level) VALUES (%s, %s)",
                            (person_id, clearance))
            elif role == 'Agent':
                success_rate = input("Success_Rate (0-100): ").strip()
                cur.execute("INSERT INTO Agent (Person_ID, Success_Rate) VALUES (%s, %s)",
                            (person_id, float(success_rate) if success_rate else None))
            elif role == 'Victim':
                injury = input("Injury_Severity: ").strip()
                cur.execute("INSERT INTO Victim (Person_ID, Injury_Severity) VALUES (%s, %s)",
                            (person_id, injury))
            elif role == 'Psychic_Subject':
                ability = input("Ability_Type: ").strip()
                power = input("Power_Level (0-100): ").strip()
                control = input("Control_Score (0-100): ").strip()
                cur.execute("INSERT INTO Psychic_Subject (Person_ID, Ability_Type, Power_Level, Control_Score) VALUES (%s, %s, %s, %s)",
                            (person_id, ability, int(power) if power else None, int(control) if control else None))

            conn.commit()
            print(Fore.GREEN + f"Created Person ID {person_id} ({role})")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating person: {exc}")


def create_artifact(conn):
    """Create Artifact."""
    print(Fore.CYAN + "Create Artifact (CREATE)")
    name = input("Name: ").strip()
    artifact_type = input("Type (Biological/Metallic/Organic/Unknown) [Unknown]: ").strip() or "Unknown"
    location_id = input("Found_At Location_ID (blank for NULL): ").strip()
    anomaly_level = input("Anomaly_Level (1-10): ").strip()

    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Artifact (Name, Type, Anomaly_Level, Found_At) VALUES (%s, %s, %s, %s)",
                (name, artifact_type, int(anomaly_level) if anomaly_level else None, parse_id(location_id))
            )
            conn.commit()
            print(Fore.GREEN + f"Created Artifact ID {cur.lastrowid}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating artifact: {exc}")


def create_entity(conn):
    """Create Entity with optional subclass."""
    print(Fore.CYAN + "Create Entity (CREATE)")
    name = input("Name: ").strip()
    species = input("Species (Monster/Shadow_Creature/Mind_Entity): ").strip()
    threat_level = input("Threat_Level (Low/Medium/High/Critical): ").strip()
    origin_world = input("Origin_World (Normal/UpsideDown): ").strip()
    first_sighting = input("First_Sighting (YYYY-MM-DD): ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Entity (Name, Species, Threat_Level, Origin_World, First_Sighting)
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, species, threat_level, origin_world, first_sighting)
            )
            entity_id = cur.lastrowid

            # Handle subclasses
            if species == 'Monster':
                aggression = input("Aggression_Index (0-100): ").strip()
                cur.execute("INSERT INTO Monster (Entity_ID, Aggression_Index) VALUES (%s, %s)",
                            (entity_id, int(aggression) if aggression else None))
            elif species == 'Shadow_Creature':
                corruption = input("Corruption_Level (0-100): ").strip()
                manifest = input("Manifestation_Type: ").strip()
                cur.execute("INSERT INTO Shadow_Creature (Entity_ID, Corruption_Level, Manifestation_Type) VALUES (%s, %s, %s)",
                            (entity_id, int(corruption) if corruption else None, manifest))
            elif species == 'Mind_Entity':
                influence = input("Influence_Range (0-100): ").strip()
                cognitive = input("Cognitive_Link_Strength (0-100): ").strip()
                cur.execute("INSERT INTO Mind_Entity (Entity_ID, Influence_Range, Cognitive_Link_Strength) VALUES (%s, %s, %s)",
                            (entity_id, int(influence) if influence else None, int(cognitive) if cognitive else None))

            conn.commit()
            print(Fore.GREEN + f"Created Entity ID {entity_id} ({species})")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating entity: {exc}")


def create_portal(conn):
    """Create Portal."""
    print(Fore.CYAN + "Create Portal (CREATE)")
    name = input("Name: ").strip()
    status = input("Status (Active/Closed) [Active]: ").strip() or "Active"
    origin_id = input("Has_Origin Location_ID: ").strip()
    dest_id = input("Has_Destination Location_ID: ").strip()
    discovered = input("Discovered_On (YYYY-MM-DD): ").strip()
    # Collect optional links and coordinates (Portal.Links_To, Coordinate_X, Coordinate_Y)
    links_to = input("Links_To Portal_ID (blank for NULL): ").strip()
    coordinate_x = input("Coordinate_X (optional, float): ").strip()
    coordinate_y = input("Coordinate_Y (optional, float): ").strip()

    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Portal (Name, Status, Has_Origin, Has_Destination, Discovered_On, Links_To, Coordinate_X, Coordinate_Y)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    name,
                    status,
                    parse_id(origin_id),
                    parse_id(dest_id),
                    discovered,
                    parse_id(links_to),
                    float(coordinate_x) if coordinate_x else None,
                    float(coordinate_y) if coordinate_y else None,
                ),
            )
            conn.commit()
            print(Fore.GREEN + f"Created Portal ID {cur.lastrowid}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating portal: {exc}")


def link_event_entity(conn):
    """Link Event to Entity (CREATE Entity_Appearance)."""
    print(Fore.CYAN + "Link Event to Entity (CREATE)")
    event_id = input("Event_ID: ").strip()
    entity_id = input("Entity_ID: ").strip()
    start_time = input("Start_Time (YYYY-MM-DD HH:MM:SS): ").strip()
    end_time = input("End_Time (YYYY-MM-DD HH:MM:SS): ").strip()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Entity_Appearance (Entity_ID, Event_ID, Start_Time, End_Time)
                   VALUES (%s, %s, %s, %s)""",
                (int(entity_id), int(event_id), start_time, end_time)
            )
            # Also link in junction table
            cur.execute("INSERT IGNORE INTO Event_Involves_Entity (Event_ID, Entity_ID) VALUES (%s, %s)",
                        (int(event_id), int(entity_id)))
            conn.commit()
            print(Fore.GREEN + f"Linked Entity {entity_id} to Event {event_id} (Appearance ID: {cur.lastrowid})")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error linking event to entity: {exc}")


def link_artifact_event(conn):
    """Link Artifact to Event."""
    print(Fore.CYAN + "Link Artifact to Event (CREATE)")
    event_id = input("Event_ID: ").strip()
    artifact_id = input("Artifact_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT IGNORE INTO Event_Affects_Artifact (Event_ID, Artifact_ID) VALUES (%s, %s)",
                        (int(event_id), int(artifact_id)))
            conn.commit()
            print(Fore.GREEN + f"Linked Artifact {artifact_id} to Event {event_id}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error linking artifact to event: {exc}")


def add_victim_to_event(conn):
    """Add Victim to Event (CREATE Victim_Record)."""
    print(Fore.CYAN + "Add Victim to Event (CREATE)")
    person_id = input("Person_ID (victim): ").strip()
    event_id = input("Event_ID: ").strip()
    injury_severity = input("Injury_Severity: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Victim_Record (Person_ID, Hurt_In, Injury_Severity)
                   VALUES (%s, %s, %s)""",
                (int(person_id), int(event_id), injury_severity)
            )
            conn.commit()
            print(Fore.GREEN + f"Added Victim {person_id} to Event {event_id} (Victim_No: {cur.lastrowid})")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error adding victim to event: {exc}")


def create_report(conn):
    """Create Report with Report_Details."""
    print(Fore.CYAN + "Create Report (CREATE)")
    date = input("Date (YYYY-MM-DD): ").strip()
    authored_by = input("Authored_By Person_ID: ").strip()
    verified_by = input("Verified_By Person_ID (blank for NULL): ").strip()
    documents_artifact = input("Documents_Artifact Artifact_ID (blank for NULL): ").strip()
    summary = input("Summary: ").strip()
    verdict = input("Verdict (True/False/Unclear) [Unclear]: ").strip() or "Unclear"

    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Report (Date, Authored_By, Verified_By, Documents_Artifact)
                   VALUES (%s, %s, %s, %s)""",
                (date, int(authored_by), parse_id(verified_by), parse_id(documents_artifact))
            )
            report_id = cur.lastrowid
            cur.execute(
                "INSERT INTO Report_Details (Report_ID, Summary, Verdict) VALUES (%s, %s, %s)",
                (report_id, summary, verdict)
            )
            conn.commit()
            print(Fore.GREEN + f"Created Report ID {report_id}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating report: {exc}")


def create_experiment(conn):
    """Create Experiment."""
    print(Fore.CYAN + "Create Experiment (CREATE)")
    purpose = input("Purpose: ").strip()
    confidentiality = input("Confidentiality (Low/Medium/High) [High]: ").strip() or "High"
    result = input("Result: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()
    conducted_by = input("Conducted_By Person_ID (blank for NULL): ").strip()

    def parse_id(value):
        if not value or value.upper() == 'NULL':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO Experiment (Purpose, Confidentiality, Result, Date, Conducted_By)
                   VALUES (%s, %s, %s, %s, %s)""",
                (purpose, confidentiality, result, date, parse_id(conducted_by))
            )
            conn.commit()
            print(Fore.GREEN + f"Created Experiment ID {cur.lastrowid}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error creating experiment: {exc}")


def global_search(conn):
    """Global Search across all main tables, scanning multiple columns per table."""
    conn.commit()  # Refresh to see latest data
    print(Fore.CYAN + "Global Search")
    query = input("Search query (text or ID): ").strip()
    if not query:
        print(Fore.RED + "Empty query.")
        return

    like = f"%{query}%"
    numeric_id = None
    if query.isdigit():
        try:
            numeric_id = int(query)
        except ValueError:
            numeric_id = None

    try:
        with conn.cursor() as cur:
            # ENTITIES: search name/species/threat/origin and optionally by ID
            cur.execute(
                """
                SELECT Entity_ID, Name, Species, Threat_Level, Origin_World
                FROM Entity
                WHERE (
                    Name LIKE %s
                    OR Species LIKE %s
                    OR Threat_Level LIKE %s
                    OR Origin_World LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Entity_ID = %s" if numeric_id is not None else ""
                ),
                (like, like, like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            entities = cur.fetchall()

            # LOCATIONS: search name/world/description
            cur.execute(
                """
                SELECT Location_ID, Name, World_Type, Description
                FROM Location
                WHERE (
                    Name LIKE %s
                    OR World_Type LIKE %s
                    OR IFNULL(Description,'') LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Location_ID = %s" if numeric_id is not None else ""
                ),
                (like, like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            locations = cur.fetchall()

            # EVENTS: search description/outcome/severity
            cur.execute(
                """
                SELECT Event_ID, Date, Time, Description, Outcome, Severity
                FROM Event
                WHERE (
                    IFNULL(Description,'') LIKE %s
                    OR Outcome LIKE %s
                    OR Severity LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Event_ID = %s" if numeric_id is not None else ""
                ),
                (like, like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            events = cur.fetchall()

            # PERSONS: search name/role/affiliation/status/aliases
            cur.execute(
                """
                SELECT Person_ID, Name, Role, Status, Affiliation, Known_Aliases
                FROM Person
                WHERE (
                    Name LIKE %s
                    OR Role LIKE %s
                    OR Status LIKE %s
                    OR IFNULL(Affiliation,'') LIKE %s
                    OR IFNULL(Known_Aliases,'') LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Person_ID = %s" if numeric_id is not None else ""
                ),
                (like, like, like, like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            persons = cur.fetchall()

            # PORTALS: search name/status
            cur.execute(
                """
                SELECT Portal_ID, Name, Status
                FROM Portal
                WHERE (
                    IFNULL(Name,'') LIKE %s
                    OR Status LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Portal_ID = %s" if numeric_id is not None else ""
                ),
                (like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            portals = cur.fetchall()

            # ARTIFACTS: search name/type
            cur.execute(
                """
                SELECT Artifact_ID, Name, Type, Anomaly_Level
                FROM Artifact
                WHERE (
                    IFNULL(Name,'') LIKE %s
                    OR Type LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Artifact_ID = %s" if numeric_id is not None else ""
                ),
                (like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            artifacts = cur.fetchall()

            # REPORTS: search details
            cur.execute(
                """
                SELECT r.Report_ID, r.Date, rd.Summary, rd.Verdict
                FROM Report r
                LEFT JOIN Report_Details rd ON r.Report_ID = rd.Report_ID
                WHERE (
                    IFNULL(rd.Summary,'') LIKE %s
                    OR IFNULL(rd.Verdict,'') LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR r.Report_ID = %s" if numeric_id is not None else ""
                ),
                (like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            reports = cur.fetchall()

            # EXPERIMENTS: search purpose/result/confidentiality
            cur.execute(
                """
                SELECT Exp_ID, Purpose, Confidentiality, Result, Date
                FROM Experiment
                WHERE (
                    IFNULL(Purpose,'') LIKE %s
                    OR IFNULL(Result,'') LIKE %s
                    OR Confidentiality LIKE %s
                )
                {id_clause}
                LIMIT 20
                """.format(
                    id_clause="OR Exp_ID = %s" if numeric_id is not None else ""
                ),
                (like, like, like) + ((numeric_id,) if numeric_id is not None else ()),
            )
            experiments = cur.fetchall()

        print(Fore.MAGENTA + f"\n=== Search Results for '{query}' ===")

        if entities:
            print(Fore.YELLOW + "\nEntities:")
            for e in entities:
                print(f"  [{e['Entity_ID']}] {e['Name']} · {e['Species']} · {e['Threat_Level']} ({e['Origin_World']})")

        if locations:
            print(Fore.YELLOW + "\nLocations:")
            for l in locations:
                desc = textwrap.shorten(l.get('Description') or '', 40)
                print(f"  [{l['Location_ID']}] {l['Name']} ({l['World_Type']}) - {desc}")

        if events:
            print(Fore.YELLOW + "\nEvents:")
            for e in events:
                desc = textwrap.shorten(e['Description'] or '', 50)
                print(f"  [{e['Event_ID']}] {e['Date']} {e['Time']} - {desc} [{e['Severity']}/{e['Outcome']}]")

        if persons:
            print(Fore.YELLOW + "\nPersons:")
            for p in persons:
                alias = f" · aka {p['Known_Aliases']}" if p.get('Known_Aliases') else ""
                print(f"  [{p['Person_ID']}] {p['Name']} - {p['Role']} ({p['Status']}, {p.get('Affiliation')}){alias}")

        if portals:
            print(Fore.YELLOW + "\nPortals:")
            for p in portals:
                print(f"  [{p['Portal_ID']}] {p['Name']} - {p['Status']}")

        if artifacts:
            print(Fore.YELLOW + "\nArtifacts:")
            for a in artifacts:
                print(f"  [{a['Artifact_ID']}] {a['Name']} - {a['Type']} (Anomaly {a['Anomaly_Level']})")

        if reports:
            print(Fore.YELLOW + "\nReports:")
            for r in reports:
                summ = textwrap.shorten(r.get('Summary') or '', 60)
                print(f"  [{r['Report_ID']}] {r['Date']} - {summ} [{r.get('Verdict')}]")

        if experiments:
            print(Fore.YELLOW + "\nExperiments:")
            for x in experiments:
                purp = textwrap.shorten(x['Purpose'] or '', 60)
                print(f"  [{x['Exp_ID']}] {x['Date']} - {purp} ({x['Confidentiality']})")

        if not any([entities, locations, events, persons, portals, artifacts, reports, experiments]):
            print(Fore.RED + "No results found.")

        print()
    except Exception as exc:
        print(Fore.RED + f"Error searching: {exc}")



def unlink_event_entity(conn):
    """Unlink Event from Entity."""
    print(Fore.CYAN + "Unlink Event from Entity")
    event_id = input("Event_ID: ").strip()
    entity_id = input("Entity_ID: ").strip()
    confirm = input("Delete Entity_Appearance records too? (yes/no) [no]: ").strip().lower()

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Event_Involves_Entity WHERE Event_ID = %s AND Entity_ID = %s",
                        (int(event_id), int(entity_id)))
            if confirm == 'yes':
                cur.execute("DELETE FROM Entity_Appearance WHERE Event_ID = %s AND Entity_ID = %s",
                            (int(event_id), int(entity_id)))
            conn.commit()
            print(Fore.GREEN + f"Unlinked Entity {entity_id} from Event {event_id}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error unlinking: {exc}")


def unlink_artifact_event(conn):
    """Unlink Artifact from Event."""
    print(Fore.CYAN + "Unlink Artifact from Event")
    event_id = input("Event_ID: ").strip()
    artifact_id = input("Artifact_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Event_Affects_Artifact WHERE Event_ID = %s AND Artifact_ID = %s",
                        (int(event_id), int(artifact_id)))
            conn.commit()
            print(Fore.GREEN + f"Unlinked Artifact {artifact_id} from Event {event_id}")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error unlinking: {exc}")


def remove_victim_from_event(conn):
    """Remove Victim from Event."""
    print(Fore.CYAN + "Remove Victim from Event")
    victim_no = input("Victim_No (or blank to use Event_ID + Person_ID): ").strip()

    try:
        with conn.cursor() as cur:
            if victim_no:
                cur.execute("DELETE FROM Victim_Record WHERE Victim_No = %s", (int(victim_no),))
            else:
                event_id = input("Event_ID: ").strip()
                person_id = input("Person_ID: ").strip()
                cur.execute("DELETE FROM Victim_Record WHERE Hurt_In = %s AND Person_ID = %s",
                            (int(event_id), int(person_id)))
            conn.commit()
            print(Fore.GREEN + "Victim removed from event")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error removing victim: {exc}")


def update_event(conn):
    """Update Event (Outcome, Severity, Portal_ID, Location_ID)."""
    print(Fore.CYAN + "Update Event (UPDATE)")
    event_id = input("Event_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Event WHERE Event_ID = %s", (int(event_id),))
            event = cur.fetchone()
            if not event:
                print(Fore.RED + "Event not found.")
                return

            print(f"Current: {event}")

            outcome = input(f"Outcome [{event['Outcome']}] (or blank to keep): ").strip() or event['Outcome']
            severity = input(f"Severity [{event['Severity']}] (or blank to keep): ").strip() or event['Severity']
            portal_id = input(f"Portal_ID [{event['Portal_ID']}] (or blank/NULL to keep): ").strip()
            location_id = input(f"Location_ID [{event['Location_ID']}] (or blank/NULL to keep): ").strip()
            # Duration is derived from Entity_Appearance Start/End times; not stored on Event

            def parse_id(value, current):
                if not value or value.upper() == 'NULL':
                    return None
                if value == '':
                    return current
                try:
                    return int(value)
                except ValueError:
                    return current

            cur.execute(
                """UPDATE Event SET Outcome = %s, Severity = %s, Portal_ID = %s, Location_ID = %s
                   WHERE Event_ID = %s""",
                (outcome, severity, parse_id(portal_id, event['Portal_ID']),
                 parse_id(location_id, event['Location_ID']), int(event_id))
            )
            conn.commit()
            print(Fore.GREEN + f"Event {event_id} updated")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error updating event: {exc}")


def update_person(conn):
    """Update Person (Affiliation, Status, Supervisor, Role change, Known_Aliases)."""
    print(Fore.CYAN + "Update Person (UPDATE)")
    person_id = input("Person_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Person WHERE Person_ID = %s", (int(person_id),))
            person = cur.fetchone()
            if not person:
                print(Fore.RED + "Person not found.")
                return

            print(f"Current: {person}")

            affiliation = input(f"Affiliation [{person['Affiliation']}] (or blank to keep): ").strip() or person['Affiliation']
            status = input(f"Status [{person['Status']}] (or blank to keep): ").strip() or person['Status']
            known_aliases = input(f"Known_Aliases [{person.get('Known_Aliases')}] (or blank to keep): ").strip()
            if known_aliases == '':
                known_aliases = person.get('Known_Aliases')
            supervisor_id = input(f"Supervisor_ID [{person['Supervisor_ID']}] (or blank/NULL to keep): ").strip()
            new_role = input(f"Role [{person['Role']}] (or blank to keep): ").strip() or person['Role']

            def parse_id(value, current):
                if not value or value.upper() == 'NULL':
                    return None
                if value == '':
                    return current
                try:
                    return int(value)
                except ValueError:
                    return current

            # If role changed, handle subclass migration
            if new_role != person['Role']:
                print(Fore.YELLOW + f"Role change detected. You may need to manually update subclass tables.")

            cur.execute(
                "UPDATE Person SET Affiliation = %s, Status = %s, Supervisor_ID = %s, Role = %s, Known_Aliases = %s WHERE Person_ID = %s",
                (affiliation, status, parse_id(supervisor_id, person['Supervisor_ID']), new_role, known_aliases, int(person_id))
            )
            conn.commit()
            print(Fore.GREEN + f"Person {person_id} updated")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error updating person: {exc}")


def update_entity(conn):
    """Update Entity (Threat_Level, Name)."""
    print(Fore.CYAN + "Update Entity (UPDATE)")
    entity_id = input("Entity_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Entity WHERE Entity_ID = %s", (int(entity_id),))
            entity = cur.fetchone()
            if not entity:
                print(Fore.RED + "Entity not found.")
                return

            print(f"Current: {entity}")

            name = input(f"Name [{entity['Name']}] (or blank to keep): ").strip() or entity['Name']
            threat_level = input(f"Threat_Level [{entity['Threat_Level']}] (or blank to keep): ").strip() or entity['Threat_Level']

            cur.execute(
                "UPDATE Entity SET Name = %s, Threat_Level = %s WHERE Entity_ID = %s",
                (name, threat_level, int(entity_id))
            )
            conn.commit()
            print(Fore.GREEN + f"Entity {entity_id} updated")
            if threat_level == 'Critical' and entity['Threat_Level'] != 'Critical':
                print(Fore.RED + "⚠️  Threat escalated to Critical - immediate action recommended!")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error updating entity: {exc}")


def update_artifact(conn):
    """Update Artifact (Found_At, Anomaly_Level)."""
    print(Fore.CYAN + "Update Artifact (UPDATE)")
    artifact_id = input("Artifact_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Artifact WHERE Artifact_ID = %s", (int(artifact_id),))
            artifact = cur.fetchone()
            if not artifact:
                print(Fore.RED + "Artifact not found.")
                return

            print(f"Current: {artifact}")

            found_at = input(f"Found_At Location_ID [{artifact['Found_At']}] (or blank/NULL to keep): ").strip()
            anomaly_level = input(f"Anomaly_Level [{artifact['Anomaly_Level']}] (or blank to keep): ").strip()

            def parse_id(value, current):
                if not value or value.upper() == 'NULL':
                    return None
                if value == '':
                    return current
                try:
                    return int(value)
                except ValueError:
                    return current

            new_anomaly = int(anomaly_level) if anomaly_level else artifact['Anomaly_Level']

            cur.execute(
                "UPDATE Artifact SET Found_At = %s, Anomaly_Level = %s WHERE Artifact_ID = %s",
                (parse_id(found_at, artifact['Found_At']), new_anomaly, int(artifact_id))
            )
            conn.commit()
            print(Fore.GREEN + f"Artifact {artifact_id} updated")
            if new_anomaly > 8:
                print(Fore.RED + "⚠️  High anomaly level detected - alert report recommended!")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error updating artifact: {exc}")


def archive_event(conn):
    """Archive Event (soft: set Outcome to 'Contained' and append reason to Description)."""
    print(Fore.CYAN + "Archive Event")
    event_id = input("Event_ID: ").strip()
    reason = input("Archive reason: ").strip()

    try:
        with conn.cursor() as cur:
            # Since we don't have an archive column, we'll update Outcome to 'Archived'
            cur.execute("UPDATE Event SET Outcome = 'Contained', Description = CONCAT(Description, ' [ARCHIVED: ', %s, ']') WHERE Event_ID = %s",
                        (reason, int(event_id)))
            conn.commit()
            print(Fore.GREEN + f"Event {event_id} archived")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error archiving event: {exc}")


def archive_person(conn):
    """Archive Person (soft delete - set Status)."""
    print(Fore.CYAN + "Archive Person")
    person_id = input("Person_ID: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE Person SET Status = 'Deceased' WHERE Person_ID = %s", (int(person_id),))
            conn.commit()
            print(Fore.GREEN + f"Person {person_id} archived (Status set to Deceased)")
    except Exception as exc:
        conn.rollback()
        print(Fore.RED + f"Error archiving person: {exc}")


def recompute_dts(conn):
    """Recompute DTS (Dimensional Threat Score)."""
    print(Fore.CYAN + "Recomputing DTS...")
    dts_value, threat_level = dimensional_threat_score(conn)
    print(Fore.GREEN + f"DTS recomputed: {dts_value} ({threat_level})")


# ----------------------- CLI LOOP ----------------------- #
def main_cli(conn):
    boot_sequence()
    try:
        while True:
            dts_value, threat_level = dimensional_threat_score(conn)
            print(Fore.BLUE + f"[Main Menu] Select function (DTS {dts_value} · {threat_level}):")
            print(" --- DASHBOARD / READ / ANALYTICS ---")
            print(" 1) Portal Stability Scanner")
            print(" 2) Entity Threat Analyzer")
            print(" 3) Reality Disturbance Map")
            print(" 4) Psychic Activity Dashboard")
            print(" 5) Temporal Breach Timeline")
            print(" 6) Global Search")
            print(" --- CREATE (atomic, can accept arrays) ---")
            print(" 7) Insert new Event (CREATE)")
            print(" 8) Create Person (CREATE)")
            print(" 9) Create Artifact (CREATE)")
            print("10) Create Entity (CREATE)")
            print("11) Create Portal (CREATE)")
            print("12) Create Report (CREATE)")
            print("13) Create Experiment (CREATE)")
            print(" --- LINK / UNLINK ---")
            print("14) Link Event to Entity (appearance)")
            print("15) Unlink Event from Entity")
            print("16) Link Artifact to Event")
            print("17) Unlink Artifact from Event")
            print("18) Add Victim to Event")
            print("19) Remove Victim from Event")
            print(" --- UPDATE ---")
            print("20) Update Event (Outcome/Severity/Portal/Location)")
            print("21) Update Portal Status / Links")
            print("22) Update Person (Role/Affiliation/Status)")
            print("23) Update Entity (Threat_Level)")
            print("24) Update Artifact (Anomaly_Level/Found_At)")
            print(" --- DELETE / ARCHIVE ---")
            print("25) Archive Event")
            print("26) Archive Person")
            print("27) Delete Artifact (hard delete) — confirm")
            print(" --- ADMIN / UTIL ---")
            print("28) Recompute DTS / Run maintenance")
            print(" q) Quit")

            cmd = input(Fore.YELLOW + "Choice> ").strip().lower()
            if cmd == '1':
                portal_stability_scanner(conn)
            elif cmd == '2':
                entity_id = input("Entity_ID: ").strip()
                entity_threat_analyzer(conn, entity_id)
            elif cmd == '3':
                reality_disturbance_map(conn)
            elif cmd == '4':
                psychic_activity_dashboard(conn)
            elif cmd == '5':
                temporal_breach_timeline(conn)
            elif cmd == '6':
                global_search(conn)
            elif cmd == '7':
                insert_event(conn)
            elif cmd == '8':
                create_person(conn)
            elif cmd == '9':
                create_artifact(conn)
            elif cmd == '10':
                create_entity(conn)
            elif cmd == '11':
                create_portal(conn)
            elif cmd == '12':
                create_report(conn)
            elif cmd == '13':
                create_experiment(conn)
            elif cmd == '14':
                link_event_entity(conn)
            elif cmd == '15':
                unlink_event_entity(conn)
            elif cmd == '16':
                link_artifact_event(conn)
            elif cmd == '17':
                unlink_artifact_event(conn)
            elif cmd == '18':
                add_victim_to_event(conn)
            elif cmd == '19':
                remove_victim_from_event(conn)
            elif cmd == '20':
                update_event(conn)
            elif cmd == '21':
                update_portal_status(conn)
            elif cmd == '22':
                update_person(conn)
            elif cmd == '23':
                update_entity(conn)
            elif cmd == '24':
                update_artifact(conn)
            elif cmd == '25':
                archive_event(conn)
            elif cmd == '26':
                archive_person(conn)
            elif cmd == '27':
                delete_artifact(conn)
            elif cmd == '28':
                recompute_dts(conn)
            elif cmd == 'q':
                print(Fore.GREEN + "Exiting console... Stay vigilant.")
                break
            else:
                print(Fore.RED + "Unknown command. Try again.")
    finally:
        conn.close()
        print(Fore.GREEN + "Database connection closed.")


if __name__ == '__main__':
    print(Fore.CYAN + "StrangerDB OPS-CONSOLE v4.2 — starting.")
    username = input("DB Username: ").strip()
    password = getpass("DB Password: ")
    connection = get_db_connection(username, password)
    if not connection:
        print(Fore.RED + "Failed to connect. Exiting.")
        sys.exit(1)

    main_cli(connection)
