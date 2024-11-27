from pulp import (
    LpMinimize,
    LpProblem,
    LpVariable,
    lpSum,
    LpStatus,
    PULP_CBC_CMD,
    GLPK_CMD
)

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])

def exact_2d_csp(rectangles, sheets, timeout=600, threads=4, verbose=False):
    n = len(rectangles)  # Number of rectangles
    m = len(sheets)      # Number of sheets
    M = max(max(sheet) for sheet in sheets)  # Big M for constraints
    Mrect = max(max(rect) for rect in rectangles)  # Big M for constraints
    M = max(M, Mrect)
    # Define the linear programming problem
    prob = LpProblem("2D_Cutting_Stock_Multiple_Sheets", LpMinimize)

    # Decision variables
    x = { (i, k): LpVariable(f"x_{i}_{k}", lowBound=0, upBound=sheets[k][0], cat='Integer') for i in range(n) for k in range(m) }
    y = { (i, k): LpVariable(f"y_{i}_{k}", lowBound=0, upBound=sheets[k][1], cat='Integer') for i in range(n) for k in range(m) }
    s = { i: LpVariable(f"s_{i}", cat='Binary') for i in range(n) }  # Rotation: 0 = no, 1 = rotated
    z = { (i, k): LpVariable(f"z_{i}_{k}", cat='Binary') for i in range(n) for k in range(m) }
    Q = { k: LpVariable(f"Q_{k}", cat='Binary') for k in range(m) }      # Sheet usage
    a = { (i, j, k): LpVariable(f"a_{i}_{j}_{k}", cat='Binary') for i in range(n) for j in range(i + 1, n) for k in range(m) }
    b = { (i, j, k): LpVariable(f"b_{i}_{j}_{k}", cat='Binary') for i in range(n) for j in range(i + 1, n) for k in range(m) }
    c = { (i, j, k): LpVariable(f"c_{i}_{j}_{k}", cat='Binary') for i in range(n) for j in range(i + 1, n) for k in range(m) }
    d = { (i, j, k): LpVariable(f"d_{i}_{j}_{k}", cat='Binary') for i in range(n) for j in range(i + 1, n) for k in range(m) }
    Sheets_area = LpVariable("Sheets_area", lowBound=least_space(rectangles), upBound=least_space(sheets),cat='Integer')
    # Objective: Minimize the number of sheets used
    # prob += lpSum(Q[k] for k in range(m)), "Minimize_Number_of_Sheets"
    prob += Sheets_area, "Minimize_Trim_loss"
    prob += Sheets_area == lpSum(Q[k] * sheets[k][0] * sheets[k][1] for k in range(m)), "Sheets_area_constraint"
    # 1. Each rectangle must be assigned to exactly one sheet
    for i in range(n):
        prob += (
            lpSum(z[i, k] for k in range(m)) == 1,
            f"Assign_Rectangle_{i}_to_one_Sheet"
        )

    # 2. If a rectangle is assigned to a sheet, activate the sheet
    # Ensures Q[k] is 1 if any z[i,k] is 1
    for k in range(m):
        for i in range(n):
            prob += (
                Q[k] >= z[i, k],
                f"Link_SheetUsage_{i}_{k}"
            )

    # 3. Placement and fitting constraints
    for i in range(n):
        for k in range(m):
            # Calculate width and height based on rotation
            w_i = rectangles[i][0] * (1 - s[i]) + rectangles[i][1] * s[i]
            h_i = rectangles[i][1] * (1 - s[i]) + rectangles[i][0] * s[i]

            # If rectangle i is placed on sheet k, it must fit within the sheet
            prob += (
                x[i, k] + w_i <= sheets[k][0] + M * (1 - z[i, k]),
                f"Fit_Width_Rect_{i}_Sheet_{k}"
            )
            prob += (
                y[i, k] + h_i <= sheets[k][1] + M * (1 - z[i, k]),
                f"Fit_Height_Rect_{i}_Sheet_{k}"
            )

    # 4. Non-overlapping constraints
    for k in range(m):
        for i in range(n):
            for j in range(i + 1, n):
                # Apply constraints only if both rectangles are on the same sheet
                # Ensure at least one non-overlapping condition is met
                prob += (
                    a[i, j, k] + b[i, j, k] + c[i, j, k] + d[i, j, k] >= z[i, k] + z[j, k] - 1,
                    f"AtLeastOne_NoOverlap_{i}_{j}_Sheet_{k}"
                )

                # Calculate width and height based on rotation
                w_i = rectangles[i][0] * (1 - s[i]) + rectangles[i][1] * s[i]
                h_i = rectangles[i][1] * (1 - s[i]) + rectangles[i][0] * s[i]
                w_j = rectangles[j][0] * (1 - s[j]) + rectangles[j][1] * s[j]
                h_j = rectangles[j][1] * (1 - s[j]) + rectangles[j][0] * s[j]

                # Non-overlapping constraints using Big M method
                prob += (
                    x[i, k] + w_i <= x[j, k] + M * (1 - a[i, j, k]),
                    f"NoOverlap_x1_{i}_{j}_Sheet_{k}"
                )
                prob += (
                    x[j, k] + w_j <= x[i, k] + M * (1 - b[i, j, k]),
                    f"NoOverlap_x2_{i}_{j}_Sheet_{k}"
                )
                prob += (
                    y[i, k] + h_i <= y[j, k] + M * (1 - c[i, j, k]),
                    f"NoOverlap_y1_{i}_{j}_Sheet_{k}"
                )
                prob += (
                    y[j, k] + h_j <= y[i, k] + M * (1 - d[i, j, k]),
                    f"NoOverlap_y2_{i}_{j}_Sheet_{k}"
                )

    # Solve the problem
    prob.solve(PULP_CBC_CMD(msg=verbose, timeLimit=timeout, threads=threads))
    # Print solver status
    print("Status:", LpStatus[prob.status])

    if LpStatus[prob.status] != 'Optimal':
        print("No optimal solution found.")
        return None, None, None
    else:
        # Extract results
        result = {}
        for i in range(n):
            for k in range(m):
                if z[i, k].value() > 0.5:
                    result[i] = {
                        'sheet': k,
                        'x': x[i, k].varValue,
                        'y': y[i, k].varValue,
                        'rotated': s[i].varValue
                    }
        return result, least_space(rectangles) / Sheets_area.varValue, prob.solutionTime