# -*- coding: utf-8 -*-
from docplex.cp.model import CpoModel
from docplex.cp import modeler
import time
import xlrd
import xlwt
from parsing import (
    extraer_salones, extraer_maestros, extraer_materias,
    extraer_curriculum, extraer_specialties
)
from printer import Printer


class SchoolSchedulingProblem(object):
    def __init__(
        self, subjects, teachers, curriculum, specialties, working_days,
        periods, courses, teacher_work_hours, dicc_salones, indistintos,
        divididas, sin_pesos, espejos, castigos, un_bloque, dia_cerrado,
        salon_por_materia, mats_examen, definidas, ahorcadas
    ):
        # list of subjects, ex: ['Arte_1A', 'Biolo_1A', 'EdFis_1A']
        self.subjects = subjects
        # list of teachers, ex: ['JesusFigueroa', 'LauraFlores']
        self.teachers = teachers
        # dictionary of pairs (group, subject) -> number of hours
        # ex: {('1E', 'Civica_1E'): 2, ('3A', 'Tutoria_2A'): 0}
        self.curriculum = curriculum
        # List of indices of teachers available for each subject
        # ex: [[[34, 35], [1], [2], [17], ...] means teachers number 34 and 35
        # can teach subject 1 whereas teacher 1 is the only one available for
        # subject 2
        self.specialties = specialties
        # Days of the week (in text), 5 days
        self.working_days = working_days
        # Slots available for classes (in text), 9 slots
        self.periods = periods
        # List of courses, ex: ['1A', '1B', '1C', '1D', '1E']
        self.courses = courses
        # list of num teacher lists, each of them with 45 (5x9) 0/1 elements
        # that represent teacher availability for a particular hour
        self.teacher_work_hours = teacher_work_hours
        # IGNORING
        self.dicc_salones = dicc_salones
        self.indistintos = indistintos
        self.en_mismo_salon = dicc_salones.values()
        self.divididas = divididas
        self.sin_pesos = sin_pesos
        # END IGNORING
        # List of pairs of subjects that happen at the same time
        # ex: [['Taller_2B', 'Taller_2A'], ['Taller_2C', 'Taller_2A']
        self.espejos = espejos
        # List of floats (one per teacher) with penalties
        self.castigos = castigos
        # List of subjects that need to have two consecutive hours at some
        # point of the week, ex: ['Arte_2A', 'Taller_2A', 'Arte_2B']
        self.un_bloque = un_bloque
        # IGNORING
        self.dia_cerrado = dia_cerrado
        self.salon_por_materia = salon_por_materia
        self.mats_examen = mats_examen
        # END IGNORING
        # Dictionary with subjects with predefined times
        # ex: {'Taller_2A': ['14', '40', '41']}
        self.definidas = definidas
        # List of floats telling how badly we should try to avoid that each
        # teacher has idle periods between classes
        self.ahorcadas = ahorcadas


