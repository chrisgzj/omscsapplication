class Printer(object):
    def __init__(self, document, problem):
        self.document = document
        self.problem = problem
        self.num_sols = 0

    def print_solution(self, solution):
        self.num_sols += 1
        hoja = self.document.add_sheet("S" + str(self.num_sols))
        aux_fila = 1
        col_ini = 1
        for course in self.problem.courses:
            hoja.write(aux_fila, col_ini, course)
            for nday, day in enumerate(self.problem.working_days):
                hoja.write(aux_fila, col_ini + 1 + nday, day)
                for nperiod, period in enumerate(self.problem.periods):
                    hoja.write(
                        aux_fila + 1 + nperiod, col_ini + 1 + nday,
                        solution.get_subject_for_course(course, day, period)
                    )
            for nperiod, period in enumerate(self.problem.periods):
                hoja.write(aux_fila + 1 + nperiod, col_ini, period)
            aux_fila = aux_fila + len(self.problem.periods) + 2
        aux_fila = 1
        col_ini = 8
        for teacher in self.problem.teachers:
            hoja.write(aux_fila, col_ini, teacher)
            for nday, day in enumerate(self.problem.working_days):
                hoja.write(aux_fila, col_ini + 1 + nday, day)
                for nperiod, period in enumerate(self.problem.periods):
                    hoja.write(
                        aux_fila + 1 + nperiod, col_ini + 1 + nday,
                        solution.get_subject_for_teacher(teacher, day, period)
                    )
            for nperiod, period in enumerate(self.problem.periods):
                hoja.write(aux_fila + 1 + nperiod, col_ini, period)
            aux_fila = aux_fila + len(self.problem.periods) + 2
        self.document.save("docs/output_NCsec.xls")
