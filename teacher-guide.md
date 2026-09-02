# Build It, Break It, Own It
## Teacher guide

A hands-on unit in which students assemble a working weather station, trace who
controls each layer of it, and then run the same trace on their own phone.

Runs as a 25-minute station, a 55-minute lesson, or a six-month project.
No prior electronics experience. No coding experience. No internet required.

OurWorlds. Built on BeagleBoard hardware.

---

## Two pathways

**Students** open the scroller and work through nine numbered steps, from tipping
the parts out of the bag to reading their own weather off a screen. Every step is
a thing they do with their hands. It also prints, so it works with no devices at
all.

**Teachers** read this document. It tells you what standards the unit meets, what
students produce that you can assess, where they reliably get stuck, and what to
say when a table's board will not start.

---

## What students actually do

| | |
|---|---|
| Build | A solar-shielded environmental sensor on a Linux single-board computer |
| Verify | Query the sensor's ID register to confirm it is the part they were sold |
| Diagnose | Work a systematic troubleshooting sequence when the bus comes back empty |
| Analyse | Compare a shielded and unshielded sensor over one day and explain the difference |
| Evaluate | Trace chip, firmware, OS and application layers on the station, then on their phone |
| Decide | Apply the CARE principles to their own data and state what they will share |

---

## Standards alignment

Standards quoted below are reproduced from the published wording.

### CSTA K-12 Computer Science Standards (2017), Level 3A, grades 9-10

CSTA 2017 standards are released under a Creative Commons licence.

| Code | Standard | Where it is met |
|---|---|---|
| **3A-CS-01** | Explain how abstractions hide the underlying implementation details of computing systems embedded in everyday objects. | The phone trace. Students can name every layer of the station they built and cannot name one for the phone. The abstraction is felt, not described. |
| **3A-CS-02** | Compare levels of abstraction and interactions between application software, system software, and hardware layers. | The core worksheet. Four rows: chip manufacturer, firmware, operating system, application. Completed twice, once per device. |
| **3A-CS-03** | Develop guidelines that convey systematic troubleshooting strategies that others can use to identify and fix errors. | The "nothing showed up" sequence: power, seating, swapped power and ground, alternate address. Students write their own version for the next cohort. |
| **3A-DA-09** | Translate between different bit representations of real-world phenomena, such as characters, numbers, and images. | Hexadecimal throughout: `0x76`, `0x3C`, `0xD0`, `0x60`, `0x58`. Students convert and interpret single-byte register values. |
| **3A-DA-10** | Evaluate the tradeoffs in how data elements are organized and where data is stored. | Local card versus cloud service. Students state what they gain and what they give up, with a working example of each. |
| **3A-NI-07** | Compare various security measures, considering tradeoffs between the usability and security of a computing system. | The closing question: what would you have to give up to make this easier? Every consumer weather station is easier. Students name the trade. |

### Next Generation Science Standards, high school

| Code | Performance expectation | Where it is met |
|---|---|---|
| **HS-ETS1-2** | Design a solution to a complex real-world problem by breaking it down into smaller, more manageable problems that can be solved through engineering. | Shielding a sensor from the sun decomposes into: block direct light at all seasonal angles, allow airflow, shed rain, avoid conductive contact. Students solve each separately. |
| **HS-ETS1-3** | Evaluate a solution to a complex real-world problem based on prioritized criteria and trade-offs that account for a range of constraints, including cost, safety, reliability, and aesthetics, as well as possible social, cultural, and environmental impacts. | The whole unit. The standard's own wording includes social and cultural impact as evaluation criteria, which is precisely what the data sovereignty content asks students to weigh. |

**Science and engineering practices** exercised throughout: Planning and Carrying
Out Investigations, Analysing and Interpreting Data, Constructing Explanations and
Designing Solutions, Engaging in Argument from Evidence.

**Crosscutting concepts**: Systems and System Models, Cause and Effect, Patterns.

### Also touched

Common Core Mathematics MP.4 (model with mathematics) in the shielded-versus-bare
comparison. CCSS RST.11-12.8 (evaluate hypotheses and data in a technical text,
verifying data where possible) in the chip verification step.

---

## Assessable artifacts

Six things a student produces that you can collect and mark.

1. **The completed device trace**, both columns. The empty column is the finding.
2. **A working station**, verified by `sws-check` output.
3. **Their own troubleshooting guide**, written for the next student.
4. **The chip ID result** and a sentence on what it means for their dataset.
5. **A shielded-versus-bare comparison** with the solar noon anomaly identified.
6. **A data statement**: what they will share, with whom, and why, against CARE.

---

## Session plans

### 25 minutes, station format
Board is pre-built. Students add the sensor, run `sws-check`, complete the phone
column of the trace, and take the worksheet away. Reaches the most students.

### 55 minutes, full lesson
Full build from parts, both trace columns, the redesign question. Ends with the
sign-up for the longer project.

### Six months, cohort
Station deployed at home. Monthly milestone: a photo and six numbers.

| Month | Milestone |
|---|---|
| 1 | First reading. Photo of the deployed station and seven days of data. |
| 2 | Trace their own build. One thing they changed and why. |
| 3 | Thirty days continuous. One anomaly, explained. |
| 4-5 | Extend. A new sensor, a second node, or the story of the site. |
| 6 | Present locally. |

Milestones are a photo and a number. No video calls, no uploads. Requiring
reliable broadband would exclude the students this is built for.

**Expect roughly 20-30% of student-held kits to complete six months.** Plan for
that rather than against it.

---

## Where students get stuck

**Counting to pin 14.** Pin numbers zig-zag: odds on one row, evens on the other.
Almost every failed build is a miscounted pin. Have them count aloud, in pairs.

**Deciding it is broken during boot.** Nothing visible happens for about thirty
seconds after power. Say this before they plug in, not after.

**Half-seated wires.** A wire pushed most of the way in looks identical to one
pushed all the way in. Re-seat all four before debugging anything else.

---

## Materials

About $60 per station, excluding the board.

Sensor, OLED display, microSD card, momentary button, jumper wires, five white
plastic plant saucers, threaded rod with nuts and washers, USB-C cable.

The image is a published build script with a checksum, not a prepared card. A
student can read every change it makes to the base operating system.

---

## Attribution and consultation

This unit references the Choctaw Code Talkers of World War I, drawing on
OurWorlds' *Choctaw Code Talkers 1918*, produced with the Choctaw Nation of
Oklahoma Historic Preservation Department, descendants of the Code Talkers, and
the School of Choctaw Language. Classroom materials for that unit are at
curriculumst.ourworlds.io.

The data governance section uses the **CARE Principles for Indigenous Data
Governance** (Collective Benefit, Authority to Control, Responsibility, Ethics),
published by the Global Indigenous Data Alliance in 2019 and building on the
First Nations principles of OCAP developed in Canada in the 1990s. GIDA's own
position is that locally developed frameworks take precedence over the global
principles. If your school serves a specific nation, teach that nation's
framework first and use CARE as the wider context.

Site-specific student data should route through your own community's process
before anything is published.
