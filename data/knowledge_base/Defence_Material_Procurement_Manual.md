# Defence & Strategic Material Procurement and Quality Assurance Manual

**Document Code:** DMP-QA-VOL-2 / REV-2026.1  
**Authority:** Directorate of Defence Procurement & Quality Assurance (DDPQA)  
**Security Classification:** RESTRICTED / STRATEGIC ENGINEERING  
**Effective Cycle:** 2026 – 2028  
**Applicable Scope:** Air-Gapped Manufacturing Plants, Heavy Defense Equipment Fabrication, Marine & Turbine Propulsion Yards

---

## 1. Executive Summary & Policy Statement

Procurement of specialized materials and fabricated assemblies for defence and heavy engineering applications demands uncompromising quality, full raw material traceability, and continuous verification. This manual prescribes the mandatory quality assurance directives, vendor audit frameworks, incoming inspection protocols, and material acceptance criteria governing all critical acquisitions.

Zero deviations from the documented chemical, mechanical, and non-destructive testing requirements are permitted without formal sanction by the Material Review Board (MRB).

---

## 2. Applicable Standards & Specifications

All procurements, material testing, and documentation packages must adhere strictly to the following standards:

1. **AS9100D / ISO 9001:2015:** Quality Management Systems — Requirements for Aviation, Space, and Defence Organizations.
2. **MIL-STD-810H:** Environmental Engineering Considerations and Laboratory Tests for Defence Hardware.
3. **MIL-STD-1537 / ASTM E1444:** Non-Destructive Inspection and Acceptance Criteria for High-Stress Alloys.
4. **EN 10204 (Types 3.1 & 3.2):** Metallic Products — Types of Inspection Documents. (Mandatory independent third-party inspection sign-off for Type 3.2).
5. **AS9102:** Aerospace First Article Inspection Requirement (FAIR).

---

## 3. Approved Strategic Material Specifications

| Material Code | Alloy Designation | Standard Specification | Primary Application | Mandatory Testing Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-MAT-AL01** | **Inconel 718 (UNS N07718)** | AMS 5662 / ASTM B637 | High-Pressure Turbine Blades & Disc Rotors | Tensile @ 650°C, Stress Rupture, 100% Phased Array UT |
| **DEF-MAT-TI02** | **Titanium Grade 5 (Ti-6Al-4V)** | AMS 4928 / MIL-T-9047 | Compressor Rotor Assemblies & Aero Vanes | Charpy V-Notch Impact @ -40°C, XRF PMI, Metallography |
| **DEF-MAT-SS03** | **Super Duplex 2507 (UNS S32750)**| ASTM A276 / EN 10088 | Marine Propulsion Shafts & High-Pressure Piping | Pitting Resistance Eq. ($PRE_N \ge 42$), ASTM G48 Corrosion |
| **DEF-MAT-CS04** | **HY-80 High Yield Steel** | MIL-S-16216 | Submarine Pressure Hull Ribs & Structural Casings | 100% Radiographic Testing (RT), Hardness Rockwell C $\le 28$ |

---

## 4. Vendor Qualification & First Article Inspection (FAI)

### 4.1 Tier Categorization
- **Tier-1 (Strategic Partner):** Fully certified AS9100D facility with indigenous melt and forging capability. Subject to annual on-site audit.
- **Tier-2 (Specialized Component Fabricator):** Machining and heat treatment subcontracted facility. Subject to semi-annual surveillance and 100% lot validation.
- **Tier-3 (Commercial Fasteners / COTS):** Commercial-off-the-shelf items requiring batch-level destructive test sampling before release.

### 4.2 First Article Inspection (AS9102 Protocol)
Prior to mass production of any newly tooled component:
1. Three (3) complete prototype units must undergo 100% dimensional CMM mapping against CAD master geometry.
2. Destructive microstructural grain-flow analysis must be conducted on sacrifice coupons.
3. FAI Dossier (Form 1: Part Number Accountability, Form 2: Product Accountability, Form 3: Characteristic Accountability) must be submitted and approved by the Lead QA Engineer.

---

## 5. Incoming Material Inspection & Acceptance Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Consignment Arrival & Quarantine Ingestion               │
│    - Verification of tamper-evident container seals         │
│    - Check Mill Test Certificates (EN 10204 Type 3.1/3.2)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 2. Positive Material Identification (PMI)                   │
│    - Handheld XRF / OES Spectrometry on 100% of billets     │
│    - Validate Ni, Cr, Mo, Ti, Al composition percentages    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 3. Non-Destructive Testing (NDT) Gate                       │
│    - Class-AA Ultrasonic Testing for internal voids / voids │
│    - Eddy Current / Magnetic Particle for surface seams     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 4. Mechanical & Metallurgical Laboratory Clearance          │
│    - Hardness testing, Room & Elevated Temp Tensile Yield   │
│    - Microstructure grain size ASTM E112 Grade 5 or finer   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        [Meets All Specs]             [Deviation Detected]
                │                             │
┌──────────────▼──────────────┐ ┌─────────────▼──────────────┐
│ 5. QA Approval & Release    │ │ 5. Non-Conformance / MRB   │
│    - Laser etched UID/QR    │ │    - Red Quarantine Tag    │
│    - Transfer to Production │ │    - RTV, Scrap, or Concess│
└─────────────────────────────┘ └────────────────────────────┘
```

---

## 6. Positive Material Identification (PMI) Acceptance Criteria

Every incoming heat number must be verified using calibrated X-ray Fluorescence (XRF) or Optical Emission Spectrometry (OES) against the master alloy matrix:

### Chemical Composition Band for Inconel 718 (AMS 5662):
- **Nickel (Ni):** 50.00% – 55.00%
- **Chromium (Cr):** 17.00% – 21.00%
- **Iron (Fe):** Balance (~17.00%)
- **Niobium (Nb) + Tantalum (Ta):** 4.75% – 5.50%
- **Molybdenum (Mo):** 2.80% – 3.30%
- **Titanium (Ti):** 0.65% – 1.15%
- **Aluminum (Al):** 0.20% – 0.80%
- **Carbon (C):** Max 0.08%

*Note: Any batch displaying Niobium content < 4.75% or Iron content > 21.00% must be flagged for immediate batch rejection.*

---

## 7. Material Review Board (MRB) & Non-Conformance Management

1. **Quarantine Protocol:** Any material or component exhibiting out-of-tolerance dimensions, surface microcracks, or spectral deviation must be immediately locked inside the Physical Material Quarantine Zone (Vault B-03).
2. **MRB Authority:** The MRB consists of the Lead Metallurgical Specialist, Chief QA Inspector, and Head of Procurement.
3. **Dispositions:**
   - **SCRAP:** Immediate rendering unserviceable through mechanical destruction under witness supervision.
   - **RETURN TO VENDOR (RTV):** Formal issuance of Defective Material Debit Note and supplier demerit scoring.
   - **REWORK / RE-HEAT-TREAT:** Permitted only for non-critical dimensional cleanup or approved solution annealing cycles.
   - **CONCESSION / USE AS-IS:** Prohibited for all primary rotating turbine or pressure-boundary components.

---

## 8. Air-Gapped Traceability & Data Integrity

- All Certificates of Conformity (CoC), mill heat logs, and spectrometer readouts must be ingested into the local air-gapped knowledge repository.
- Each document ingestion automatically computes a SHA-256 cryptographic hash to guarantee tamper-proof auditability during external ISO 9001 and defense oversight audits.
- No supplier documentation containing classified or ITAR-restricted component drawings may be transmitted across external or public network interfaces.
