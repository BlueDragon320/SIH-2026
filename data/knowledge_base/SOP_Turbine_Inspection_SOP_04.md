# Standard Operating Procedure: Gas & Steam Turbine Blade Inspection (SOP-04)

**Document Identifier:** SOP-MECH-TURB-04  
**Revision:** 4.2  
**Effective Date:** 2026-09-01  
**Classification:** Restricted / Defence & Power Systems Engineering  
**Compliance Authority:** ISO 9001:2015 Quality Management Systems & ISO 10816-3 Mechanical Vibration Standard  
**Facility:** Heavy Engineering & Gas Turbine Overhaul Facility (Air-Gapped Maintenance Wing)

---

## 1. Purpose & Scope

This Standard Operating Procedure (SOP) defines the mandatory protocol for in-process and periodic non-destructive, dimensional, dynamic, and thermal inspection of high-pressure (HP) and low-pressure (LP) turbine rotor blades, stator vanes, and casing assemblies. Compliance with this procedure is strictly enforced to prevent catastrophic aerodynamic failure, high-cycle fatigue (HCF), and creep-induced blade ejection.

This document applies to all certified quality assurance (QA) inspectors, non-destructive testing (NDT) Level II/III technicians, and overhaul engineers operating within air-gapped turbine testing facilities.

---

## 2. Regulatory & Compliance Standards

All inspection procedures, measurement calibrations, and reporting workflows must strictly conform to:
1. **ISO 9001:2015** — Quality Management Systems: Requirements for traceability, calibration logs, and non-conformance records (NCR).
2. **ISO 10816-3** — Mechanical vibration: Evaluation of machine vibration by measurements on non-rotating parts and industrial rotor assemblies.
3. **ASTM E1417 / E1444** — Standard Practice for Liquid Penetrant and Magnetic Particle Testing.
4. **AS9100D** — Quality Systems for Aerospace, Marine, and Defence Heavy Assemblies.

---

## 3. Dimensional Tolerances & Critical Thresholds

All dimensional evaluations must be performed at standard ambient reference temperature (20.0 °C ± 2.0 °C) using calibrated dial test indicators, laser micrometers, or Coordinate Measuring Machines (CMM).

| Inspection Parameter | Target Nominal | Allowable Tolerance Band | Rejection Threshold |
| :--- | :--- | :--- | :--- |
| **Radial Blade Tip Clearance (HP)** | 1.200 mm | ±0.050 mm (1.150 mm – 1.250 mm) | < 1.100 mm or > 1.300 mm |
| **Axial Blade Clearance (HP/LP)** | 2.500 mm | ±0.100 mm (2.400 mm – 2.600 mm) | < 2.350 mm or > 2.650 mm |
| **Root Fir-Tree Groove Fit Play** | 0.015 mm | +0.010 mm / -0.005 mm | > 0.025 mm |
| **Aerodynamic Leading Edge Radius** | 2.400 mm | ±0.080 mm | < 2.250 mm or > 2.550 mm |
| **Blade Surface Roughness ($R_a$)** | 0.60 µm | Max limit: 0.80 µm | > 0.80 µm |
| **Shroud Interlock Gap** | 0.450 mm | ±0.040 mm (0.410 mm – 0.490 mm) | > 0.520 mm |

---

## 4. Dynamic Vibration Limits & RMS Velocity Thresholds

Vibration measurements must be acquired using dual-axis piezoelectric accelerometers mounted on turbine bearing housings (DE - Drive End, NDE - Non-Drive End) conforming to ISO 10816-3 Zone Classifications for Class Group 1 large industrial machines with rigid foundations:

- **Zone A (Nominal / Newly Commissioned):** $V_{\text{RMS}} \le 0.28\text{ mm/s}$
- **Zone B (Acceptable for Long-term Operation):** $0.28\text{ mm/s} < V_{\text{RMS}} \le 0.35\text{ mm/s}$
- **Zone C (Warning / Alert Threshold):** $0.35\text{ mm/s} < V_{\text{RMS}} \le 0.48\text{ mm/s}$ — Schedule borescope and root inspection within 48 operating hours.
- **Zone D (Mandatory Shutdown & Trip Threshold):** **$V_{\text{RMS}} \ge 0.50\text{ mm/s}$** — Automatic emergency interlock trip. Unconditional engine isolation and rotor demounting required.

> **CRITICAL SAFETY DIRECTIVE:** Any vibration transient exceeding **0.50 mm/s RMS** requires immediate trip engagement, isolation of fuel/steam inlet control valves, and mandatory 100% dye-penetrant inspection of all stage blades before re-cranking.

