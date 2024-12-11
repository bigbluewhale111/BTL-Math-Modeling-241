import time

least_space = lambda rectangles: sum([rect[0] * rect[1] for rect in rectangles])

class Rectangle:
    def __init__(self, width, height, rid):
        self.width = width
        self.height = height
        self.original_width = width
        self.original_height = height
        self.rid = rid  # Rectangle ID
        self.x = None
        self.y = None
        self.rotated = False
        self.bin_index = None  # The index of the bin where the rectangle is placed

class MaxRects_BLSF:
    def __init__(self, width, height):
        self.bin_width = width
        self.bin_height = height
        self.free_rectangles = []
        self.used_rectangles = []
        # Initialize with the bin size as the first free rectangle
        self.free_rectangles.append({'x': 0, 'y': 0, 'width': width, 'height': height})

    def is_contained_in(self, rect_a, rect_b):
        return (rect_a['x'] >= rect_b['x'] and
                rect_a['y'] >= rect_b['y'] and
                rect_a['x'] + rect_a['width'] <= rect_b['x'] + rect_b['width'] and
                rect_a['y'] + rect_a['height'] <= rect_b['y'] + rect_b['height'])

    def split_free_rectangle(self, free_rect, used_rect):
        new_rects = []

        # Left
        if used_rect['x'] > free_rect['x']:
            new_rect = {
                'x': free_rect['x'],
                'y': free_rect['y'],
                'width': used_rect['x'] - free_rect['x'],
                'height': free_rect['height']
            }
            new_rects.append(new_rect)
        # Right
        if used_rect['x'] + used_rect['width'] < free_rect['x'] + free_rect['width']:
            new_rect = {
                'x': used_rect['x'] + used_rect['width'],
                'y': free_rect['y'],
                'width': (free_rect['x'] + free_rect['width']) - (used_rect['x'] + used_rect['width']),
                'height': free_rect['height']
            }
            new_rects.append(new_rect)
        # Bottom
        if used_rect['y'] > free_rect['y']:
            new_rect = {
                'x': free_rect['x'],
                'y': free_rect['y'],
                'width': free_rect['width'],
                'height': used_rect['y'] - free_rect['y']
            }
            new_rects.append(new_rect)
        # Top
        if used_rect['y'] + used_rect['height'] < free_rect['y'] + free_rect['height']:
            new_rect = {
                'x': free_rect['x'],
                'y': used_rect['y'] + used_rect['height'],
                'width': free_rect['width'],
                'height': (free_rect['y'] + free_rect['height']) - (used_rect['y'] + used_rect['height'])
            }
            new_rects.append(new_rect)

        return new_rects

    def place_rectangle(self, rect, best_node):
        rect.x = best_node['x']
        rect.y = best_node['y']
        rect.rotated = best_node.get('rotated', False)
        if rect.rotated:
            rect.width = rect.original_height
            rect.height = rect.original_width
        else:
            rect.width = rect.original_width
            rect.height = rect.original_height
        self.used_rectangles.append(rect)

        i = 0
        while i < len(self.free_rectangles):
            free_rect = self.free_rectangles[i]
            if self.intersect(free_rect, best_node):
                new_rects = self.split_free_rectangle(free_rect, best_node)
                self.free_rectangles.pop(i)
                self.free_rectangles.extend(new_rects)
                i -= 1
            i += 1

        self.prune_free_list()

    def intersect(self, rect_a, rect_b):
        return not (rect_a['x'] >= rect_b['x'] + rect_b['width'] or
                    rect_a['x'] + rect_a['width'] <= rect_b['x'] or
                    rect_a['y'] >= rect_b['y'] + rect_b['height'] or
                    rect_a['y'] + rect_a['height'] <= rect_b['y'])

    def prune_free_list(self):
        i = 0
        while i < len(self.free_rectangles):
            j = i + 1
            while j < len(self.free_rectangles):
                rect_i = self.free_rectangles[i]
                rect_j = self.free_rectangles[j]
                if self.is_contained_in(rect_i, rect_j):
                    self.free_rectangles.pop(i)
                    i -= 1
                    break
                if self.is_contained_in(rect_j, rect_i):
                    self.free_rectangles.pop(j)
                    j -= 1
                j += 1
            i += 1

    def score_blsf(self, width, height, free_rect):
        leftover_h = abs(free_rect['width'] - width)
        leftover_v = abs(free_rect['height'] - height)
        long_side_fit = max(leftover_h, leftover_v)
        short_side_fit = min(leftover_h, leftover_v)
        return (long_side_fit, short_side_fit)

    def find_pos_blsf(self, rect):
        best_score = (float('inf'), float('inf'))
        best_node = None
        for free_rect in self.free_rectangles:
            # No rotation fit
            if rect.original_width <= free_rect['width'] and rect.original_height <= free_rect['height']:
                score = self.score_blsf(rect.original_width, rect.original_height, free_rect)
                if score < best_score:
                    best_node = {
                        'x': free_rect['x'],
                        'y': free_rect['y'],
                        'width': rect.original_width,
                        'height': rect.original_height,
                        'rotated': False
                    }
                    best_score = score
            # Rotated fit
            if rect.original_height <= free_rect['width'] and rect.original_width <= free_rect['height']:
                score = self.score_blsf(rect.original_height, rect.original_width, free_rect)
                if score < best_score:
                    best_node = {
                        'x': free_rect['x'],
                        'y': free_rect['y'],
                        'width': rect.original_height,
                        'height': rect.original_width,
                        'rotated': True
                    }
                    best_score = score
        return best_node

    def insert(self, rect):
        best_node = self.find_pos_blsf(rect)
        if best_node:
            self.place_rectangle(rect, best_node)
            return True
        else:
            return False

