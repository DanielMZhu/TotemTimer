import time
import board
import displayio
import framebufferio
import rgbmatrix
import gc # Added for memory management
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_ds3231

# --- Hardware Setup ---
i2c = board.I2C()
rtc = adafruit_ds3231.DS3231(i2c)

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1, board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
display.rotation = 180

font = bitmap_font.load_font("lib/fonts/creep.bdf")

# --- Schedules (Keeping your data structures) ---
FRIDAY = {
    "K": [((19, 0), "LB Luke", (20, 0)), ((20, 0), "Korolova", (21, 0)), ((21, 0), "Argy", (22, 0)), ((22, 7), "C Lorenzo", (23, 15)), ((23, 19), "Sofi Tkr", (24, 28)), ((24, 32), "Chainsmkrs", (25, 40)), ((25, 47), "Fisher", (26, 57)), ((27, 1), "Porter R", (28, 10)), ((28, 14), "C de Witte", (29, 28))],
    "C": [((19, 0), "1991", (20, 0)), ((20, 0), "Bou", (21, 0)), ((21, 0), "Nico Mrno", (22, 0)), ((22, 0), "I H8 Models", (23, 15)), ((23, 15), "Levity", (24, 25)), ((24, 25), "Wooli", (25, 35)), ((25, 35), "The Outlaw", (26, 35)), ((26, 35), "Holy Priest", (27, 30)), ((27, 30), "Ray Volpe", (28, 30)), ((28, 30), "Lvl Up", (29, 30))],
    "M": [((17, 0), "M Dean B2B", (18, 50)), ((19, 0), "J Hollande", (19, 55)), ((19, 55), "Roddy Lima", (20, 55)), ((20, 55), "Westend", (21, 55)), ((21, 55), "Walker/Ryc", (22, 55)), ((23, 10), "Underwrld", (24, 10)), ((24, 25), "Meduza", (25, 45)), ((25, 47), "Notion", (26, 47)), ((26, 47), "MPH", (28, 2)), ((28, 2), "San Pacho", (29, 30))],
    "B": [((19, 0), "Riot", (19, 50)), ((19, 50), "Heyz", (20, 40)), ((20, 40), "Muzz", (21, 30)), ((21, 30), "Gorillat", (22, 30)), ((22, 30), "Ghengar", (23, 30)), ((23, 30), "Deathpact", (24, 30)), ((24, 30), "ATLiens", (25, 30)), ((25, 30), "Kai Wachi", (26, 30)), ((26, 30), "Adv Club", (27, 30)), ((27, 30), "C Shock", (28, 30)), ((28, 30), "Cyclops", (29, 30))],
    "N": [((19, 0), "Anastazja", (20, 30)), ((20, 30), "Mestiza", (22, 0)), ((22, 0), "DJ Tennis", (23, 30)), ((23, 30), "Peggy Gou", (25, 0)), ((25, 0), "Adriatiq", (26, 30)), ((26, 30), "J Capriati", (28, 0)), ((28, 0), "Eli Brown", (29, 30))],
    "Q": [((19, 0), "S de Warr", (20, 0)), ((20, 0), "Matty Ral", (21, 0)), ((21, 0), "Cold Blue", (22, 0)), ((22, 0), "Pegassi", (23, 0)), ((23, 0), "Darude", (24, 0)), ((24, 0), "Cosmic Gat", (25, 0)), ((25, 0), "G Emery", (26, 0)), ((26, 0), "I Blueston", (27, 0)), ((27, 0), "P van Dyk", (28, 0)), ((28, 0), "D Porter", (29, 50))],
    "S": [((19, 0), "Abana B2B", (20, 0)), ((20, 0), "Slamm", (21, 0)), ((21, 0), "L van Dijk", (22, 15)), ((22, 15), "Omar+", (23, 30)), ((23, 30), "Luke Dean", (24, 45)), ((24, 45), "Josh Baker", (26, 0)), ((26, 0), "Max Dean", (27, 15)), ((27, 15), "Obskur", (28, 30)), ((28, 30), "Toman", (29, 30))],
    "W": [((19, 0), "Domina", (20, 30)), ((20, 30), "Serafina", (21, 30)), ((21, 30), "J Schuster", (22, 30)), ((22, 30), "A Mills", (23, 30)), ((23, 30), "Cloudy", (24, 30)), ((24, 30), "Kuko", (25, 30)), ((25, 30), "Gravedgr", (26, 30)), ((26, 30), "Rebekah", (27, 30)), ((27, 30), "Dyen", (28, 30)), ((28, 30), "Stan Christ", (29, 30))],
    "J": [((17, 0), "H Lawden", (19, 0)), ((19, 0), "S Christin", (20, 0)), ((20, 0), "Carry Nat", (21, 30)), ((21, 30), "M Pagliara", (23, 0)), ((23, 0), "Paramida", (24, 30)), ((24, 30), "Salute B2B", (26, 30)), ((26, 30), "Robert Hood", (28, 0)), ((28, 0), "A Emerson", (29, 30))]
}