class SchoolSchedulingSatSolver(object):

    def __init__(self, problem):
        # Problem
        self.problem = problem
        self.current_solution = None

        # Utilities
        self.num_days = len(problem.working_days)
        self.num_periods = len(problem.periods)
        self.num_teachers = len(problem.teachers)
        self.num_subjects = len(problem.subjects)
        self.courses = problem.courses
        self.num_courses = len(problem.courses)

        all_courses = range(self.num_courses)
        all_teachers = range(self.num_teachers)
        all_slots = range(len(problem.working_days) * len(problem.periods))
        all_subjects = range(self.num_subjects)

        # IGNORING
        salones = {}
        for salon in problem.dicc_salones:
            salones[salon] = [
                problem.subjects.index(j)
                for j in problem.dicc_salones[salon]
            ]
        # END IGNORING

        dicc_curriculum = {}
        subjects_in_course = {}
        hours_for_subject = {}
        for c in all_courses:
            tmp = []
            for s in all_subjects:
                # if the subject s has hours for the course c
                if self.problem.curriculum[
                    (self.problem.courses[c], self.problem.subjects[s])
                ] > 0:
                    # tmp is holding the list of subjects for course c
                    tmp.append(s)
                    # course corresponding to subject s
                    dicc_curriculum[s] = c
                    # amount of hours for subject s
                    hours_for_subject[s] = self.problem.curriculum[
                        (self.problem.courses[c], self.problem.subjects[s])
                    ]
            subjects_in_course[c] = tmp

        # list of subjects that are assigned to a course
        all_subjects = [i for i in all_subjects if i in dicc_curriculum]

        self.all_subjects = all_subjects
        self.hours_for_subject = hours_for_subject
        self.dicc_curriculum = dicc_curriculum

        # computing all the subjects a teacher can teach (basically inverting
        # the specialties dict)
        subjects_for_teacher = {}
        for t in all_teachers:
            subjects_for_teacher[t] = []
        for s in all_subjects:
            for sp in self.problem.specialties[s]:
                subjects_for_teacher[sp].append(s)

        self.subjects_for_teacher = subjects_for_teacher

        # Create a cplex constraint programming model
        self.model = CpoModel()

        # Variable that determines what slot corresponds to each hour/subject.
        self.assig_subjects = {}

        for s in all_subjects:
            # c is the course of subject s
            c = dicc_curriculum[s]
            # hrs = how many hours long this subject is
            hrs = hours_for_subject[s]
            for h in range(hrs):
                nom = "S:{%i} Hr:{%i}" % (s, h)
                disp = [i for i in range(44)]
                # all teachers that can teach subject s
                for t in self.problem.specialties[s]:
                    # we only take in consideration their availabilities is
                    # their castigo is greater that 2
                    if self.problem.castigos[t] > 2:
                        disp_teach = self.problem.teacher_work_hours[t]
                        for sl in range(44):
                            # remove slots when teachers are not available
                            if sl in disp and disp_teach[sl] == 0:
                                disp.remove(sl)
                self.assig_subjects[s, h] = self.model.integer_var(
                    name=nom, domain=disp
                )
                # Break symmetries.
                if h > 0:
                    self.model.add(
                        self.assig_subjects[s, h] >
                        self.assig_subjects[s, h - 1]
                    )

        # Only one class at the same time for each group.
        # Achieves that by requesting that each slot for each course is used
        # exactly once
        for c in all_courses:
            tmp = []
            for s in subjects_in_course[c]:
                if self.problem.divididas[s] < 2:
                    hrs = hours_for_subject[s]
                    for h in range(hrs):
                        tmp.append(self.assig_subjects[s, h])
            for d in range(44):
                self.model.add(modeler.count(tmp, d) == 1)

        # Same as above for divided subjects.
        for c in all_courses:
            tmp = []
            for s in subjects_in_course[c]:
                if self.problem.divididas[s] != 1:
                    hrs = hours_for_subject[s]
                    for h in range(hrs):
                        tmp.append(self.assig_subjects[s, h])
            for d in range(44):
                self.model.add(modeler.count(tmp, d) == 1)

        # Sólo una materia de la segunda mitad del grupo en cada slot.
        for c in all_courses:
            temp = []
            mitad_dos_c = [
                x for x in subjects_in_course[c]
                if self.problem.divididas[x] == 2
            ]
            for mdc in mitad_dos_c:
                hrs = hours_for_subject[mdc]
                for h in range(hrs):
                    temp.append(self.assig_subjects[mdc, h])
            self.model.add(modeler.all_diff(temp))

        # Teacher can do at most one class at a time
        sin_peso_maestros = [
            self.problem.subjects.index(esp[0])
            for esp in self.problem.espejos
        ]
        for t in all_teachers:
            if len(subjects_for_teacher[t]) > 0:
                tmp = []
                for st in subjects_for_teacher[t]:
                    if st not in sin_peso_maestros:
                        hrs = hours_for_subject[st]
                        for h in range(hrs):
                            tmp.append(self.assig_subjects[st, h])
                self.model.add(modeler.all_diff(tmp))

        # Mirrored subjects (from different classrooms) must correspond:
        for esp in self.problem.espejos:
            s1 = self.problem.subjects.index(esp[0])
            s2 = self.problem.subjects.index(esp[1])
            if s1 in dicc_curriculum and s2 in dicc_curriculum:
                hrs = hours_for_subject[s1]
                for h in range(hrs):
                    self.model.add(
                        self.assig_subjects[s1, h] ==
                        self.assig_subjects[s2, h]
                    )

        # Special classrooms may have at most one class at the same time.
        mats_tmp = self.problem.subjects
        for salon in self.problem.en_mismo_salon:
            ms = [i for i in range(len(mats_tmp)) if mats_tmp[i] in salon]
            tmp = []
            for s in ms:
                if s in dicc_curriculum:
                    hrs = hours_for_subject[s]
                    for h in range(hrs):
                        tmp.append(self.assig_subjects[s, h])
            self.model.add(modeler.all_diff(tmp))

        bloques2 = [
            [0, 1], [2, 3], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12],
            [12, 13], [14, 15], [16, 17], [18, 19], [20, 21], [21, 22],
            [23, 24], [25, 26], [27, 28], [29, 30], [30, 31], [32, 33],
            [34, 35], [36, 37], [38, 39], [39, 40], [41, 42], [43, 44]
        ]

        # No subject should have more than one class per day.
        # Except for the blocks.
        # Dejamos fuera las materias que ya tienen horario definido.
        for s in all_subjects:
            if (
                s in dicc_curriculum and
                self.problem.subjects[s] not in self.problem.definidas
            ):
                hrs = hours_for_subject[s]
                if not self.problem.subjects[s] in self.problem.un_bloque:
                    self.model.add(
                        modeler.all_diff(
                            [modeler.int_div(self.assig_subjects[s, h], 9)
                             for h in range(hrs)]
                        )
                    )
                else:
                    self.model.add(
                        modeler.count_different(
                            [
                                modeler.int_div(self.assig_subjects[s, h], 9)
                                for h in range(hrs)
                            ]
                        ) == hrs - 1
                    )
                    # Prefiere que sean alternadas...
                    if self.problem.subjects[s] in [
                        "Geo_1A", "Geo_1B", "Geo_1C"
                    ]:
                        self.model.add(
                            modeler.all_min_distance(
                                [
                                    self.assig_subjects[s, h]
                                    for h in range(hrs)
                                ], 2
                            )
                        )
                    else:
                        self.model.add(
                            modeler.max(
                                [
                                    sum([
                                        self.assig_subjects[s, h] == sl
                                        for h in range(hrs)
                                        for sl in bl
                                    ]) for bl in bloques2
                                ]
                            ) == 2
                        )

        # Que Mate y Laboratorio de Mate no sean el mismo día.
        for gpo in self.problem.courses:
            if gpo != "3C":
                arr_temp = []
                s1 = self.problem.subjects.index("Matem_" + gpo)
                [arr_temp.append(self.assig_subjects[s1, h]) for h in range(4)]
                s2 = self.problem.subjects.index("L_Mate_" + gpo)
                arr_temp.append(self.assig_subjects[s2, 0])
                self.model.add(
                    modeler.all_diff(
                        [modeler.int_div(x, 9) for x in arr_temp]
                    )
                )

        # Que Arte con Claudia y Gloria en tercero no sean el mismo día.
        terceros = ["A", "B", "C", "D", "E"]
        for gpo in terceros:
            arr_temp = []
            s1 = self.problem.subjects.index("Arte_3" + gpo)
            [arr_temp.append(self.assig_subjects[s1, h]) for h in range(1)]
            s2 = self.problem.subjects.index("Arte_C_3" + gpo)
            arr_temp.append(self.assig_subjects[s2, 0])
            self.model.add(
                modeler.all_diff(
                    [modeler.int_div(x, 9) for x in arr_temp]
                )
            )

        # Que los laboratorios de ciencias estén en bloque con la materia.
        mats = [
            'Biolo_1A', 'Biolo_1B', 'Biolo_1C', 'Biolo_1D', 'Biolo_1E',
            'Biolo_1F', 'Fisica_2A', 'Fisica_2B', 'Fisica_2C', 'Fisica_2D',
            'Fisica_2E', 'Fisica_2F', 'Quimica_3A', 'Quimica_3B', 'Quimica_3C',
            'Quimica_3D', 'Quimica_3E'
        ]
        labs = [
            'L_Biol_1A', 'L_Biol_1B', 'L_Biol_1C', 'L_Biol_1D', 'L_Biol_1E',
            'L_Biol_1F', 'L_Fisica_2A', 'L_Fisica_2B', 'L_Fisica_2C',
            'L_Fisica_2D', 'L_Fisica_2E', 'L_Fisica_2F', 'L_Quim_3A',
            'L_Quim_3B', 'L_Quim_3C', 'L_Quim_3D', 'L_Quim_3E'
        ]

        for gpo in range(17):
            arr_temp = []
            s1 = self.problem.subjects.index(mats[gpo])
            hrs = 4 if gpo < 6 else 5
            [arr_temp.append(self.assig_subjects[s1, h]) for h in range(hrs)]
            s2 = self.problem.subjects.index(labs[gpo])
            arr_temp.append(self.assig_subjects[s2, 0])
            self.model.add(
                modeler.max([
                    sum([x == sl for x in arr_temp for sl in bl])
                    for bl in bloques2
                ]) == 2
            )

        # Minimizar traslados:
        min_tras = []
        maestros = [
            'GabrielaSoriano', 'EnriqueVazquez', 'AmaliaKing',
            'JoseRubenOrtega', 'RubenSanchez'
        ]
        for teach in maestros:
            min_tras_mae = []
            t = self.problem.teachers.index(teach)
            subs = subjects_for_teacher[t]
            m12 = []
            m3 = []
            for s in subs:
                hrs = range(hours_for_subject[s])
                if dicc_curriculum[s] < 12:
                    [m12.append(self.assig_subjects[s, h]) for h in hrs]
                else:
                    [m3.append(self.assig_subjects[s, h]) for h in hrs]
            for bl in bloques2:
                min_tras_mae.append(
                    modeler.logical_and(
                        modeler.logical_or(
                            modeler.count(m12, bl[0]) == 1,
                            modeler.count(m12, bl[1]) == 1
                        ),
                        modeler.logical_or(
                            modeler.count(m3, bl[0]) == 1,
                            modeler.count(m3, bl[1]) == 1)
                    )
                )
            min_tras.append(sum(min_tras_mae))

        # Materias definidas:
        # Asume que todas las horas de una materia están definidas y en orden.
        for mat_def in self.problem.definidas:
            s = self.problem.subjects.index(mat_def)
            sls = [float(x) for x in self.problem.definidas[mat_def]]
            for nsl in range(len(sls)):
                self.model.add(self.assig_subjects[s, nsl] == sls[nsl])

        # Teacher availability NVA
        min_t1 = []
        min_t2 = []
        min_completos = []
        min_aislados = []
        for t in all_teachers:
            if subjects_for_teacher[t] and self.problem.castigos[t] < 3:
                disp_inv = [abs(x - 1)
                            for x in self.problem.teacher_work_hours[t]]
                subs_teach = []
                for s in subjects_for_teacher[t]:
                    [subs_teach.append(self.assig_subjects[s, h])
                     for h in range(hours_for_subject[s])]
                arr_teach = [modeler.count(
                    subs_teach, sl) > 0 for sl in all_slots]
                if self.problem.castigos[t] == 2:
                    min_t2.append(modeler.scal_prod(arr_teach, disp_inv))
                if self.problem.castigos[t] == 1:
                    min_t1.append(modeler.scal_prod(arr_teach, disp_inv))
                dias = [modeler.int_div(x, 9) for x in subs_teach]
                if self.problem.ahorcadas[t] < 4:
                    for d in range(5):
                        min_completos.append(
                            modeler.count(dias, d) == 9
                        )
                        min_aislados.append(
                            modeler.count(dias, d) == 1
                        )

        # Horas ahorcadas
        lims = [[0, 8], [9, 17], [18, 26], [27, 35], [36, 44]]
        min_ahorcadas_1 = []
        min_ahorcadas_2 = []
        min_dias = []
        prop_ahorcadas_1 = []
        ahorcadas_mults_1 = []
        prop_ahorcadas_2 = []
        ahorcadas_mults_2 = []
        for t in all_teachers:
            if self.problem.ahorcadas[t] < 4:
                slots_teach = []
                for s in subjects_for_teacher[t]:
                    if s in dicc_curriculum:
                        hrs = hours_for_subject[s]
                        for h in range(hrs):
                            slots_teach.append(self.assig_subjects[s, h])
                totales_teacher = 0
                if len(slots_teach) > 1:
                    dias_sem = [modeler.int_div(x, 9) for x in slots_teach]
                    min_dias.append(modeler.count_different(dias_sem))
                    for lim in lims:
                        new_slots_teach = [
                            modeler.conditional(
                                modeler.logical_and(x <= lim[1], x >= lim[0]),
                                x,
                                -1000
                            ) for x in slots_teach
                        ]
                        new_slots_teach_2 = [
                            modeler.conditional(
                                modeler.logical_and(x <= lim[1], x >= lim[0]),
                                x,
                                1000
                            ) for x in slots_teach
                        ]
                        totales_teacher = (
                            totales_teacher +
                            modeler.mod(modeler.max(new_slots_teach), 1000) -
                            modeler.mod(modeler.min(new_slots_teach_2), 1000)
                        )
                        if self.problem.ahorcadas[t] == 1:
                            min_ahorcadas_1.append(
                                modeler.mod(
                                    modeler.max(new_slots_teach), 1000
                                ) - modeler.mod(
                                    modeler.min(new_slots_teach_2), 1000
                                )
                            )
                        if self.problem.ahorcadas[t] == 2:
                            min_ahorcadas_2.append(
                                modeler.mod(
                                    modeler.max(new_slots_teach), 1000
                                ) - modeler.mod(
                                    modeler.min(new_slots_teach_2), 1000
                                )
                            )
                        for slot_ind in new_slots_teach:
                            aux_mults = [
                                modeler.conditional(
                                    slot_dummy > slot_ind, slot_dummy, 1000
                                ) - slot_ind
                                for slot_dummy in new_slots_teach
                            ]
                            if self.problem.ahorcadas[t] == 1:
                                ahorcadas_mults_1.append(
                                    modeler.conditional(
                                        modeler.min(aux_mults) < 10,
                                        modeler.conditional(
                                            modeler.min(aux_mults) > 2,
                                            modeler.min(aux_mults),
                                            0
                                        ),
                                        0
                                    )
                                )
                            if self.problem.ahorcadas[t] == 2:
                                ahorcadas_mults_2.append(
                                    modeler.conditional(
                                        modeler.min(aux_mults) < 10,
                                        modeler.conditional(
                                            modeler.min(aux_mults) > 2,
                                            modeler.min(aux_mults),
                                            0
                                        ),
                                        0
                                    )
                                )
                    totales_teacher = totales_teacher + \
                        modeler.count_different(dias_sem)
                    if self.problem.ahorcadas[t] == 1:
                        prop_ahorcadas_1.append(
                            (totales_teacher / len(slots_teach)))
                    if self.problem.ahorcadas[t] == 2:
                        prop_ahorcadas_2.append(
                            (totales_teacher / len(slots_teach)))

        # Últimas horas preferenciales:
        maestras = ["SilvanaSenzio", "GabrielaSoriano"]
        arr_tmp = []
        for mae in maestras:
            t = self.problem.teachers.index(mae)
            subs = subjects_for_teacher[t]
            for s in subs:
                hrs = range(hours_for_subject[s])
                [arr_tmp.append(self.assig_subjects[s, h]) for h in hrs]
        min_ufpref = modeler.count(
            [modeler.mod(x, 9) for x in arr_tmp], 8)

        # No una hora en lunes:
        mae = "IsabelGonzalez"
        arr_tmp = []
        t = self.problem.teachers.index(mae)
        subs = subjects_for_teacher[t]
        for s in subs:
            hrs = range(hours_for_subject[s])
            [arr_tmp.append(self.assig_subjects[s, h]) for h in hrs]

        self.model.add(sum(min_t2) == 0)
        self.model.add(min_ufpref <= 5)
        self.model.add(sum(ahorcadas_mults_1) <= 9)
        self.model.add(sum(prop_ahorcadas_1) == 0)
        self.model.add(sum(min_ahorcadas_1) <= 191)
        self.model.add(sum(ahorcadas_mults_2) <= 37)
        self.model.add(sum(min_completos) <= 3)
        self.model.add(sum(min_ahorcadas_2) <= 555)
        self.model.add(sum(min_completos) + sum(min_aislados) == 0)
        self.model.add(sum(ahorcadas_mults_1) <= 13)
        self.model.add(sum(prop_ahorcadas_1) <= 9.8737)
        self.model.add(modeler.max(prop_ahorcadas_1) -
                       modeler.min(prop_ahorcadas_1) <= 0.16667)
        self.model.add(min_ufpref <= 6)
        self.model.add(sum(ahorcadas_mults_2) <= 47)

        diffs = [modeler.abs(x - y)
                 for x in prop_ahorcadas_2 for y in prop_ahorcadas_2]
        self.model.add(sum(diffs) <= 63)  # 61.665
        self.model.add(sum(prop_ahorcadas_2) <= 28)  # 26.03
        self.model.add(min_tras[1] <= 4)  # 3
        self.model.add(min_tras[0] <= 6)
        self.model.add(sum(min_tras) <= 24)  # 20

        self.model.add(modeler.minimize_static_lex(
            [min_tras[1], min_tras[0], min_tras[3], min_tras[2], min_tras[4]]))

    def get_subject_for_teacher(self, teacher, day, period):
        nday = self.problem.index(day)
        nperiod = self.problem.index(period)
        nteacher = self.problem.teachers.index(teacher)
        for nsubject, subject in enumerate(self.problem.subjects):
            if nteacher not in self.problem.specialties[nsubject]:
                continue
            for hour in range(self.hours_for_subject[nsubject]):
                slot = self.current_solution[
                    self.assig_subjects[nsubject, hour]
                ]
                if slot is not None:
                    if (
                        nday == int(slot / self.num_periods) and
                        nperiod == slot % self.num_periods
                    ):
                        return subject
        return "---"

    def get_subject_for_course(self, course, day, period):
        nday = self.problem.index(day)
        nperiod = self.problem.index(period)
        for nsubject, subject in enumerate(self.problem.subjects):
            if course != self.dicc_curriculum[nsubject]:
                continue
            for hour in range(self.hours_for_subject[nsubject]):
                slot = self.current_solution[
                    self.assig_subjects[nsubject, hour]
                ]
                if slot is not None:
                    if (
                        nday == int(slot / self.num_periods) and
                        nperiod == slot % self.num_periods
                    ):
                        return subject
        return "---"

    def solve(self, printer):
        print('Solving')
        print time.ctime()
        # file_object = open("export.cpo", "w")
        # file_object.write(self.model.get_cpo_string())
        # file_object.close()
        # sol = self.model.solve(TimeLimit = None)
        # if not sol:
        #     print ("No hay solución!..")
        #     print ("Buscando explicación:")
        #     print time.ctime()
        #     rsol = self.model.refine_conflict()
        #     print ("Explicación encontrada:")
        #     print time.ctime()
        #     rsol.print_conflict()
        # else:
        #     print("Al menos hay una.")
        #     print time.ctime()
        #     self.imprimir(sol, output)
        #     assert(sol.is_solution()) # Just in case...
        #     print("Buscando más:")
        resps = self.model.start_search(TimeLimit=None)
        print time.ctime()
        for msol in resps:
            print str(printer.num_sols) + ".- " + time.ctime() + \
                "  Obj: " + str(msol.get_objective_values())
            # if msol.get_objective_values()[0] < 10:
            self.current_solution = msol
            printer.print_solution(self)


