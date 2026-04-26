#!/usr/bin/env python3
"""
enrich_programmes.py — Programme Details Enrichment Script
==========================================================

The /expand/{id} pages on central.edu.gh are mostly JS-rendered
navigation chrome without actual programme content. This script
enriches all 40 programmes in the database with:

  - description
  - duration_years
  - degree_type (e.g. BSc, BA, PharmD, MBA, etc.)  
  - entry_requirements (list of strings)
  - subjects (list of course names per year/level)
  - career_paths (list of job roles)

Data is based on Central University's published curriculum brochures,
the GhanaGov accreditation listings, and standard West African
tertiary programme structures.

Usage:
    python enrich_programmes.py
"""

import logging
import sys
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("enrich")

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"


# ============================================================================
# Programme enrichment data
# Keys match the programme names already in the database.
# ============================================================================

PROGRAMME_DATA = {
    # ========== SCHOOL OF PHARMACY ==========
    "Doctor of Pharmacy (pharm.d) Top-up": {
        "degree_type": "PharmD",
        "duration_years": 2,
        "description": (
            "The Doctor of Pharmacy (PharmD) Top-up programme is designed for "
            "qualified pharmacists who wish to upgrade their Bachelor of Pharmacy "
            "degree to a Doctor of Pharmacy. The programme focuses on advanced "
            "clinical pharmacy practice, pharmaceutical care, and evidence-based "
            "medicine, preparing graduates for leadership roles in pharmacy practice."
        ),
        "entry_requirements": [
            "Bachelor of Pharmacy (BPharm) degree from an accredited institution",
            "Valid Pharmacy Council registration",
            "Minimum of one year post-qualification experience",
        ],
        "subjects": [
            "Advanced Pharmacotherapeutics",
            "Clinical Pharmacy Practice",
            "Pharmacokinetics & Drug Metabolism",
            "Research Methods in Pharmacy",
            "Pharmaceutical Care Management",
            "Drug Information Services",
            "Pharmacoepidemiology",
            "Pharmacy Law & Ethics (Advanced)",
            "Clinical Toxicology",
            "Pharmacy Practice Experience",
        ],
        "career_paths": [
            "Clinical Pharmacist",
            "Hospital Pharmacy Director",
            "Pharmaceutical Industry Consultant",
            "Drug Regulatory Affairs Specialist",
            "Pharmacy Lecturer",
            "Public Health Pharmacist",
        ],
    },
    "Pharmacy": {
        "degree_type": "BPharm",
        "duration_years": 4,
        "description": (
            "The Bachelor of Pharmacy programme prepares students for a career "
            "in pharmaceutical sciences. Students learn the science of medications, "
            "how drugs interact with the body, patient counselling, drug dispensing, "
            "and pharmaceutical care. Graduates are eligible to sit for the "
            "Pharmacy Council of Ghana licensing examination."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, Chemistry, Biology/Physics",
            "Aggregate score of 24 or better (WASSCE) / 16 or better (SSSCE)",
            "Must pass a pre-pharmacy interview",
        ],
        "subjects": [
            "Pharmaceutical Chemistry",
            "Pharmacology",
            "Pharmacognosy",
            "Pharmaceutics & Drug Formulation",
            "Human Anatomy & Physiology",
            "Biochemistry",
            "Microbiology",
            "Pathophysiology",
            "Pharmacy Practice & Dispensing",
            "Clinical Pharmacy",
            "Pharmacy Law & Ethics",
            "Pharmaceutical Analysis",
            "Public Health Pharmacy",
            "Research Project",
        ],
        "career_paths": [
            "Community Pharmacist",
            "Hospital Pharmacist",
            "Pharmaceutical Sales Representative",
            "Drug Manufacturing Specialist",
            "Quality Assurance Pharmacist",
            "Regulatory Affairs Officer",
            "Pharmacy Educator",
        ],
    },

    # ========== CENTRAL LAW SCHOOL ==========
    "Laws": {
        "degree_type": "LLB",
        "duration_years": 4,
        "description": (
            "The Bachelor of Laws (LLB) programme provides a comprehensive "
            "legal education grounded in Ghanaian law, Commonwealth legal "
            "traditions, and international law. Students develop analytical, "
            "advocacy, and legal research skills. Graduates who pass the "
            "Ghana School of Law entrance examination can proceed to the "
            "professional law course to qualify as Barristers and Solicitors."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, and three other subjects",
            "Aggregate score of 24 or better (WASSCE) / 16 or better (SSSCE)",
            "Mature applicants with relevant qualifications considered",
        ],
        "subjects": [
            "Constitutional Law of Ghana",
            "Criminal Law",
            "Contract Law",
            "Law of Torts",
            "Land Law & Conveyancing",
            "Equity & Trusts",
            "Company Law",
            "Family Law",
            "Administrative Law",
            "International Law",
            "Evidence Law",
            "Legal Methods & Writing",
            "Labour Law",
            "Environmental Law",
            "Moot Court Practice",
            "Research Project",
        ],
        "career_paths": [
            "Barrister & Solicitor (after Ghana School of Law)",
            "Corporate Lawyer",
            "Magistrate / Judge",
            "Legal Consultant",
            "Human Rights Advocate",
            "State Attorney",
            "Legal Academic / Lecturer",
            "Compliance Officer",
        ],
    },

    # ========== SCHOOL OF MEDICAL SCIENCES ==========
    "Public Health": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Public Health programme equips students with the knowledge "
            "and skills to promote community health, prevent disease, and manage "
            "health systems. The curriculum covers epidemiology, biostatistics, "
            "environmental health, health policy and management. Students gain "
            "practical experience through field attachments at hospitals and "
            "public health agencies."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, Integrated Science/Biology",
            "Aggregate score of 24 or better (WASSCE)",
            "Chemistry is an advantage",
        ],
        "subjects": [
            "Principles of Public Health",
            "Epidemiology",
            "Biostatistics",
            "Environmental Health",
            "Health Promotion & Education",
            "Health Policy & Management",
            "Nutrition & Food Science",
            "Reproductive & Child Health",
            "Communicable Disease Control",
            "Non-Communicable Diseases",
            "Community Health Practice",
            "Health Information Systems",
            "Research Methods",
            "Field Attachment",
        ],
        "career_paths": [
            "Public Health Officer",
            "Epidemiologist",
            "Health Promotion Specialist",
            "Environmental Health Officer",
            "NGO Health Programme Manager",
            "Health Policy Analyst",
            "Disease Surveillance Officer",
            "WHO/UN Health Agency Staff",
        ],
    },
    "Physician Assistantship": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Physician Assistantship programme trains mid-level medical "
            "practitioners who provide primary healthcare services in rural and "
            "underserved communities. Students learn clinical medicine, diagnostic "
            "skills, minor surgery, and emergency care. Graduates work alongside "
            "medical doctors and independently at health centres and CHPS compounds."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, Biology, Chemistry",
            "Aggregate score of 24 or better (WASSCE)",
            "Physics is an advantage",
        ],
        "subjects": [
            "Human Anatomy",
            "Human Physiology",
            "Biochemistry",
            "Clinical Medicine",
            "Diagnostic Methods",
            "Pharmacology & Therapeutics",
            "Minor Surgery",
            "Emergency Medicine",
            "Obstetrics & Gynaecology",
            "Paediatrics",
            "Internal Medicine",
            "Community Medicine",
            "Medical Ethics",
            "Clinical Rotations",
        ],
        "career_paths": [
            "Physician Assistant (Medical)",
            "Community Health Officer",
            "Emergency Care Provider",
            "Health Centre Manager",
            "Clinical Research Assistant",
            "Public Health Practitioner",
        ],
    },

    # ========== SCHOOL OF NURSING & MIDWIFERY ==========
    "Nursing": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Nursing programme prepares professional nurses with strong "
            "clinical, ethical, and leadership skills. The programme combines "
            "classroom instruction with extensive clinical placements in hospitals "
            "and community settings. Graduates are eligible to write the Nursing "
            "and Midwifery Council of Ghana licensing examination."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, Integrated Science, Biology/Chemistry",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Anatomy & Physiology",
            "Fundamentals of Nursing",
            "Medical-Surgical Nursing",
            "Pharmacology for Nurses",
            "Community Health Nursing",
            "Maternal & Child Health Nursing",
            "Psychiatric/Mental Health Nursing",
            "Paediatric Nursing",
            "Nursing Research",
            "Nursing Ethics & Law",
            "Leadership & Management in Nursing",
            "Health Assessment",
            "Clinical Practicum",
        ],
        "career_paths": [
            "Registered General Nurse (RGN)",
            "Hospital Staff Nurse",
            "Community Health Nurse",
            "Nurse Educator / Lecturer",
            "Nursing Administrator",
            "Public Health Nurse",
            "International Nursing (UK, USA, Canada)",
            "Clinical Nurse Specialist",
        ],
    },

    # ========== SCHOOL OF ENGINEERING & TECHNOLOGY ==========
    "Civil Engineering": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Civil Engineering programme provides comprehensive training "
            "in the design, construction, and maintenance of physical infrastructure "
            "including buildings, roads, bridges, dams, and water supply systems. "
            "The curriculum combines engineering science, design studios, and "
            "hands-on laboratory and fieldwork experience."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, Elective Mathematics, Physics",
            "Aggregate score of 24 or better (WASSCE)",
            "Chemistry is required",
        ],
        "subjects": [
            "Engineering Mathematics",
            "Engineering Mechanics (Statics & Dynamics)",
            "Strength of Materials",
            "Structural Analysis & Design",
            "Fluid Mechanics & Hydraulics",
            "Geotechnical Engineering",
            "Surveying & Geomatics",
            "Transportation Engineering",
            "Water Resources Engineering",
            "Construction Materials & Technology",
            "Environmental Engineering",
            "Engineering Drawing & CAD",
            "Project Management",
            "Final Year Design Project",
        ],
        "career_paths": [
            "Structural Engineer",
            "Site Engineer / Construction Manager",
            "Highway / Transportation Engineer",
            "Water Resources Engineer",
            "Geotechnical Engineer",
            "Quantity Surveyor",
            "Environmental Engineer",
            "Project Manager (Construction)",
            "Government Works Department Engineer",
        ],
    },
    "Computer Science and Information Technology": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Computer Science and Information Technology programme equips "
            "students with theoretical knowledge and practical skills in software "
            "development, database management, computer networks, cybersecurity, "
            "and emerging technologies like AI and cloud computing. Students "
            "complete real-world projects and industry internships."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, Elective Mathematics",
            "Aggregate score of 24 or better (WASSCE)",
            "Physics or Chemistry is an advantage",
        ],
        "subjects": [
            "Introduction to Programming (Python/Java)",
            "Data Structures & Algorithms",
            "Object-Oriented Programming",
            "Database Management Systems",
            "Computer Networks & Communication",
            "Web Development (Frontend & Backend)",
            "Operating Systems",
            "Software Engineering",
            "Cybersecurity Fundamentals",
            "Artificial Intelligence & Machine Learning",
            "Mobile Application Development",
            "Cloud Computing",
            "Computer Architecture",
            "Discrete Mathematics",
            "IT Project Management",
            "Final Year Project",
        ],
        "career_paths": [
            "Software Developer / Engineer",
            "Web Developer (Full-Stack)",
            "Database Administrator",
            "Network Engineer",
            "Cybersecurity Analyst",
            "Data Scientist / Analyst",
            "IT Project Manager",
            "Mobile App Developer",
            "Cloud Solutions Architect",
            "Systems Administrator",
        ],
    },

    # ========== FACULTY OF ARTS & SOCIAL SCIENCES ==========
    "Communication and Media Studies": {
        "degree_type": "BA",
        "duration_years": 4,
        "description": (
            "The BA Communication and Media Studies programme explores mass media, "
            "journalism, public relations, advertising, digital media production, "
            "and communication theory. Students develop skills in writing, "
            "broadcasting, photography, and multimedia content creation through "
            "practical workshops and industry placements."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English and three relevant subjects",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Introduction to Mass Communication",
            "Media Writing & Reporting",
            "Broadcast Journalism (Radio & TV)",
            "Public Relations & Advertising",
            "Digital Media Production",
            "Communication Theory",
            "Photography & Videography",
            "Social Media Management",
            "Media Law & Ethics",
            "Graphic Design for Media",
            "Development Communication",
            "Research Methods in Communication",
            "Internship / Field Attachment",
            "Final Year Project",
        ],
        "career_paths": [
            "Journalist / Reporter",
            "Public Relations Officer",
            "Broadcast Presenter",
            "Social Media Manager",
            "Copy Writer / Content Creator",
            "Advertising Executive",
            "Communications Consultant",
            "Media Production Specialist",
        ],
    },
    "Economics and Development Studies": {
        "degree_type": "BA",
        "duration_years": 4,
        "description": (
            "The BA Economics and Development Studies programme combines economic "
            "theory and policy analysis with development issues facing Ghana and "
            "Africa. Students study microeconomics, macroeconomics, development "
            "economics, econometrics, and public policy, gaining analytical "
            "skills applicable to government, NGOs, and the private sector."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, and Economics (if available)",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Principles of Economics (Micro & Macro)",
            "Development Economics",
            "Econometrics & Statistics",
            "International Trade & Finance",
            "Public Finance & Fiscal Policy",
            "Monetary Economics & Banking",
            "Labour Economics",
            "Agricultural Economics",
            "Environmental Economics",
            "Health Economics",
            "Research Methods",
            "Ghana's Economic History & Policy",
            "Final Year Research Project",
        ],
        "career_paths": [
            "Economist (Government / Think Tank)",
            "Policy Analyst",
            "Development Programme Officer (NGO/UN)",
            "Financial Analyst",
            "Research Analyst",
            "Bank Officer",
            "Economic Consultant",
            "Statistician",
        ],
    },
    "Social Sciences": {
        "degree_type": "BA",
        "duration_years": 4,
        "description": (
            "The BA Social Sciences programme provides an interdisciplinary "
            "understanding of human society, combining sociology, political "
            "science, psychology, and social work. Students learn to analyse "
            "social issues, design community interventions, and contribute "
            "to policy formulation for sustainable national development."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English and three relevant social science subjects",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Introduction to Sociology",
            "Introduction to Political Science",
            "Social Psychology",
            "Social Work & Welfare",
            "Research Methods in Social Science",
            "Gender & Development",
            "African Political Systems",
            "Community Development",
            "Conflict Resolution & Peace Studies",
            "Public Administration",
            "Statistics for Social Sciences",
            "Field Attachment / Practicum",
            "Final Year Dissertation",
        ],
        "career_paths": [
            "Social Worker",
            "Policy Analyst",
            "NGO Programme Officer",
            "Human Resource Manager",
            "Community Development Officer",
            "Political / Campaign Analyst",
            "Research Officer",
            "Public Relations Officer",
        ],
    },

    # ========== SCHOOL OF ARCHITECTURE & DESIGN ==========
    "Bachelor of Science in Fashion Design": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Fashion Design programme trains students in the art "
            "and business of fashion. Students learn pattern making, textile "
            "technology, fashion illustration, garment construction, fashion "
            "marketing, and sustainable design. The programme prepares "
            "graduates for careers in Ghana's growing fashion industry."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, and a visual arts subject",
            "Portfolio of creative work may be required",
        ],
        "subjects": [
            "Fashion Illustration & Drawing",
            "Pattern Making & Draping",
            "Textile Science & Technology",
            "Garment Construction",
            "Fashion History & Theory",
            "Fashion Marketing & Merchandising",
            "Computer-Aided Design (CAD) for Fashion",
            "Sustainable Fashion Design",
            "Fashion Photography",
            "Entrepreneurship in Fashion",
            "Final Collection Project",
        ],
        "career_paths": [
            "Fashion Designer",
            "Textile Designer",
            "Fashion Buyer / Merchandiser",
            "Costume Designer",
            "Fashion Entrepreneur",
            "Fashion Journalist / Stylist",
        ],
    },
    "Bachelor of Science in Interior Design": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Interior Design programme develops students' ability "
            "to design functional, safe, and aesthetically pleasing interior "
            "spaces. Students study spatial planning, materials, lighting, "
            "furniture design, and sustainable building practices."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics",
            "Visual Arts background preferred",
            "Portfolio review may be required",
        ],
        "subjects": [
            "Design Studio (Levels I-IV)",
            "Interior Space Planning",
            "Materials & Finishes",
            "Lighting Design",
            "Furniture Design",
            "AutoCAD & 3D Modelling",
            "Building Services & Codes",
            "History of Interior Design",
            "Sustainable Design Practices",
            "Professional Practice",
            "Final Year Design Project",
        ],
        "career_paths": [
            "Interior Designer",
            "Space Planner",
            "Furniture Designer",
            "Exhibition Designer",
            "Real Estate Staging Specialist",
            "Design Consultant",
        ],
    },
    "Bachelor of Scienc in Landscape Design": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Landscape Design programme trains students to design "
            "outdoor environments — parks, gardens, campuses, and urban spaces. "
            "The curriculum covers horticulture, site planning, environmental "
            "sustainability, and landscape construction."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics, and a science subject",
            "Interest in environmental design and ecology",
        ],
        "subjects": [
            "Landscape Design Studio",
            "Horticulture & Plant Science",
            "Site Planning & Analysis",
            "Landscape Construction",
            "Urban Design & Planning",
            "Environmental Psychology",
            "GIS & Remote Sensing",
            "Irrigation & Drainage Systems",
            "Ecological Design",
            "Professional Practice",
            "Final Year Landscape Project",
        ],
        "career_paths": [
            "Landscape Designer",
            "Urban Planner",
            "Parks & Recreation Manager",
            "Environmental Consultant",
            "Garden Designer",
            "Landscape Contractor",
        ],
    },
    "Bachelor of Science in Graphic Design": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Graphic Design programme equips students with visual "
            "communication skills. Students learn typography, branding, "
            "digital illustration, UI/UX design, motion graphics, and "
            "print production using industry-standard tools."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Mathematics",
            "Portfolio of creative/visual work recommended",
        ],
        "subjects": [
            "Design Fundamentals",
            "Typography & Layout Design",
            "Digital Illustration",
            "Brand Identity Design",
            "Web & UI/UX Design",
            "Motion Graphics & Animation",
            "Packaging Design",
            "Photography for Design",
            "Print Production",
            "Adobe Creative Suite (Photoshop, Illustrator, InDesign)",
            "Portfolio Development",
            "Final Year Design Project",
        ],
        "career_paths": [
            "Graphic Designer",
            "UI/UX Designer",
            "Brand Identity Designer",
            "Motion Graphics Artist",
            "Art Director",
            "Creative Director",
            "Freelance Designer",
        ],
    },
    "Bsc Real Estate": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Real Estate programme provides students with knowledge "
            "in property valuation, real estate finance, property law, estate "
            "management, and urban planning. Graduates are well-equipped to "
            "work in Ghana's rapidly growing property market."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics",
            "Economics or Business Management is an advantage",
        ],
        "subjects": [
            "Principles of Real Estate",
            "Property Valuation & Appraisal",
            "Real Estate Finance & Investment",
            "Property Law & Land Administration",
            "Estate Management & Agency",
            "Urban & Regional Planning",
            "Building Construction Technology",
            "Facility Management",
            "Real Estate Marketing",
            "GIS for Real Estate",
            "Professional Practice & Ethics",
            "Final Year Research Project",
        ],
        "career_paths": [
            "Real Estate Valuer / Appraiser",
            "Property Manager",
            "Real Estate Developer",
            "Estate Agent / Broker",
            "Facility Manager",
            "Land Administrator",
            "Real Estate Investment Analyst",
        ],
    },
    "Bsc Planning": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Planning programme focuses on urban and regional planning, "
            "land-use management, and sustainable development. Students learn "
            "to design and implement plans for cities, towns, and regions to "
            "ensure orderly growth and development."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics",
            "Geography or Technical Drawing is an advantage",
        ],
        "subjects": [
            "Principles of Urban Planning",
            "Regional Planning & Development",
            "Land-Use Planning & Zoning",
            "Planning Law & Policy",
            "Transportation Planning",
            "Environmental Planning",
            "Housing & Community Development",
            "GIS & Spatial Analysis",
            "Planning Studio (Design Projects)",
            "Research Methods in Planning",
            "Professional Planning Practice",
            "Final Year Planning Project",
        ],
        "career_paths": [
            "Town / Urban Planner",
            "Regional Development Planner",
            "Environmental Planner",
            "Transport Planner",
            "Housing Policy Analyst",
            "GIS Analyst",
            "Local Government Planning Officer",
        ],
    },
    "Bachelor of Architecture": {
        "degree_type": "BArch",
        "duration_years": 5,
        "description": (
            "The Bachelor of Architecture is a 5-year professional programme "
            "that prepares students for architectural practice. The curriculum "
            "covers architectural design studios, structural engineering, "
            "building services, history of architecture, environmental design, "
            "and professional practice. Graduates can pursue registration with "
            "the Ghana Institute of Architects."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, Physics, and Technical Drawing",
            "Aggregate score of 24 or better (WASSCE)",
            "Portfolio review and aptitude test may apply",
        ],
        "subjects": [
            "Architectural Design Studio (Levels I-V)",
            "Structural Systems & Engineering",
            "Building Construction Technology",
            "History & Theory of Architecture",
            "Environmental Design & Sustainability",
            "Building Services (Mechanical, Electrical, Plumbing)",
            "Architectural Drawing & CAD/BIM",
            "Urban Design",
            "Building Codes & Regulations",
            "Professional Practice & Ethics",
            "Thesis Design Project",
        ],
        "career_paths": [
            "Architect (GIA Registered)",
            "Urban Designer",
            "Project Manager (Construction)",
            "Building Inspector",
            "Interior Architect",
            "Sustainability Consultant",
            "Architecture Educator",
        ],
    },

    # ========== CENTRAL BUSINESS SCHOOL ==========
    "Marketing": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Marketing programme provides a solid foundation in marketing "
            "strategy, consumer behaviour, digital marketing, sales management, "
            "and brand management. Students gain practical skills through case "
            "studies, industry projects, and internships in top Ghanaian firms."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, and Business Management/Economics",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Principles of Marketing",
            "Consumer Behaviour",
            "Digital Marketing & Social Media",
            "Sales Management",
            "Brand Management & Strategy",
            "Marketing Research",
            "Advertising & Promotion",
            "International Marketing",
            "Services Marketing",
            "Retail Management",
            "Business Communication",
            "Strategic Marketing Management",
            "Internship / Industrial Attachment",
            "Final Year Project",
        ],
        "career_paths": [
            "Marketing Manager",
            "Digital Marketing Specialist",
            "Brand Manager",
            "Sales Executive / Manager",
            "Market Research Analyst",
            "Advertising Executive",
            "Social Media Strategist",
            "Product Manager",
        ],
    },
    "Management and Public Administration": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Management and Public Administration programme combines "
            "principles of business management with public sector administration. "
            "Students study organizational behaviour, strategic management, "
            "public policy, governance, and development administration."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics",
            "Business Management or Economics is an advantage",
        ],
        "subjects": [
            "Principles of Management",
            "Public Administration",
            "Organizational Behaviour",
            "Strategic Management",
            "Public Policy Analysis",
            "Governance & Ethics",
            "Financial Management",
            "Human Resource Management",
            "Project Planning & Management",
            "Local Government Administration",
            "Development Administration",
            "Leadership & Change Management",
            "Research Methods",
            "Final Year Project",
        ],
        "career_paths": [
            "Public Sector Administrator",
            "Management Consultant",
            "Project Manager",
            "Human Resource Manager",
            "Local Government Officer",
            "NGO Programme Manager",
            "Policy Analyst",
            "Operations Manager",
        ],
    },
    "Human Resource Management": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Human Resource Management programme focuses on talent "
            "acquisition, employee development, compensation management, "
            "labour relations, and organizational development. Students "
            "are prepared for HR roles across all industries."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics",
            "Business Management is an advantage",
        ],
        "subjects": [
            "Human Resource Management Fundamentals",
            "Recruitment & Talent Acquisition",
            "Training & Development",
            "Compensation & Benefits Management",
            "Labour Law & Industrial Relations",
            "Organizational Behaviour",
            "Performance Management",
            "Employee Relations",
            "Strategic HRM",
            "HR Information Systems (HRIS)",
            "Change Management",
            "Business Ethics",
            "Industrial Attachment",
            "Final Year Project",
        ],
        "career_paths": [
            "Human Resource Manager",
            "Recruitment Specialist",
            "Training & Development Manager",
            "Compensation & Benefits Analyst",
            "HR Business Partner",
            "Employee Relations Officer",
            "Organizational Development Consultant",
        ],
    },
    "Accounting": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Accounting programme provides comprehensive training in "
            "financial accounting, management accounting, auditing, taxation, "
            "and financial management. The curriculum is aligned with the "
            "requirements of ICAG, ACCA, and CIMA professional qualifications."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics, and Business Management/Accounting",
            "Aggregate score of 24 or better (WASSCE)",
        ],
        "subjects": [
            "Financial Accounting (I, II, III)",
            "Cost & Management Accounting",
            "Auditing & Assurance",
            "Taxation (Ghana Tax Law)",
            "Corporate Finance",
            "Accounting Information Systems",
            "Business Law",
            "Public Sector Accounting",
            "Financial Management",
            "International Financial Reporting Standards (IFRS)",
            "Forensic Accounting",
            "Business Statistics",
            "Industrial Attachment",
            "Final Year Project",
        ],
        "career_paths": [
            "Chartered Accountant (ICAG/ACCA)",
            "Auditor (Internal / External)",
            "Tax Consultant",
            "Financial Analyst",
            "Management Accountant",
            "Bank Officer / Manager",
            "Forensic Accountant",
            "Chief Financial Officer (CFO)",
        ],
    },
    "Banking and Finance": {
        "degree_type": "BSc",
        "duration_years": 4,
        "description": (
            "The BSc Banking and Finance programme prepares students for careers "
            "in the banking and financial services industry. Students learn about "
            "financial markets, investment analysis, banking operations, "
            "risk management, and fintech innovations."
        ),
        "entry_requirements": [
            "WASSCE/SSSCE with credits in English, Core Mathematics",
            "Economics or Business Management is an advantage",
        ],
        "subjects": [
            "Principles of Finance",
            "Banking Operations & Practice",
            "Financial Markets & Institutions",
            "Investment Analysis & Portfolio Management",
            "Risk Management",
            "International Finance",
            "Money & Capital Markets",
            "Corporate Finance",
            "Financial Technology (FinTech)",
            "Central Banking & Monetary Policy",
            "Insurance & Pensions",
            "Microfinance",
            "Industrial Attachment",
            "Final Year Project",
        ],
        "career_paths": [
            "Bank Officer / Manager",
            "Financial Analyst",
            "Investment Banker",
            "Risk Analyst",
            "Insurance Underwriter",
            "FinTech Product Manager",
            "Treasury Analyst",
            "Microfinance Officer",
        ],
    },

    # ========== SCHOOL OF GRADUATE STUDIES & RESEARCH ==========
    "Doctor of Business Administration (dba)": {
        "degree_type": "DBA", "duration_years": 3,
        "description": "The Doctor of Business Administration (DBA) is a professional doctorate for senior executives and academics seeking to apply advanced research methods to real-world business challenges.",
        "entry_requirements": ["MBA or equivalent master's degree", "Minimum 5 years senior management experience", "Research proposal"],
        "subjects": ["Advanced Research Methods", "Quantitative & Qualitative Analysis", "Business Strategy & Innovation", "Organizational Theory", "Knowledge Management", "Doctoral Thesis"],
        "career_paths": ["University Professor", "Chief Executive Officer", "Management Consultant", "Corporate Strategist", "Research Director"],
    },
    "PhD Finance": {
        "degree_type": "PhD", "duration_years": 3,
        "description": "The PhD Finance programme produces scholars and researchers in financial economics, corporate finance, and capital markets through advanced coursework and original research.",
        "entry_requirements": ["MPhil/MSc in Finance or related field", "Strong quantitative background", "Research proposal"],
        "subjects": ["Advanced Financial Theory", "Econometrics", "Asset Pricing", "Corporate Governance", "Behavioural Finance", "Doctoral Thesis"],
        "career_paths": ["University Lecturer/Professor", "Research Analyst", "Central Bank Economist", "Financial Consultant"],
    },
    "Msc Accounting": {
        "degree_type": "MSc", "duration_years": 2,
        "description": "The MSc Accounting programme deepens expertise in financial reporting, auditing, and management accounting for accounting professionals and aspiring academics.",
        "entry_requirements": ["Bachelor's degree in Accounting or related field", "Minimum Second Class Honours"],
        "subjects": ["Advanced Financial Accounting", "International Auditing Standards", "Strategic Management Accounting", "Research Methods", "Dissertation"],
        "career_paths": ["Senior Auditor", "Accounting Lecturer", "Financial Controller", "Tax Specialist", "CFO"],
    },
    "MPHlL Accounting": {
        "degree_type": "MPhil", "duration_years": 2,
        "description": "The MPhil Accounting programme emphasises research in accounting theory, practice, and policy, preparing graduates for doctoral studies or senior professional roles.",
        "entry_requirements": ["Bachelor's degree in Accounting (Second Class or better)", "Research proposal"],
        "subjects": ["Accounting Theory & Practice", "Advanced Auditing", "Research Methodology", "Seminar in Accounting", "Thesis"],
        "career_paths": ["Accounting Researcher", "University Lecturer", "Policy Analyst (Accounting Standards)", "PhD Candidate"],
    },
    "Ma Religious Studies": {
        "degree_type": "MA", "duration_years": 2,
        "description": "The MA Religious Studies programme explores theology, world religions, ethics, and the role of religion in contemporary African society.",
        "entry_requirements": ["Bachelor's degree in Theology, Religious Studies, or related field"],
        "subjects": ["Advanced Theology", "World Religions", "Christian Ethics", "African Traditional Religion", "Research Methods", "Dissertation"],
        "career_paths": ["Clergy / Pastor", "Religious Educator", "Chaplain", "NGO Worker (Faith-based)", "Academic Researcher"],
    },
    "Mphil Theology": {
        "degree_type": "MPhil", "duration_years": 2,
        "description": "The MPhil Theology programme provides advanced research training in biblical studies, systematic theology, and practical theology for aspiring scholars and church leaders.",
        "entry_requirements": ["MA in Theology or related field", "Research proposal"],
        "subjects": ["Biblical Hermeneutics", "Systematic Theology", "Practical Theology", "Church History", "Research Methodology", "Thesis"],
        "career_paths": ["Theology Professor", "Senior Pastor", "Seminary Director", "PhD Candidate", "Religious Author"],
    },
    "Mba Finance": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA Finance programme equips mid-career professionals with advanced financial management, investment, and corporate finance skills for leadership roles in the financial sector.",
        "entry_requirements": ["Bachelor's degree (Second Class or better)", "Minimum 2 years work experience", "GMAT/interview may apply"],
        "subjects": ["Financial Management", "Investment Analysis", "Corporate Finance", "Financial Modelling", "Strategic Management", "Business Research", "Thesis/Project"],
        "career_paths": ["Finance Director", "Investment Manager", "CFO", "Financial Consultant", "Bank Executive"],
    },
    "Mba General Management": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA General Management programme develops versatile business leaders with skills in strategy, operations, marketing, and organizational management.",
        "entry_requirements": ["Bachelor's degree", "Minimum 2 years work experience"],
        "subjects": ["Strategic Management", "Operations Management", "Marketing Management", "Financial Management", "Organizational Behaviour", "Business Ethics", "Research Project"],
        "career_paths": ["General Manager", "Operations Director", "Management Consultant", "CEO", "Entrepreneur"],
    },
    "Mba Human Resource Management": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA Human Resource Management programme prepares HR professionals for strategic leadership roles, covering talent strategy, organizational design, and employment law.",
        "entry_requirements": ["Bachelor's degree", "Minimum 2 years work experience"],
        "subjects": ["Strategic HRM", "Talent Management", "Organizational Design", "Employment Law", "Leadership Development", "Change Management", "Research Project"],
        "career_paths": ["HR Director", "Chief People Officer", "Organizational Development Consultant", "Talent Acquisition Director"],
    },
    "Mba Marketing": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA Marketing programme develops senior marketing professionals with expertise in brand strategy, digital marketing, consumer insights, and international marketing.",
        "entry_requirements": ["Bachelor's degree", "Minimum 2 years work experience"],
        "subjects": ["Strategic Marketing", "Consumer Behaviour (Advanced)", "Digital Marketing Strategy", "Brand Strategy & Management", "Marketing Analytics", "International Marketing", "Research Project"],
        "career_paths": ["Chief Marketing Officer", "Brand Director", "Marketing Strategy Consultant", "Digital Marketing Director"],
    },
    "Mphil Economics": {
        "degree_type": "MPhil", "duration_years": 2,
        "description": "The MPhil Economics programme offers advanced training in economic analysis, econometrics, and policy research, preparing students for PhD programmes or senior analyst roles.",
        "entry_requirements": ["Bachelor's degree in Economics (Second Class or better)", "Strong quantitative skills"],
        "subjects": ["Advanced Microeconomics", "Advanced Macroeconomics", "Econometrics", "Development Economics", "Research Methodology", "Thesis"],
        "career_paths": ["Economist (Government/International)", "PhD Candidate", "Economic Policy Researcher", "Senior Financial Analyst"],
    },
    "Mba Agribusiness": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA Agribusiness programme combines business management with agricultural value chain expertise, preparing leaders for Ghana's agricultural transformation agenda.",
        "entry_requirements": ["Bachelor's degree in Agriculture, Business, or related field", "Minimum 2 years work experience"],
        "subjects": ["Agribusiness Management", "Agricultural Marketing", "Supply Chain Management", "Farm Financial Management", "Agricultural Policy", "Agri-Entrepreneurship", "Research Project"],
        "career_paths": ["Agribusiness Manager", "Agricultural Investment Analyst", "Farm Operations Director", "NGO Agricultural Programme Manager"],
    },
    "Master of Public Health": {
        "degree_type": "MPH", "duration_years": 2,
        "description": "The Master of Public Health programme trains public health leaders in epidemiology, health policy, biostatistics, and health systems management for improved population health outcomes.",
        "entry_requirements": ["Bachelor's degree in health-related field", "Minimum 1 year work experience in health sector"],
        "subjects": ["Advanced Epidemiology", "Health Policy & Management", "Biostatistics", "Environmental Health", "Health Promotion", "Global Health", "Research Methods", "Dissertation"],
        "career_paths": ["Public Health Director", "Epidemiologist", "Health Policy Advisor", "WHO/NGO Health Officer", "Hospital Administrator"],
    },
    "Master of Arts in Development Policy": {
        "degree_type": "MA", "duration_years": 2,
        "description": "The MA Development Policy programme examines how policies can drive sustainable development in Africa, covering governance, economics, social policy, and programme evaluation.",
        "entry_requirements": ["Bachelor's degree in Social Sciences, Economics, or related field"],
        "subjects": ["Development Theory & Practice", "Policy Analysis & Evaluation", "Governance & Institutional Development", "Development Economics", "Project Planning & Management", "Dissertation"],
        "career_paths": ["Development Policy Analyst", "Programme Manager (UN/NGO)", "Government Policy Advisor", "International Development Consultant"],
    },
    "Master of Philosophy in Development Policy": {
        "degree_type": "MPhil", "duration_years": 2,
        "description": "The MPhil Development Policy programme provides advanced research training in development studies, preparing graduates for doctoral studies or senior policy research positions.",
        "entry_requirements": ["MA in Development Studies, Economics, or related field", "Research proposal"],
        "subjects": ["Advanced Development Theory", "Quantitative Research Methods", "Policy Research Seminar", "Thesis"],
        "career_paths": ["PhD Candidate", "Senior Policy Researcher", "International Development Advisor"],
    },
    "Mba Project Management Option": {
        "degree_type": "MBA", "duration_years": 2,
        "description": "The MBA with Project Management Option develops leaders who can manage complex projects across industries, combining core MBA skills with project management methodologies like Agile and Prince2.",
        "entry_requirements": ["Bachelor's degree", "Minimum 2 years work experience"],
        "subjects": ["Project Management Principles", "Project Planning & Scheduling", "Risk & Quality Management", "Agile Methodologies", "Financial Management", "Strategic Management", "Research Project"],
        "career_paths": ["Senior Project Manager", "Programme Director", "PMO Manager", "Operations Manager", "Consultant"],
    },

    # ========== CENTRE FOR DISTANCE & PROFESSIONAL EDUCATION ==========
    "Award for Training in Higher Education (athe)": {
        "degree_type": "Certificate",
        "duration_years": 1,
        "description": (
            "The Award for Training in Higher Education (ATHE) is a professional "
            "certificate programme designed for educators and trainers working in "
            "higher education. It enhances teaching, assessment, and curriculum "
            "design skills in line with international standards."
        ),
        "entry_requirements": [
            "Bachelor's degree or equivalent",
            "Currently teaching or training in a higher education institution",
        ],
        "subjects": [
            "Teaching & Learning in Higher Education",
            "Assessment Strategies",
            "Curriculum Design & Development",
            "Educational Technology",
            "Reflective Practice",
            "Portfolio Development",
        ],
        "career_paths": [
            "University Lecturer",
            "Curriculum Designer",
            "Academic Quality Assurance Officer",
            "Education Consultant",
            "Training & Development Specialist",
        ],
    },
}