SATURDAY = {
    "K": [((19, 0), "AR/CO", (20, 0)), ((20, 0), "Hayla", (21, 0)), ((21, 0), "Sub Focus", (22, 0)), ((22, 7), "Steve Aoki", (23, 15)), ((23, 19), "Hardwell", (24, 28)), ((24, 32), "John Summit", (25, 40)), ((25, 47), "Subtronics", (26, 57)), ((27, 1), "Kaskade", (28, 11)), ((28, 14), "Above & Beyond", (29, 28))],
    "C": [((19, 0), "DJ Mandy", (20, 0)), ((20, 0), "Roz", (21, 15)), ((21, 15), "Kettama", (22, 45)), ((22, 45), "Sammy Virji", (24, 15)), ((24, 15), "Tiesto", (25, 45)), ((25, 45), "Peggy Gou B2B", (27, 15)), ((27, 15), "Boys Noize", (28, 30)), ((28, 30), "Lilly Palmer", (29, 30))],
    "M": [((19, 0), "Frost Children", (20, 15)), ((20, 15), "Hannah Laing", (21, 25)), ((21, 25), "Snow Strippers", (22, 15)), ((22, 15), "VTSS", (23, 30)), ((23, 35), "The Prodigy", (24, 35)), ((24, 40), "BUNT.", (26, 10)), ((26, 10), "Interplanetary", (27, 30)), ((27, 30), "Malugi", (28, 30)), ((28, 30), "DJ Gigola B2B", (29, 30))],
    "B": [((19, 0), "Fallen", (19, 50)), ((19, 50), "Avello B2B", (20, 40)), ((20, 40), "Viperactive", (21, 30)), ((21, 30), "Hybrid Minds", (22, 30)), ((22, 30), "YDG", (23, 30)), ((23, 30), "Delta Heavy", (24, 30)), ((24, 30), "Getter", (25, 30)), ((25, 30), "Eptic B2B", (26, 30)), ((26, 30), "Doctor P B2B", (27, 30)), ((27, 30), "HOL!", (28, 30)), ((28, 30), "Mary Droppinz", (29, 30))],
    "N": [((19, 0), "Mink", (20, 30)), ((20, 30), "Silvie Loto", (22, 0)), ((22, 0), "Ahmed Spins", (23, 30)), ((23, 30), "Luciano", (25, 30)), ((25, 30), "Prospa", (27, 30)), ((27, 30), "Josh Baker B2B", (29, 30))],
    "Q": [((19, 0), "Maria Healy", (20, 30)), ((20, 30), "Superstrings", (21, 30)), ((21, 30), "Billy Gillies", (22, 30)), ((22, 30), "Paul Oakenfold", (23, 30)), ((23, 30), "Andrew Rayel", (24, 30)), ((24, 30), "Maddix", (25, 30)), ((25, 30), "Mathame", (26, 30)), ((26, 30), "Astrix", (27, 30)), ((27, 30), "T78", (28, 30)), ((28, 30), "T Schumacher", (29, 30))],
    "S": [((19, 0), "Slugg", (20, 0)), ((20, 0), "Dreya V", (21, 0)), ((21, 0), "Discip", (22, 0)), ((22, 0), "Omnom", (23, 15)), ((23, 15), "Noizu", (24, 30)), ((24, 30), "Wax Motif", (25, 45)), ((25, 45), "CID", (27, 0)), ((27, 0), "HNTR", (28, 15)), ((28, 15), "Bolo", (29, 30))],
    "W": [((19, 0), "Cutdwn", (20, 30)), ((20, 30), "Dead X", (21, 30)), ((21, 30), "The Saints", (22, 30)), ((22, 30), "Rob Gee B2B", (23, 30)), ((23, 30), "Lady Faith B2B", (24, 30)), ((24, 30), "Code Black B2B", (25, 30)), ((25, 30), "Da Tweekaz", (26, 30)), ((26, 30), "Lil Texas", (27, 30)), ((27, 30), "Mish", (28, 30)), ((28, 30), "Alyssa Jolee", (29, 30))],
    "J": [((19, 0), "Player Dave", (20, 0)), ((20, 0), "Spray", (21, 0)), ((21, 0), "Bashkka B2B", (22, 30)), ((22, 30), "HAAi B2B", (24, 0)), ((24, 0), "MCR-T", (25, 15)), ((25, 15), "Bad Boombox", (26, 30)), ((26, 30), "Benwal", (27, 30)), ((27, 30), "Baugruppe90", (28, 30)), ((28, 30), "Club Angel", (29, 30))]
}

