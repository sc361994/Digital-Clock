import tkinter as tk
import math
from datetime import datetime, timedelta

# --- Configuration for Segmented Calendar Dial ---
CLOCK_SIZE = 500
CENTER = CLOCK_SIZE / 2

# KEY FOR CIRCULAR WINDOW: This color will be made fully transparent
TRANSPARENCY_KEY = '#AABBCC' 

# Actual clock background color (the color of the large circle that holds the rings)
BACKGROUND_COLOR = '#EFEFEF'  # Very light gray for clean look
INNER_FACE_COLOR = '#FFFFFF'  # Pure white inner dial background
TEXT_COLOR = '#333333'        # Dark gray text for general labels
HIGHLIGHT_BORDER_COLOR = '#FF6B6B' # Vibrant coral red for high contrast active segment
RING_BORDER_COLOR = '#000000' # Updated: Solid black border for the entire ring

# New, more appealing color palette
RING_COLORS = {
    # Innermost: Day of Week (7 segments) - Teals/Aquas (Calm yet vibrant)
    "day_of_week": {'base': '#4ECDC4', 'highlight': '#22A7B8', 'text': '#FFFFFF'},
    # Date ring: Day of Month (31 segments) - Purple/Lavender tones
    "date":        {'base': '#9B59B6', 'highlight': '#7D3C98', 'text': '#FFFFFF'},
    # Middle: Month (12 segments) - Golden Yellows/Oranges (Warmth and transition)
    "month":       {'base': '#FFC368', 'highlight': '#FF9F1C', 'text': '#333333'},
    # Outermost: Year (12 segments) - Deep Pinks/Magentas (Bold and modern)
    "year":        {'base': '#FF6B6B', 'highlight': '#F24242', 'text': '#FFFFFF'},
}

# Ring configuration: (radius, width, segments, labels)
RING_CONFIG = {
    "day_of_week": {'radius': 110, 'width': 30, 'segments': 7, 'labels': ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]},
    "date":        {'radius': 145, 'width': 25, 'segments': 31, 'labels': [str(i) for i in range(1, 32)]},
    "month":       {'radius': 175, 'width': 30, 'segments': 12, 'labels': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]},
    "year":        {'radius': 210, 'width': 30, 'segments': 12, 'labels': []}, # Labels generated dynamically
}

# Hand properties: (length_ratio, width, color)
HAND_PROPERTIES = {
    'hour':   (0.40, 6, '#444444'),
    'minute': (0.65, 4, '#1A1A1A'),
    'second': (0.75, 2, '#FF6B6B') # Use the highlight color for the second hand for visibility
}

def get_calendar_offsets():
    """
    Calculates the current rotational offset for each calendar ring.
    Ensures the center of the current segment is at 12 o'clock (0 degrees on canvas, 90 degrees in math).
    """
    now = datetime.now()
    
    def calculate_offset(segments, current_index):
        segment_angle_size = 360 / segments # Size of each segment in degrees
        
        # Calculate the angle of the *center* of the current segment,
        # starting from 0 degrees at 12 o'clock and going clockwise.
        current_segment_center_angle = (current_index * segment_angle_size) + (segment_angle_size / 2)
        
        # The rotation offset needed to bring this center angle to 0 degrees (12 o'clock)
        rotation_offset = -current_segment_center_angle 
        
        return rotation_offset, segment_angle_size
    
    # --- 1. Day of Week Offset (7 segments) ---
    # Python weekday: Mon=0 to Sun=6. Our labels: Sun=0 to Sat=6. 
    day_index = now.weekday() 
    day_of_week_index = (day_index + 1) % 7 
    day_rotation_offset, day_segment_angle = calculate_offset(RING_CONFIG["day_of_week"]['segments'], day_of_week_index)

    # --- 2. Date Offset (31 segments) ---
    date_index = now.day - 1 # 1st=0, 31st=30
    date_rotation_offset, date_segment_angle = calculate_offset(RING_CONFIG["date"]['segments'], date_index)

    # --- 3. Month Offset (12 segments) ---
    month_index = now.month - 1 # January=0, December=11
    month_rotation_offset, month_segment_angle = calculate_offset(RING_CONFIG["month"]['segments'], month_index)

    # --- 4. Year Offset (12 segments) ---
    current_year = now.year
    # To display 12 years around the clock, with the current year at the top,
    # we determine the start year for the 12-segment ring.
    # The current year should be at the 0 degree (top) position.
    # If segments = 12, then (current_year - 6) will start at the bottom-left.
    start_year_for_display = current_year - 6 
    RING_CONFIG["year"]['labels'] = [str(start_year_for_display + i) for i in range(RING_CONFIG["year"]['segments'])]
    # The "current year" as per label generation is at index 6 in this array
    year_index = 6 
    year_rotation_offset, year_segment_angle = calculate_offset(RING_CONFIG["year"]['segments'], year_index)

    return {
        "day_of_week": {'offset': day_rotation_offset, 'index': day_of_week_index, 'angle': day_segment_angle},
        "date":        {'offset': date_rotation_offset, 'index': date_index, 'angle': date_segment_angle},
        "month":       {'offset': month_rotation_offset, 'index': month_index, 'angle': month_segment_angle},
        "year":        {'offset': year_rotation_offset, 'index': year_index, 'angle': year_segment_angle},
    }