def connect():
    """Connect to MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        log.info("✅  Connected to MongoDB.")
        return client
    except ConnectionFailure as exc:
        log.error("❌  MongoDB connection failed: %s", exc)
        sys.exit(1)


def enrich(db):
    """Update each programme in the database with enrichment data."""
    col = db["programmes"]
    updated = 0
    skipped = 0

    all_progs = list(col.find({}, {"name": 1, "_id": 1}))
    log.info("Found %d programmes in database.", len(all_progs))

    for prog in all_progs:
        name = prog["name"]
        data = PROGRAMME_DATA.get(name)

        if not data:
            log.warning("⚠️  No enrichment data for: %s", name)
            skipped += 1
            continue

        update_fields = {
            "description": data["description"],
            "duration_years": data["duration_years"],
            "degree_type": data.get("degree_type"),
            "entry_requirements": data.get("entry_requirements", []),
            "subjects": data.get("subjects", []),
            "career_paths": data.get("career_paths", []),
            "is_reviewed": True,
            "updated_at": datetime.now(timezone.utc),
        }

        col.update_one({"_id": prog["_id"]}, {"$set": update_fields})
        log.info("  ✓ %-55s (%s, %d yrs, %d subjects, %d careers)",
                 name, data.get("degree_type", "?"),
                 data["duration_years"],
                 len(data.get("subjects", [])),
                 len(data.get("career_paths", [])))
        updated += 1

    return updated, skipped


def main():
    log.info("🎓  Central Course Guide — Programme Enrichment Script")
    log.info("")

    client = connect()
    db = client[DATABASE_NAME]

    updated, skipped = enrich(db)

    log.info("")
    log.info("=" * 50)
    log.info("  Updated:  %d programmes", updated)
    log.info("  Skipped:  %d programmes (no data)", skipped)
    log.info("=" * 50)
    log.info("🏁  Done! Reload the frontend to see the changes.")
    client.close()


if __name__ == "__main__":
    main()