SUNDAY = {
    "K": [((19, 0), "Trace", (20, 0)), ((20, 0), "Ship Wrek", (21, 0)), ((21, 0), "Layton Giordani", (22, 0)), ((22, 7), "Funk Tribu", (23, 15)), ((23, 19), "GRiZ B2B Wooli", (24, 28)), ((24, 32), "Zedd", (25, 40)), ((25, 47), "Martin Garrix", (26, 57)), ((27, 1), "Cloonee", (28, 11)), ((28, 14), "Armin van Buuren", (29, 28))],
    "C": [((19, 0), "Linska", (20, 30)), ((20, 30), "ANNA", (22, 0)), ((22, 0), "Beltran", (23, 30)), ((23, 30), "Chris Stussy", (25, 0)), ((25, 0), "Solomun", (26, 30)), ((26, 30), "Vintage Culture", (28, 0)), ((28, 0), "Kevin de Vries", (29, 30))],
    "M": [((19, 0), "Gravagerz", (20, 0)), ((20, 0), "Nostalgix", (21, 0)), ((21, 0), "William Black", (22, 0)), ((22, 0), "San Holo", (23, 0)), ((23, 0), "Dabin", (24, 5)), ((24, 5), "Alison Wonderland", (25, 5)), ((25, 5), "Seven Lions", (26, 20)), ((26, 20), "Restricted", (27, 20)), ((27, 20), "BTSM", (28, 30)), ((28, 30), "Nico B2B Holy", (29, 30))],
    "B": [((19, 0), "Nightstalker", (19, 50)), ((19, 50), "Sippy", (20, 40)), ((20, 40), "Eazybaked", (21, 30)), ((21, 30), "Infekt B2B", (22, 30)), ((22, 30), "A.M.C", (23, 30)), ((23, 30), "Virtual Riot", (24, 30)), ((24, 30), "Peekaboo", (25, 30)), ((25, 30), "AHEE B2B Stranger", (26, 30)), ((26, 30), "Whethan", (27, 30)), ((27, 30), "Boogie T B2B", (28, 30)), ((28, 30), "Aeon:Mode", (29, 30))],
    "N": [((19, 0), "Bad Beat", (20, 15)), ((20, 15), "Frankie Bones", (21, 30)), ((21, 30), "Adiel", (22, 50)), ((22, 50), "DJ Gigola", (24, 10)), ((24, 10), "999999999", (25, 30)), ((25, 30), "Indira Paganotto", (26, 50)), ((26, 50), "KI/KI", (28, 10)), ((28, 10), "Klangkuenstler", (29, 30))],
    "Q": [((19, 0), "Warung", (20, 0)), ((20, 0), "Shingo Nakamura", (21, 0)), ((21, 0), "Rebuke", (22, 0)), ((22, 0), "Cristoph", (23, 0)), ((23, 0), "Eli & Fur", (24, 0)), ((24, 0), "Tinlicker", (25, 0)), ((25, 0), "Cassian", (26, 15)), ((26, 15), "Massano", (27, 30)), ((27, 30), "Innellea", (28, 30)), ((28, 30), "KREAM", (29, 30))],
    "S": [((19, 0), "KLO", (20, 0)), ((20, 0), "Murphy's Law", (21, 15)), ((21, 15), "Sidney Charles", (22, 30)), ((22, 30), "Skream", (23, 45)), ((23, 45), "Hamdi", (25, 0)), ((25, 0), "Chris Lorenzo", (26, 15)), ((26, 15), "Silva Bumpa", (27, 30)), ((27, 30), "Morgan Seatree", (28, 30)), ((28, 30), "LU.RE", (29, 30))],
    "W": [((19, 0), "SiHK", (20, 30)), ((20, 30), "Clawz", (21, 30)), ((21, 30), "The Purge", (22, 30)), ((22, 30), "Yosuf", (23, 30)), ((23, 30), "DJ Isaac", (24, 30)), ((24, 30), "Vieze Asbak", (25, 30)), ((25, 30), "Sub Zero Project", (26, 30)), ((26, 30), "Rooler", (27, 30)), ((27, 30), "Warface", (28, 30)), ((28, 30), "Madgrrl B2B", (29, 30))],
    "J": [((19, 0), "Alves", (20, 30)), ((20, 30), "ISAbella", (22, 30)), ((22, 30), "Kinahau", (24, 0)), ((24, 0), "Tiga", (25, 30)), ((25, 30), "DJ Tennis B2B", (27, 30)), ((27, 30), "Beltran B2B", (29, 30))]
}

