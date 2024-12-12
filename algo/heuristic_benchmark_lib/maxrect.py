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

class MaxRects:
    def __init__(self, width, height):
        self.bin_width = width
        self.bin_height = height
        self.free_rectangles = []
        self.placed_rectangles = []
        self.fill_percentage = 0.0
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
        self.placed_rectangles.append(rect)

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

    # SCORE METHODS [BL, BAF, BSSF, BLSF]
    def score_bl(self, x, y, free_rect):
        return (y, x)

    def score_baf(self, width, height, free_rect):
        free_area = free_rect['width'] * free_rect['height']
        rect_area = width * height
        area_fit = free_area - rect_area
        leftover_h = abs(free_rect['width'] - width)
        leftover_v = abs(free_rect['height'] - height)
        short_side_fit = min(leftover_h, leftover_v)
        return (area_fit, short_side_fit)

    def score_bssf(self, width, height, free_rect):
        leftover_h = abs(free_rect['width'] - width)
        leftover_v = abs(free_rect['height'] - height)
        short_side_fit = min(leftover_h, leftover_v)
        long_side_fit = max(leftover_h, leftover_v)
        return (short_side_fit, long_side_fit)

    def score_blsf(self, width, height, free_rect):
        leftover_h = abs(free_rect['width'] - width)
        leftover_v = abs(free_rect['height'] - height)
        long_side_fit = max(leftover_h, leftover_v)
        short_side_fit = min(leftover_h, leftover_v)
        return (long_side_fit, short_side_fit)

    def find_pos(self, rect, mode):
        score_method = None
        if mode == 'BAF':
            score_method = self.score_baf
        elif mode == 'BL':
            score_method = self.score_bl
        elif mode == 'BSSF':
            score_method = self.score_bssf
        elif mode == 'BLSF':
            score_method = self.score_blsf
        else:
            print("INVALID MODE")
            exit()
        best_node = None
        best_score = (float('inf'), float('inf'))  # Minimize (y, x)

        for free_rect in self.free_rectangles:
            # No rotation fit
            if rect.original_width <= free_rect['width'] and rect.original_height <= free_rect['height']:
                score = score_method(rect.original_width, rect.original_height, free_rect)
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
                score = score_method(rect.original_width, rect.original_height, free_rect)
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

    def insert(self, rect, mode):
        best_node = self.find_pos(rect, mode)
        if best_node:
            self.place_rectangle(rect, best_node)
            self.fill_percentage += (rect.width * rect.height) / (self.bin_width * self.bin_height)
            return True

        return False