def main():
    print "Inicio:"
    print time.ctime()
    # DATA
    courses = ['1A', '1B', '1C', '1D', '1E', '1F', '2A', '2B', '2C',
               '2D', '2E', '2F', '3A', '3B', '3C', '3D', '3E']  # [' ]
    working_days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    periods = [
        '07:30 a 08:20', '08:20 a 09:05', '09:15 a 10:00', '10:00 a 10:50',
        '10:50 a 11:35', '12:05 a 12:50', '12:50 a 13:35', '13:40 a 14:25',
        '14:25 a 15:10'
    ]

    fname = "docs/Especs_NvoCont.xlsm"
    hoja_materias = xlrd.open_workbook(fname).sheet_by_name("Materias_Sec")
    hoja_docentes = xlrd.open_workbook(fname).sheet_by_name("Docentes_Sec")

    [subjects, divididas, espejos, un_bloque, dia_cerrado,
        mats_examen, definidas] = extraer_materias(hoja_materias)
    [teachers, teachers_work_hours, sin_pesos, castigo,
        ahorcadas] = extraer_maestros(hoja_docentes)
    curriculum = extraer_curriculum(courses, subjects, hoja_materias)
    [dicc_salones, indistintos, salon_por_materia] = extraer_salones(
        hoja_materias)

    specialties_idx_inverse = extraer_specialties(hoja_materias, hoja_docentes)

    problem = SchoolSchedulingProblem(
        subjects, teachers, curriculum, specialties_idx_inverse, working_days,
        periods, courses, teachers_work_hours, dicc_salones, indistintos,
        divididas, sin_pesos, espejos, castigo, un_bloque, dia_cerrado,
        salon_por_materia, mats_examen, definidas, ahorcadas
    )
    solver = SchoolSchedulingSatSolver(problem)
    output = xlwt.Workbook(encoding="utf-8")
    printer = Printer(output, problem)
    solver.solve(printer)


if __name__ == '__main__':
    main()