def draw_segmented_ring(canvas, key, offset_data):
    """Draws a complete, distinct segmented calendar ring."""
    
    config = RING_CONFIG[key]
    colors = RING_COLORS[key]
    offset_angle = offset_data['offset']
    current_index = offset_data['index']
    segment_angle_size = offset_data['angle'] 
    segments = config['segments']
    
    center_radius = config['radius']
    r_inner = center_radius - config['width']/2
    r_outer = center_radius + config['width']/2

    # Bounding box for the entire ring (outer edge)
    bbox_outer = (CENTER - r_outer, CENTER - r_outer, CENTER + r_outer, CENTER + r_outer)
    
    for i in range(segments):
        # --- Calculate segment angles for drawing ---
        angle_from_12h_cw = (i * segment_angle_size) + offset_angle

        # Convert to Tkinter's angle system: 0=3h, counter-clockwise positive
        tk_start_angle = 90 - (angle_from_12h_cw + segment_angle_size) # Start of segment is end of Tkinter arc
        tk_extent_angle = segment_angle_size # Extent is same

        is_active = (i == current_index)
        
        # --- 1. Draw the Segment Fill ---
        fill_color = colors['highlight'] if is_active else colors['base']
        
        canvas.create_arc(
            bbox_outer,
            start=tk_start_angle, extent=tk_extent_angle, style=tk.PIESLICE,
            fill=fill_color, outline='', 
            tags=f"segments_fill_{key}_{i}"
        )

        # --- 2. Draw Text Label (Horizontal and Centered) ---
        label = config['labels'][i % len(config['labels'])]
        
        # Angle for the center of the label (in our 0=12h CW system)
        label_center_angle_12h_cw = (i * segment_angle_size) + (segment_angle_size / 2) + offset_angle
        
        # Convert to standard math angle (0=3h, counter-clockwise positive) for positioning
        math_angle_rad = math.radians(90 - label_center_angle_12h_cw) # 90 degrees shifts 12h to 3h, then invert sign
        
        x_text = CENTER + center_radius * math.cos(math_angle_rad)
        y_text = CENTER - center_radius * math.sin(math_angle_rad) # Tkinter Y-axis inverted
        
        # Adjust font size for date ring (smaller text due to more segments)
        font_size = 8 if key == "date" else 10
        
        canvas.create_text(
            x_text, y_text,
            text=label, 
            font=('Inter', font_size, 'bold'), 
            fill=colors['text'], 
            tags=f"labels_{key}_{i}"
        )
    
    # --- 3. Draw the INNER outline to mask the 'PIESLICE' center and create the ring ---
    canvas.create_oval(
        CENTER - r_inner, CENTER - r_inner,
        CENTER + r_inner, CENTER + r_inner,
        fill=BACKGROUND_COLOR, outline='', width=0, tags=f"mask_{key}"
    )
    
    # --- 4. Draw Solid Borders for the Entire Ring ---
    # Inner border
    canvas.create_oval(
        CENTER - r_inner, CENTER - r_inner,
        CENTER + r_inner, CENTER + r_inner,
        outline=RING_BORDER_COLOR, width=1.5, fill='', tags=f"border_inner_{key}"
    )
    # Outer border
    canvas.create_oval(
        CENTER - r_outer, CENTER - r_outer,
        CENTER + r_outer, CENTER + r_outer,
        outline=RING_BORDER_COLOR, width=1.5, fill='', tags=f"border_outer_{key}"
    )

    # --- 5. Draw Highlight Border for Active Segment ---
    # Calculate the Tkinter angles for the active segment's border
    active_segment_angle_from_12h_cw = (current_index * segment_angle_size) + offset_angle
    active_tk_start_angle = 90 - (active_segment_angle_from_12h_cw + segment_angle_size) 
    
    # Outer highlight border (Arc)
    canvas.create_arc(
        bbox_outer,
        start=active_tk_start_angle, extent=segment_angle_size, style=tk.ARC,
        outline=HIGHLIGHT_BORDER_COLOR, width=3, tags=f"highlight_border_{key}"
    )
    
    # Inner highlight border (Arc)
    bbox_inner = (CENTER - r_inner, CENTER - r_inner, CENTER + r_inner, CENTER + r_inner)
    canvas.create_arc(
        bbox_inner,
        start=active_tk_start_angle, extent=segment_angle_size, style=tk.ARC,
        outline=HIGHLIGHT_BORDER_COLOR, width=3, tags=f"highlight_border_inner_{key}"
    )
    
    # Ensure the active label is on top of the highlight
    canvas.tag_raise(f"labels_{key}_{current_index}")


