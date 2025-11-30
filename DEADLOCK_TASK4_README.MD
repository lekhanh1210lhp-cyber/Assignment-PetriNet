## **TASK 4: PERFORMANCE REPORT**
1. **Methodology**
* To evaluate the performance of the Deadlock Detection algorithm (using ILP formulation and BDD), we executed the code on four distinct models representing different structural properties (Loops, Choices, Resource Sharing).

    * Environment: Python 3.x

    * Library: `dd` (C-based BDD library wrapper)

    * Measurement Metrics:

        * Execution Time (s): Total time for Reachability Analysis + Deadlock Checking.

        * Reachable States (RS): Total number of states found 

        * Memory (MB): Peak memory usage during execution.

2. **Experimental Results**

    | Model Name | Description | Expected Result | Actual Result | Reachable States (RS) | Avg Execution Time (s) | Status |
    |:----------|:----------|:----------|:----------|:----------:|:----------|:----------:|
    | `case_no_deadlock.pnml` | Simple loop structure, infinite run. | NO DEADLOCK | NO DEADLOCK | 6 | 0.002052 | PASS |
    | `case_choice_deadlock.pnml` | Non-deterministic choice leading to a sink state. | DEADLOCK | DEADLOCK | 2 | 0.000661 | PASS |
    | `case_resource_deadlock.pnml` | Resource contention (Circular Wait). | DEADLOCK | DEADLOCK | 3 | 0.000799 | PASS |

3. **Analysis**

    * **Performance**: The algorithm solves all example models in a fraction of a second (under 0.01s). This demonstrates the efficiency of BDDs for 1-safe Petri nets compared to explicit state enumeration, especially as the state space grows.

    * **Complexity (RS)**: The `Reachable States` column correlates with the complexity. Even with a larger state space, the symbolic BDD approach maintains low execution time.

    * **Accuracy**: The logic correctly identified deadlocks in scenarios involving choices and resource sharing, while correctly identifying the liveness of the loop model.

    * **ILP/BDD Logic**: The logic `Deadlock = Reachable AND (NOT Enabled_T1 AND NOT Enabled_T2 ...)` proved effective without requiring an external ILP solver.


## **DETAIL UPDATE FOR TASK 4 FROM PREVIOUS VERSION- THEHOANG**

1. `petrinet.py` **Modifications**

    * Updated **run_reachability_bdd**: Now returns 3 values: `num_states`, `visited_bdd`, and `bdd` (the manager). This is crucial because Task 4 needs the same BDD manager context to perform logical operations on the variables.

    * Added **check_deadlock_bdd**: Implements the logic described above. It performs bitwise `OR` (`|`) for the disabled condition and bitwise AND (&) for the system-wide dead condition.

2. `main.py` **Modifications**

    * **Pipeline Update:** The script now captures the `bdd_manager` returned from Task 3.

    * **Execution**: It calls `net.check_deadlock_bdd(bdd_manager, visited_bdd)` immediately after Task 3 finishes.

    * **Reporting**: Prints whether a deadlock is found and displays the specific marking (e.g., `{'p1': 0, 'p2': 0}`) if one exists.

3. **Test Data**

* **3 specific test case** was created to verify the logic. located in the `data` folder :

    * `case_choice_deadlock.pnml`

    * `case_no_deadlock.pnml`

    * `case_resource_deadlock.pnml`


## **How to Run & Verify**

1. **Prerequisites**

    Ensure the `dd` library is installed:
    ```
    pip install dd
    ```

2. **Change testcase file location**

    in **main.py** Chose the test case you want in in data folder, and put it in the `file_path` (replace the `XXXXXX.pnml` )
    ```
    file_path = os.path.join(root_dir, "data", "XXXXXX.pnml")
    ```

3. **Execution**

    Run the main script from the `src` directory:
    ```
    python main.py
    ```

**Expected Output (Example)**
```
>>> TASK 3: SYMBOLIC BDD <<<
--> States found: 3
...

>>> TASK 4: DEADLOCK DETECTION (ILP/BDD) <<<
Đang kiểm tra Deadlock...
--> DEADLOCK DETECTED! Found one dead marking:
    {'p1': 0, 'p2': 0}
```