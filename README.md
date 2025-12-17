# StrangerDB CONSOLE

**Demo Video:**  
https://drive.google.com/file/d/1vQW4BlJjeacLWwvkL0_U6LsTllZbJItZ/view?usp=sharing

---

## Overview

**StrangerDB OPS-CONSOLE v4.2** is an interactive, terminal-based operations console built for a fictional **Hawkins National Laboratory (HNL)** anomaly monitoring system.

The application connects to a MySQL database (`strangerdb`) and provides a unified interface for **analytics, operations, and data management** over a complex relational schema modeling interdimensional events, entities, portals, artifacts, and personnel.

The system is implemented in **Python** using `PyMySQL` for database connectivity and is designed to emphasize **schema design, query correctness, relational integrity, and operational workflows** rather than UI complexity.

---

## Key Capabilities

### Analytics & Dashboards
- Portal stability and breach tracking
- Entity threat analysis and profiling
- Reality disturbance mapping
- Psychic activity monitoring
- Temporal event timelines

### Data Management
- Full CRUD operations for:
  - Events
  - Persons
  - Entities
  - Artifacts
  - Portals
  - Reports
  - Experiments
- Relationship management across M:N junction tables
- Soft-delete (archiving) with reason tracking
- Hard deletes for selected entities where appropriate

### Operational Logic
- Real-time computation of a **Dimensional Threat Score (DTS)**
- Referential integrity enforced via foreign keys and constraints
- Multi-entity updates through guided CLI workflows

---

## Technology Stack

- **Language:** Python 3.8+
- **Database:** MySQL 5.7+ / MariaDB 10.3+
- **Connector:** PyMySQL
- **Interface:** Terminal-based interactive CLI
- **Dataset:** Synthetic but realistic, large-scale relational data

---

## Prerequisites

- **Python**: 3.8+ (recommended 3.9+)
- **MySQL Server**: 5.7+ (or MariaDB 10.3+) installed and running on `localhost`
- **MySQL User**: A user account with full privileges on the `strangerdb` database (e.g., `root` or `stranger_app`)

