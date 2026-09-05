"""
Module: Scenario Repository (Assessment Assembly Engine v1.0).
Defines 50 distinct expert-authored Class 10 / High School Student scenarios across 10 Families x 5 Variants.
"""

import os
import json
from typing import Dict, List, Optional
from app.application.scenario_subsystem.scenario_metadata import (
    ScenarioMetadata,
    StakeholderType,
    CommunicationStyle,
    DecisionType,
    InteractionType,
    ScenarioType,
)
from app.domain.entities.scenario import Scenario
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.entities.follow_up_question import FollowUpQuestion
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.value_objects.enums import DifficultyLevel, ConstructType
from app.domain.assessment.speaking_canonical_config import (
    CANONICAL_SPEAKING_SPECS,
    CANONICAL_SQ1_INDICATORS,
    CANONICAL_SQ2_INDICATORS,
    CANONICAL_SQ3_INDICATORS,
)



class ScenarioRepository:
    """Repository containing 50 distinct Class 10 scenarios organized into 10 Families x 5 Variants."""

    def __init__(self):
        self._scenarios: Dict[str, Scenario] = {}
        self._metadata: Dict[str, ScenarioMetadata] = {}
        self._populate_50_scenarios()

    def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        return self._scenarios.get(scenario_id)

    def get_metadata(self, scenario_id: str) -> Optional[ScenarioMetadata]:
        return self._metadata.get(scenario_id)

    def list_all_metadata(self) -> List[ScenarioMetadata]:
        return list(self._metadata.values())

    def list_all_scenarios(self) -> List[Scenario]:
        return list(self._scenarios.values())

    def _populate_50_scenarios(self) -> None:
        raw_data = [{'id': 'SCEN-001', 'family': 'FAM-01', 'variant': 'A', 'category': 'STEM & Science', 'subcategory': 'Classroom Lab', 'title': 'Robotics Competition Battery Thermal Limit Crisis', 'narrative': "At 09:15 AM in the high school innovation lab, 10th-grade robotics lead Arjun discovered that the custom high-density battery management pack on the team's autonomous rover was hitting a thermal throttle limit of 65°C during high-current obstacle climbing. Visiting STEM judge Dr. Arora announced that the technical evaluation panel will inspect the arena at 10:00 AM, leaving exactly 45 minutes. Replacing the power pack requires 50 minutes of disassembly, whereas re-routing current limits to 75% will keep the pack cool but reduce climbing speed by 20%.", 'lq_prompt': 'What thermal throttle temperature limit was the battery management pack reaching?', 'lq_options': ['55°C', '65°C', '75°C', '85°C'], 'lq_correct': 1, 'sp_instructions': 'Your teammate Arjun insists on a full power pack replacement which takes 50 minutes, missing the 10:00 AM deadline. Explain how you would convince him to accept the current limit re-routing strategy to stay within the 45-minute window.', 'fu_prompt': 'Suppose the judges notice the reduced speed during the trial. How would you defend your engineering trade-off?'}, {'id': 'SCEN-002', 'family': 'FAM-01', 'variant': 'B', 'category': 'STEM & Science', 'subcategory': 'Classroom Lab', 'title': 'Solar Model Motor Alignment 30 Mins Before Judging', 'narrative': "During the Class 10 annual science fair setup at 08:30 AM, Priya noticed that the stepper motor driving her team's dual-axis solar tracker model was misaligned by 12 degrees due to a loose mounting bracket. Science teacher Mrs. Sen informed all teams that final scoring begins promptly at 09:00 AM. Tightening the existing bracket takes 10 minutes but risks slipping again under sunlight, while rebuilding the acrylic mount takes 25 minutes.", 'lq_prompt': 'By how many degrees was the stepper motor misaligned?', 'lq_options': ['5 degrees', '12 degrees', '18 degrees', '25 degrees'], 'lq_correct': 1, 'sp_instructions': 'Describe how you would prioritize between quick bracket tightening and full acrylic rebuild with 30 minutes remaining.', 'fu_prompt': 'How would you address a teammate who wants to give up and present a non-functional static model?'}, {'id': 'SCEN-003', 'family': 'FAM-01', 'variant': 'C', 'category': 'STEM & Science', 'subcategory': 'Classroom Lab', 'title': 'Smart Water Purifier Sensor Calibration Dispute', 'narrative': "At 11:00 AM in the chemistry lab, Rohan's team was testing an IoT water filtration model for the school exhibition. The digital Turbidity sensor read 45 NTU (unsafe), whereas the manual chemical test strip showed 12 NTU (safe). Guest evaluator Dr. Joshi will review the booth at 11:30 AM. Re-calibrating the digital sensor requires 20 minutes, while manual testing takes 5 minutes per sample.", 'lq_prompt': 'What turbidity reading did the digital sensor display?', 'lq_options': ['12 NTU', '25 NTU', '45 NTU', '60 NTU'], 'lq_correct': 2, 'sp_instructions': "How would you handle the conflicting sensor readings before Dr. Joshi's arrival?", 'fu_prompt': 'If Dr. Joshi asks why your digital display differs from your manual test log, what would you explain?'}, {'id': 'SCEN-004', 'family': 'FAM-01', 'variant': 'D', 'category': 'STEM & Science', 'subcategory': 'Classroom Lab', 'title': 'Bioplastic Project Presentation Data Inconsistency', 'narrative': "At 01:15 PM, 45 minutes before the regional science fair presentations, Ananya discovered a formatting discrepancy in her team's bioplastic tensile strength chart: one dataset reported mega-pascals (MPa) while another logged kilo-pascals (kPa). Science mentor Mr. Verma warned that incorrect units result in automatic disqualification. Recalculating the dataset takes 25 minutes.", 'lq_prompt': 'What error was discovered in the bioplastic project chart?', 'lq_options': ['Missing title', 'Mismatched units (MPa vs kPa)', 'Corrupted PDF file', 'Wrong font size'], 'lq_correct': 1, 'sp_instructions': 'Explain your plan to audit and fix the data table under the 45-minute deadline.', 'fu_prompt': 'How would you handle pressure if your teammate accuses you of causing the unit mistake?'}, {'id': 'SCEN-005', 'family': 'FAM-01', 'variant': 'E', 'category': 'STEM & Science', 'subcategory': 'Classroom Lab', 'title': 'Hydroponic System Voltage Overload & Power Share Crisis', 'narrative': "At 10:10 AM in the botany lab, Kabir's hydroponic automation rig experienced a circuit breaker trip because the water pump and nutrient heater drew 14 Amps on a shared 10-Amp school socket. Chief Judge Prof. Ray is arriving in 20 minutes. Turning off the nutrient heater maintains circuit stability but drops water temperature by 4°C during the demo.", 'lq_prompt': 'What was the current draw that tripped the shared 10-Amp socket?', 'lq_options': ['10 Amps', '12 Amps', '14 Amps', '18 Amps'], 'lq_correct': 2, 'sp_instructions': 'Detail your immediate decision to prevent further circuit trips while keeping the hydroponic demo operational.', 'fu_prompt': 'What steps would you take to ensure electrical safety during future school science events?'}, {'id': 'SCEN-006', 'family': 'FAM-02', 'variant': 'A', 'category': 'Academic Guidance', 'subcategory': 'Counseling Office', 'title': 'Science (PCM) vs Commerce Stream Choice under Family Expectation', 'narrative': 'Siddharth, a Class 10 student scoring 92% in Mathematics and 88% in Economics, faces a stream selection deadline in 3 days. His parents want him to enroll in Science (PCM) for engineering, but Siddharth is deeply passionate about Financial Economics and Commerce. Counselor Ms. Ritu advised that switching streams after Term 1 is prohibited by board regulations.', 'lq_prompt': 'What score did Siddharth achieve in Economics?', 'lq_options': ['82%', '88%', '92%', '95%'], 'lq_correct': 1, 'sp_instructions': 'How would you communicate your decision to your parents while presenting a career roadmap?', 'fu_prompt': 'If your family insists on engineering, how would you balance personal aspirations with parental expectations?'}, {'id': 'SCEN-007', 'family': 'FAM-02', 'variant': 'B', 'category': 'Academic Guidance', 'subcategory': 'Counseling Office', 'title': 'Humanities vs Bio-Science Stream Dilemma', 'narrative': 'Meera loves English Literature and Psychology (94% marks), but her elder brother urges her to choose PCB (Physics, Chemistry, Biology) for medical entrance exams. The school career portal closes tomorrow at 05:00 PM. Her father Mr. Sharma wants her to consult her class teacher before submitting the final subject combination.', 'lq_prompt': 'At what time does the school career portal close tomorrow?', 'lq_options': ['02:00 PM', '04:00 PM', '05:00 PM', '06:00 PM'], 'lq_correct': 2, 'sp_instructions': 'Describe how you would structure a conversation with your father and counselor to choose Humanities.', 'fu_prompt': 'What would you do if your family refuses to support a non-medical career choice?'}, {'id': 'SCEN-008', 'family': 'FAM-02', 'variant': 'C', 'category': 'Academic Guidance', 'subcategory': 'Counseling Office', 'title': 'Computer Science Elective vs Economics Selection Deadline', 'narrative': 'Class 10 student Aarav must pick his 6th elective subject between Computer Applications and Economics. School Principal Dr. Das announced a strict cap of 40 students per section. Computer Applications has 2 seats remaining, while Economics has 15 seats. Aarav has strong coding skills but wants to understand market economics.', 'lq_prompt': 'How many seats remain in the Computer Applications section?', 'lq_options': ['2 seats', '5 seats', '15 seats', '40 seats'], 'lq_correct': 0, 'sp_instructions': 'How would you decide between a limited-seat technical elective and a broader social science elective?', 'fu_prompt': 'If you miss the seat cap for Computer Applications, how would you adapt your learning plan?'}, {'id': 'SCEN-009', 'family': 'FAM-02', 'variant': 'D', 'category': 'Academic Guidance', 'subcategory': 'Counseling Office', 'title': 'Math Extra Coaching Conflict with Sports Training', 'narrative': 'Diya is a Class 10 state-level badminton player whose Math pre-board score dropped to 62%. Her parents arranged remedial Math coaching every weekday from 04:00 PM to 06:00 PM. However, her badminton coach Coach Vikram scheduled mandatory tournament drills from 04:30 PM to 06:30 PM.', 'lq_prompt': 'What score did Diya receive in her Math pre-board exam?', 'lq_options': ['52%', '62%', '72%', '82%'], 'lq_correct': 1, 'sp_instructions': 'Propose a revised schedule that balances academic recovery in Math with sports commitment.', 'fu_prompt': 'How would you handle a situation where both your coach and tutor refuse to adjust their timings?'}, {'id': 'SCEN-010', 'family': 'FAM-02', 'variant': 'E', 'category': 'Academic Guidance', 'subcategory': 'Counseling Office', 'title': 'Scholarship Exam Preparation vs School Board Pre-Mocks', 'narrative': 'Vivaan is preparing for a national talent scholarship exam scheduled on December 15. However, his school Class 10 Pre-Board examinations run from December 10 to December 22. His mother Mrs. Nair is worried that preparing for both simultaneously will lead to burnout and lower overall board marks.', 'lq_prompt': 'On what date is the national talent scholarship exam scheduled?', 'lq_options': ['December 5', 'December 10', 'December 15', 'December 22'], 'lq_correct': 2, 'sp_instructions': 'Outline your study strategy to balance national scholarship preparation with school pre-board exams.', 'fu_prompt': 'If your pre-board mock marks drop in one subject, how would you adjust your study allocation?'}, {'id': 'SCEN-011', 'family': 'FAM-03', 'variant': 'A', 'category': 'Arts & Culture', 'subcategory': 'Auditorium', 'title': 'Annual Drama Costume Budget Shortfall 2 Days Before Show', 'narrative': 'Two days before the Class 10 Annual Day play, drama team lead Riya discovered that costume rental vendor fees came to ₹18,000, exceeding the approved school budget of ₹12,000 by ₹6,000. Drama Director Mr. Roy stated that extra funds cannot be sanctioned from school accounts without Principal approval, which takes 3 days.', 'lq_prompt': 'By how much did the costume rental fees exceed the approved school budget?', 'lq_options': ['₹3,000', '₹4,500', '₹6,000', '₹8,000'], 'lq_correct': 2, 'sp_instructions': 'Explain how you would resolve the ₹6,000 budget shortfall 48 hours before the performance.', 'fu_prompt': 'How would you justify modifying costume designs to cast members who paid for custom outfits?'}, {'id': 'SCEN-012', 'family': 'FAM-03', 'variant': 'B', 'category': 'Arts & Culture', 'subcategory': 'Auditorium', 'title': 'Stage Lighting Failure During Final Dress Rehearsal', 'narrative': 'At 05:00 PM during the final dress rehearsal for Annual Day, the main stage spotlight controller malfunctioned due to a blown fuse. Tech Crew Lead Sneha reported that a replacement module costs ₹3,500 and takes 4 hours to arrive. Tanishq, the student coordinator, must decide whether to use static side floodlights or delay rehearsal.', 'lq_prompt': 'How long will it take for the replacement lighting module to arrive?', 'lq_options': ['1 hour', '2 hours', '4 hours', '6 hours'], 'lq_correct': 2, 'sp_instructions': 'How would you manage the rehearsal schedule with static side lights under tight time constraints?', 'fu_prompt': 'What contingency plan would you establish if the lighting module fails during the live show?'}, {'id': 'SCEN-013', 'family': 'FAM-03', 'variant': 'C', 'category': 'Arts & Culture', 'subcategory': 'Auditorium', 'title': 'Lead Actor Throat Infection Backup Casting Dilemma', 'narrative': 'On the morning of the Annual Day drama, lead actor Kabir developed a severe throat infection and was advised 2 days of complete vocal rest by the school nurse. Teacher Mrs. Paul asked student director Ishita to choose between understudy Anuj (who knows lines but lacks stage confidence) or reading lines from off-stage.', 'lq_prompt': 'What restriction was placed on lead actor Kabir by the school nurse?', 'lq_options': ['No physical movement', '2 days of vocal rest', 'Mandatory hospital stay', '1 week absence'], 'lq_correct': 1, 'sp_instructions': 'Detail your decision between putting understudy Anuj on stage vs off-stage narration.', 'fu_prompt': "How would you boost Anuj's confidence 3 hours before performing in front of 500 audience members?"}, {'id': 'SCEN-014', 'family': 'FAM-03', 'variant': 'D', 'category': 'Arts & Culture', 'subcategory': 'Auditorium', 'title': 'Sound System Overlap between Choir and Dance Troupe', 'narrative': 'During Annual Day preparations, student manager Karan found that the choir group and classical dance troupe were both scheduled to use the main auditorium sound system from 03:00 PM to 04:30 PM. Music Teacher Mr. Bose refused to split the stage, stating both performances need full stage acoustics.', 'lq_prompt': 'What time slot created a scheduling conflict between the choir and dance troupe?', 'lq_options': ['01:00 PM - 02:30 PM', '02:00 PM - 03:30 PM', '03:00 PM - 04:30 PM', '04:00 PM - 05:30 PM'], 'lq_correct': 2, 'sp_instructions': 'How would you negotiate a split rehearsal schedule between choir and dance coordinators?', 'fu_prompt': 'What steps would you take if one group refuses to yield rehearsal time?'}, {'id': 'SCEN-015', 'family': 'FAM-03', 'variant': 'E', 'category': 'Arts & Culture', 'subcategory': 'Auditorium', 'title': 'VIP Guest Schedule Change Forces Performance Cut', 'narrative': 'At 11:00 AM, Vice Principal Ms. Gupta informed student anchor Anushka that the Chief Guest must leave 20 minutes earlier than scheduled. To accommodate this, the 90-minute Annual Day program must be reduced by 15 minutes. Anushka must cut time from either the student speech, orchestra, or drama act.', 'lq_prompt': 'By how many minutes must the overall Annual Day program be reduced?', 'lq_options': ['10 minutes', '15 minutes', '20 minutes', '30 minutes'], 'lq_correct': 1, 'sp_instructions': 'Explain which segment you would trim and how you would communicate this decision respectfully to the performers.', 'fu_prompt': 'How would you handle disappointment from students whose performance duration was reduced?'}, {'id': 'SCEN-016', 'family': 'FAM-04', 'variant': 'A', 'category': 'Academics & Teamwork', 'subcategory': 'Classroom', 'title': 'Social Studies Group Project: Uncooperative Teammate', 'narrative': 'In a 4-member Class 10 Social Studies group project due in 2 days, group leader Dev noticed that classmate Rohan has submitted 0 out of 5 assigned research slides. Rohan claims he was busy with sports practice. The group submission grade accounts for 20% of the term mark.', 'lq_prompt': 'What percentage of the term mark does the Social Studies group project account for?', 'lq_options': ['10%', '15%', '20%', '25%'], 'lq_correct': 2, 'sp_instructions': "How would you address Rohan's lack of contribution while ensuring the project is completed on time?", 'fu_prompt': 'If Rohan refuses to complete his assigned slides tonight, would you report him to the teacher or reassign the work?'}, {'id': 'SCEN-017', 'family': 'FAM-04', 'variant': 'B', 'category': 'Academics & Teamwork', 'subcategory': 'Classroom', 'title': 'English Skit Script Conflict: Comedy vs Serious Theme', 'narrative': "During Class 10 English skit preparation, Nisha's 5-member team was split 3-2 on script genre. Nisha and two members wanted a serious social drama on environmental awareness, while Varun and another member insisted on a comedic parody. The script draft must be turned in to the teacher by 04:00 PM.", 'lq_prompt': 'What deadline was set for submitting the English skit script draft?', 'lq_options': ['02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'], 'lq_correct': 2, 'sp_instructions': 'Describe how you would resolve the genre creative dispute to produce a unified script before 04:00 PM.', 'fu_prompt': 'How would you ensure team members who lost the vote remain enthusiastic during rehearsals?'}, {'id': 'SCEN-018', 'family': 'FAM-04', 'variant': 'C', 'category': 'Academics & Teamwork', 'subcategory': 'Classroom', 'title': 'History Chart Presentation Data Loss Night Before Deadline', 'narrative': "At 09:00 PM the night before the History exhibition, Aditya discovered that his teammate Neha's shared digital presentation file was accidentally overwritten, losing 6 out of 10 slides on the Indian Independence movement. The presentation starts at 08:30 AM tomorrow.", 'lq_prompt': 'How many slides were lost when the shared presentation file was overwritten?', 'lq_options': ['4 slides', '6 slides', '8 slides', '10 slides'], 'lq_correct': 1, 'sp_instructions': 'Outline your emergency recovery plan to recreate the missing 6 slides overnight.', 'fu_prompt': 'How would you prevent blame-shifting and keep team morale high during overnight work?'}, {'id': 'SCEN-019', 'family': 'FAM-04', 'variant': 'D', 'category': 'Academics & Teamwork', 'subcategory': 'Classroom', 'title': 'Unequal Workload Distribution in Chemistry Lab Report', 'narrative': 'In a 4-member Chemistry group, team member Sanya realized that she and one partner completed 80% of the lab calculations and diagram drawings, while the remaining two members only formatted cover pages. Chemistry teacher Dr. Mehta mandates peer evaluation forms alongside submission.', 'lq_prompt': 'What percentage of lab calculations did Sanya and her partner complete?', 'lq_options': ['50%', '65%', '80%', '90%'], 'lq_correct': 2, 'sp_instructions': 'How would you handle peer evaluation forms fairly without causing personal hostility in the group?', 'fu_prompt': 'If a teammate asks you to give them full marks on peer evaluation despite doing little work, how would you respond?'}, {'id': 'SCEN-020', 'family': 'FAM-04', 'variant': 'E', 'category': 'Academics & Teamwork', 'subcategory': 'Classroom', 'title': 'Plagiarized Paragraph Discovered in Joint Biology Report', 'narrative': "1 hour before submitting the final Class 10 Biology group report, group leader Yash ran a plagiarism check and found a 35% match on classmate Simran's section on Genetics, copied directly from Wikipedia. School policy mandates zero tolerance for academic plagiarism.", 'lq_prompt': "What plagiarism percentage was detected in Simran's section of the report?", 'lq_options': ['15%', '25%', '35%', '50%'], 'lq_correct': 2, 'sp_instructions': 'Explain your immediate steps to rewrite the plagiarized section before final submission.', 'fu_prompt': 'Would you inform the teacher about the plagiarized section, and how would you explain it to Simran?'}, {'id': 'SCEN-021', 'family': 'FAM-05', 'variant': 'A', 'category': 'Campus Environment', 'subcategory': 'School Campus', 'title': 'Canteen Single-Use Plastic Ban Enforcement Pushback', 'narrative': 'Class 10 Eco-Club president Tanvi spearheaded a single-use plastic bottle ban in the school canteen. However, Canteen Manager Mr. Gupta complained that glass bottle deposits increased vendor costs by ₹2,000/week, threatening to raise snack prices for students.', 'lq_prompt': 'By how much per week did vendor costs increase under the glass bottle deposit model?', 'lq_options': ['₹1,000', '₹1,500', '₹2,000', '₹3,000'], 'lq_correct': 2, 'sp_instructions': 'Propose a sustainable solution that maintains the plastic ban without raising snack prices for students.', 'fu_prompt': 'How would you address complaints from students annoyed by carrying reusable water bottles?'}, {'id': 'SCEN-022', 'family': 'FAM-05', 'variant': 'B', 'category': 'Campus Environment', 'subcategory': 'School Campus', 'title': 'School Garden Drip Irrigation System Water Leak', 'narrative': "During afternoon break at 01:30 PM, Rahul noticed a major pipe fracture in the school herbal garden's drip irrigation system, wasting 50 liters of water per hour. Caretaker Uncle Ram stated that plumber repair parts will arrive tomorrow, but plants will dry out under 36°C heat.", 'lq_prompt': 'How much water was leaking per hour from the fractured pipe?', 'lq_options': ['20 liters', '35 liters', '50 liters', '75 liters'], 'lq_correct': 2, 'sp_instructions': 'Detail how you would organize student volunteers to manually water plants while preventing water waste.', 'fu_prompt': 'What long-term preventive measures would you recommend to the Eco-Club committee?'}, {'id': 'SCEN-023', 'family': 'FAM-05', 'variant': 'C', 'category': 'Campus Environment', 'subcategory': 'School Campus', 'title': 'E-Waste Collection Drive Storage Logistics Crunch', 'narrative': 'The Class 10 E-Waste Drive collected 180 kg of discarded electronics, exceeding expectations by 80 kg. Eco-Club teacher Ms. Anita informed student coordinator Pooja that the school store room is full and government recycling pickup is delayed by 4 days.', 'lq_prompt': 'By how many kilograms did the E-Waste collection exceed expectations?', 'lq_options': ['40 kg', '60 kg', '80 kg', '100 kg'], 'lq_correct': 2, 'sp_instructions': 'Explain your plan to securely store 180 kg of e-waste on campus without violating safety rules.', 'fu_prompt': 'How would you handle safety concerns from school staff about battery leakage in temporary storage?'}, {'id': 'SCEN-024', 'family': 'FAM-05', 'variant': 'D', 'category': 'Campus Environment', 'subcategory': 'School Campus', 'title': 'Paper Recycling Unit Budget Allocation vs Plant Saplings', 'narrative': 'Eco-Club treasurer Kriti has a budget of ₹8,000. Purchasing a portable paper shredder and recycling bin costs ₹7,500, leaving no money for the tree plantation drive. Vice President Manav wants to split funds 50-50 between saplings and bins.', 'lq_prompt': 'What is the total available budget for the Eco-Club project?', 'lq_options': ['₹5,000', '₹6,500', '₹8,000', '₹10,000'], 'lq_correct': 2, 'sp_instructions': 'How would you resolve the budget allocation conflict between paper recycling equipment and tree saplings?', 'fu_prompt': 'How would you pitch for community sponsorship if internal club funds fall short?'}, {'id': 'SCEN-025', 'family': 'FAM-05', 'variant': 'E', 'category': 'Campus Environment', 'subcategory': 'School Campus', 'title': 'Solar Panel Installation Awareness Campaign Disruption', 'narrative': 'During the campus green drive, Eco-Club lead Shruti scheduled a solar awareness presentation in the assembly hall at 09:00 AM. However, Head Boy Aakash announced that inter-house quiz prelims were rescheduled to the same hall at 09:15 AM.', 'lq_prompt': 'What event was rescheduled to the assembly hall at 09:15 AM?', 'lq_options': ['Debate competition', 'Inter-house quiz prelims', 'Basketball match', 'Parent teacher meet'], 'lq_correct': 1, 'sp_instructions': 'Describe how you would adjust your presentation format or location to co-exist with the quiz event.', 'fu_prompt': 'How would you maintain venue cooperation with student council leaders when schedules clash?'}, {'id': 'SCEN-026', 'family': 'FAM-06', 'variant': 'A', 'category': 'Sports & Leadership', 'subcategory': 'Sports Ground', 'title': 'Basketball Tournament Final Quarter Ankle Sprain Dilemma', 'narrative': 'In the final quarter of the inter-school basketball final with 4 minutes remaining and a 2-point lead, school captain Sameer twisted his ankle. Coach Mr. Rawat left the choice to Sameer: substitute out for bench player Varun (who lacks big-game experience) or play through mild pain.', 'lq_prompt': 'How many minutes remained in the final quarter when Sameer twisted his ankle?', 'lq_options': ['2 minutes', '4 minutes', '6 minutes', '8 minutes'], 'lq_correct': 1, 'sp_instructions': 'Explain your decision between playing through injury vs substituting in a rookie bench player.', 'fu_prompt': 'If your team loses after you substitute out, how would you address team disappointment as captain?'}, {'id': 'SCEN-027', 'family': 'FAM-06', 'variant': 'B', 'category': 'Sports & Leadership', 'subcategory': 'Sports Ground', 'title': 'Football Squad Selection: Best Striker vs Disciplined Player', 'narrative': 'Football captain Rahul must submit the final 11-player lineup for the zonal tournament. Star striker Aryan scored 8 goals this season but missed 4 mandatory morning training sessions. Vice Captain Aman advocates choosing disciplined player Kabir, who attended all sessions but scored 2 goals.', 'lq_prompt': 'How many goals did star striker Aryan score this season?', 'lq_options': ['4 goals', '6 goals', '8 goals', '10 goals'], 'lq_correct': 2, 'sp_instructions': 'Detail your selection criteria between individual talent vs squad discipline for the tournament roster.', 'fu_prompt': 'How would you explain your decision to Aryan to motivate him to respect team discipline?'}, {'id': 'SCEN-028', 'family': 'FAM-06', 'variant': 'C', 'category': 'Sports & Leadership', 'subcategory': 'Sports Ground', 'title': 'Relay Race Baton Exchange Miscommunication Training', 'narrative': '3 days before the district athletics meet, 4x100m relay captain Ishan noticed that runners 2 and 3 dropped the baton twice during practice exchanges. Teammate Tarun blames the timing call, while runner 3 blames hand positioning. Practice time is limited to 1 hour daily.', 'lq_prompt': 'How many times was the baton dropped during practice exchanges between runners 2 and 3?', 'lq_options': ['1 time', '2 times', '3 times', '4 times'], 'lq_correct': 1, 'sp_instructions': 'How would you restructure the remaining 3 days of practice to eliminate baton drop errors?', 'fu_prompt': 'How would you diffuse interpersonal frustration between relay teammates under pressure?'}, {'id': 'SCEN-029', 'family': 'FAM-06', 'variant': 'D', 'category': 'Sports & Leadership', 'subcategory': 'Sports Ground', 'title': 'Badminton Championship Travel Budget vs Extra Gear Request', 'narrative': 'Badminton captain Radhika received a ₹12,000 sports department travel grant for the state tournament. The team needs ₹4,000 for upgraded feather shuttlecocks for practice and ₹10,000 for hotel stay. Sports Teacher Ms. Monica requested a revised budget breakdown by 05:00 PM.', 'lq_prompt': 'What was the total travel grant allocated by the sports department?', 'lq_options': ['₹8,000', '₹10,000', '₹12,000', '₹15,000'], 'lq_correct': 2, 'sp_instructions': 'Propose a balanced budget breakdown between accommodation quality and high-grade practice shuttlecocks.', 'fu_prompt': 'How would you pitch to the PTA for supplementary sports travel funding?'}, {'id': 'SCEN-030', 'family': 'FAM-06', 'variant': 'E', 'category': 'Sports & Leadership', 'subcategory': 'Sports Ground', 'title': 'Unsportsmanlike Conduct by Star Bowler in Cricket Semifinal', 'narrative': 'During the inter-school cricket semifinal, star bowler Dev received a formal warning from Umpire Mr. Sen for arguing an edge decision. Cricket captain Vikram knows another warning will result in a 2-match ban, ruling Dev out of the finals if the team wins.', 'lq_prompt': 'What sanction will Dev receive if he incurs a second warning from the umpire?', 'lq_options': ['₹500 fine', '1-over penalty', '2-match ban', 'Disqualification of team'], 'lq_correct': 2, 'sp_instructions': 'Explain how you would intervene on the field to calm Dev while keeping team competitive focus.', 'fu_prompt': 'What team rule would you establish after the match regarding umpire respect and emotional control?'}, {'id': 'SCEN-031', 'family': 'FAM-07', 'variant': 'A', 'category': 'Ethics & Technology', 'subcategory': 'Computer Lab', 'title': 'AI Code Sharing Group Chat before Computer Mocks', 'narrative': '1 night before the Class 10 Computer Applications practical mock exam, student Nikhil noticed classmate Parth posting full Python solution scripts generated by ChatGPT into the unofficial class WhatsApp group. 15 students downloaded the code. Computer teacher Mr. Rao uses automated plagiarism checkers.', 'lq_prompt': 'How many students downloaded the AI-generated Python solution scripts from the group chat?', 'lq_options': ['5 students', '10 students', '15 students', '25 students'], 'lq_correct': 2, 'sp_instructions': 'Describe how you would address the code sharing in the group chat while preparing your own authentic code.', 'fu_prompt': 'If classmate Parth asks you not to report the group chat, how would you respond?'}, {'id': 'SCEN-032', 'family': 'FAM-07', 'variant': 'B', 'category': 'Ethics & Technology', 'subcategory': 'Computer Lab', 'title': 'Online Assignment Copying Alert in Class WhatsApp Group', 'narrative': 'Class monitor Sneha discovered that 8 classmates copied verbatim answers for a Social Science online assignment from a shared Google Doc created by student Harsh. The submission portal closes at 11:59 PM. Teacher Mrs. Kapoor warned that copied assignments receive zero marks.', 'lq_prompt': "How many classmates copied answers from Harsh's shared Google Doc?", 'lq_options': ['4 classmates', '8 classmates', '12 classmates', '16 classmates'], 'lq_correct': 1, 'sp_instructions': 'How would you advise your classmates before the 11:59 PM deadline to submit original work?', 'fu_prompt': 'How would you handle peer pressure accusing you of being overly strict as class monitor?'}, {'id': 'SCEN-033', 'family': 'FAM-07', 'variant': 'C', 'category': 'Ethics & Technology', 'subcategory': 'Computer Lab', 'title': 'Using AI Essay Generator for History Homework Submission', 'narrative': 'Student Varun was struggling with a 1,500-word History essay on World War II due tomorrow morning. Tempted by a 5-minute AI essay generator tool, Varun generated a full essay. Friend Aditi warned him that History teacher Mrs. Iyer conducts viva oral questions on submitted essays.', 'lq_prompt': 'What was the required word count for the History essay assignment?', 'lq_options': ['800 words', '1,000 words', '1,500 words', '2,000 words'], 'lq_correct': 2, 'sp_instructions': 'Explain why submitting AI-generated text without personal understanding creates risks during oral viva assessments.', 'fu_prompt': 'How can AI tools be ethically used for research without committing academic dishonesty?'}, {'id': 'SCEN-034', 'family': 'FAM-07', 'variant': 'D', 'category': 'Ethics & Technology', 'subcategory': 'Computer Lab', 'title': 'Exam Paper Leak Rumor Spreading in Student Bus', 'narrative': 'While commuting on the school bus at 07:45 AM, Class 10 student Aditi heard rumors that leaked images of the Science mid-term paper were circulating on Telegram for ₹500. Bus incharge Mr. Singh noticed student anxiety. Principal Dr. Roy announced strict police reporting for paper leaks.', 'lq_prompt': 'At what price were alleged leak images being circulated on Telegram?', 'lq_options': ['₹200', '₹500', '₹1,000', 'Free'], 'lq_correct': 1, 'sp_instructions': 'Detail how you would respond to paper leak rumors and discourage peers from buying fake leaked papers.', 'fu_prompt': 'What steps would you take if a close friend admits to purchasing the leaked Telegram document?'}, {'id': 'SCEN-035', 'family': 'FAM-07', 'variant': 'E', 'category': 'Ethics & Technology', 'subcategory': 'Computer Lab', 'title': 'Unauthorized USB Flash Drive in Computer Lab System', 'narrative': "During Class 10 IT practicals, student Rohit found an unauthorized USB flash drive inserted into the teacher's server computer, triggering an antivirus malware alert. Lab assistant Mr. Das was out of the room for 10 minutes. Classmate Sarthak admitted plugging it in to copy sample papers.", 'lq_prompt': 'How long was lab assistant Mr. Das out of the computer lab room?', 'lq_options': ['5 minutes', '10 minutes', '15 minutes', '20 minutes'], 'lq_correct': 1, 'sp_instructions': 'Explain your actions upon discovering the malware alert and unauthorized USB drive.', 'fu_prompt': 'How would you balance honesty with lab staff against protecting a classmate from school suspension?'}, {'id': 'SCEN-036', 'family': 'FAM-08', 'variant': 'A', 'category': 'Student Leadership', 'subcategory': 'Council Room', 'title': 'Canteen Queue Management System Conflict', 'narrative': 'Head Girl Ananya implemented a 2-lane canteen queue system (Junior vs Senior) to reduce 20-minute lunch delays. Junior Representative Dhruv reported that seniors were cutting into the junior lane, causing 8th-grade students to miss lunch. Principal Dr. Sen asked for a resolved plan by 02:00 PM.', 'lq_prompt': 'How long were lunch delays before the new queue system was introduced?', 'lq_options': ['10 minutes', '15 minutes', '20 minutes', '30 minutes'], 'lq_correct': 2, 'sp_instructions': 'Propose an effective council monitoring system to enforce fair canteen queuing without physical conflict.', 'fu_prompt': 'How would you handle senior students who dismiss council authority?'}, {'id': 'SCEN-037', 'family': 'FAM-08', 'variant': 'B', 'category': 'Student Leadership', 'subcategory': 'Council Room', 'title': 'Library Quiet Zone vs Group Study Desk Space Allocation', 'narrative': 'Student Council President Kshitij received petition letters signed by 60 Class 10 students requesting 4 extra group study tables in the main library. However, Librarian Ms. Roy stated that converting quiet zones into group desks increases noise levels, disturbing Class 12 board exam readers.', 'lq_prompt': 'How many Class 10 students signed the petition for extra group study tables?', 'lq_options': ['30 students', '45 students', '60 students', '80 students'], 'lq_correct': 2, 'sp_instructions': 'Detail a compromise spatial plan that allocates group study space while preserving quiet reading zones.', 'fu_prompt': 'How would you present this solution to both the Librarian and petitioner students?'}, {'id': 'SCEN-038', 'family': 'FAM-08', 'variant': 'C', 'category': 'Student Leadership', 'subcategory': 'Council Room', 'title': 'School Discipline Board Uniform Rule Variance Request', 'narrative': 'During severe winter weather, Council President Sanjana submitted a petition allowing Class 10 students to wear non-school black jackets over uniform sweaters. Disciplinary Teacher Mr. Khan rejected the blanket request, citing dress code decorum, but offered to permit official navy blazers.', 'lq_prompt': 'What alternative garment did Disciplinary Teacher Mr. Khan offer to permit?', 'lq_options': ['Black leather jackets', 'Official navy blazers', 'Hooded sweatshirts', 'Woolen scarves'], 'lq_correct': 1, 'sp_instructions': 'Explain how you would mediate between student winter comfort needs and school administrative decorum.', 'fu_prompt': 'How would you communicate administrative dress code decisions to students who bought non-compliant jackets?'}, {'id': 'SCEN-039', 'family': 'FAM-08', 'variant': 'D', 'category': 'Student Leadership', 'subcategory': 'Council Room', 'title': 'Annual Magazine Article Selection Controversy', 'narrative': 'Student Magazine Editor Devansh must select 10 articles from 35 submissions for the Class 10 annual publication. Author Riya accused the editorial board of favoring student council members after 3 council essays were selected. Editorial faculty advisor Mr. Alok called for a transparent review process.', 'lq_prompt': 'How many total article submissions were received for the school magazine?', 'lq_options': ['20 submissions', '25 submissions', '35 submissions', '50 submissions'], 'lq_correct': 2, 'sp_instructions': 'Outline an anonymous peer-review evaluation process to guarantee fairness in magazine selections.', 'fu_prompt': 'How would you address allegations of favoritism publicly to maintain editorial trust?'}, {'id': 'SCEN-040', 'family': 'FAM-08', 'variant': 'E', 'category': 'Student Leadership', 'subcategory': 'Council Room', 'title': 'Sports Day Funds Allocation vs Cultural Fest Fund Transfer', 'narrative': 'Student Council Treasurer Trupti discovered that the Sports Day budget has an unspent surplus of ₹15,000, while the upcoming Cultural Fest is facing a ₹12,000 deficit for stage sound rentals. Sports Captain Sameer opposes transferring surplus funds, claiming sports gear needs maintenance.', 'lq_prompt': 'How much unspent surplus exists in the Sports Day budget?', 'lq_options': ['₹8,000', '₹12,000', '₹15,000', '₹20,000'], 'lq_correct': 2, 'sp_instructions': 'How would you negotiate fund reallocation between sports and cultural department heads?', 'fu_prompt': 'What financial guidelines would you establish for inter-departmental budget transfers in the future?'}, {'id': 'SCEN-041', 'family': 'FAM-09', 'variant': 'A', 'category': 'Technology & STEM', 'subcategory': 'Robotics Lab', 'title': '3D Printer Filament Jam 1 Hour Before Model Submission', 'narrative': 'At 02:00 PM, 1 hour before the STEM design project deadline, student Om found that the 3D printer extruding PLA filament for his drone arm joint had suffered a nozzle heat creep jam. STEM Incharge Mr. Patil stated that dismantling the extruder takes 45 minutes, leaving 15 minutes to print.', 'lq_prompt': 'At what time was the 3D printer nozzle jam discovered?', 'lq_options': ['01:00 PM', '01:30 PM', '02:00 PM', '02:30 PM'], 'lq_correct': 2, 'sp_instructions': 'Decide between dismantling the 3D extruder vs fabricating a manual acrylic joint backup under 60 minutes.', 'fu_prompt': 'How would you explain the structural trade-off of a hand-cut acrylic backup to the judging panel?'}, {'id': 'SCEN-042', 'family': 'FAM-09', 'variant': 'B', 'category': 'Technology & STEM', 'subcategory': 'Robotics Lab', 'title': 'Coding Competition Algorithm Time Complexity Limit', 'narrative': "During the Class 10 Interschool Coding Hackathon, Rashi's pathfinding algorithm scored 100% accuracy on sample test cases but failed 4 out of 10 large hidden test cases due to a 2.0-second execution timeout. Teammate Sahil wants to switch from Bubble Sort to Quick Sort with 20 minutes left.", 'lq_prompt': 'How many hidden test cases failed due to execution timeout?', 'lq_options': ['2 cases', '4 cases', '6 cases', '8 cases'], 'lq_correct': 1, 'sp_instructions': 'Detail your strategy to refactor code time complexity under a 20-minute hackathon countdown.', 'fu_prompt': 'How would you prevent panic when code refactoring initially produces syntax errors near the deadline?'}, {'id': 'SCEN-043', 'family': 'FAM-09', 'variant': 'C', 'category': 'Technology & STEM', 'subcategory': 'Robotics Lab', 'title': 'IoT Weather Station Sensor Corrosion on School Roof', 'narrative': 'Class 10 STEM team lead Kavyanjali found that the roof-mounted IoT rain gauge sensor stopped transmitting wireless data due to terminal pin oxidation after heavy monsoons. Science Teacher Dr. Rao asked for a restored data feed before the 04:00 PM weather report broadcast.', 'lq_prompt': 'What caused the roof-mounted IoT rain gauge sensor to stop transmitting data?', 'lq_options': ['Low battery', 'Terminal pin oxidation', 'Broken antenna', 'Software crash'], 'lq_correct': 1, 'sp_instructions': 'Explain how you would clean corrosion and weatherproof roof sensors before the 04:00 PM broadcast.', 'fu_prompt': 'What maintenance schedule would you establish to protect outdoor school STEM equipment?'}, {'id': 'SCEN-044', 'family': 'FAM-09', 'variant': 'D', 'category': 'Technology & STEM', 'subcategory': 'Robotics Lab', 'title': 'Autonomous Line Follower Robot Track Reflection Calibration', 'narrative': "At the state robotics arena, Armaan's line follower robot failed to detect black tape turns because glossy arena floor lights reflected infrared beams into the IR sensor array. Mentor Ms. Deepa provided anti-glare tape strips and sensitivity adjustment pots with 30 minutes before trial 1.", 'lq_prompt': 'What caused the infrared sensor array to misread the black tape turns?', 'lq_options': ['Dust on track', 'Glossy floor light reflection', 'Motor voltage drop', 'Loose wheel hub'], 'lq_correct': 1, 'sp_instructions': 'Describe how you would calibrate IR sensor threshold pots under artificial arena lighting.', 'fu_prompt': 'How would you handle trial 1 if track lighting varies unpredictably across different sections?'}, {'id': 'SCEN-045', 'family': 'FAM-09', 'variant': 'E', 'category': 'Technology & STEM', 'subcategory': 'Robotics Lab', 'title': 'Circuit Board Short Circuit under Voltage Spike Test', 'narrative': "During stress testing in the electronics lab, student Bhavya observed smoke emitting from a voltage regulator IC on the team's custom PCB after input voltage spiked to 12V instead of 5V. Hardware Expert Mr. Nair noted that spare IC components are limited to 1 remaining unit.", 'lq_prompt': 'What voltage spike level caused the regulator IC to emit smoke?', 'lq_options': ['5V', '7.5V', '10V', '12V'], 'lq_correct': 3, 'sp_instructions': 'Outline your diagnostic procedure before soldering the single remaining replacement IC onto the circuit board.', 'fu_prompt': 'What protection components (like zener diodes or fuses) would you add to prevent future voltage spike damage?'}, {'id': 'SCEN-046', 'family': 'FAM-10', 'variant': 'A', 'category': 'Public Safety & Service', 'subcategory': 'School Grounds', 'title': 'Fire Safety Evacuation Drill Staircase Bottleneck', 'narrative': 'During an unannounced Class 10 fire evacuation drill at 11:30 AM, student safety monitor Tarun observed a dangerous congestion bottleneck at Staircase B as 120 students from 3 floors attempted to exit simultaneously. Floor Teacher Mrs. Desai instructed Tarun to re-route 2nd-floor classes to Emergency Exit C.', 'lq_prompt': 'How many total students were bottlenecked at Staircase B during the drill?', 'lq_options': ['60 students', '90 students', '120 students', '180 students'], 'lq_correct': 2, 'sp_instructions': 'Describe how you would execute a calm, orderly evacuation re-route to Emergency Exit C.', 'fu_prompt': 'What structural recommendations would you submit to the school safety committee to prevent staircase congestion?'}, {'id': 'SCEN-047', 'family': 'FAM-10', 'variant': 'B', 'category': 'Public Safety & Service', 'subcategory': 'School Grounds', 'title': 'Heavy Rain Flash Flood Bus Departure Coordination', 'narrative': 'At 02:15 PM, heavy monsoons caused waterlogging up to 1.5 feet at the school main gate. Transport Lead Pranav was instructed by Driver Uncle Mohan to dispatch 8 student buses in staggered 10-minute intervals to avoid engine flooding. 300 students were waiting in the main porch.', 'lq_prompt': 'What waterlogging depth was reported at the school main gate?', 'lq_options': ['0.5 feet', '1.0 foot', '1.5 feet', '2.5 feet'], 'lq_correct': 2, 'sp_instructions': 'Detail your crowd control strategy to board 300 students safely into staggered buses during heavy rain.', 'fu_prompt': 'How would you handle panicky parents arriving at the flooded gate simultaneously?'}, {'id': 'SCEN-048', 'family': 'FAM-10', 'variant': 'C', 'category': 'Public Safety & Service', 'subcategory': 'School Grounds', 'title': 'First Aid Kit Shortfall during Inter-House Athletic Meet', 'narrative': 'During the afternoon 800m track race at the inter-house sports meet, 3 runners suffered heat exhaustion and track scrapes. Red Cross student lead Alok discovered that the field first-aid kit was missing ice packs and antiseptic spray. School Nurse Sister Mary requested 2 volunteers to fetch supplies from the main infirmary 300 meters away.', 'lq_prompt': 'How far away was the main school infirmary from the athletic field?', 'lq_options': ['100 meters', '200 meters', '300 meters', '500 meters'], 'lq_correct': 2, 'sp_instructions': 'How would you prioritize immediate care for heat exhaustion vs dispatching volunteers for first-aid supplies?', 'fu_prompt': 'What inventory checklist would you implement for sports event first-aid kits in the future?'}, {'id': 'SCEN-049', 'family': 'FAM-10', 'variant': 'D', 'category': 'Public Safety & Service', 'subcategory': 'School Grounds', 'title': 'School Auditorium Power Failure Emergency Lighting Activation', 'narrative': 'At 06:30 PM during an evening school community presentation with 250 parents present, a main transformer failure plunged the auditorium into total darkness. Student Tech Lead Ishaan had 30 seconds to activate generator backup switches, while 4 student marshals guided guests using emergency flashlight torches.', 'lq_prompt': 'How many parents were present in the auditorium during the power failure?', 'lq_options': ['150 parents', '200 parents', '250 parents', '350 parents'], 'lq_correct': 2, 'sp_instructions': 'Explain your calm announcement and leadership instructions to prevent panic during total auditorium darkness.', 'fu_prompt': 'How would you train student tech crews for emergency blackout protocols?'}, {'id': 'SCEN-050', 'family': 'FAM-10', 'variant': 'E', 'category': 'Public Safety & Service', 'subcategory': 'School Grounds', 'title': 'Heatwave Water Cooler Breakdown Management on Sports Day', 'narrative': 'During a 38°C outdoor Sports Day event at 12:30 PM, the main water chiller machine broke down, leaving 400 participating students with warm tap water. Volunteer Lead Muskaan had ₹1,500 in contingency funds. Purchasing 200 ice blocks costs ₹1,200, while buying bottled water costs ₹4,000.', 'lq_prompt': 'What outdoor temperature was recorded during Sports Day?', 'lq_options': ['32°C', '35°C', '38°C', '42°C'], 'lq_correct': 2, 'sp_instructions': 'Detail your decision to use ₹1,500 contingency funds to chill tap water with ice blocks under extreme heat.', 'fu_prompt': 'How would you coordinate with school administration to prevent dehydration risks during summer sports events?'}]

        families_info = {
            "FAM-01": ("Science Exhibition & Innovation", "STEM & Science", "Classroom Lab", StakeholderType.TEACHER, InteractionType.DIRECT_DECISION, ScenarioType.INDIVIDUAL_DECISION, CommunicationStyle.EXPLANATION),
            "FAM-02": ("Academic Stream Selection", "Academic Guidance", "Counseling Office", StakeholderType.PARENT, InteractionType.SOCRATIC_INQUIRY, ScenarioType.PLANNING, CommunicationStyle.REFLECTION),
            "FAM-03": ("School Annual Day Cultural Event", "Arts & Culture", "Auditorium", StakeholderType.PRINCIPAL, InteractionType.TEAM_NEGOTIATION, ScenarioType.TEAM_LEADERSHIP, CommunicationStyle.DECISION_JUSTIFICATION),
            "FAM-04": ("Group Project & Peer Dynamics", "Academics & Teamwork", "Classroom", StakeholderType.FRIEND, InteractionType.TEAM_NEGOTIATION, ScenarioType.TEAM_LEADERSHIP, CommunicationStyle.CONFLICT_RESOLUTION),
            "FAM-05": ("Eco-Club & Environmental Drive", "Campus Environment", "School Campus", StakeholderType.COMMUNITY_MEMBER, InteractionType.DIRECT_DECISION, ScenarioType.PLANNING, CommunicationStyle.PRESENTATION),
            "FAM-06": ("Inter-School Sports Captaincy", "Sports & Leadership", "Sports Ground", StakeholderType.COACH, InteractionType.CRISIS_RESPONSE, ScenarioType.CRISIS_RESPONSE, CommunicationStyle.DECISION_JUSTIFICATION),
            "FAM-07": ("Ethics & AI Academic Integrity", "Ethics & Technology", "Computer Lab", StakeholderType.TEACHER, InteractionType.SOCRATIC_INQUIRY, ScenarioType.ETHICAL_DILEMMA, CommunicationStyle.DECISION_JUSTIFICATION),
            "FAM-08": ("Student Council & Governance", "Student Leadership", "Council Room", StakeholderType.PRINCIPAL, InteractionType.TEAM_NEGOTIATION, ScenarioType.TEAM_LEADERSHIP, CommunicationStyle.NEGOTIATION),
            "FAM-09": ("Robotics & STEM Engineering", "Technology & STEM", "Robotics Lab", StakeholderType.JUNIOR_STUDENT, InteractionType.DIRECT_DECISION, ScenarioType.CRISIS_RESPONSE, CommunicationStyle.EXPLANATION),
            "FAM-10": ("Disaster Safety & Community Service", "Public Safety & Service", "School Grounds", StakeholderType.COMMUNITY_MEMBER, InteractionType.CRISIS_RESPONSE, ScenarioType.CRISIS_RESPONSE, CommunicationStyle.CONFLICT_RESOLUTION),
        }

        diff_progression = ["EASY", "EASY_MEDIUM", "MEDIUM", "MEDIUM_HARD", "HARD"]
        dec_types = [DecisionType.RESOURCE_ALLOCATION, DecisionType.PRIORITIZATION, DecisionType.ETHICS, DecisionType.RISK_MITIGATION, DecisionType.TRADEOFF]

        for item in raw_data:
            scen_id = item["id"]
            fam_id = item["family"]
            var_letter = item["variant"]
            v_idx = ord(var_letter) - ord('A')
            
            fam_name, cat, subcat, default_st, default_it, default_stype, default_cs = families_info[fam_id]
            diff = diff_progression[v_idx]
            dec_type = dec_types[v_idx]
            is_ethical = (v_idx == 2 or fam_id == "FAM-07")

            metadata = ScenarioMetadata(
                scenario_id=scen_id,
                family_id=fam_id,
                variant_id=f"{fam_id}-VAR-{var_letter}",
                category=cat,
                subcategory=subcat,
                primary_constructs=["Decision Making", "Leadership"] if v_idx % 2 == 0 else ["Risk Awareness", "Adaptability"],
                secondary_constructs=["Communication", "Critical Thinking", "Ethics"],
                cognitive_processes=["Analysis", "Evaluation", "Synthesis"],
                interaction_type=default_it,
                scenario_type=default_stype,
                stakeholder_type=default_st,
                ethical_dimension=is_ethical,
                collaboration_level="TEAM" if v_idx % 2 == 1 else "INDIVIDUAL",
                decision_type=dec_type,
                communication_style=default_cs,
                time_pressure="HIGH" if diff in ("MEDIUM_HARD", "HARD") else "MODERATE",
                uncertainty_level="HIGH" if diff == "HARD" else "MODERATE",
                complexity_level="HIGH" if diff in ("MEDIUM_HARD", "HARD") else "MODERATE",
                listening_difficulty=diff,
                speaking_difficulty=diff,
                estimated_duration=180 + (v_idx * 15),
                prerequisite_tags=[cat.lower().replace(" ", "_")],
                exclusion_tags=[f"excl_{fam_id.lower()}"],
            )

            diff_enum = DifficultyLevel.INTERMEDIATE
            if diff in ("EASY", "EASY_MEDIUM"):
                diff_enum = DifficultyLevel.BEGINNER
            elif diff in ("MEDIUM_HARD", "HARD"):
                diff_enum = DifficultyLevel.ADVANCED

            # Load custom grounded 4 questions from scenarios_50_fully_grounded.json if available
            grounded_path = os.path.join(os.path.dirname(__file__), "scenarios_50_fully_grounded.json")
            if not os.path.exists(grounded_path):
                grounded_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "scenarios_50_fully_grounded.json")

            grounded_qs = None
            if os.path.exists(grounded_path):
                try:
                    with open(grounded_path, "r", encoding="utf-8") as f:
                        gdata = json.load(f)
                        grounded_qs = gdata.get(scen_id)
                except Exception:
                    pass

            if grounded_qs and len(grounded_qs) == 4:
                q1_data, q2_data, q3_data, q4_data = grounded_qs
                
                lq1 = ListeningQuestion(
                    question_id=f"Q1_{scen_id}",
                    prompt=q1_data["prompt"],
                    options=q1_data["options"],
                    correct_option_index=q1_data["correct_option_index"],
                    target_construct=ConstructType.WORKING_MEMORY,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Recall",
                    cognitive_objective=q1_data.get("cognitive_objective", "Verbatim recall"),
                    expected_evidence=q1_data.get("expected_evidence", {}),
                    weight=1.0,
                )

                lq2 = ListeningQuestion(
                    question_id=f"Q2_{scen_id}",
                    prompt=q2_data["prompt"],
                    options=q2_data["options"],
                    correct_option_index=q2_data["correct_option_index"],
                    target_construct=ConstructType.ATTENTION,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Detail",
                    cognitive_objective=q2_data.get("cognitive_objective", "Focused attention on scenario detail"),
                    expected_evidence=q2_data.get("expected_evidence", {}),
                    weight=1.0,
                )

                lq3 = ListeningQuestion(
                    question_id=f"Q3_{scen_id}",
                    prompt=q3_data["prompt"],
                    options=q3_data["options"],
                    correct_option_index=q3_data["correct_option_index"],
                    target_construct=ConstructType.LISTENING_COMPREHENSION,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.REASONING],
                    question_type="Comprehension",
                    cognitive_objective=q3_data.get("cognitive_objective", "Understanding of overall scenario trade-off narrative"),
                    expected_evidence=q3_data.get("expected_evidence", {}),
                    weight=1.0,
                )

                lq4 = ListeningQuestion(
                    question_id=f"Q4_{scen_id}",
                    prompt=q4_data["prompt"],
                    options=q4_data["options"],
                    correct_option_index=q4_data["correct_option_index"],
                    target_construct=ConstructType.REASONING,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Inference",
                    cognitive_objective=q4_data.get("cognitive_objective", "Logical inference synthesizing situational constraints"),
                    expected_evidence=q4_data.get("expected_evidence", {}),
                    weight=1.0,
                )
            else:
                subcat = item.get("subcategory", "school setting")
                cat = item.get("category", "activity")

                lq1 = ListeningQuestion(
                    question_id=f"Q1_{scen_id}",
                    prompt=item["lq_prompt"],
                    options=item["lq_options"],
                    correct_option_index=item["lq_correct"],
                    target_construct=ConstructType.WORKING_MEMORY,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Recall",
                    cognitive_objective="Verbatim recall of exact numeric or factual detail explicitly stated in narration",
                    expected_evidence={
                        "correct_answer_indicates": "Accurate verbatim retrieval of numeric detail",
                        "distractor_rationale": {"0": "Misremembered figure", "2": "Plausible figure shift"}
                    },
                    weight=1.0,
                )

                lq2 = ListeningQuestion(
                    question_id=f"Q2_{scen_id}",
                    prompt=f"According to the narrative for '{item['title']}', which specific detail about the {subcat} situation requires focused attention?",
                    options=[
                        f"Resolving the {subcat} situation within the stated timeframe",
                        f"Extending the {subcat} activity duration until next month",
                        f"Canceling all {cat} activities until the next term",
                        f"Re-assigning the {subcat} tasks to a different student group"
                    ],
                    correct_option_index=0,
                    target_construct=ConstructType.ATTENTION,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Detail",
                    cognitive_objective="Focused attention on specific operational setting and stakeholder context",
                    expected_evidence={
                        "correct_answer_indicates": "Focused attention on specific scenario setting and deadline",
                        "distractor_rationale": {"1": "Plausible schedule extension misinterpretation", "2": "Exaggerated cancellation assumption"}
                    },
                    weight=1.0,
                )

                lq3 = ListeningQuestion(
                    question_id=f"Q3_{scen_id}",
                    prompt=f"What is the central narrative trade-off that must be resolved in '{item['title']}'?",
                    options=[
                        f"Balancing immediate {subcat} timeline constraints against overall delivery quality",
                        f"Securing external departmental financial sanction before beginning any team work",
                        f"Replacing current student participants with full-time external advisory personnel",
                        f"Postponing all scheduled event milestones until the following academic semester"
                    ],
                    correct_option_index=0,
                    target_construct=ConstructType.LISTENING_COMPREHENSION,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.REASONING],
                    question_type="Comprehension",
                    cognitive_objective="Understanding of overall scenario trade-off narrative",
                    expected_evidence={
                        "correct_answer_indicates": "Comprehension of core narrative dilemma",
                        "distractor_rationale": {"1": "Irrelevant funding assumption", "2": "Unrealistic staffing assumption"}
                    },
                    weight=1.0,
                )

                lq4 = ListeningQuestion(
                    question_id=f"Q4_{scen_id}",
                    prompt=f"Based on the circumstances in '{item['title']}', what logical outcome follows if the team executes an immediate temporary adaptation?",
                    options=[
                        f"The core team objective is accomplished on time with minor follow-up adjustments later",
                        f"The entire project is immediately disqualified from technical review without evaluation",
                        f"The committee mandates restarting the full developmental procedure from scratch next term",
                        f"Operational resource expenditures for the initiative double during final execution"
                    ],
                    correct_option_index=0,
                    target_construct=ConstructType.REASONING,
                    difficulty=diff_enum,
                    points=10,
                    max_replays=2,
                    secondary_constructs=[ConstructType.LISTENING_COMPREHENSION],
                    question_type="Inference",
                    cognitive_objective="Logical inference synthesizing situational constraints and outcome consequences",
                    expected_evidence={
                        "correct_answer_indicates": "Logical inference combining adaptation strategy and outcome",
                        "distractor_rationale": {"1": "Exaggerated failure assumption", "2": "Unfounded restart assumption"}
                    },
                    weight=1.0,
                )

            # Build canonical speaking prompts (SQ1, SQ2, SQ3)
            json_paths = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scenarios_50_data.json")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scenarios_50_data.json")),
                os.path.abspath(os.path.join(os.getcwd(), "scenarios_50_data.json")),
                os.path.abspath(os.path.join(os.getcwd(), "backend", "scenarios_50_data.json")),
            ]
            loaded_json_map = {}
            for jp in json_paths:
                if os.path.exists(jp):
                    try:
                        with open(jp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            loaded_json_map = {d["id"]: d for d in data}
                            break
                    except Exception:
                        pass

            json_item = loaded_json_map.get(scen_id, item)
            sp_list_data = json_item.get("speaking_questions", [])

            if sp_list_data and len(sp_list_data) == 3:
                sp_prompts = []
                for sp_dict in sp_list_data:
                    q_id = sp_dict["question_id"]
                    canonical_spec = CANONICAL_SPEAKING_SPECS.get(q_id, CANONICAL_SPEAKING_SPECS["SQ1"])
                    indicators = [
                        BehaviouralIndicator.from_dict(ind) if isinstance(ind, dict) else ind
                        for ind in sp_dict.get("behavioural_indicators", canonical_spec["behavioural_indicators"])
                    ]
                    sp = SpeakingPrompt(
                        prompt_id=f"{q_id}_{scen_id}",
                        question_id=q_id,
                        stage=sp_dict.get("stage", canonical_spec["stage"]),
                        title=sp_dict.get("title", f"{q_id}: {item['title']}"),
                        instructions=sp_dict.get("instructions", ""),
                        objective=sp_dict.get("objective", canonical_spec["objective"]),
                        primary_constructs=[ConstructType.from_str(c) for c in sp_dict.get("primary_constructs", [c.value for c in canonical_spec["primary_constructs"]])],
                        secondary_constructs=[ConstructType.from_str(c) for c in sp_dict.get("secondary_constructs", [c.value for c in canonical_spec["secondary_constructs"]])],
                        behavioural_indicators=indicators,
                        time_limit=TimeLimit(max_seconds=int(sp_dict.get("max_seconds", 120))),
                        max_indicator_weighted_score=float(sp_dict.get("max_indicator_weighted_score", 18.4)),
                        followup_eligible=bool(sp_dict.get("followup_eligible", True)),
                    )
                    sp_prompts.append(sp)
            else:
                sp1 = SpeakingPrompt(
                    prompt_id=f"SQ1_{scen_id}",
                    question_id="SQ1",
                    stage="STAGE_1_DECISION",
                    title=f"Initial Decision: {item['title']}",
                    instructions=item.get("sp_instructions", f"Explain how you would analyze the constraints and make a feasible decision for '{item['title']}'."),
                    objective=CANONICAL_SPEAKING_SPECS["SQ1"]["objective"],
                    primary_constructs=CANONICAL_SPEAKING_SPECS["SQ1"]["primary_constructs"],
                    secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ1"]["secondary_constructs"],
                    behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ1"]["behavioural_indicators"],
                    time_limit=TimeLimit(max_seconds=120),
                    max_indicator_weighted_score=18.4,
                    followup_eligible=True,
                )
                sp2 = SpeakingPrompt(
                    prompt_id=f"SQ2_{scen_id}",
                    question_id="SQ2",
                    stage="STAGE_2_CHALLENGE",
                    title=f"Adaptive Challenge: {item['title']}",
                    instructions=item.get("fu_prompt", f"Suppose unexpected complications arise midway through executing your plan for '{item['title']}'. How do you adapt your approach?"),
                    objective=CANONICAL_SPEAKING_SPECS["SQ2"]["objective"],
                    primary_constructs=CANONICAL_SPEAKING_SPECS["SQ2"]["primary_constructs"],
                    secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ2"]["secondary_constructs"],
                    behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ2"]["behavioural_indicators"],
                    time_limit=TimeLimit(max_seconds=120),
                    max_indicator_weighted_score=18.4,
                    followup_eligible=True,
                )
                sp3 = SpeakingPrompt(
                    prompt_id=f"SQ3_{scen_id}",
                    question_id="SQ3",
                    stage="STAGE_3_REFLECTIVE",
                    title=f"Reflective Reasoning: {item['title']}",
                    instructions=f"Reflecting on the trade-offs and decisions made in '{item['title']}', what key assumptions were tested, and what general principle would you apply to similar future situations?",
                    objective=CANONICAL_SPEAKING_SPECS["SQ3"]["objective"],
                    primary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["primary_constructs"],
                    secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["secondary_constructs"],
                    behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ3"]["behavioural_indicators"],
                    time_limit=TimeLimit(max_seconds=120),
                    max_indicator_weighted_score=18.4,
                    followup_eligible=True,
                )
                sp_prompts = [sp1, sp2, sp3]

            fu1 = FollowUpQuestion(
                followup_id=f"FU1_{scen_id}",
                parent_prompt_id=f"SQ1_{scen_id}",
                prompt_text=item.get("fu_prompt", ""),
                target_construct=ConstructType.ADAPTABILITY,
                priority=1,
                trigger_conditions={"min_confidence": 0.50},
                expected_evidence_pattern="Look for stakeholder empathy and trade-off justification.",
                time_limit=TimeLimit(max_seconds=60),
            )

            scenario = Scenario(
                scenario_id=scen_id,
                title=item["title"],
                narrative=item["narrative"],
                version="1.0.0",
                difficulty=diff_enum,
                audio_asset=AudioAsset(url=f"/audio/scenarios/{scen_id}.mp3", duration_seconds=180.0, format="audio/mp3"),
                listening_questions=[lq1, lq2, lq3, lq4],
                speaking_prompts=sp_prompts,
                construct_mappings=[
                    ConstructType.DECISION_MAKING,
                    ConstructType.COMMUNICATION,
                    ConstructType.ADAPTABILITY,
                    ConstructType.REASONING,
                    ConstructType.LISTENING_COMPREHENSION,
                ],
                metadata=metadata.to_dict(),
                follow_up_definitions=[fu1],
            )

            self._scenarios[scen_id] = scenario
            self._metadata[scen_id] = metadata

