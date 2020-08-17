def extraer_specialties(hoja_materias, hoja_docentes):
    corresponds = []
    aux_fila = 1
    while aux_fila < hoja_materias.nrows:
        ls = []
        profs_tmp = hoja_materias.cell(aux_fila, 8).value.split("/")
        for prof in profs_tmp:
            ls.append(int(float(buscarv(hoja_docentes, prof, 1, 0))))
        corresponds.append(ls)
        aux_fila = aux_fila + 1
    return corresponds


def buscarv(hoja, dato, col_busq, col_res):
    resp = ""
    aux_fila = 0
    while (resp == "" and aux_fila < hoja.nrows):
        if hoja.cell(aux_fila, col_busq).value == dato:
            resp = hoja.cell(aux_fila, col_res).value
        aux_fila = aux_fila + 1
    return resp


def extraer_salones(hoja):
    salones = {}
    indistintos = []
    aux_fila = 1
    salon_por_materia = []
    while (aux_fila < hoja.nrows):
        if hoja.cell(aux_fila, 9).value != "":
            if not('%' in hoja.cell(aux_fila, 9).value):
                sals_tmp = (hoja.cell(aux_fila, 9).value).split("/")
                salon_por_materia.append(sals_tmp)
                for sal in sals_tmp:
                    if sal not in salones:
                        salones[sal] = []
                    salones[sal].append(hoja.cell(aux_fila, 1).value)
            else:
                salon_por_materia.append("")
                ind = []
                ind.append(hoja.cell(aux_fila, 4).value)
                ind.append(hoja.cell(aux_fila, 1).value)
                sal_ind = []
                sals_tmp = (hoja.cell(aux_fila, 9).value).split("%")
                for sal in sals_tmp:
                    sal_ind.append(sal)
                ind.append(sal_ind)
                indistintos.append(ind)
        else:
            salon_por_materia.append("")
        aux_fila = aux_fila + 1
    return [salones, indistintos, salon_por_materia]


def extraer_materias(hoja):
    aux_fila = 1
    materias = []
    w_divididas = []
    espejos = []
    un_bloque = []
    dia_cerrado = {}
    mats_examen = {}
    definidas = {}
    while (aux_fila < hoja.nrows and hoja.cell(aux_fila, 1).value != ""):
        materias.append(hoja.cell(aux_fila, 1).value)
        w_divididas.append(hoja.cell(aux_fila, 6).value)
        if hoja.cell(aux_fila, 10).value != "":
            espejos.append([hoja.cell(aux_fila, 1).value,
                            hoja.cell(aux_fila, 10).value])
        if hoja.cell(aux_fila, 11).value == 1:
            un_bloque.append(hoja.cell(aux_fila, 1).value)
        if hoja.cell(aux_fila, 12).value != "":
            dia_cerrado[hoja.cell(aux_fila, 1).value] = hoja.cell(
                aux_fila, 12).value
        if hoja.cell(aux_fila, 13).value != "":
            definidas[hoja.cell(aux_fila, 1).value] = (
                hoja.cell(aux_fila, 13).value).split(",")
        nom_mat = hoja.cell(aux_fila, 2).value
        grado = hoja.cell(aux_fila, 3).value
        if not (nom_mat, grado) in mats_examen:
            mats_examen[(nom_mat, grado)] = []
        mats_examen[(nom_mat, grado)].append(hoja.cell(aux_fila, 1).value)
        aux_fila = aux_fila + 1
    return [materias, w_divididas, espejos, un_bloque, dia_cerrado, mats_examen, definidas]


def extraer_maestros(hoja):
    aux_fila = 1
    maestros = []
    disps = []
    sin_pesos = []
    castigo = []
    ahorcadas = []
    while (aux_fila < hoja.nrows and hoja.cell(aux_fila, 1).value != ""):
        maestro_tmp = hoja.cell(aux_fila, 1).value
        maestros.append(maestro_tmp)
        disp_raw = (hoja.cell(aux_fila, 3).value).split(",")
        disp = []
        for k in disp_raw:
            disp.append(int(float(k)))
        disps.append(disp)
        if hoja.cell(aux_fila, 8).value != "":
            sp_raw = (hoja.cell(aux_fila, 8).value).split("/")
            for h in sp_raw:
                sin_pesos.append((maestro_tmp, h))
        castigo.append(hoja.cell(aux_fila, 9).value)
        ahorcadas.append(hoja.cell(aux_fila, 10).value)
        aux_fila = aux_fila + 1
    return [maestros, disps, sin_pesos, castigo, ahorcadas]


def extraer_curriculum(grupos, materias, hoja):
    curri = {}
    for materia in materias:
        for grupo in grupos:
            curri[(grupo, materia)] = buscar_horas(hoja, grupo, materia)
    return curri


def buscar_horas(hoja, grupo, materia):
    horas = 0
    for fila in range(1, hoja.nrows):
        if hoja.cell(fila, 1).value == materia and hoja.cell(fila, 4).value == grupo:
            horas = int(float(hoja.cell(fila, 5).value))
    return horas

# def leer_inicial(nom_hoja, resp_ini, prob_subjects):
#     fname = "/Users/chrisgzj/Desktop/opciones_sec_nvocont.xlsx"
#     hoja = xlrd.open_workbook(fname).sheet_by_name(nom_hoja)
#     n_gpos = 17 ###########################################
#     dicc_subjects = {}
#     for gpo in range(n_gpos):
#         for j in range(5):
#             for i in range(9):
#                 mats_out = (hoja.cell(2 + gpo * 11 + i, 2 + j).value).split("//")
#                 for m in mats_out:
#                     if not m in dicc_subjects:
#                         dicc_subjects[m] = []
#                     dicc_subjects[m].append(9*j+i)
#     for mat in dicc_subjects:
#         if mat in prob_subjects:
#             s = prob_subjects.index(mat)
#             slots = dicc_subjects[mat]
#             for h in range(len(slots)):
#                 resp_ini.add_integer_var_solution("S:{%i} Hr:{%i}" % (s, h), slots[h])
#         else:
#             print "Excluida, ", mat
#     return resp_ini