Python dependencies are managed via `requirements.txt` (see [Installation](#installation)).

---

## Project Structure

Key files in the `src/` directory:

| File | Purpose |
|------|---------|
| `main_app.py` | Main OPS console application (interactive CLI menu) |
| `schema.sql` | Database DDL (creates `strangerdb`, all tables, constraints, enums) |
| `populate.sql` | Sample dataset with 50+ locations, 100+ events, 500+ sightings, and more |
| `requirements.txt` | Python dependencies (PyMySQL, colorama) |

---

## Installation

### Step 1: Set Up Python Virtual Environment (Windows PowerShell)

```powershell
# Navigate to project root
cd 'c:\Users\maith\Desktop\dna'

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**Dependencies installed:**
- `PyMySQL==1.1.0` — MySQL database driver
- `colorama==0.4.6` — Colored terminal output

---

## Database Setup

### Step 1: Create Database & Schema

The `schema.sql` file automatically creates the `strangerdb` database and all tables. From the project root (in PowerShell):

```powershell
mysql -u root -p < .\src\schema.sql
```

When prompted, enter your MySQL password. This will:
- Drop any existing `strangerdb` (if present)
- Create a fresh `strangerdb` with proper charset (`utf8mb4`)
- Create all 25 tables with proper constraints, enums, and foreign keys

### Step 2: Populate with Sample Data

Load the pre-generated dataset:

```powershell
mysql -u root -p strangerdb < .\src\populate.sql
```

**Note:** If you encounter a foreign key error, verify that `schema.sql` ran successfully first.

### Verification

To verify the setup, query the database:

```powershell
mysql -u root -p -e "SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema='strangerdb';"
```

You should see 25 tables listed.

---

## Running the System

You will typically use **two terminals** for the full demonstration: one for the Python application (Terminal A) and one for direct MySQL queries (Terminal B).

### Terminal A: Python OPS Console

From the project root (PowerShell):

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the application
python .\src\main_app.py
```

**First Run:**
- The console will prompt for your MySQL credentials:
  ```
  Please enter your MySQL credentials.
  Username: root
  Password: ••••••••
  ```
- After authentication, you'll see the main menu.

**Main Menu Options:**

```
[Main Menu] Select function (DTS XYZ · LEVEL):

--- DASHBOARD / READ / ANALYTICS ---
  1) Portal Stability Scanner
  2) Entity Threat Analyzer
  3) Reality Disturbance Map
  4) Psychic Activity Dashboard
  5) Temporal Breach Timeline
  6) Global Search

--- CREATE (INSERT) ---
  7) Insert new Event (CREATE)
  8) Create Person (CREATE)
  9) Create Artifact (CREATE)
 10) Create Entity (CREATE)
 11) Create Portal (CREATE)
 12) Create Report (CREATE)
 13) Create Experiment (CREATE)

--- LINK / UNLINK ---
 14) Link Event to Entity (appearance)
 15) Unlink Event from Entity
 16) Link Artifact to Event
 17) Unlink Artifact from Event
 18) Add Victim to Event
 19) Remove Victim from Event

--- UPDATE ---
 20) Update Event (Outcome/Severity/Portal/Location)
 21) Update Portal Status / Links
 22) Update Person (Role/Affiliation/Status)
 23) Update Entity (Threat_Level)
 24) Update Artifact (Anomaly_Level/Found_At)

--- DELETE / ARCHIVE ---
 25) Archive Event
 26) Archive Person
 27) Delete Artifact (hard delete)

--- ADMIN / UTIL ---
 28) Recompute DTS / Run maintenance
  q) Quit
```

**Typical Workflow:**
1. Enter a menu option number
2. Follow the prompts to enter required information
3. Results are printed to the console
4. Return to the main menu

---

### Terminal B: Live MySQL Inspection (for Demo)

In a **second terminal**, connect directly to MySQL to inspect data before/after operations:

```powershell
mysql -u root -p strangerdb
```

**Common inspection queries:**

```sql
-- Show all events
SELECT Event_ID, Date, Description, Outcome, Severity FROM Event LIMIT 10;

-- Show all portals
SELECT Portal_ID, Name, Status, Has_Origin, Has_Destination FROM Portal LIMIT 10;

-- Show all entities
SELECT Entity_ID, Name, Species, Threat_Level, Origin_World FROM Entity LIMIT 10;

-- Show all persons
SELECT Person_ID, Name, Role, Status, Affiliation FROM Person LIMIT 10;

-- Check event details for a specific ID
SELECT * FROM Event WHERE Event_ID = 1\G

-- Check portal details for a specific ID
SELECT * FROM Portal WHERE Portal_ID = 1\G
```

---

## Demo Flow (Terminal A ↔ Terminal B Pattern)

For your final video submission, follow this pattern for **each update operation** (INSERT, UPDATE, DELETE):

### Before Operation (Terminal B):
```powershell
# Show the current state
mysql -u root -p -e "SELECT Event_ID, Date, Outcome, Severity FROM Event WHERE Event_ID = 5 \G"
```

### During Operation (Terminal A):
```powershell
# Run the application
python .\src\main_app.py

# Choose option: 20 (Update Event)
# Follow prompts to modify Event_ID = 5 (e.g., change Outcome to 'Contained')
```

### After Operation (Terminal B):
```powershell
# Re-run the same SELECT query to show the change
mysql -u root -p -e "SELECT Event_ID, Date, Outcome, Severity FROM Event WHERE Event_ID = 5 \G"
```

**Repeat this pattern for:**
1. One **INSERT** operation (e.g., "Create new Event" - option 7)
2. One **UPDATE** operation (e.g., "Update Portal Status" - option 21)
3. One **DELETE** operation (e.g., "Delete Artifact" - option 27)

---

## Database Schema Overview

### Core Entities

| Table | Purpose | Superclass |
|-------|---------|-----------|
| `Person` | Researchers, agents, victims, psychic subjects | Base |
| `Location` | Normal world and UpsideDown locations | Base |
| `Entity` | Creatures and anomalies | Base |
| `Portal` | Dimensional gateways | - |
| `Event` | Incidents and anomaly events | - |
| `Artifact` | Physical evidence and objects | - |
| `Report` | Documentation and analysis | - |
| `Experiment` | Research trials | - |

### Subclasses

**Person subclasses:**
- `Researcher` (clearance level)
- `Agent` (success rate)
- `Victim` (injury severity)
- `Psychic_Subject` (ability type, power level, control score)

**Location subclasses:**
- `Surface_Location` (population density, proximity to lab)
- `UpsideDown_Location` (distortion level, hazard type)

**Entity subclasses:**
- `Monster` (aggression index)
- `Shadow_Creature` (corruption level, manifestation type)
- `Mind_Entity` (influence range, cognitive link strength)

### Junction Tables

- `Event_Involves_Entity` — M:N relationship between events and entities
- `Event_Affects_Artifact` — M:N relationship between events and artifacts
- `Event_Documented_By_Report` — M:N relationship between events and reports

### Weak Entity

- `Victim_Record` — Records persons injured in specific events (composite key: Victim_No, Person_ID)

---

## Troubleshooting

### Connection Errors

**Error:** `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")`

- Ensure MySQL server is running
- On Windows: Check Services (search "Services" → find "MySQL" → ensure it's "Running")
- Test connection: `mysql -u root -p -e "SELECT VERSION();"`

**Error:** `pymysql.err.OperationalError: (1045, "Access denied for user 'root'@'localhost'")`

- Verify your password is correct
- Try connecting from Terminal B first: `mysql -u root -p`

### Database Not Found

**Error:** `pymysql.err.ProgrammingError: (1049, "Unknown database 'strangerdb'")`

- Run `schema.sql` first: `mysql -u root -p < .\src\schema.sql`
- Verify: `mysql -u root -p -e "SHOW DATABASES;" | findstr strangerdb`

### Missing Tables

**Error:** `pymysql.err.ProgrammingError: (1146, "Table 'strangerdb.Event' doesn't exist")`

- Run `schema.sql` again to create all tables

### Foreign Key Constraint Errors

**Error during `populate.sql`:** `pymysql.err.IntegrityError: (1452, "Cannot add or update a child row")`

- Ensure `schema.sql` ran successfully before `populate.sql`
- Data insertion order is critical; `populate.sql` handles this automatically

---

## Performance Notes

- The synthetic dataset includes:
  - 50+ locations (25 Normal, 25 UpsideDown)
  - 100+ events with varying severity
  - 500+ entity sightings (Entity_Appearance records)
  - 150+ persons (researchers, agents, victims, psychic subjects)
  - 200+ artifacts and portal linkages
  - 220+ reports and experiments

- Analytic queries (like Reality Disturbance Map) compute values dynamically from the database state
- Event duration is calculated via `TIMESTAMPDIFF` (no stored Duration column)
- Portal–Event linking uses `Event.Portal_ID` foreign key (not a separate junction table)

---

## Python Dependencies

The `requirements.txt` file specifies:

```
PyMySQL==1.1.0
colorama==0.4.6
```

All other imports in `main_app.py` are from the Python standard library (`sys`, `time`, `getpass`, etc.).

---

## Notes & Tips

1. **Use Numeric IDs**: When prompted for entity identifiers, always use numeric IDs (Entity_ID, Person_ID, Event_ID) to avoid issues with duplicate names.

2. **Soft Deletes**: The "Archive" operations (options 25–26) are soft deletes — they mark records as archived but don't remove them from the database.

3. **Hard Deletes**: "Delete Artifact" (option 27) is a hard delete that removes the record entirely. Use with caution.

4. **Terminal Clearing**: Keep terminals clean during demos:
   - PowerShell: `Clear-Host` or `cls`
   - CMD: `cls`

5. **Video Submission**: Your final submission should clearly show:
   - Terminal A running Python (`main_app.py`)
   - Terminal B running MySQL client
   - Before/after SELECT queries for each update operation
   - All query functions (options 1–6) working correctly

---

## Quick Start (All-in-One)

```powershell
# 1. Navigate to project
cd 'c:\Users\maith\Desktop\dna'

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database (in MySQL)
# mysql -u root -p < .\src\schema.sql
# mysql -u root -p strangerdb < .\src\populate.sql

# 5. Run the application
cd src
python main_app.py
```

---

## Limitations

- The application uses a **single-node MySQL deployment** and does not address replication, sharding, or distributed database concerns.
- Authentication relies on **database credentials only**; no role-based access control is implemented at the application layer.
- The CLI interface is intentionally minimal and does not include pagination, autocomplete, or rich visualization.
- Analytics are computed **on-demand** and are not pre-aggregated or cached.
- Concurrency control relies on MySQL’s default isolation mechanisms; no explicit transaction orchestration or locking strategies are implemented in the application layer.
- The system is designed for **educational and evaluative use**, not as a production-ready operations console.

## Conclusion

StrangerDB demonstrates a complete, end-to-end approach to relational database–backed system design, combining schema modeling, query logic, and operational workflows within a single interactive application. By focusing on correctness, traceability, and data integrity, the project highlights how thoughtful schema design and disciplined SQL usage directly shape application behavior.

The console’s analytics, CRUD operations, and relationship management illustrate practical challenges such as maintaining referential integrity, handling historical data through soft deletes, and computing derived metrics from normalized data. The two-terminal demo workflow further emphasizes transparency and verifiability, reinforcing best practices for debugging and validating database-driven systems.

Overall, this project serves as a strong foundation for reasoning about backend systems, database design, and operational tooling, and provides a solid basis for further extensions such as access control, performance optimization, and scalable deployment architectures.
---

