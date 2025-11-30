## DETAIL CHANGED FOR TASK 4 - THEHOANG

1. petrinet.py Modifications

    * Updated run_reachability_bdd: Now returns 3 values: num_states, visited_bdd, and bdd (the manager). This is crucial because Task 4 needs the same BDD manager context to perform logical operations on the variables.

    * Added check_deadlock_bdd: Implements the logic described above. It performs bitwise OR (|) for the disabled condition and bitwise AND (&) for the system-wide dead condition.

2. main.py Modifications

    * Pipeline Update: The script now captures the bdd_manager returned from Task 3.

    * Execution: It calls net.check_deadlock_bdd(bdd_manager, visited_bdd) immediately after Task 3 finishes.

    * Reporting: Prints whether a deadlock is found and displays the specific marking (e.g., {'p1': 0, 'p2': 0}) if one exists.

3. Test Data (deadlock_task4.pnml)

* A specific test case was created to verify the logic:

    * Structure: $P1 \to T1 \to P2 \to T2$

    * Scenario: $T2$ consumes a token from $P2$ but has no output place.

    * Outcome: After $T2$ fires, the system loses all tokens. All places are 0. No transition can fire. This is a generic Deadlock state caught by the algorithm.

## How to Run & Verify

Prerequisites

Ensure the dd library is installed:
```
pip install dd
```

Execution

Run the main script from the src directory:
```
python main.py
```

Expected Output (Example)
```
>>> TASK 3: SYMBOLIC BDD <<<
--> States found: 3
...

>>> TASK 4: DEADLOCK DETECTION (ILP/BDD) <<<
Đang kiểm tra Deadlock...
--> DEADLOCK DETECTED! Found one dead marking:
    {'p1': 0, 'p2': 0}
```