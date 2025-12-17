-- STAGE 1 – Relational Schema (matches diagram exactly)

DROP DATABASE IF EXISTS strangerdb;
CREATE DATABASE strangerdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE strangerdb;

-- --------------------------------------------------
-- PERSON (superclass)
-- --------------------------------------------------
CREATE TABLE Person (
  Person_ID      INT AUTO_INCREMENT PRIMARY KEY,
  Name           VARCHAR(200) NOT NULL,
  Role           ENUM('Researcher','Agent','Victim','Psychic_Subject') NOT NULL,
  Age            INT,
  Status         ENUM('Active','Deceased','Missing') DEFAULT 'Active',
  Affiliation    VARCHAR(200),
  Supervisor_ID  INT NULL,
  Known_Aliases  TEXT,
  CONSTRAINT fk_person_supervisor
    FOREIGN KEY (Supervisor_ID)
    REFERENCES Person(Person_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- SUBCLASSES OF PERSON
-- --------------------------------------------------
CREATE TABLE Researcher (
  Person_ID       INT PRIMARY KEY,
  Clearance_Level VARCHAR(100),
  CONSTRAINT fk_researcher_person
    FOREIGN KEY (Person_ID)
    REFERENCES Person(Person_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Agent (
  Person_ID    INT PRIMARY KEY,
  Success_Rate DECIMAL(5,2),
  CONSTRAINT fk_agent_person
    FOREIGN KEY (Person_ID)
    REFERENCES Person(Person_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Victim (
  Person_ID       INT PRIMARY KEY,
  Injury_Severity VARCHAR(100),
  CONSTRAINT fk_victim_person
    FOREIGN KEY (Person_ID)
    REFERENCES Person(Person_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Psychic_Subject (
  Person_ID     INT PRIMARY KEY,
  Ability_Type  VARCHAR(100),
  Power_Level   INT,
  Control_Score INT,
  CONSTRAINT fk_psychic_person
    FOREIGN KEY (Person_ID)
    REFERENCES Person(Person_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- EXPERIMENT
-- --------------------------------------------------
CREATE TABLE Experiment (
  Exp_ID          INT AUTO_INCREMENT PRIMARY KEY,
  Purpose         VARCHAR(400),
  Confidentiality ENUM('Low','Medium','High') DEFAULT 'High',
  Result          TEXT,
  Date            DATE,
  Conducted_By    INT,
  CONSTRAINT fk_experiment_person
    FOREIGN KEY (Conducted_By)
    REFERENCES Person(Person_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- LOCATION (superclass)
-- --------------------------------------------------
CREATE TABLE Location (
  Location_ID   INT AUTO_INCREMENT PRIMARY KEY,
  Name          VARCHAR(200) NOT NULL,
  World_Type    ENUM('Normal','UpsideDown') NOT NULL,
  Risk_Level    INT DEFAULT 1,
  Description   TEXT,
  Links_To      INT NULL,
  Discovered_On DATE,
  Coordinate_X  DECIMAL(9,6),
  Coordinate_Y  DECIMAL(9,6),
  CONSTRAINT fk_location_links_to
    FOREIGN KEY (Links_To)
    REFERENCES Location(Location_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- SUBCLASSES OF LOCATION
CREATE TABLE Surface_Location (
  Location_ID        INT PRIMARY KEY,
  Population_Density INT,
  Proximity_To_Lab   DECIMAL(5,2),
  CONSTRAINT fk_surface_location
    FOREIGN KEY (Location_ID)
    REFERENCES Location(Location_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE UpsideDown_Location (
  Location_ID      INT PRIMARY KEY,
  Distortion_Level INT,
  Hazard_Type      VARCHAR(100),
  CONSTRAINT fk_upsidedown_location
    FOREIGN KEY (Location_ID)
    REFERENCES Location(Location_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- ARTIFACT
-- --------------------------------------------------
CREATE TABLE Artifact (
  Artifact_ID   INT AUTO_INCREMENT PRIMARY KEY,
  Name          VARCHAR(200),
  Type          ENUM('Biological','Metallic','Organic','Unknown') DEFAULT 'Unknown',
  Anomaly_Level INT,
  Found_At      INT,
  CONSTRAINT fk_artifact_location
    FOREIGN KEY (Found_At)
    REFERENCES Location(Location_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- PORTAL
-- --------------------------------------------------
CREATE TABLE Portal (
  Portal_ID       INT AUTO_INCREMENT PRIMARY KEY,
  Name            VARCHAR(200),
  Status          ENUM('Active','Closed') DEFAULT 'Active',
  Has_Origin      INT,
  Has_Destination INT,
  Links_To        INT NULL,
  Discovered_On   DATE,
  Coordinate_X    DECIMAL(9,6),
  Coordinate_Y    DECIMAL(9,6),
  CONSTRAINT fk_portal_origin
    FOREIGN KEY (Has_Origin)
    REFERENCES Location(Location_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_portal_destination
    FOREIGN KEY (Has_Destination)
    REFERENCES Location(Location_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_portal_links_to
    FOREIGN KEY (Links_To)
    REFERENCES Portal(Portal_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- ENTITY (superclass)
-- --------------------------------------------------
CREATE TABLE Entity (
  Entity_ID      INT AUTO_INCREMENT PRIMARY KEY,
  Name           VARCHAR(200),
  Species        VARCHAR(100),
  Threat_Level   ENUM('Low','Medium','High','Critical') DEFAULT 'Low',
  Origin_World   ENUM('Normal','UpsideDown'),
  First_Sighting DATE
);

-- SUBCLASSES OF ENTITY
CREATE TABLE Monster (
  Entity_ID        INT PRIMARY KEY,
  Aggression_Index INT,
  CONSTRAINT fk_monster_entity
    FOREIGN KEY (Entity_ID)
    REFERENCES Entity(Entity_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Shadow_Creature (
  Entity_ID          INT PRIMARY KEY,
  Corruption_Level   INT,
  Manifestation_Type VARCHAR(100),
  CONSTRAINT fk_shadow_entity
    FOREIGN KEY (Entity_ID)
    REFERENCES Entity(Entity_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Mind_Entity (
  Entity_ID              INT PRIMARY KEY,
  Influence_Range        INT,
  Cognitive_Link_Strength INT,
  CONSTRAINT fk_mind_entity
    FOREIGN KEY (Entity_ID)
    REFERENCES Entity(Entity_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- EVENT
-- --------------------------------------------------
CREATE TABLE Event (
  Event_ID    INT AUTO_INCREMENT PRIMARY KEY,
  Date        DATE,
  Time        TIME,
  Description TEXT,
  Outcome     ENUM('Contained','Ongoing','Catastrophic') DEFAULT 'Ongoing',
  Severity    ENUM('Minor','Moderate','Severe') DEFAULT 'Moderate',
  Location_ID INT,
  Portal_ID   INT,
  CONSTRAINT fk_event_location
    FOREIGN KEY (Location_ID)
    REFERENCES Location(Location_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_event_portal
    FOREIGN KEY (Portal_ID)
    REFERENCES Portal(Portal_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- ENTITY_APPEARANCE
-- --------------------------------------------------
CREATE TABLE Entity_Appearance (
  Appearance_ID INT AUTO_INCREMENT PRIMARY KEY,
  Entity_ID     INT,
  Event_ID      INT,
  Start_Time    DATETIME,
  End_Time      DATETIME,
  CONSTRAINT fk_appearance_entity
    FOREIGN KEY (Entity_ID)
    REFERENCES Entity(Entity_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_appearance_event
    FOREIGN KEY (Event_ID)
    REFERENCES Event(Event_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- REPORT (base) + REPORT_DETAILS
-- --------------------------------------------------
CREATE TABLE Report (
  Report_ID          INT AUTO_INCREMENT PRIMARY KEY,
  Date               DATE,
  Authored_By        INT,
  Verified_By        INT,
  Documents_Artifact INT,
  CONSTRAINT fk_report_authored
    FOREIGN KEY (Authored_By)
    REFERENCES Person(Person_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_report_verified
    FOREIGN KEY (Verified_By)
    REFERENCES Person(Person_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT fk_report_documents
    FOREIGN KEY (Documents_Artifact)
    REFERENCES Artifact(Artifact_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

CREATE TABLE Report_Details (
  Report_ID INT PRIMARY KEY,
  Summary   TEXT,
  Verdict   ENUM('True','False','Unclear') DEFAULT 'Unclear',
  CONSTRAINT fk_reportdetails_report
    FOREIGN KEY (Report_ID)
    REFERENCES Report(Report_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- VICTIM_RECORD (weak entity)
-- --------------------------------------------------
CREATE TABLE Victim_Record (
  Victim_No       INT AUTO_INCREMENT,
  Person_ID       INT,
  Hurt_In         INT,
  Injury_Severity VARCHAR(100),
  PRIMARY KEY (Victim_No, Person_ID),
  CONSTRAINT fk_victim_record_person
    FOREIGN KEY (Person_ID)
    REFERENCES Person(Person_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_victim_event
    FOREIGN KEY (Hurt_In)
    REFERENCES Event(Event_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- --------------------------------------------------
-- M:N JUNCTION TABLES
-- --------------------------------------------------
CREATE TABLE Event_Involves_Entity (
  Event_ID  INT NOT NULL,
  Entity_ID INT NOT NULL,
  PRIMARY KEY (Event_ID, Entity_ID),
  CONSTRAINT fk_eie_event
    FOREIGN KEY (Event_ID)
    REFERENCES Event(Event_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_eie_entity
    FOREIGN KEY (Entity_ID)
    REFERENCES Entity(Entity_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Event_Affects_Artifact (
  Event_ID    INT NOT NULL,
  Artifact_ID INT NOT NULL,
  PRIMARY KEY (Event_ID, Artifact_ID),
  CONSTRAINT fk_eaa_event
    FOREIGN KEY (Event_ID)
    REFERENCES Event(Event_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_eaa_artifact
    FOREIGN KEY (Artifact_ID)
    REFERENCES Artifact(Artifact_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE Event_Documented_By_Report (
  Event_ID  INT NOT NULL,
  Report_ID INT NOT NULL,
  PRIMARY KEY (Event_ID, Report_ID),
  CONSTRAINT fk_edbr_event
    FOREIGN KEY (Event_ID)
    REFERENCES Event(Event_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_edbr_report
    FOREIGN KEY (Report_ID)
    REFERENCES Report(Report_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
