---- MODULE WORKFLOW ----
EXTENDS Naturals, Sequences, TLC

\* Workflow states
CONSTANTS PLAN, PLAN_REVIEW, PLAN_READY, WORK, WORK_REVIEW, WORK_DONE
States == {PLAN, PLAN_REVIEW, PLAN_READY, WORK, WORK_REVIEW, WORK_DONE}

\* Linear order
NextMap ==
  [PLAN |-> PLAN_REVIEW,
   PLAN_REVIEW |-> PLAN_READY,
   PLAN_READY |-> WORK,
   WORK |-> WORK_REVIEW,
   WORK_REVIEW |-> WORK_DONE]

\* Chore identifiers (bounded for TLC)
CONSTANTS Chores

VARIABLES status

Init ==
  /\ status = [c \in Chores |-> PLAN]

NextStatus(s) ==
  IF s = WORK_DONE THEN WORK_DONE ELSE NextMap[s]

\* Single-step advance for one chore
Advance(id) ==
  /\ id \in Chores
  /\ status[id] # WORK_DONE
  /\ status' = [status EXCEPT ![id] = NextStatus(@)]

\* Single-step rejection from review states
Reject(id) ==
  /\ id \in Chores
  /\ status[id] = PLAN_REVIEW \/ status[id] = WORK_REVIEW
  /\ status' = [status EXCEPT ![id] = IF @ = PLAN_REVIEW THEN PLAN ELSE WORK]

\* Stutter (no-op)
NoOp ==
  /\ status' = status

Next ==
  \/ \E id \in Chores: Advance(id)
  \/ \E id \in Chores: Reject(id)
  \/ NoOp

\* Safety: only valid states
TypeOK == status \in [Chores -> States]

\* Safety: status advances at most one step (forward or rejection)
LinearAdvance ==
  \A id \in Chores:
    status'[id] = status[id] \/
    (status[id] # WORK_DONE /\ status'[id] = NextStatus(status[id]))
    \/ (status[id] = PLAN_REVIEW /\ status'[id] = PLAN)
    \/ (status[id] = WORK_REVIEW /\ status'[id] = WORK)

Spec == Init /\ [][Next]_<<status>>

THEOREM Spec => []TypeOK

=============================================================================
