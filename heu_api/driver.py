from heu_api.maxrect import Rectangle, MaxRects
import time

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])

mr_vars = ["BAF", "BL", "BSSF", "BLSF"]
sort_modes = [None, (False, False), (False, True), (True, False), (True, True)]

def pack_rectangles(rectangles, idx_sheets, mr_var, sort_mode, verbose=False):
    """
    pack_rectangles function
    Greedy
    
    Arguments:
    rectangles: list of Rectangle objects
    idx_sheets: enumerated sheets
    
    Output:
    bin_packs: list of bins (either MaxRects_BSSF, SkylineBinPack) with placed_rectangles attribute containing placed rectangles
    
    ### SUBMISSION CONFIG ###
    
    Sort mode:
    products:           descending order by area
    unused_sheets:      descending order by area
    used_sheets:        descending order by fill percentage
    
    ### SPEED UP ADDITION TO POLICY SUBMISSION ###
    # CAUTION: DO NOT MODIFY ANY SORT MODE
    
    bin_packs (used_sheets) list, when add new, append and sort
    sorted_bins list, since it is in descending order
        => any rectangle that doesn't fit, it won't fit in any other sheets
    """
    bin_packs = []
    
    sorted_rectangles = []
    sorted_bins = []

    if sort_mode:
        # FFD-like algorithm, place large products first
        sorted_rectangles = sorted(rectangles, key=lambda r: r.width * r.height, reverse=sort_mode[0])
        # If product category is large (diverse) enough, using larger bins first may benefit
        sorted_bins = sorted(idx_sheets, key=lambda b: b[0]*b[1],reverse=sort_mode[1])
    else:
        sorted_rectangles = rectangles.copy()
        sorted_bins = idx_sheets.copy()

    # Traverse all rectangles
    for rect in sorted_rectangles:
        placed = False

        # Check for used bin packs, if can fit then use
        for bin_index, bin_pack in bin_packs:
            if bin_pack.insert(rect, mr_var):
                rect.bin_index = bin_index 
                placed = True
                break

        # Else, use new bin
        if not placed:
            for w, h, idx in sorted_bins:
                if any(bp[0] == idx for bp in bin_packs):
                    continue
                
                can_fit = (rect.original_width <= w and rect.original_height <= h) or \
                          (rect.original_height <= w and rect.original_width <= h)
                if not can_fit:
                    continue
                
                bin_pack = MaxRects(w, h)
                # insert success
                if bin_pack.insert(rect, mr_var):
                    # Insert newly used bin and sort for next placement
                    sorted_bins.remove((w, h, idx))
                    bin_packs.append((idx, bin_pack))
                    # BFD sort
                    # bin_packs = sorted(bin_packs, key=lambda r: r[1].fill_percentage, reverse=True)
                    if sort_mode:
                        bin_packs = sorted(bin_packs, key=lambda r: r[1].bin_width * r[1].bin_height, reverse=True)
                    
                    rect.bin_index = idx
                    placed = True
                    break
                else:
                    pass

            # this assumes all bins have been iterated through, if fail then 100% no solution
            if not placed:
                return None

    if verbose:
        print("All products have been successfully packed.")
    return bin_packs

def maxrect_driver(given_rectangles, sheets, mr_var, sort_mode, verbose=True):
    rectangles = []
    for idx, rect in enumerate(given_rectangles):
        rectangles.append(Rectangle(rect[0], rect[1], idx))
    idx_sheets = [(w, h, idx) for idx, (w, h) in enumerate(sheets)]
    # Pack rectangles
    start_time = time.perf_counter()
    bin_packs = pack_rectangles(rectangles, idx_sheets, mr_var, sort_mode, verbose)
    end_time = time.perf_counter()
    if bin_packs is None:
        return None, None, None, None
    solution_time = end_time - start_time
    # Calculate fill percentage
    filled_area = least_space(given_rectangles)
    bin_packs_dict = {bin_index: bin_pack for bin_index, bin_pack in bin_packs}
    result = {}
    total_area = 0
    for k in range(len(sheets)):
        if k in bin_packs_dict:
            bin_pack = bin_packs_dict[k]
            total_area += bin_pack.bin_width * bin_pack.bin_height
            for rect in bin_pack.placed_rectangles:
                result[rect.rid] = {
                    'sheet': k,
                    'x': rect.x,
                    'y': rect.y,
                    'rotated': rect.rotated
                }
    fill_percentage = filled_area / total_area
    fill_ratio = len(bin_packs) / len(sheets)
    return result, fill_percentage, fill_ratio, solution_time