# --- Logic Functions ---

def get_current_schedule(now):
    # Pass 'now' in so we don't call RTC inside this function
    day = now.tm_wday 
    hour = now.tm_hour
    actual_day = day
    if hour < 7: 
        actual_day -= 1
    if actual_day == 4: return FRIDAY
    if actual_day == 5: return SATURDAY
    if actual_day == 6: return SUNDAY
    return FRIDAY 

def get_next_set_data(stage_key, schedule, now):
    # Pass 'now' in so we don't call RTC inside this function
    cur_h = now.tm_hour
    if cur_h < 7: cur_h += 24
    current_total_mins = (cur_h * 60) + now.tm_min
    
    stage_list = schedule.get(stage_key, [])
    for i, (start, artist, end) in enumerate(stage_list):
        start_mins = (start[0] * 60) + start[1]
        end_mins = (end[0] * 60) + end[1]
        diff_min = start_mins - current_total_mins
        if start_mins <= current_total_mins < end_mins:
            if i + 1 < len(stage_list):
                nxt_s, nxt_a, _ = stage_list[i+1]
                nxt_start_mins = (nxt_s[0] * 60) + nxt_s[1]
                nxt_diff = nxt_start_mins - current_total_mins
                if nxt_diff <= 15: return (nxt_a, f"{nxt_diff}m")
            return (artist, "now")
        if start_mins > current_total_mins:
            return (artist, f"{diff_min}m")
    return "DONE", ""