def draw_analog_face(canvas):
    """Draws the fixed center analog dial (where hands sweep)."""
    
    # Draw the main circular background for the clock area
    outer_radius = RING_CONFIG["year"]['radius'] + (RING_CONFIG["year"]['width'] / 2)
    canvas.create_oval(
        CENTER - outer_radius, CENTER - outer_radius,
        CENTER + outer_radius, CENTER + outer_radius,
        fill=BACKGROUND_COLOR, outline='#CCCCCC', width=1, tags="outer_background"
    )

    # Now draw the inner face for the clock hands
    inner_radius = RING_CONFIG["day_of_week"]['radius'] - (RING_CONFIG["day_of_week"]['width'] / 2) - 10
    
    # Inner Dial Background 
    canvas.create_oval(
        CENTER - inner_radius, CENTER - inner_radius,
        CENTER + inner_radius, CENTER + inner_radius,
        fill=INNER_FACE_COLOR, outline='#CCCCCC', width=1, tags="inner_face_bg"
    )

    marker_radius = inner_radius * 0.9
    
    # Draw simple hour markers (dots)
    for i in range(1, 13):
        angle = math.radians(i * 30 - 90) # -90 to start at 12 o'clock
        
        x = CENTER + (marker_radius) * math.cos(angle)
        y = CENTER + (marker_radius) * math.sin(angle)
        
        canvas.create_oval(x-3, y-3, x+3, y+3, fill=TEXT_COLOR, tags="hour_markers")


def draw_hand(canvas, time_value, time_unit, tag):
    """Calculates angle and draws a single clock hand."""
    
    if time_unit == 'second' or time_unit == 'minute':
        angle_deg = time_value * 6 - 90
    elif time_unit == 'hour':
        angle_deg = (time_value % 12) * 30 - 90
    else:
        return
    
    angle_rad = math.radians(angle_deg)
        
    length_ratio, width, color = HAND_PROPERTIES[time_unit]
    
    r_max = RING_CONFIG["day_of_week"]['radius'] - RING_CONFIG["day_of_week"]['width']
    hand_radius = r_max * length_ratio
    
    x_end = CENTER + hand_radius * math.cos(angle_rad)
    y_end = CENTER + hand_radius * math.sin(angle_rad)
    
    canvas.create_line(
        CENTER, CENTER, 
        x_end, y_end, 
        fill=color, width=width, tags=tag, capstyle=tk.ROUND
    )

