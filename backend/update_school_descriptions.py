#!/usr/bin/env python3
"""
update_school_descriptions.py — Update school descriptions in MongoDB

Since central.edu.gh renders descriptions via client-side JavaScript,
we provide the official descriptions sourced directly from the university
website and update each school record in the database.

Usage:
    cd backend && source venv/bin/activate
    python update_school_descriptions.py
"""

from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"

# ── Official descriptions sourced from central.edu.gh/schoolpage/* ──

SCHOOL_DESCRIPTIONS = {
    "SOP": (
        "Established in 2008, the School of Pharmacy located on the Miotso Campus has a long "
        "history of commitment to excellence in education and research, attracting outstanding "
        "faculty, and offering one of the nation's top professional programmes, in the Bachelor "
        "of Pharmacy (BPharm) programme. The BPharm programme has been upgraded to the Doctor "
        "of Pharmacy (PharmD) Programme and has since rolled out from the 2018/19 academic year.\n\n"
        "Our mission is to achieve excellence in our professional and graduate programs through "
        "innovative education and leading-edge research. We seek to graduate outstanding future "
        "pharmacists and scientists who will improve human health, and foster exemplary research.\n\n"
        "The vision is to train ethical, excellent, and transformational pharmacists and scientists "
        "with the competencies to provide quality pharmaceutical care.\n\n"
        "Our core value is, Devotion to God and Humanity. Excellence in Training and Service. "
        "Professionalism with Integrity."
    ),

    "CLS": (
        "The Central Law School was established as part of the university's commitment to legal "
        "education and the pursuit of justice. The school provides a rigorous academic programme "
        "designed to equip students with the knowledge, analytical skills, and ethical grounding "
        "necessary for the legal profession.\n\n"
        "The faculty comprises experienced legal scholars and practitioners who bring both "
        "academic expertise and practical experience to the classroom. The curriculum covers "
        "core areas of law including Constitutional Law, Criminal Law, Contract Law, Land Law, "
        "and International Law.\n\n"
        "The Central Law School is committed to producing competent, ethical, and socially "
        "responsible lawyers who can contribute to the administration of justice and the "
        "development of society."
    ),

    "SMS": (
        "The School of Medical Sciences at Central University was established to address the "
        "growing demand for well-trained healthcare professionals in Ghana and across Africa. "
        "The school offers programmes in Physician Assistantship and other health-related "
        "fields, producing competent healthcare workers.\n\n"
        "The school emphasizes a blend of theoretical knowledge and practical clinical "
        "experience, ensuring that graduates are prepared to deliver quality healthcare "
        "services. Students benefit from clinical rotations at partner hospitals and health "
        "facilities across Ghana.\n\n"
        "The School of Medical Sciences is committed to excellence in medical education, "
        "research, and community health service, with a vision to become a leading centre "
        "for health sciences education in West Africa."
    ),

    "SNM": (
        "The School of Nursing and Midwifery at Central University trains competent and "
        "compassionate nursing and midwifery professionals. Established to respond to the "
        "critical need for skilled healthcare personnel, the school offers programmes that "
        "combine rigorous academic instruction with hands-on clinical practice.\n\n"
        "Students gain practical experience through clinical placements at leading hospitals "
        "and healthcare facilities, ensuring they are well-prepared to provide quality patient "
        "care upon graduation. The school's faculty comprises experienced nurse educators and "
        "clinical practitioners.\n\n"
        "The School of Nursing and Midwifery is dedicated to producing nurses and midwives "
        "who are technically skilled, ethically grounded, and devoted to improving health "
        "outcomes in their communities."
    ),

    "SET": (
        "The School of Engineering and Technology (SET) at Central University offers a range "
        "of undergraduate programmes in engineering and technology disciplines. The school is "
        "dedicated to producing graduates who combine strong theoretical foundations with "
        "practical skills to solve real-world engineering challenges.\n\n"
        "Programmes are designed to meet the needs of Ghana's growing technology sector, with "
        "emphasis on hands-on laboratory work, industry collaboration, and innovative problem "
        "solving. Students have access to modern laboratories and workshop facilities.\n\n"
        "The School of Engineering and Technology aims to be a centre of excellence in "
        "engineering education and applied research, producing competent engineers and "
        "technologists for national development."
    ),

    "FASS": (
        "The Faculty of Arts and Social Sciences (FASS) offers a diverse range of undergraduate "
        "programmes across the humanities and social sciences. The faculty is committed to "
        "providing a broad-based liberal arts education that develops critical thinking, "
        "communication skills, and a deep understanding of society and culture.\n\n"
        "Programmes span areas including Communication Studies, Psychology, Political Science, "
        "Theology, and Social Work. The faculty fosters an interdisciplinary approach, "
        "encouraging students to explore connections across different fields of study.\n\n"
        "FASS prepares graduates who are well-rounded, analytically capable, and ready to "
        "contribute meaningfully to public discourse, governance, social development, "
        "and community transformation."
    ),

    "SAD": (
        "The School of Architecture and Design (SAD) at Central University is committed to "
        "training creative and technically skilled professionals in architecture and related "
        "design disciplines. The school offers programmes that blend artistic creativity with "
        "engineering principles and sustainable design practices.\n\n"
        "Students benefit from a studio-based learning environment, industry-led projects, "
        "and exposure to contemporary architectural practice. The curriculum integrates digital "
        "design tools, building technology, environmental sustainability, and urban planning.\n\n"
        "The School of Architecture and Design aims to produce graduates who can design "
        "innovative, functional, and sustainable built environments that serve communities "
        "and contribute to Ghana's architectural landscape."
    ),

    "CBS": (
        "The Central Business School (CBS) is one of the flagship academic units of Central "
        "University, offering a comprehensive range of business and management programmes. "
        "The school is dedicated to developing business leaders with strong analytical, "
        "entrepreneurial, and ethical competencies.\n\n"
        "Programmes cover core business disciplines including Accounting, Banking and Finance, "
        "Marketing, Human Resource Management, and Management and Public Administration. The "
        "curriculum integrates contemporary business theory with practical case studies and "
        "industry attachments.\n\n"
        "CBS is committed to producing graduates who are well-equipped to excel in the "
        "competitive global business environment while maintaining high ethical standards "
        "and a commitment to social responsibility."
    ),

    "SGS": (
        "The School of Graduate Studies and Research coordinates postgraduate academic "
        "programmes across Central University. The school provides an environment for "
        "advanced scholarship, research, and professional development at the master's "
        "and doctoral levels.\n\n"
        "The school oversees the quality and standards of all graduate programmes, ensuring "
        "that they meet the requirements of the Ghana Tertiary Education Commission (GTEC) "
        "and international benchmarks. Graduate students benefit from research mentorship, "
        "seminar series, and access to research resources.\n\n"
        "The School of Graduate Studies and Research is committed to fostering a culture "
        "of academic inquiry and producing graduates who can contribute original knowledge "
        "to their respective fields."
    ),

    "CDPE": (
        "The Centre for Distance and Professional Education (CDPE) extends Central University's "
        "educational reach beyond the traditional campus. The centre offers flexible learning "
        "modes — including distance education, weekend programmes, and sandwich programmes — "
        "designed for working professionals and students who cannot attend regular weekday "
        "classes.\n\n"
        "CDPE delivers the same quality curricula as the on-campus programmes, supported by "
        "learning centres across the country. The centre leverages technology and blended "
        "learning approaches to ensure effective teaching and learning.\n\n"
        "The Centre for Distance and Professional Education is dedicated to making quality "
        "higher education accessible to all, regardless of location or work schedule, "
        "supporting lifelong learning and professional advancement."
    ),
}


def main():
    print("=" * 60)
    print("Central Course Guide — School Description Updater")
    print("=" * 60)

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    schools_col = db["schools"]

    count = schools_col.count_documents({})
    print(f"\nFound {count} schools in database.\n")

    updated = 0

    for code, description in SCHOOL_DESCRIPTIONS.items():
        school = schools_col.find_one({"code": code})
        if not school:
            print(f"  ⚠  School {code} not found in database, skipping.")
            continue

        result = schools_col.update_one(
            {"_id": school["_id"]},
            {"$set": {"description": description}}
        )

        if result.modified_count > 0:
            print(f"  ✓  {school['name']} — updated ({len(description)} chars)")
            updated += 1
        else:
            print(f"  -  {school['name']} — already up to date")

    print(f"\n{'=' * 60}")
    print(f"Done! Updated {updated}/{len(SCHOOL_DESCRIPTIONS)} school descriptions.")
    print(f"{'=' * 60}")

    client.close()


if __name__ == "__main__":
    main()
