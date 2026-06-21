import calendar
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_ui_calendar(year, month, reservations):
    # Set up calendar data
    cal = calendar.Calendar(firstweekday=6) # 6 = Sunday as first day of week
    month_days = list(cal.itermonthdays2(year, month))
    num_weeks = len(month_days) // 7
    
    # Create plot layout
    fig, ax = plt.subplots(figsize=(11, 8.5), facecolor='white')
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(-0.5, num_weeks - 0.5)
    ax.invert_yaxis() # Top-down calendar view
    ax.axis('off')
    
    # Title / Header
    month_name = calendar.month_name[month][:3]
    plt.text(0, -0.6, f"{month_name}  {year}", fontsize=24, weight='bold', color='#1e293b', ha='left')
    filename = f"vrbo_calendar_{month_name}_{year}.png"
    
    # Draw Day Headers
    days_headers = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for idx, day_name in enumerate(days_headers):
        ax.text(idx, -0.2, day_name, fontsize=12, weight='bold', color='#1e293b', ha='center')
        
    day_coords = {}
    
    # Draw Grid and Day Numbers
    for i, (day, weekday) in enumerate(month_days):
        row = i // 7
        col = i % 7
        
        rect = patches.Rectangle((col - 0.5, row - 0.5), 1, 1, linewidth=1, edgecolor='#cbd5e1', facecolor='none')
        ax.add_patch(rect)
        
        if day != 0:
            day_coords[day] = (row , col -.5)
            is_crossed = any(
                datetime.date(year, month, day) >= datetime.date(year, start_m, start_d) and 
                datetime.date(year, month, day) <= datetime.date(year, end_m, end_d)
                for start_d, start_m, end_d, end_m, _ in reservations
            )
            
#           if is_crossed:
#               ax.plot([col - 0.15, col + 0.15], [row - 0.35, row - 0.35], color='#0f172a', linewidth=1)
                
            ax.text(col - 0.4, row - 0.35, str(day), fontsize=12, color='#0f172a', ha='left', va='center')

    # Plot Reservation Bars
    for start_d, start_m, end_d, end_m, label in reservations:
        start_date = datetime.date(year, start_m, start_d)
        end_date = datetime.date(year, end_m, end_d)
        current_month_start = datetime.date(year, month, 1)
        
        last_day = calendar.monthrange(year, month)[1]
        current_month_end = datetime.date(year, month, last_day)
        
        effective_start = max(start_date, current_month_start)
        effective_end = min(end_date, current_month_end)
        
        if effective_start > effective_end:
            continue

        curr = effective_start
        while curr <= effective_end:
            row, col = day_coords[curr.day]
            
            seg_start_col = col
            seg_end_col = col
            seg_start_day = curr
            
            while curr + datetime.timedelta(days=1) <= effective_end:
                next_day = curr + datetime.timedelta(days=1)
                next_row, next_col = day_coords[next_day.day]
                if next_row != row:
                    break
                seg_end_col = next_col
                curr = next_day
            
            seg_end_day = curr
            
            # Base horizontal bounds for this row segment
            # Add micro-padding (0.08) to separate back-to-back bookings sharing a day boundary
            x_start = seg_start_col + .05 # + 0.08
            x_end = seg_end_col  # - 0.08
            y_pos = row - 0.05
            height = 0.20
            y_bottom = y_pos - ( height / 4)

            # Determine corner styling logic based on wrap contexts
            is_actual_start = (seg_start_day == start_date)
            is_actual_end = (seg_end_day == end_date)
            
            if is_actual_start and is_actual_end:
                # Entire stay fits on one row -> fully rounded capsule
                bar = patches.FancyBboxPatch(
                    (x_start + 0.5, y_bottom), (x_end - x_start) - 0.04, height,
                    boxstyle="round,pad=0.0,rounding_size=0.1",
                    facecolor='#1e2238', edgecolor='none', zorder=3
                )
            elif is_actual_start and not is_actual_end:
                # Starts here but wraps to next line -> Round Left, Sharp Right
                bar = patches.FancyBboxPatch(
                    (x_start + .5, y_bottom), (x_end +.8 - x_start), height,
                    boxstyle="round,pad=0.0,rounding_size=0.1",
                    facecolor='#1e2238', edgecolor='none', zorder=3
                )
                # Overwrite the right side with a sharp rectangle to hide the curve
                sharp_patch = patches.Rectangle((x_end +.8 , y_bottom), x_end  - x_start, height, facecolor='#1e2238', zorder=3)
                ax.add_patch(sharp_patch)
            elif not is_actual_start and is_actual_end:
                # Continued from previous line and ends here -> Sharp Left, Round Right
                bar = patches.FancyBboxPatch(
                    (x_start - .5 , y_bottom), (x_end +.8  - x_start ) , height,
                    boxstyle="round,pad=0.0,rounding_size=0.1",
                    facecolor='#1e2238', edgecolor='none', zorder=3
                )
                # Overwrite the left side with a sharp rectangle
                sharp_patch = patches.Rectangle((x_start-.5, y_bottom), 0.1, height, facecolor='#1e2238', zorder=3)
                ax.add_patch(sharp_patch)
            else:
                # Middle fragment passing entirely through the week -> Completely sharp rectangle
                bar = patches.Rectangle((x_start, y_bottom), x_end - x_start, height, facecolor='#1e2238', zorder=3)

            ax.add_patch(bar)
            
            # Print label text properties safely on the segment
            clean_label = label.replace("Reserved ", "")
            if seg_start_day == effective_start or seg_start_col == 0:
                ax.text(x_start + 0.8, y_pos + .02 , clean_label, color='white', 
                        fontsize=11, weight='medium', va='center', zorder=4)
                
            curr += datetime.timedelta(days=1)

    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
#   plt.show()
    return filename

# Test dataset matching your timeline parameters
input_data = [
    (25, 5, 1, 6, 'Reserved Mary'), 
    (2, 6, 4, 6, 'Reserved Melany'), 
    (5, 6, 7, 6, 'Reserved Bobby'), 
    (8, 6, 11, 6, 'Blocked'), 
    (12, 6, 15, 6, 'Reserved Veronica'), 
    (15, 6, 19, 6, 'Reserved Luisa'), 
    (19, 6, 21, 6, 'Reserved LaToyia'), 
    (21, 6, 24, 6, 'Reserved Dan'), 
    (26, 6, 28, 6, 'Reserved Laura')
]

#generate_ui_calendar(2026, 6, input_data)
