# Time Management Portal - Database Structure

*Extracted from database query file analysis*

## Database Tables and Views

### 1. **Login_Account** (Table)
User authentication and account management

**Columns:**
- `ID` - INTEGER PRIMARY KEY
- `Login_Name` - TEXT (username for login)
- `Password` - TEXT (hashed password)
- `Account_Type` - TEXT (user role/type)
- `Account_Type_ID` - INTEGER (role identifier)
- `Full_Name` - TEXT (computed from first + last name)
- `First_Name` - TEXT
- `Last_Name` - TEXT
- `Email` - TEXT
- `Status` - TEXT (account status)

**Indexes/Constraints:**
- Primary Key: ID
- Unique constraint likely on Login_Name

**Usage:** User authentication, session management, account administration

---

### 2. **Task_Ticket** (Table) 
Primary task management and tracking system

**Columns:**
- `ID` - INTEGER PRIMARY KEY
- `Task_Type` - TEXT (ASR, Project, etc.)
- `Task_Sub_Type` - TEXT (specific subtype based on task type)
- `Ticket_ID` - TEXT (reference ticket identifier)
- `Status` - TEXT (Open, Closed, etc.)
- `Task_Owner` - TEXT (full name of person assigned)
- `Task_Create_Date` - DATETIME (YYYY-MM-DD HH:MM:SS format)
- `Task_Close_date` - DATETIME (when task was completed)
- `Task_Last_Update` - DATETIME (last modification timestamp)
- `Time_Spent_On_Task` - NUMERIC (hours spent)
- `Description` - TEXT (task details)

**Business Rules:**
- When status changes to 'Closed', Task_Close_date is auto-set if not provided
- Task types and subtypes reference Alias table
- Non-administrators can only see tasks where Task_Owner = their full name

**Usage:** Main task tracking, time logging, dashboard reporting

---

### 3. **incident_ticket** (Table)
IT incident tracking and resolution

**Columns:**
- `ID` - INTEGER PRIMARY KEY
- `Incident_Ticket_ID` - TEXT (external ticket reference)
- `Impact_Service` - TEXT (affected service/system)
- `Description` - TEXT (incident details)
- `Status` - TEXT (Active states vs 'Resolved'/'Closed')
- `Open_By` - TEXT (person who reported)
- `Open_Date` - DATETIME (when incident was reported)
- `Close_Date` - DATETIME (when incident was resolved)
- `Time_Spent` - NUMERIC (hours spent on resolution)
- `Assign_Group` - TEXT (team assigned to incident)
- `Assign_to` - TEXT (individual assigned)
- `Root_Cause` - TEXT (analysis of incident cause)

**Status Workflow:**
- Active: Any status except 'Resolved', 'Closed'
- Closed: 'Resolved', 'Closed'

**Usage:** Incident management, response tracking, root cause analysis

---

### 4. **Change_Ticket** (Table)
Change request and change management

**Columns:**
- `ID` - INTEGER PRIMARY KEY
- `Change_Ticket_ID` - TEXT (external change reference)
- `Impact_Service` - TEXT (services affected by change)
- `Task_name` - TEXT (change task description)
- `Change_state` - TEXT (workflow status)
- `Request_Ticket_ID` - TEXT (originating request reference)
- `Task_Start_Date` - DATE (planned start)
- `Task_End_Date` - DATE (planned/actual completion)
- `Time_Spent` - NUMERIC (hours spent on change)
- `Assignment_Group` - TEXT (team responsible)
- `Request_By` - TEXT (change requestor)
- `Change_Delegation` - TEXT (person delegated to)

**Status Workflow:**
- Active: Any status except 'Completed', 'Cancelled'
- Closed: 'Completed', 'Cancelled'

**Integration:** Can create Task_Ticket records from change tickets

**Usage:** Change management, task creation, planning and tracking

---

### 5. **Alias** (Table)
Reference data and lookup values

**Columns:**
- `Name` - TEXT (display name/value)
- `Object_Type_ID` - INTEGER (category identifier)
- `Object_Sub_Type_ID` - INTEGER (subcategory link)
- `Sequence_No` - INTEGER (ordering/hierarchy)

**Reference Categories:**
- `Object_Type_ID = 8`: Task Types
  - Sequence_No = 1: ASR
  - Sequence_No = 2: Project
- `Object_Type_ID = 9`: Task Subtypes
  - Object_Sub_Type_ID links to parent task type's Sequence_No

**Usage:** Dropdown population, data validation, type hierarchies

---

### 6. **user_account_view** (View)
Simplified user authentication view

**Columns:**
- `ID` - INTEGER
- `Account_Type` - TEXT
- `Full_Name` - TEXT
- `Login_Name` - TEXT
- `Password` - TEXT

**Usage:** Login authentication, user lookup

---

### 7. **Task** (Table)
Additional task-related data (distinct from Task_Ticket)

**Usage:** Team workload calculations, reporting aggregations

*Note: Limited column information available from current query analysis*

---

## Database Relationships

### Primary Relationships
1. **Login_Account.Account_Type_ID** → **Account_Type.ID**
2. **Task_Ticket.Task_Type** → **Alias.Name** (where Object_Type_ID=8)
3. **Task_Ticket.Task_Sub_Type** → **Alias.Name** (where Object_Type_ID=9)
4. **Alias(Object_Type_ID=9).Object_Sub_Type_ID** → **Alias(Object_Type_ID=8).Sequence_No**

### View Relationships
1. **Account_View** joins **Login_Account** with **Account_Type** for readable account types

### Data Flow Relationships
1. **incident_ticket** can generate **Task_Ticket** records
2. **Change_Ticket** can generate **Task_Ticket** records
3. **Login_Account** provides authentication for all ticket access

## Security and Access Control

### User Role System
- **Administrator**: Full access to all data across all modules
- **Regular User**: Restricted access based on assignment/ownership
  - Tasks: Only where Task_Owner = user's Full_Name
  - Incidents: Based on assignment (implementation varies)
  - Changes: Based on delegation/assignment

### Session Management
- Login credentials validated against Login_Account/user_account_view
- Session stores: id, username, account_type, full_name
- All routes check session['username'] for authentication

## Data Integrity and Business Rules

### Date Handling
- All datetime fields use 'YYYY-MM-DD HH:MM:SS' format
- Auto-population of creation dates when not specified
- Auto-setting of close dates when status changes to closed states

### Time Tracking
- Numeric fields for hours spent across all ticket types
- Aggregation for dashboard reporting and workload analysis

### Status Workflows
Each ticket type has defined status progressions:
- **Tasks**: Open → Closed
- **Incidents**: Various → Resolved/Closed
- **Changes**: Various → Completed/Cancelled

### Filtering and Search
All main entities support:
- ID/Ticket ID partial matching
- Status filtering
- Date range filtering
- User/assignment filtering

## Dashboard and Reporting

### Data Sources
- **Daily Task Hours**: Aggregated from Task_Ticket
- **Task Type Distribution**: Monthly breakdown by user
- **Team Workload**: Cross-user analysis
- **Activity Summaries**: Time-based metrics

### Performance Considerations
- Indexes likely on ID fields, dates, and assignment fields
- Views for simplified authentication queries
- Date-based filtering for dashboard performance

---

*This structure is derived from comprehensive analysis of the database query modules. For exact schema DDL, direct database inspection tools would be required.*