def pack_rectangles(rectangles, bins, verbose=False):
    rev_a, rev_b = True, False
    
    bin_packs = []
    unplaced_rectangles = rectangles.copy()

    # Sort rectangles in descending order of area (larger rectangles first)
    rectangles_sorted = sorted(unplaced_rectangles, key=lambda r: r.width * r.height, reverse=rev_a)
    # rectangles_sorted = unplaced_rectangles.copy()

    # Keep bins' indices
    bins_with_indices = [(w, h, idx) for idx, (w, h) in enumerate(bins)]
    # Sort bins by area in ascending order
    # Try to use the smallest bins first, this way we can minimize trim loss
    bins_sorted = sorted(bins_with_indices, key=lambda b: b[0]*b[1],reverse=rev_b)
    # bins_sorted = bins_with_indices.copy()

    # Traverse all rectangles
    for rect in rectangles_sorted:
        placed = False

        # Sort used bins by area (ascending)
        existing_bin_packs = sorted(bin_packs, key=lambda bp: bins[bp[0]][0] * bins[bp[0]][1], reverse=rev_b)
        # existing_bin_packs = bin_packs.copy()
        for bin_index, bin_pack in existing_bin_packs:
            # Try to insert the rectangle into the existing bin pack
            if bin_pack.insert(rect):
                rect.bin_index = bin_index  # Use existing bin index
                placed = True
                break  # Rectangle placed, move to the next rectangle

        if not placed:
            # Try to place the rectangle into the smallest possible new bin (not yet used)
            for bin_width, bin_height, bin_original_index in bins_sorted:
                # Skip bins that already have bin packs (already tried)
                if any(bp[0] == bin_original_index for bp in bin_packs):
                    continue  # Bin already used

                # Check if the rectangle can fit into the bin (considering rotation)
                can_fit = (rect.original_width <= bin_width and rect.original_height <= bin_height) or \
                          (rect.original_height <= bin_width and rect.original_width <= bin_height)
                if not can_fit:
                    continue  # Try the next bin

                # Create a new bin pack for this bin
                bin_pack = MaxRects_BLSF(bin_width, bin_height)
                if bin_pack.insert(rect):
                    bin_packs.append((bin_original_index, bin_pack))
                    rect.bin_index = bin_original_index  # Use original bin index
                    placed = True
                    break  # Rectangle placed, move to the next rectangle
                else:
                    # Cannot place rectangle in this new bin, discard bin pack
                    pass  # Continue trying next bin

            if not placed:
                # Unable to place rectangle in any bin
                # Since the rectangle couldn't be placed, we add it to the unplaced list
                rect.bin_index = None  # Ensure bin_index is None
                unplaced_rectangles.append(rect)

    # Remove placed rectangles from the unplaced list
    unplaced_rectangles = [rect for rect in rectangles_sorted if rect.bin_index is None]

    # Check if there are unfulfilled products
    if unplaced_rectangles:
        if verbose:
            print("Not all products could be packed into the bins.")
            print("Unfulfilled products:")
            for rect in unplaced_rectangles:
                print(f"  Rectangle {rect.rid}: width={rect.width}, height={rect.height}")
        return None
    if verbose:
        print("All products have been successfully packed.")
    return bin_packs

def blsf_2d_csp(given_rectangles, sheets, verbose=True):
    rectangles = []
    rid = 0
    for idx, rect in enumerate(given_rectangles):
        rectangles.append(Rectangle(rect[0], rect[1], idx))
    # Pack rectangles
    start_time = time.perf_counter()
    bin_packs = pack_rectangles(rectangles, sheets, verbose)
    end_time = time.perf_counter()
    if bin_packs is None:
        return None, None, None
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
            for rect in bin_pack.used_rectangles:
                result[rect.rid] = {
                    'sheet': k,
                    'x': rect.x,
                    'y': rect.y,
                    'rotated': rect.rotated
                }
    fill_percentage = filled_area / total_area
    return result, fill_percentage, solution_time
    # return None, None, None