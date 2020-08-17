# Timetable design

The aim of this software is to design a timetable for a school. The code builds the data structures according to an abstract model and uses an optimization engine for the solution. It has been used with real life problems for over 3 years. The main components of the problem are the courses (examples `1A`, `3C`, etc), the subjects (for example `Math_1A`) and the teachers (example `John Doe`). The assignment from subjects to courses and from teachers to subjects is already done. The only thing missing is to decide at what time each subject is taught.
For that there are 45 possible slots (5 days a week, 9 possible times during the day).

## Parameters

All the parameters for this problem are described in a single spreadsheet file.
The file has two sheets corresponding to subject and teacher parameters
respectively.

### Subject Parameters
Each course has an ID of the form *NAME_COURSE* (for example `ARTE_1A`),
a course to which it belongs and the number of hours a week it takes.
We can also consider for each subject the list of teachers that must teach it at the same time.
Some of the subjects have fixed time slots (described by the `definidas` variable).
There also some pairs of subjects that should happen at the same time (controlled
by the `espejos` variable) and some subjects that are part of a block, meaning
that they should use two consecutive slots at some point during the week.

### Teacher Parameters
Each teacher has an ID (essentially the name) an array of availabilities
(1/0 for each slot) and a list of subjects that can teach.
There are two more parameters, `castigo` and `ahorcadas` that control how much
we have to respect the time availability and the *dead hours* (idle time between
classes) for them.

## Variables
There is a set of integer variables `assig_subjects` that determine for each
subject and each hour what's the corresponding slot.

## Restrictions
There are a lot of different restrictions that we can separate in some classes.

### Basic Restrictions
Here we can find the following
 * Each course has only one subject at any given time
 * Each teacher can only be teaching one subject at a time
 * Each course shouldn't have more than one block of a subject the same day

### Castigos and Ahorcadas
Restrictions controlling if availability is taken in consideration and if we allow idle time between classes

### Espejos
These are pairs of subjects that should happen at the same time

### Definidas
These are subjects with defined slots

### Labs
Science subjects and it corresponding labs should be in block.

### Traslados
For some teachers we should try to minimize "traslados"

### Ad-hoc
 * Math and Math lab are different days
 * Art with `Claudia` and `Gloria` for third grade are on different days
