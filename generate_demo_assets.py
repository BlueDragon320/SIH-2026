#!/usr/bin/env python3
"""
Generate realistic industrial demonstration assets for the Air-Gapped Agentic AI Workbench:
1. data/workspace/scanned_inspection_report.png
2. data/workspace/pid_pump_loop.png
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "workspace"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_font(font_name, size, bold=False, italic=False):
    font_paths = {
        ("sans", False, False): "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        ("sans", True, False): "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        ("sans", False, True): "/usr/share/fonts/liberation/LiberationSans-Italic.ttf",
        ("sans", True, True): "/usr/share/fonts/liberation/LiberationSans-BoldItalic.ttf",
        ("serif", False, False): "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf",
        ("serif", True, False): "/usr/share/fonts/liberation/LiberationSerif-Bold.ttf",
        ("serif", False, True): "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf",
        ("mono", False, False): "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
        ("mono", True, False): "/usr/share/fonts/liberation/LiberationMono-Bold.ttf",
    }
    path = font_paths.get((font_name, bold, italic), "/usr/share/fonts/liberation/LiberationSans-Regular.ttf")
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def generate_scanned_inspection_report():
    width, height = 1654, 2338  # Standard A4 @ 200 DPI
    img = Image.new("RGB", (width, height), (252, 250, 245))
    draw = ImageDraw.Draw(img)

    # Realistic subtle paper scan grain/noise
    random.seed(42)
    pixels = img.load()
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            noise = random.randint(-4, 4)
            r = min(255, max(0, 252 + noise))
            g = min(255, max(0, 250 + noise))
            b = min(255, max(0, 245 + noise))
            pixels[x, y] = (r, g, b)
            if x + 1 < width: pixels[x + 1, y] = (r, g, b)
            if y + 1 < height: pixels[x, y + 1] = (r, g, b)

    # Margin scan shadows
    for x in range(width):
        for y in range(height):
            if x < 40:
                factor = 1.0 - (40 - x) / 120.0
                r, g, b = pixels[x, y]
                pixels[x, y] = (int(r * factor), int(g * factor), int(b * factor))
            if y < 30:
                factor = 1.0 - (30 - y) / 100.0
                r, g, b = pixels[x, y]
                pixels[x, y] = (int(r * factor), int(g * factor), int(b * factor))

    # Outer border / frame
    draw.rectangle([50, 50, width - 50, height - 50], outline=(30, 45, 65), width=3)
    draw.rectangle([56, 56, width - 56, height - 56], outline=(90, 105, 120), width=1)

    # Corner registration marks
    for cx, cy in [(70, 70), (width - 70, 70), (70, height - 70), (width - 70, height - 70)]:
        draw.line([cx - 12, cy, cx + 12, cy], fill=(30, 30, 30), width=2)
        draw.line([cx, cy - 12, cx, cy + 12], fill=(30, 30, 30), width=2)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(30, 30, 30), width=1)

    # Official Header Section
    draw.rectangle([80, 75, 200, 195], outline=(15, 45, 80), width=2, fill=(240, 244, 250))
    draw.polygon([(140, 85), (185, 135), (140, 185), (95, 135)], outline=(15, 45, 80), fill=(210, 225, 245), width=2)
    font_logo = get_font("sans", 22, bold=True)
    draw.text((118, 122), "BHP", fill=(15, 45, 80), font=font_logo)

    font_org = get_font("serif", 32, bold=True)
    font_sub_org = get_font("sans", 18, bold=True)
    font_doc_title = get_font("sans", 24, bold=True)
    font_cert = get_font("sans", 14, italic=True)

    draw.text((220, 80), "BHARAT HEAVY PRECISION & DEFENCE SYSTEMS CORP.", fill=(15, 30, 60), font=font_org)
    draw.text((220, 122), "DIRECTORATE OF QUALITY ASSURANCE & METROLOGY (AIR-GAPPED FACILITY 04)", fill=(60, 70, 80), font=font_sub_org)
    draw.text((220, 152), "TURBINE COMPONENT IN-PROCESS INSPECTION CERTIFICATE", fill=(180, 20, 20), font=font_doc_title)
    draw.text((220, 186), "Accreditation: ISO 9001:2015 / AS9100D Quality Management Protocols | MIL-STD-810H Compliant", fill=(80, 90, 100), font=font_cert)

    draw.line([80, 215], fill=(20, 40, 70), width=2)
    draw.line([80, 215, width - 80, 215], fill=(20, 40, 70), width=2)

    # Document & Batch Metadata Table Box
    draw.rectangle([80, 230, width - 80, 435], outline=(60, 70, 80), fill=(246, 248, 252), width=1)
    
    meta_left = [
        ("Certificate / Report No:", "IR-2026-T789-Q4"),
        ("Standard Operating Proc:", "SOP-MECH-TURB-04 (Rev 4.2)"),
        ("Component Name:", "HP Turbine Rotor Blade Ring (Stage 3)"),
        ("Part Number:", "TRB-HP3-718-AMS"),
        ("Material Specification:", "Inconel 718 (AMS 5662 / ASTM B637)"),
    ]
    meta_right = [
        ("Inspection Date:", "11-SEP-2026 08:30 IST"),
        ("Testing Facility Bay:", "Test Bay 4B / Containment Cell 2"),
        ("Heat / Batch Number:", "HT-98442-IN718"),
        ("Batch Inspection Size:", "6 Units (100% Sampled)"),
        ("Inspected Serial Nos:", "SN-2026-8810 through SN-2026-8815"),
    ]

    font_lbl = get_font("sans", 15, bold=True)
    font_val = get_font("mono", 15, bold=False)

    y_pos = 244
    for lbl, val in meta_left:
        draw.text((95, y_pos), lbl, fill=(40, 50, 60), font=font_lbl)
        draw.text((335, y_pos), val, fill=(10, 15, 25), font=font_val)
        y_pos += 35

    y_pos = 244
    for lbl, val in meta_right:
        draw.text((860, y_pos), lbl, fill=(40, 50, 60), font=font_lbl)
        draw.text((1100, y_pos), val, fill=(10, 15, 25), font=font_val)
        y_pos += 35

    # Section 1 Heading
    font_sec = get_font("sans", 18, bold=True)
    draw.text((80, 460), "1. METROLOGY & CHARACTERISTIC TOLERANCE MEASUREMENTS", fill=(15, 30, 60), font=font_sec)

    table_top = 495
    table_left = 80
    table_right = width - 80

    cols = [
        ("Param #", 80, 90),
        ("Inspection Parameter / Characteristic", 170, 440),
        ("Engineering Nominal", 610, 210),
        ("Allowable Limit", 820, 240),
        ("Measured (Avg)", 1060, 200),
        ("Deviation", 1260, 140),
        ("Status", 1400, 174),
    ]

    draw.rectangle([table_left, table_top, table_right, table_top + 45], fill=(30, 55, 90))
    font_th = get_font("sans", 15, bold=True)
    
    for name, cx, cw in cols:
        draw.text((cx + 10, table_top + 12), name, fill=(255, 255, 255), font=font_th)

    table_rows = [
        ("01", "Radial Blade Tip Clearance (HP Stg 3)", "1.200 mm", "1.150 - 1.250 mm", "1.218 mm", "+0.018 mm", "PASS"),
        ("02", "Axial Blade-to-Stator Clearance", "2.500 mm", "2.400 - 2.600 mm", "2.492 mm", "-0.008 mm", "PASS"),
        ("03", "Fir-Tree Root Groove Backlash Fit", "0.015 mm", "Max 0.025 mm", "0.019 mm", "+0.004 mm", "PASS"),
        ("04", "Aerodynamic Leading Edge Radius", "2.400 mm", "2.320 - 2.480 mm", "2.395 mm", "-0.005 mm", "PASS"),
        ("05", "Blade Airfoil Surface Roughness (Ra)", "0.60 µm", "Max 0.80 µm", "0.64 µm", "+0.04 µm", "PASS"),
        ("06", "Shroud Interlock Contact Gap", "0.450 mm", "0.410 - 0.490 mm", "0.442 mm", "-0.008 mm", "PASS"),
        ("07", "Dynamic Vibration Velocity RMS (FSNL)", "0.25 mm/s", "Max 0.50 mm/s", "0.34 mm/s", "+0.09 mm/s", "PASS"),
        ("08", "Steady-State Bearing Metal Temp", "72.0 °C", "Max 85.0 °C", "76.8 °C", "+4.8 °C", "PASS"),
        ("09", "Fluorescent Penetrant Testing (FPI)", "ASTM E1417", "Zero Cracks/Pits", "No Indications", "0.000", "PASS"),
        ("10", "Eddy Current Scallop Inspection", "Defect <0.15mm", "Zero Discontinuities", "Clear (0.00mm)", "0.000", "PASS"),
    ]

    font_tb = get_font("sans", 14, bold=False)
    font_tb_mono = get_font("mono", 14, bold=False)
    font_pass = get_font("sans", 15, bold=True)

    curr_y = table_top + 45
    row_height = 48

    for i, row in enumerate(table_rows):
        row_bg = (255, 255, 255) if i % 2 == 0 else (244, 246, 250)
        draw.rectangle([table_left, curr_y, table_right, curr_y + row_height], fill=row_bg, outline=(200, 205, 215), width=1)
        
        draw.text((cols[0][1] + 15, curr_y + 14), row[0], fill=(60, 60, 60), font=font_tb)
        draw.text((cols[1][1] + 10, curr_y + 14), row[1], fill=(20, 25, 35), font=font_tb)
        draw.text((cols[2][1] + 10, curr_y + 14), row[2], fill=(40, 45, 55), font=font_tb_mono)
        draw.text((cols[3][1] + 10, curr_y + 14), row[3], fill=(40, 45, 55), font=font_tb_mono)
        draw.text((cols[4][1] + 10, curr_y + 14), row[4], fill=(10, 20, 80), font=font_tb_mono)
        draw.text((cols[5][1] + 10, curr_y + 14), row[5], fill=(50, 50, 60), font=font_tb_mono)
        
        draw.rectangle([cols[6][1] + 20, curr_y + 8, cols[6][1] + 110, curr_y + 39], fill=(225, 245, 230), outline=(35, 140, 60), width=1)
        draw.text((cols[6][1] + 42, curr_y + 12), row[6], fill=(20, 120, 45), font=font_pass)

        curr_y += row_height

    draw.rectangle([table_left, table_top, table_right, curr_y], outline=(30, 55, 90), width=2)
    for _, cx, _ in cols[1:]:
        draw.line([cx, table_top, cx, curr_y], fill=(190, 195, 205), width=1)

    # Section 2: Material & Metallurgical Verification
    draw.text((80, curr_y + 30), "2. METALLURGICAL & CHEMICAL VERIFICATION (XRF / PMI SPECTROMETRY)", fill=(15, 30, 60), font=font_sec)
    
    curr_y += 65
    draw.rectangle([80, curr_y, width - 80, curr_y + 135], outline=(60, 70, 80), fill=(250, 251, 253), width=1)
    
    font_spec = get_font("mono", 14, bold=False)
    pmi_lines = [
        "Alloy Confirmation: Inconel 718 (UNS N07718) | Spectrometer Instrument: Thermo Niton XL3t Goldd+ (Calibrated)",
        "Spectral Readout : Ni: 53.25% (Spec: 50-55%) | Cr: 18.62% (Spec: 17-21%) | Fe: 17.85% (Bal) | Nb+Ta: 5.12% (Spec: 4.75-5.50%)",
        "                   Mo: 3.08% (Spec: 2.8-3.3%) | Ti: 0.94% (Spec: 0.65-1.15%) | Al: 0.52% (Spec: 0.20-0.80%) | C: 0.04% (Max 0.08%)",
        "PMI Evaluation   : COMPLIANT WITH DEF-MAT-AL01 & AMS 5662 SPECIFICATIONS. ZERO SEGREGATION DETECTED.",
    ]
    py = curr_y + 14
    for pline in pmi_lines:
        draw.text((95, py), pline, fill=(25, 35, 45), font=font_spec)
        py += 28

    # Section 3: Summary Remarks & Sign-off
    curr_y += 165
    draw.text((80, curr_y), "3. QA DISPOSITION & AUTHORIZED SIGN-OFF", fill=(15, 30, 60), font=font_sec)

    curr_y += 35
    draw.rectangle([80, curr_y, width - 80, curr_y + 150], outline=(30, 110, 60), fill=(244, 252, 246), width=2)
    font_disp = get_font("sans", 16, bold=True)
    font_disp_txt = get_font("sans", 14, bold=False)

    draw.text((100, curr_y + 16), "FINAL QUALITY CONFORMANCE VERDICT: ACCEPTED & CERTIFIED", fill=(20, 120, 45), font=font_disp)
    remark_txt = (
        "All six (6) turbine blade assemblies serial numbers SN-2026-8810 to SN-2026-8815 have been fully inspected in\n"
        "accordance with SOP-MECH-TURB-04 and AS9100D directives. Dimensional tolerances, dynamic vibration signatures\n"
        "(0.34 mm/s RMS < 0.50 mm/s limit), and thermal boundaries (76.8 °C < 85.0 °C max limit) are within approved limits.\n"
        "Components are cleared for rotor disc assembly and hot spin testing in Test Cell 2."
    )
    draw.text((100, curr_y + 48), remark_txt, fill=(35, 45, 55), font=font_disp_txt)

    # Signatures and Stamps Area
    curr_y += 180
    sig_bottom = height - 80
    draw.rectangle([80, curr_y, width - 80, sig_bottom], outline=(150, 160, 170), fill=(255, 255, 255), width=1)

    # Vertical dividers
    draw.line([560, curr_y, 560, sig_bottom], fill=(200, 205, 215), width=1)
    draw.line([1040, curr_y, 1040, sig_bottom], fill=(200, 205, 215), width=1)

    font_sig_title = get_font("sans", 15, bold=True)
    font_sig_meta = get_font("sans", 13, bold=False)

    # Left: Inspector
    draw.text((100, curr_y + 20), "Lead Metrology & QA Inspector:", fill=(40, 50, 60), font=font_sig_title)
    draw.text((100, sig_bottom - 130), "Name: K. S. Ramanujam", fill=(20, 25, 30), font=font_sig_title)
    draw.text((100, sig_bottom - 100), "Designation: Senior Metrology Specialist", fill=(60, 70, 80), font=font_sig_meta)
    draw.text((100, sig_bottom - 75), "Employee ID: QA-4402 | Level III NDT", fill=(60, 70, 80), font=font_sig_meta)
    draw.text((100, sig_bottom - 50), "Date: 11-SEP-2026 09:15 IST", fill=(60, 70, 80), font=font_sig_meta)

    # Middle: Chief QA Officer
    draw.text((580, curr_y + 20), "Chief Quality & Safety Officer:", fill=(40, 50, 60), font=font_sig_title)
    draw.text((580, sig_bottom - 130), "Name: Dr. Arvind Verma", fill=(20, 25, 30), font=font_sig_title)
    draw.text((580, sig_bottom - 100), "Designation: Head of Defence QA Division", fill=(60, 70, 80), font=font_sig_meta)
    draw.text((580, sig_bottom - 75), "Authority: Directorate of Technical Approvals", fill=(60, 70, 80), font=font_sig_meta)
    draw.text((580, sig_bottom - 50), "Date: 11-SEP-2026 09:40 IST", fill=(60, 70, 80), font=font_sig_meta)

    # Right: Stamp info
    draw.text((1060, curr_y + 20), "Cryptographic Audit Stamp:", fill=(40, 50, 60), font=font_sig_title)
    font_crypto = get_font("mono", 12, bold=False)
    draw.text((1060, sig_bottom - 110), "SHA-256 INTEGRITY DIGEST:", fill=(80, 90, 100), font=font_crypto)
    draw.text((1060, sig_bottom - 85), "e3b0c44298fc1c149afbf4c8996fb", fill=(30, 40, 50), font=font_crypto)
    draw.text((1060, sig_bottom - 63), "92427ae41e4649b934ca495991b78", fill=(30, 40, 50), font=font_crypto)
    draw.text((1060, sig_bottom - 38), "AIR-GAP SIGNED: SEC-ENCLAVE-04", fill=(10, 120, 40), font=font_crypto)

    # Smooth signature curves
    def draw_smooth_curve(points, width_val=3, color=(25, 55, 145)):
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=width_val)

    # Signature 1
    sig_y_mid = curr_y + 110
    sig1_color = (25, 55, 145)
    sig1_pts1 = [(130, sig_y_mid + 15), (150, sig_y_mid - 45), (175, sig_y_mid + 45), (195, sig_y_mid - 30), (220, sig_y_mid + 25)]
    sig1_pts2 = [(220, sig_y_mid + 25), (245, sig_y_mid + 5), (270, sig_y_mid + 20), (295, sig_y_mid - 10), (330, sig_y_mid + 15), (365, sig_y_mid - 15), (400, sig_y_mid + 20), (440, sig_y_mid - 25), (480, sig_y_mid + 20)]
    sig1_pts3 = [(160, sig_y_mid + 35), (250, sig_y_mid + 40), (380, sig_y_mid + 45), (480, sig_y_mid + 35), (520, sig_y_mid + 15)]
    draw_smooth_curve(sig1_pts1, 3, sig1_color)
    draw_smooth_curve(sig1_pts2, 2, sig1_color)
    draw_smooth_curve(sig1_pts3, 2, sig1_color)

    # Signature 2
    sig2_color = (15, 45, 120)
    sig2_pts1 = [(610, sig_y_mid + 20), (635, sig_y_mid - 50), (675, sig_y_mid + 45), (705, sig_y_mid - 30), (730, sig_y_mid + 15)]
    sig2_pts2 = [(730, sig_y_mid + 15), (765, sig_y_mid - 10), (800, sig_y_mid + 15), (845, sig_y_mid - 20), (895, sig_y_mid + 10), (945, sig_y_mid - 30), (990, sig_y_mid + 30)]
    sig2_pts3 = [(640, sig_y_mid + 42), (760, sig_y_mid + 46), (900, sig_y_mid + 38), (1000, sig_y_mid + 22)]
    draw_smooth_curve(sig2_pts1, 3, sig2_color)
    draw_smooth_curve(sig2_pts2, 2, sig2_color)
    draw_smooth_curve(sig2_pts3, 2, sig2_color)

    # Red Stamp
    seal_size = 200
    seal_img = Image.new("RGBA", (seal_size, seal_size), (255, 255, 255, 0))
    sdraw = ImageDraw.Draw(seal_img)
    sc = (185, 30, 30, 220)

    sdraw.ellipse([6, 6, seal_size - 6, seal_size - 6], outline=sc, width=3)
    sdraw.ellipse([12, 12, seal_size - 12, seal_size - 12], outline=sc, width=1)
    sdraw.ellipse([36, 36, seal_size - 36, seal_size - 36], outline=sc, width=2)

    font_stamp = get_font("sans", 10, bold=True)
    font_stamp_lg = get_font("sans", 14, bold=True)
    font_stamp_sm = get_font("sans", 8, bold=True)

    sdraw.text((50, 52), "DEFENCE QA", fill=sc, font=font_stamp)
    sdraw.text((45, 76), "APPROVED", fill=sc, font=font_stamp_lg)
    sdraw.text((54, 102), "★ PASSED ★", fill=sc, font=font_stamp)
    sdraw.text((42, 126), "ISO 9001:2015", fill=sc, font=font_stamp_sm)
    sdraw.text((48, 140), "AUDIT DIV 04", fill=sc, font=font_stamp_sm)

    s_pixels = seal_img.load()
    for sy in range(seal_size):
        for sx in range(seal_size):
            if s_pixels[sx, sy][3] > 0 and random.random() < 0.15:
                alpha = max(0, s_pixels[sx, sy][3] - random.randint(60, 180))
                s_pixels[sx, sy] = (sc[0], sc[1], sc[2], alpha)

    rotated_seal = seal_img.rotate(-6, resample=Image.BICUBIC, expand=True)
    img.paste(rotated_seal, (1220, curr_y + 40), rotated_seal)

    # Slight overall scan rotation
    img = img.rotate(0.3, resample=Image.BICUBIC, fillcolor=(235, 232, 225))

    output_path = os.path.join(OUTPUT_DIR, "scanned_inspection_report.png")
    img.save(output_path, "PNG", dpi=(200, 200))
    print(f"Generated scanned inspection report: {output_path} ({width}x{height})")


def generate_pid_pump_loop():
    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), (250, 252, 255))
    draw = ImageDraw.Draw(img)

    # Engineering grid
    grid_color = (235, 240, 248)
    for x in range(0, width, 25):
        draw.line([x, 0, x, height], fill=grid_color, width=1)
    for y in range(0, height, 25):
        draw.line([0, y, width, y], fill=grid_color, width=1)

    # Outer border
    draw.rectangle([30, 30, width - 30, height - 30], outline=(15, 30, 50), width=3)
    draw.rectangle([36, 36, width - 36, height - 36], outline=(70, 90, 120), width=1)

    # Header Bar
    font_main_title = get_font("sans", 22, bold=True)
    font_subtitle = get_font("sans", 15, bold=False)
    font_tag = get_font("mono", 14, bold=True)
    font_pipe = get_font("sans", 13, bold=True)
    font_sym = get_font("sans", 12, bold=True)

    draw.rectangle([36, 36, width - 36, 95], fill=(240, 245, 252), outline=(50, 70, 100), width=2)
    draw.text((55, 45), "PROCESS & INSTRUMENTATION DIAGRAM (P&ID)", fill=(10, 25, 50), font=font_main_title)
    draw.text((55, 72), "CENTRIFUGAL PUMP P-101 LOOP WITH MINIMUM FLOW RECIRCULATION & PRESSURE CONTROL", fill=(50, 70, 95), font=font_subtitle)
    draw.text((width - 440, 50), "AREA: TURBINE AUXILIARY SKID", fill=(10, 30, 60), font=font_tag)
    draw.text((width - 440, 70), "SYSTEM ID: SYS-P101-LOOP-01", fill=(10, 30, 60), font=font_tag)

    # Title Block (Bottom Right)
    tb_w, tb_h = 520, 160
    tb_x, tb_y = width - 36 - tb_w, height - 36 - tb_h
    draw.rectangle([tb_x, tb_y, width - 36, height - 36], fill=(245, 248, 253), outline=(15, 30, 50), width=2)
    draw.line([tb_x, tb_y + 40, width - 36, tb_y + 40], fill=(50, 70, 100), width=1)
    draw.line([tb_x, tb_y + 80, width - 36, tb_y + 80], fill=(50, 70, 100), width=1)
    draw.line([tb_x, tb_y + 120, width - 36, tb_y + 120], fill=(50, 70, 100), width=1)
    draw.line([tb_x + 260, tb_y, tb_x + 260, height - 36], fill=(50, 70, 100), width=1)

    draw.text((tb_x + 15, tb_y + 10), "DWG NO: PID-P101-REC-001", fill=(10, 20, 40), font=font_tag)
    draw.text((tb_x + 275, tb_y + 10), "REV: 02 (APPROVED)", fill=(180, 20, 20), font=font_tag)
    draw.text((tb_x + 15, tb_y + 50), "DRAWN BY: MECH ENG DIV", fill=(40, 50, 60), font=font_subtitle)
    draw.text((tb_x + 275, tb_y + 50), "DATE: 11-SEP-2026", fill=(40, 50, 60), font=font_subtitle)
    draw.text((tb_x + 15, tb_y + 90), "CHECKED BY: QA METROLOGY", fill=(40, 50, 60), font=font_subtitle)
    draw.text((tb_x + 275, tb_y + 90), "SCALE: N.T.S.", fill=(40, 50, 60), font=font_subtitle)
    draw.text((tb_x + 15, tb_y + 130), "STATUS: AIR-GAPPED CONTROLLED", fill=(10, 120, 40), font=font_tag)
    draw.text((tb_x + 275, tb_y + 130), "ISO 9001 / MIL-STD-810H", fill=(50, 60, 70), font=font_subtitle)

    # Legend Box (Top Right)
    lg_x, lg_y = width - 36 - 360, 115
    draw.rectangle([lg_x, lg_y, width - 36, lg_y + 240], fill=(255, 255, 255), outline=(100, 120, 140), width=1)
    draw.rectangle([lg_x, lg_y, width - 36, lg_y + 30], fill=(230, 238, 248))
    draw.text((lg_x + 10, lg_y + 6), "INSTRUMENTATION & SYMBOL LEGEND", fill=(10, 30, 60), font=font_sym)
    
    legend_items = [
        ("───", "Process Main Line (Carbon Steel)"),
        ("- - -", "Electrical / 4-20mA Signal Line"),
        ("PT-103", "Pressure Transmitter (Field Mounted)"),
        ("PIC-103", "Pressure Indicating Controller (DCS)"),
        ("CV-102", "Control Valve (Pneumatic Diaphragm - FO)"),
        ("P-101", "Centrifugal Feed Pump (Electric Motor)"),
        ("STR-101", "Suction Basket Strainer"),
    ]
    ly = lg_y + 38
    for sym, desc in legend_items:
        draw.text((lg_x + 12, ly), sym, fill=(180, 20, 20) if "-" in sym or "P" in sym else (10, 20, 40), font=font_tag)
        draw.text((lg_x + 95, ly), desc, fill=(40, 50, 60), font=get_font("sans", 11, bold=False))
        ly += 28

    pipe_color = (15, 45, 90)
    signal_color = (200, 30, 30)

    # Helper for ball valve
    def draw_ball_valve(vx, vy, label="BV-101"):
        draw.polygon([(vx - 16, vy - 12), (vx - 16, vy + 12), (vx + 16, vy - 12), (vx + 16, vy + 12)], fill=(255, 255, 255), outline=pipe_color, width=2)
        draw.line([vx, vy, vx, vy - 16], fill=pipe_color, width=2)
        draw.ellipse([vx - 5, vy - 21, vx + 5, vy - 11], fill=pipe_color)
        draw.text((vx - 22, vy + 16), label, fill=(10, 20, 40), font=font_sym)

    def draw_dashed_line(x1, y1, x2, y2, color=signal_color, width_val=2, dash=6, gap=4):
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0: return
        dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
        curr = 0
        while curr < dist:
            end = min(curr + dash, dist)
            draw.line([x1 + dx * curr, y1 + dy * curr, x1 + dx * end, y1 + dy * end], fill=color, width=width_val)
            curr += dash + gap

    def draw_arrow_right(ax, ay):
        draw.polygon([(ax - 10, ay - 8), (ax + 10, ay), (ax - 10, ay + 8)], fill=pipe_color)

    def draw_arrow_left(ax, ay):
        draw.polygon([(ax + 10, ay - 8), (ax - 10, ay), (ax + 10, ay + 8)], fill=pipe_color)

    # 1. Suction Storage Tank TK-100 (Left side)
    tk_x, tk_y, tk_w, tk_h = 80, 400, 160, 380
    draw.rectangle([tk_x, tk_y, tk_x + tk_w, tk_y + tk_h], outline=(20, 40, 70), fill=(235, 242, 250), width=3)
    draw.arc([tk_x, tk_y - 25, tk_x + tk_w, tk_y + 25], start=180, end=360, fill=(20, 40, 70), width=3)
    draw.arc([tk_x, tk_y + tk_h - 25, tk_x + tk_w, tk_y + tk_h + 25], start=0, end=180, fill=(20, 40, 70), width=3)
    draw.text((tk_x + 25, tk_y + 160), "TK-100", fill=(10, 30, 60), font=get_font("sans", 20, bold=True))
    draw.text((tk_x + 15, tk_y + 190), "FEED STORAGE", fill=(50, 70, 90), font=get_font("sans", 13, bold=False))
    draw.text((tk_x + 35, tk_y + 210), "VESSEL", fill=(50, 70, 90), font=get_font("sans", 13, bold=False))

    # Suction line at y = 690
    suct_y = 690
    suct_nozzle_x = tk_x + tk_w
    draw.rectangle([suct_nozzle_x, suct_y - 12, suct_nozzle_x + 20, suct_y + 12], fill=(180, 195, 215), outline=(20, 40, 70), width=2)

    # Pump center at (580, 690)
    pump_cx, pump_cy, pump_r = 580, 690, 52
    draw.line([suct_nozzle_x + 20, suct_y, pump_cx - pump_r, suct_y], fill=pipe_color, width=6)
    draw.text((260, suct_y - 30), '8"-PR-101-CS300 (SUCTION LINE)', fill=(15, 45, 90), font=font_pipe)
    draw_arrow_right(250, suct_y)

    # Suction valve & strainer
    draw_ball_valve(330, suct_y, "BV-101")
    
    str_x = 440
    draw.polygon([(str_x - 16, suct_y - 16), (str_x + 16, suct_y - 16), (str_x, suct_y + 18)], fill=(240, 244, 250), outline=pipe_color, width=2)
    draw.line([str_x - 10, suct_y - 8, str_x + 10, suct_y + 8], fill=pipe_color, width=1)
    draw.text((str_x - 24, suct_y + 22), "STR-101", fill=(10, 20, 40), font=font_sym)

    # Centrifugal Pump P-101
    draw.ellipse([pump_cx - pump_r, pump_cy - pump_r, pump_cx + pump_r, pump_cy + pump_r], fill=(235, 245, 255), outline=pipe_color, width=4)
    # Impeller tangential exit triangle
    draw.polygon([(pump_cx + 10, pump_cy - 48), (pump_cx + 48, pump_cy - 10), (pump_cx + 48, pump_cy - 48)], fill=(20, 50, 100))
    draw.text((pump_cx - 32, pump_cy - 12), "P-101", fill=(10, 25, 50), font=get_font("sans", 18, bold=True))
    draw.text((pump_cx - 75, pump_cy - 75), "CENTRIFUGAL PUMP", fill=(15, 35, 70), font=font_sym)

    # Motor Driver M
    motor_cx, motor_cy, motor_r = pump_cx, 850, 38
    draw.rectangle([pump_cx - 8, pump_cy + pump_r, pump_cx + 8, motor_cy - motor_r], fill=(120, 130, 140), outline=pipe_color, width=2)
    draw.ellipse([motor_cx - motor_r, motor_cy - motor_r, motor_cx + motor_r, motor_cy + motor_r], fill=(245, 248, 252), outline=pipe_color, width=3)
    draw.text((motor_cx - 12, motor_cy - 16), "M", fill=(15, 30, 60), font=get_font("sans", 24, bold=True))
    draw.text((motor_cx - 50, motor_cy + motor_r + 10), "MOTOR 350 kW", fill=(50, 60, 70), font=font_sym)

    # Discharge line at y = 520
    disch_x = pump_cx + 48
    disch_y_top = 520
    draw.line([disch_x, pump_cy - 45, disch_x, disch_y_top], fill=pipe_color, width=6)

    outlet_x = 1420
    draw.line([disch_x, disch_y_top, outlet_x, disch_y_top], fill=pipe_color, width=6)
    draw.text((680, disch_y_top + 30), '6"-PR-102-CS300 (DISCHARGE HEADER)', fill=(15, 45, 90), font=font_pipe)
    draw_arrow_right(720, disch_y_top)
    draw_arrow_right(1340, disch_y_top)

    # Check valve NRV-102
    nrv_x = 760
    draw.polygon([(nrv_x - 16, disch_y_top - 12), (nrv_x - 16, disch_y_top + 12), (nrv_x + 16, disch_y_top)], fill=(255, 255, 255), outline=pipe_color, width=2)
    draw.line([nrv_x + 16, disch_y_top - 12, nrv_x + 16, disch_y_top + 12], fill=pipe_color, width=2)
    draw.text((nrv_x - 25, disch_y_top + 20), "NRV-102", fill=(10, 20, 40), font=font_sym)

    # Local Pressure Gauge PG-101
    pg_x = 860
    draw.line([pg_x, disch_y_top, pg_x, disch_y_top + 50], fill=pipe_color, width=2)
    draw.ellipse([pg_x - 20, disch_y_top + 50, pg_x + 20, disch_y_top + 90], fill=(255, 255, 255), outline=pipe_color, width=2)
    draw.text((pg_x - 12, disch_y_top + 58), "PG", fill=(10, 20, 40), font=font_sym)
    draw.text((pg_x - 14, disch_y_top + 72), "101", fill=(10, 20, 40), font=font_sym)

    # Pressure Transmitter PT-103 (tapped upwards towards PIC)
    pt_x = 980
    draw.line([pt_x, disch_y_top, pt_x, disch_y_top - 50], fill=pipe_color, width=2)
    draw.ellipse([pt_x - 24, disch_y_top - 98, pt_x + 24, disch_y_top - 50], fill=(255, 255, 255), outline=pipe_color, width=2)
    draw.text((pt_x - 12, disch_y_top - 88), "PT", fill=(10, 20, 40), font=font_sym)
    draw.text((pt_x - 16, disch_y_top - 72), "103", fill=(10, 20, 40), font=font_sym)
    draw.text((pt_x + 32, disch_y_top - 78), "0-10 BAR", fill=(80, 90, 100), font=get_font("sans", 11, bold=False))

    # Pressure Controller PIC-103
    pic_x, pic_y = 980, 160
    draw.ellipse([pic_x - 30, pic_y - 30, pic_x + 30, pic_y + 30], fill=(245, 250, 255), outline=pipe_color, width=2)
    draw.line([pic_x - 30, pic_y, pic_x + 30, pic_y], fill=pipe_color, width=2)
    draw.text((pic_x - 16, pic_y - 20), "PIC", fill=(10, 20, 40), font=font_sym)
    draw.text((pic_x - 16, pic_y + 8), "103", fill=(10, 20, 40), font=font_sym)

    # Signal from PT-103 to PIC-103 (Vertical dashed red line)
    draw_dashed_line(pt_x, disch_y_top - 98, pic_x, pic_y + 30)
    draw.text((pt_x + 12, 340), "4-20 mA", fill=signal_color, font=font_sym)

    # Discharge Isolation Valve BV-103
    draw_ball_valve(1260, disch_y_top, "BV-103")

    # Header Outlet Arrow
    draw.rectangle([outlet_x, disch_y_top - 25, outlet_x + 240, disch_y_top + 25], fill=(230, 242, 255), outline=(20, 50, 90), width=2)
    draw.polygon([(outlet_x + 240, disch_y_top - 35), (outlet_x + 270, disch_y_top), (outlet_x + 240, disch_y_top + 35)], fill=(20, 50, 90))
    draw.text((outlet_x + 15, disch_y_top - 12), "TO TURBINE HEADER", fill=(10, 25, 60), font=font_pipe)
    draw.text((outlet_x + 15, disch_y_top + 6), '6" LINE / 2.5 BAR', fill=(70, 85, 100), font=get_font("mono", 11, bold=False))

    # 4. Minimum Flow Recirculation Line (Placed cleanly at y = 260)
    recirc_branch_x = 1140
    recirc_y = 260

    # Vertical branch upward from discharge header
    draw.line([recirc_branch_x, disch_y_top, recirc_branch_x, recirc_y], fill=pipe_color, width=5)
    # Horizontal line back to Tank
    draw.line([recirc_branch_x, recirc_y, 180, recirc_y], fill=pipe_color, width=5)
    # Vertical line down to top nozzle of TK-100
    draw.line([180, recirc_y, 180, tk_y - 20], fill=pipe_color, width=5)
    draw.rectangle([165, tk_y - 20, 195, tk_y - 5], fill=(180, 195, 215), outline=(20, 40, 70), width=2)

    draw.text((220, recirc_y - 30), '4"-REC-104-CS300 (MINIMUM FLOW RECIRCULATION LINE)', fill=(15, 45, 90), font=font_pipe)
    draw_arrow_left(560, recirc_y)
    draw_arrow_left(195, recirc_y)

    # Restriction Orifice RO-104
    ro_x = 880
    draw.line([ro_x - 8, recirc_y - 14, ro_x - 8, recirc_y + 14], fill=pipe_color, width=2)
    draw.line([ro_x + 8, recirc_y - 14, ro_x + 8, recirc_y + 14], fill=pipe_color, width=2)
    draw.ellipse([ro_x - 4, recirc_y - 4, ro_x + 4, recirc_y + 4], fill=pipe_color)
    draw.text((ro_x - 25, recirc_y + 18), "RO-104", fill=(10, 20, 40), font=font_sym)

    # Control Valve CV-102 at x = 700, y = 260
    cv_x, cv_y = 700, recirc_y
    draw.polygon([(cv_x - 18, cv_y - 12), (cv_x - 18, cv_y + 12), (cv_x + 18, cv_y - 12), (cv_x + 18, cv_y + 12)], fill=(255, 255, 255), outline=pipe_color, width=2)
    draw.line([cv_x, cv_y, cv_x, cv_y - 28], fill=pipe_color, width=2)
    draw.arc([cv_x - 22, cv_y - 56, cv_x + 22, cv_y - 24], start=180, end=360, fill=pipe_color, width=3)
    draw.line([cv_x - 22, cv_y - 40, cv_x + 22, cv_y - 40], fill=pipe_color, width=2)
    
    draw.text((cv_x - 24, cv_y + 18), "CV-102", fill=(180, 20, 20), font=get_font("sans", 13, bold=True))
    draw.text((cv_x - 45, cv_y + 36), "FO (FAIL OPEN)", fill=(180, 20, 20), font=get_font("sans", 11, bold=True))

    # Clean orthogonal signal Line from PIC-103 to CV-102 Actuator
    draw_dashed_line(pic_x - 30, pic_y, cv_x, pic_y)
    draw_dashed_line(cv_x, pic_y, cv_x, cv_y - 56)
    draw.text((450, pic_y - 20), "PNEUMATIC SIGNAL (AIR TO CLOSE)", fill=signal_color, font=get_font("sans", 11, bold=True))

    # Recirc Isolation Valve BV-105
    draw_ball_valve(380, recirc_y, "BV-105")

    # Safety Relief Valve PSV-101
    psv_x, psv_y = 1100, disch_y_top
    draw.line([psv_x, psv_y, psv_x, psv_y + 70], fill=pipe_color, width=3)
    draw.polygon([(psv_x - 12, psv_y + 70), (psv_x + 12, psv_y + 70), (psv_x, psv_y + 90)], fill=(255, 255, 255), outline=pipe_color, width=2)
    draw.line([psv_x, psv_y + 90, psv_x + 25, psv_y + 90], fill=pipe_color, width=2)
    draw.text((psv_x - 25, psv_y + 102), "PSV-101", fill=(10, 20, 40), font=font_sym)
    draw.text((psv_x - 35, psv_y + 118), "SET: 4.5 BAR", fill=(70, 80, 90), font=get_font("sans", 10, bold=False))

    output_path = os.path.join(OUTPUT_DIR, "pid_pump_loop.png")
    img.save(output_path, "PNG", dpi=(150, 150))
    print(f"Generated P&ID pump loop diagram: {output_path} ({width}x{height})")


if __name__ == "__main__":
    generate_scanned_inspection_report()
    generate_pid_pump_loop()
    print("All assets successfully generated!")