---

## 5. Thermal Tolerances & Bearing Temperature Limits

Thermal gradients and temperature boundaries must be continuously logged during spin-up, rated load, and spin-down:

- **Journal & Thrust Bearing Metal Temperature:**
  - Continuous Nominal: $65.0\text{ }^\circ\text{C} - 78.0\text{ }^\circ\text{C}$
  - High Temperature Advisory Alarm: $80.0\text{ }^\circ\text{C}$
  - **Maximum Thermal Tolerance / Emergency Trip Limit:** **$85.0\text{ }^\circ\text{C}$**
- **Exhaust Circumferential Temperature Spread ($\Delta T_{\text{spread}}$):**
  - Permissible limit: $\Delta T_{\text{spread}} \le 25.0\text{ }^\circ\text{C}$ across all 12 thermocouple wells.
- **Rotor Pre-Heating Ramp Rate:**
  - Maximum allowable ramp rate: $\le 5.0\text{ }^\circ\text{C}/\text{min}$ to prevent differential thermal expansion between rotor disc and blade roots.

---

## 6. Step-by-Step Inspection Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Machine Lockdown & Thermal Cooldown (< 40.0 °C)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 2: High-Definition Borescope Visual Sweep             │
│          - Check for foreign object damage (FOD) & erosion  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 3: Non-Destructive Testing (NDT) Protocols            │
│          - Fluorescent Penetrant (ASTM E1417) on airfoils   │
│          - Eddy Current Testing (ECT) on trailing edges     │
│          - Ultrasonic Phased Array (UT) on fir-tree roots   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 4: Precision Dimensional & Clearance Metrology        │
│          - Tip radial clearance via feeder gauges & optical │
│          - Surface profile roughness (Ra <= 0.80 µm)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 5: Dynamic Spin & Thermal Signature Verification      │
│          - Verify RMS vibration < 0.50 mm/s                 │
│          - Verify bearing temperature <= 85.0 °C            │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ Phase 6: QA Documentation & ISO 9001 Sign-Off               │
│          - Stamp approval certificate, file NCR if failed    │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Phase Execution:

1. **Phase 1 — Safety & Thermal Isolation:**
   - Verify zero-energy lock-out / tag-out (LOTO) on auxiliary lube pumps and main steam/gas admission valves.
   - Wait until internal turbine casing thermocouple reads below $40.0\text{ }^\circ\text{C}$.

2. **Phase 2 — Borescope Inspection:**
   - Insert 4-way articulating 6.0 mm video-borescope through inspection ports IP-01 through IP-08.
   - Inspect leading and trailing edges for micro-pitting, thermal oxidation, and foreign object damage (FOD).

3. **Phase 3 — NDT Testing:**
   - Apply Type 1, Method A, Level 3 fluorescent penetrant. Dwell time: 20 minutes. Inspect under UV-A light ($\ge 1200\text{ }\mu\text{W/cm}^2$).
   - Run Eddy Current Testing probe along trailing edge scallops. Any crack indication $\ge 0.15\text{ mm}$ length requires blade replacement.

4. **Phase 4 — Dimensional Verification:**
   - Measure 360-degree radial tip clearance at 8 equidistant angular positions ($0^\circ, 45^\circ, 90^\circ, \dots, 315^\circ$).
   - Confirm readings fall strictly within $1.150\text{ mm} - 1.250\text{ mm}$.

5. **Phase 5 — Dynamic Validation:**
   - Run unit at Full Speed No Load (FSNL). Record telemetry batch for 15 minutes.
   - Confirm vibration RMS is strictly below **$0.50\text{ mm/s}$** and steady bearing temperature remains below **$85.0\text{ }^\circ\text{C}$**.

6. **Phase 6 — Certification & Sign-Off:**
   - Record serial numbers, measured clearances, and vibration readings in the official Inspection Certificate.
   - Apply the QA physical/digital approval stamp and countersign by the Lead Quality Assurance Inspector.

---

## 7. Quality Records & Non-Conformance Protocol

- In the event of any parameter exceeding the tolerance threshold (e.g., tip clearance > 1.250 mm or vibration RMS $\ge 0.50\text{ mm/s}$), an immediate **Non-Conformance Report (NCR)** must be filed in the air-gapped QA repository.
- Non-conforming blades must be physically tagged with a red quarantine marker and moved to the containment area.
- All digital records must be signed with SHA-256 cryptographic verification before inclusion in the plant master logbook.