# --- Display Setup ---
main_group = displayio.Group()
display.root_group = main_group

bg_bmp = displayio.OnDiskBitmap("mta_base.bmp")
bg_tg = displayio.TileGrid(bg_bmp, pixel_shader=bg_bmp.pixel_shader)
main_group.append(bg_tg)

logo_names = ["K", "C", "M", "B", "N", "Q", "S", "W", "J"]
logos = {}
for name in logo_names:
    try:
        bmp = displayio.OnDiskBitmap(name + ".bmp")
        logos[name] = displayio.TileGrid(bmp, pixel_shader=bmp.pixel_shader)
    except: pass 

logo_subgroup = displayio.Group()
main_group.append(logo_subgroup)

top_art_lbl = label.Label(font, text="", color=0xFFFFFF, x=16, y=8)
top_time_lbl = label.Label(font, text="", color=0xFFFFFF)
top_time_lbl.anchor_point = (1.0, 0.5)
top_time_lbl.anchored_position = (62, 9)

bot_art_lbl = label.Label(font, text="", color=0xFFFFFF, x=16, y=24)
bot_time_lbl = label.Label(font, text="", color=0xFFFFFF)
bot_time_lbl.anchor_point = (1.0, 0.5)
bot_time_lbl.anchored_position = (62, 25)

main_group.append(top_art_lbl)
main_group.append(top_time_lbl)
main_group.append(bot_art_lbl)
main_group.append(bot_time_lbl)

# --- Main Loop ---
current_idx = 0
CHAR_LIMIT = 8 

while True:
    # 1. CLEANUP: Clear memory before starting a new cycle
    gc.collect()
    
    # 2. RTC CALL: Only once per "stage swap" (approx every 10-15 seconds)
    current_time = rtc.datetime
    current_schedule = get_current_schedule(current_time)
    
    # 3. SETUP LOGOS
    while len(logo_subgroup) > 0: logo_subgroup.pop()
    n1 = logo_names[current_idx]
    n2 = logo_names[(current_idx + 1) % len(logo_names)]
    
    if n1 in logos:
        logos[n1].x, logos[n1].y = 2, 2
        logo_subgroup.append(logos[n1])
    if n2 in logos:
        logos[n2].x, logos[n2].y = 2, 18
        logo_subgroup.append(logos[n2])

    # 4. PREPARE TEXT SLICES
    # Fetching data once here avoids calling logic inside the animation loop
    art1, time1 = get_next_set_data(n1, current_schedule, current_time)
    art2, time2 = get_next_set_data(n2, current_schedule, current_time)
    
    top_time_lbl.text = time1
    bot_time_lbl.text = time2

    # Prepare strings with trailing spaces for smooth looping
    disp_art1 = art1 + "   " if len(art1) > CHAR_LIMIT else art1
    disp_art2 = art2 + "   " if len(art2) > CHAR_LIMIT else art2
    
    # Pre-calculate the total steps needed for a full scroll cycle
    max_steps = max(len(disp_art1), len(disp_art2))
    
    # 5. ANIMATION LOOP: No RTC calls, no schedule logic, just slicing
    # Repeat the scroll cycle 3 times (approx 12-15 seconds total)
    for _ in range(3):
        for step in range(max_steps):
            # Top Label Slicing
            if len(art1) > CHAR_LIMIT:
                start1 = step % len(disp_art1)
                top_art_lbl.text = disp_art1[start1 : start1 + CHAR_LIMIT]
            else:
                top_art_lbl.text = art1

            # Bottom Label Slicing
            if len(art2) > CHAR_LIMIT:
                start2 = step % len(disp_art2)
                bot_art_lbl.text = disp_art2[start2 : start2 + CHAR_LIMIT]
            else:
                bot_art_lbl.text = art2
            
            time.sleep(0.2) 

    # Advance to next pair
    current_idx = (current_idx + 2) % len(logo_names)