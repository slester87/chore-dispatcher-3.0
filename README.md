# Chore Dispatcher 3.0

![ci](https://github.com/slester87/chore-dispatcher-3.0/actions/workflows/ci.yml/badge.svg)

Greenfield implementation of the Chore Dispatcher system per the 3.0 technical specification.

- Spec source: `chore_dispatcher_3.0_technical_spec.md`
- Build plan: `PLAN.md`

## TMUX behavior (default on)

- PLAN: create `chore<id>_Planner`.
- PLAN_REVIEW: add a review pane to `chore<id>_Planner`.
- PLAN_READY: tear down `chore<id>_Planner`.
- WORK: create `chore<id>_Worker`.
- WORK_REVIEW: add a review pane to `chore<id>_Worker`.
- WORK_DONE: tear down `chore<id>_Worker`.

## Running the HTTP MCP server

By default it binds to `127.0.0.1:8080` and mounts MCP at `/mcp` (configurable in `configs/default.toml`).

```
python -m chore_dispatcher.mcp.http_server
```

To override config:

```
export CHORE_DISPATCHER_CONFIG=/path/to/config.toml
python -m chore_dispatcher.mcp.http_server
```

## HTTP client usage

```
from chore_dispatcher.client import ChoreDispatcherClient

with ChoreDispatcherClient("http://127.0.0.1:8080") as client:
    chore = client.create("Example chore")
    print(chore["id"])
```

## HTTP CLI

```
chore-dispatcher-http --base-url http://127.0.0.1:8080 health
chore-dispatcher-http create "Example chore"
chore-dispatcher-http list-active
```

---

## Technical Specification

Below is the full 3.0 technical spec (mirrored here for convenience).

# Chore Dispatcher System - Technical Specification

## Overview

The Chore Dispatcher is a chore management system built on an MCP server that uses agents to work through a structured 6-stage workflow with unique identifiers, chaining capabilities, and automated tmux-based execution environments. Each chore progresses through defined states with validation, review processes, and automatic advancement capabilities.


## Core Architecture

### 1. Workflow State Machine

The system implements a linear 6-stage workflow:

```
PLAN → PLAN_REVIEW → PLAN_READY → WORK → WORK_REVIEW → WORK_DONE
```

#### 1.1 TMUX Workflow Intention
 TMUX dispatch rules (implementation)

  - PLAN → create planner window
  - PLAN_REVIEW → add review pane to plan window
  - PLAN_READY → tear down plan window
  - WORK → create worker window
  - WORK_REVIEW → add review pane to work window
  - WORK_DONE → tear down work window

#### State Definitions


1. **PLAN** - Implementation planning phase with detailed steps
2. **PLAN_REVIEW** - Review of the implementation plan
3. **PLAN_READY** - Plan approved, ready for implementation
4. **WORK** - Active development/implementation phase
5. **WORK_REVIEW** - Review of completed work
6. **WORK_DONE** - Work complete and approved (terminal state)

#### Roles

The system uses exactly four roles:

1. **PLANNER**
2. **PLAN_REVIEWER**
3. **WORKER**
4. **WORK_REVIEWER**

Design responsibilities are handled within the PLANNER phase; there is no separate design role or state.

#### State Transition Rules

- States advance linearly through the workflow
- Only one state transition per advancement operation
- Sub-chores must be complete before parent chore can advance
- Review states can approve (advance) or reject (return to previous work state)
- Terminal state (WORK_DONE) cannot advance further

### 2. Unique Identifier System (Snowflake)

#### Algorithm Specification

64-bit unique identifier generation using Twitter Snowflake algorithm:

```
Bit Layout: [41 bits timestamp][10 bits node_id][12 bits sequence]
```

#### Implementation Details

- **Timestamp**: 41 bits, milliseconds since custom epoch (Jan 1, 2024 UTC: 1704067200000)
- **Node ID**: 10 bits, supports 1024 unique nodes (0-1023)
- **Sequence**: 12 bits, supports 4096 IDs per millisecond per node
- **Thread Safety**: Mutex-protected sequence generation
- **Clock Drift**: Throws runtime error if clock moves backwards
- **Sequence Overflow**: Waits for next millisecond when sequence exhausted

#### Key Methods

```python
class Snowflake:
    def __init__(self, node_id: int)  # Validates node_id range
    def next_id(self) -> int         # Thread-safe ID generation
    def _now_ms(self) -> int         # Current timestamp in milliseconds
    def _wait_next_ms(self, ts) -> int  # Wait for next millisecond
```

### 3. Chore Data Structure

#### Core Properties

```python
class Chore:
    id: int                          # Snowflake-generated unique ID
    name: str                        # Human-readable chore name
    description: str                 # Detailed description
    status: ChoreStatus              # Current workflow state
    next_chore: Optional[Chore]      # Chained next chore
    progress_info: Optional[str]     # Worker progress updates
    review_info: Optional[str]       # Reviewer feedback
    parent_chore_id: Optional[int]   # Parent chore ID for hierarchical structure
    sub_chores: List[Chore]          # Child chores
```

#### Behavioral Methods

- `can_advance() -> bool`: Validates if chore can advance (all sub-chores complete)
- `advance_status() -> bool`: Advances to next state if possible
- `is_complete() -> bool`: Returns true if status is WORK_DONE
- `set_next_chore(chore)`: Establishes chaining relationship
- `get_next_chore() -> Optional[Chore]`: Returns next chore if current is complete
- `add_sub_chore(chore)`: Adds hierarchical sub-chore
- `get_sub_chores() -> List[Chore]`: Returns all sub-chores

### 4. Chore Repository (CRUD Operations)

#### Interface Specification

```python
class ChoreRepository:
    def create(name: str, description: str = "") -> Chore
    def read(chore_id: int) -> Optional[Chore]
    def update(chore_id: int, **kwargs) -> Optional[Chore]
    def delete(chore_id: int) -> bool
    def list_all() -> List[Chore]
    def find_by_status(status: ChoreStatus) -> List[Chore]
```

#### Unit-of-Work (Transactional Semantics)

The repository layer supports a Unit-of-Work (UoW) abstraction to stage changes and apply them atomically.

```python
class UnitOfWork:
    def begin() -> None
    def commit() -> None
    def rollback() -> None
    def repository() -> ChoreRepository
```

- CRUD operations performed within a UoW may operate on a staged snapshot until commit.
- If validation fails during a UoW, the UoW must be rolled back and no partial state is exposed.

#### Hierarchical Operations

```python
def create_sub_chore(parent_id: int, name: str, description: str) -> Optional[Chore]
def get_sub_chores(parent_id: int) -> List[Chore]
def get_parent_chore(chore_id: int) -> Optional[Chore]
def find_root_chores() -> List[Chore]  # Chores without parents
```

#### Persistence Layer

- **Storage Format**: JSONL (JSON Lines) for active chores
- **Archive Format**: Separate JSONL file for completed chores
- **Serialization**: Bidirectional chore ↔ dictionary conversion
- **Relationship Linking**: Post-load linking of chore chains and parent-child relationships
- **Atomic Operations**: Cross-file atomicity via a manifest pointer file. Writes must stage both active and archive JSONL files, then atomically swap a single manifest file that points to the new pair (write-temp + fsync + rename). This ensures active and archive are updated as one logical unit.
- **Mutual Exclusivity Rule**: A chore must never exist in both the active JSONL store and the archive JSONL store at the same time. Archival is a move operation, not a copy.

#### Data Integrity

- **Chain Validation**: Detects circular references in chore chains
- **Orphan Detection**: Identifies sub-chores with missing parents
- **Duplicate Cleanup**: Removes duplicate chore entries
- **System Repair**: Automated integrity validation and repair

### 5. Chore Chaining Mechanism

#### Chain Establishment

```python
chore_a.set_next_chore(chore_b)  # Creates A → B chain
```

#### Chain Activation

- Chains activate only when current chore reaches WORK_DONE status
- `get_next_chore()` returns next chore only if current is complete
- Automatic chain activation through lifecycle manager
- Circular chain detection prevents infinite loops

#### Chain Validation

- Validates chain integrity on system startup
- Detects and reports circular references
- Repairs broken chain links where possible

### 6. TMUX Integration & Execution Environment

#### Session Management

- **Session Name**: "chore-dispatcher" (configurable)
- **Session Isolation**: Dedicated session for all chore windows
- **Session Persistence**: Survives terminal disconnection
- **Auto-Creation**: Creates session if not exists
- **Calls KIRO with Role Prompt + Chore instructions**: The critical component delivering value in this project is building a string out of a role prompt and the instructions needed to complete the chore, and then giving that string to a new process of KIRO called in the correct working directory for that KIRO to make the required changes. When the KIRO completes work on chore, it should automatically advance chore to the next state and tear down.

#### Dispatch Triggers (Window/Panes)

- **PLAN**: Create a new window for the planner.
- **PLAN_REVIEW**: Add a review pane to the existing plan window.
- **PLAN_READY**: Tear down the plan window after approval.
- **WORK**: Create a new window for the worker.
- **WORK_REVIEW**: Add a review pane to the existing work window.
- **WORK_DONE**: Tear down the work window after approval.

#### Window Naming Convention

```
chore{chore_id}_{Planner|Worker}
```

- **Planner Window**: Used for PLAN and PLAN_REVIEW states
- **Worker Window**: Used for WORK and WORK_REVIEW states
- **Unique Identification**: Chore ID ensures uniqueness

#### Window Types by Status


1. **PLAN**: Single-pane planner window with Kiro CLI  
2. **WORK**: Single-pane worker window with Kiro CLI
3. **REVIEW States**: Split-pane with Planner + Reviewer and Worker + reviewer

#### Kiro CLI Integration

```bash
# Command Template
{wrapper_script} {chore_id} {role_type} {kiro_path} {trusted_tools} {prompt}
```

- **Wrapper Script**: Monitors exit signals and handles cleanup
- **Role Types**: planner, plan_reviewer, worker, work_reviewer
- **Trusted Tools**: "@chore-dispatcher,read,write,web_fetch,web_search,grep,glob,shell,code"
- **Context Injection**: Role-specific prompts with chore context

#### Environment Variables

```bash
CHORE_ID="{chore.id}"
CHORE_NAME="{chore.name}"
CHORE_DESCRIPTION="{chore.description}"
CHORE_STATUS="{chore.status.value}"
CHORE_ROLE="{role.upper()}"
```

### 7. Auto-Advancement System

#### Configuration

```python
class AutoAdvanceConfig:
    delays = { 
        ChoreStatus.PLAN: 5,      # seconds
        ChoreStatus.WORK: 10,
        ChoreStatus.PLAN_REVIEW: 3,
        ChoreStatus.WORK_REVIEW: 5,
    }
```

#### Timer Management

- **Thread-Safe**: Mutex-protected timer operations
- **Cancellation**: Active timers cancelled on status change
- **Validation**: Only advances if chore still in expected status
- **Logging**: Comprehensive advancement tracking

#### Advancement Actions

- **Action Phases** (PLAN, WORK): Advance to corresponding REVIEW state
- **Review Phases**: Approve to advance to next READY/DONE state only if the plan/work is Acceptable.
Otherwise, Disapprove and send back to the previous state for re-work.
- **Status Validation**: Confirms expected status before advancement

### 8. Signal-Based Communication

#### Signal Files

```
/tmp/kiro_signals/chore_{chore_id}_complete
/tmp/kiro_signals/chore_{chore_id}_exit
```

#### Signal Detection

- **Completion Signals**: Trigger phase advancement
- **Exit Signals**: Graceful shutdown of chore windows
- **File Monitoring**: Periodic signal file checking
- **Cleanup**: Signal files removed after processing

### 9. Completion Standards

Before marking chore as WORK_DONE, it must satisfy these conditions:

- ✅ Compile without errors
- ✅ Pass linter checks  
- ✅ Build successfully
- ✅ Run without runtime errors
- ✅ Pass all tests
- ✅ Meet release quality standards

### 10. Error Handling & Validation

#### Phase Validation

```python
class PhaseValidator:
    def validate_transition(from_status, to_status, chore) -> bool
    def _validate_progress_info(progress_info: str) -> bool
    def _validate_review_info(review_info: str) -> bool
    def _validate_work_quality(chore: Chore) -> bool
```

#### Exception Types

- `ValidationError`: Phase transition validation failures
- `TransitionError`: Invalid state transitions
- `RuntimeError`: Clock drift in Snowflake generation

#### Recovery Mechanisms

- **System Repair**: Automated integrity validation and repair
- **Chain Repair**: Fixes broken chore chain references
- **Orphan Cleanup**: Handles sub-chores with missing parents
- **Duplicate Resolution**: Removes duplicate entries
- **Transactional Safety**: Validation errors inside a UoW trigger rollback with no partial writes

### 11. Communication Templates

#### Progress Updates

```python
def format_progress_info(phase: str, content: str) -> str
def parse_progress_info(progress_info: str) -> Dict[str, str]
```

#### Review Feedback

```python
def format_review_info(approved: bool, feedback: str) -> str
def parse_review_info(review_info: str) -> Dict[str, Any]
```

#### Template Types

- **Plan Progress**: Implementation steps, resource planning
- **Work Progress**: Development updates, completion status
- **Review Templates**: Approval/rejection with structured feedback

### 12. Lifecycle Management

#### State Transition Engine

```python
class StateTransitionEngine:
    def execute_transition(chore_id, from_status, to_status) -> bool
    def validate_transition(from_status, to_status) -> bool
```

#### Chain Activation Engine

```python
class ChainActivationEngine:
    def handle_chain_completion(completed_chore: Chore) -> Optional[Chore]
    def activate_next_chore(chore_id: int) -> bool
    def validate_chain_integrity() -> List[str]  # Returns validation errors
```

#### Archival Manager

```python
class ArchivalManager:
    def archive_completed_chore(chore: Chore) -> None
    def save_active_chores(chores: Dict[int, Chore]) -> None
    def cleanup_duplicates() -> int  # Returns count of removed duplicates
```

#### Transaction Boundaries

- Lifecycle operations (state transition, chain activation, archival) should occur within a single UoW to ensure consistency.

### 13. Integration Hooks

#### Dispatcher Hooks

```python
class DispatcherHooks:
    def on_chore_created(chore: Chore) -> None
    def on_chore_state_change(chore: Chore, old_status: ChoreStatus) -> None
    def on_chore_deleted(chore_id: int) -> None
```

#### MCP HTTP Interface

- **Server**: FastAPI + FastMCP implementation.
- **Mounts**: MCP tools at configurable `mcp_path` (default `/mcp`).
- **JSON API**: Simple HTTP endpoint at `/api` for production clients.

**HTTP API Request (POST /api):**

```json
{
  "id": "optional",
  "method": "create|read|update|delete|list_active|list_all|...",
  "params": { "..." : "..." }
}
```

**HTTP API Response:**

```json
{
  "id": "optional",
  "result": { "..." : "..." }
}
```

Errors return:

```json
{
  "id": "optional",
  "error": { "message": "..." }
}
```

**Client Module**: A production-ready HTTP client is provided for the `/api` endpoint.

#### TMUX Integration

- **Window Creation**: Automatic window creation on chore dispatch which invokes KIRO with a dynamically generated string corresponding to the chore body such that a new process of KIRO is spun up to work on the chore body in the correct role for the current phase of the chore (Planner/PlanReviewer/Worker/WorkReviewer)
- **Prompt Updates**: Dynamic window title updates based on chore status
- **Pane Management**: Split-pane creation for review phases
- **Session Cleanup**: Automatic cleanup of completed chore windows

### 14. Testing Requirements

#### Unit Test Coverage

- Chore creation and status progression
- Snowflake ID uniqueness and thread safety
- Repository CRUD operations
- Chain validation and activation
- Auto-advancement timing and cancellation

#### Integration Test Coverage

- Complete workflow progression (PLAN → WORK_DONE)
- TMUX window creation and management
- Signal-based communication
- System integrity validation
- Archival and persistence operations

#### Performance Test Coverage

- Bulk chore creation (1000+ chores)
- Concurrent access patterns
- Memory usage under load
- TMUX window operation stress testing
- File I/O performance with large datasets

### 15. Quality Gates

#### Pre-Push Validation

```bash
python3 chore_dispatcher/test_chore.py  # Core functionality
python3 chore_dispatcher/tests/run_tests.py  # Full test suite
```

#### Continuous Validation

- Git pre-push hooks enforce test execution
- System integrity validation on startup
- Automated chain validation
- Orphan detection and cleanup

### 16. Implementation Notes

#### Thread Safety

- Snowflake ID generation is mutex-protected
- Auto-advance timer operations are thread-safe
- Repository operations use file-based locking and may be mediated through a UoW abstraction for transactional semantics

#### Platform Compatibility

- TMUX binary detection across platforms
- Path handling for macOS/Linux differences
- Shell command escaping for security

#### Extensibility Points

- Pluggable completion criteria validation
- Configurable auto-advancement delays
- Custom signal handlers
- Template-based communication formats

## Conclusion

This specification provides complete behavioral and implementation details for the Chore Dispatcher system. The design emphasizes reliability, thread safety, and extensibility while maintaining simplicity in core operations. The system can be implemented in any programming language following these specifications while preserving all functional requirements and behavioral characteristics.