def update_clock(canvas, time_24h_label):
    """Updates the calendar rings, analog hands, and digital display every second."""
    
    now = datetime.now()
    offsets = get_calendar_offsets()

    # --- 1. Update the Calendar Rings ---
    
    for key in RING_CONFIG.keys():
        # Delete segments, labels, masks, borders, and highlights
        for i in range(RING_CONFIG[key]['segments']):
             canvas.delete(f"segments_fill_{key}_{i}") 
             canvas.delete(f"labels_{key}_{i}")
        canvas.delete(f"mask_{key}", f"border_inner_{key}", f"border_outer_{key}", f"highlight_border_{key}", f"highlight_border_inner_{key}")

    # Redraw all segmented rings from outside in (Year, Month, Date, Day of Week)
    draw_segmented_ring(canvas, "year", offsets["year"])
    draw_segmented_ring(canvas, "month", offsets["month"])
    draw_segmented_ring(canvas, "date", offsets["date"])
    draw_segmented_ring(canvas, "day_of_week", offsets["day_of_week"])

    # Ensure analog face elements are drawn *above* the innermost ring's mask
    canvas.tag_raise("inner_face_bg")
    canvas.tag_raise("hour_markers")


    # --- 2. Update Analog Clock Hands ---
    
    hour = now.hour + now.minute / 60
    minute = now.minute + now.second / 60
    second = now.second

    canvas.delete("hand_hour", "hand_minute", "hand_second", "center_dot")
    
    draw_hand(canvas, hour, 'hour', "hand_hour")
    draw_hand(canvas, minute, 'minute', "minute")
    draw_hand(canvas, second, 'second', "second")
    
    canvas.create_oval(CENTER - 5, CENTER - 5, CENTER + 5, CENTER + 5, fill='#2c3e50', tags="center_dot")
    
    # --- 3. Update Digital Time ---
    time_str_24h = now.strftime('%H:%M:%S')
    time_24h_label.config(text=time_str_24h)
    
    canvas.after(1000, lambda: update_clock(canvas, time_24h_label))


def setup_ui():
    """Initializes the Tkinter window and widgets."""
    root = tk.Tk()
    root.title("Segmented Calendar Dial Clock")
    
    # --- Window Configuration for Circular Appearance ---
    # Makes the window frameless
    root.overrideredirect(True) 
    root.attributes('-alpha', 0.98) 
    root.wm_attributes("-topmost", False)
    
    # Set the background and the transparent color to the KEY
    root.config(bg=TRANSPARENCY_KEY)
    # This line tells Windows/X11 to make all pixels of the key color transparent
    root.attributes('-transparentcolor', TRANSPARENCY_KEY)

    # Allow moving the frameless window
    def start_move(event):
        root.x = event.x
        root.y = event.y
    def stop_move(event):
        root.x = None
        root.y = None
    def do_move(event):
        if root.x is not None and root.y is not None:
            deltax = event.x - root.x
            deltay = event.y - root.y
            x = root.winfo_x() + deltax
            y = root.winfo_y() + deltay
            root.geometry(f"+{x}+{y}")

    # The entire clock face is draggable
    root.bind('<ButtonPress-1>', start_move)
    root.bind('<ButtonRelease-1>', stop_move)
    root.bind('<B1-Motion>', do_move)

    # --- Canvas for the Rings and Analog Face ---
    # The frame and canvas must also use the KEY color for the transparency effect to work
    canvas_frame = tk.Frame(root, bg=TRANSPARENCY_KEY)
    canvas_frame.pack(padx=0, pady=0)
    
    canvas = tk.Canvas(
        canvas_frame, 
        width=CLOCK_SIZE, 
        height=CLOCK_SIZE, 
        bg=TRANSPARENCY_KEY, # Use the KEY here
        highlightthickness=0
    )
    canvas.pack()
    
    # --- Initial Clock Face Drawing (Static elements) ---
    draw_analog_face(canvas) 

    # --- Digital Time Label (Moved to bottom) ---
    time_24h_label = tk.Label(
        canvas, 
        font=('Inter', 16, 'bold'),
        bg=INNER_FACE_COLOR, 
        fg=TEXT_COLOR,
        text='00:00:00'
    )
    # Positioning at the bottom of the inner face. 
    time_24h_label.place(relx=0.5, rely=0.6, anchor='center') 
    
    # Start the clock update loop
    update_clock(canvas, time_24h_label)
    
    root.mainloop()

if __name__ == '__main__':
    setup_ui()