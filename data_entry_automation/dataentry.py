# -*- coding: utf-8 -*-

def llenar_sep(nivel, usuario, password, i_bim, fname, nom_hoja, sologrupos, mats, con_interrupciones):
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
    from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import xlrd
    import time


    driver = webdriver.Firefox(executable_path='/Users/chrisgzj/geckodriver')
    espera = WebDriverWait(driver, 40)
    if nivel == "Primaria":
        driver.get("http://www6.sepdf.gob.mx:8015/siie/")
    if nivel == "Secundaria":
        driver.get("http://www6.sepdf.gob.mx:8006/siie/")
    time.sleep(1)
    driver.execute_script(usuario)
    driver.execute_script(password)
    driver.execute_script("document.querySelector('#ext-gen24').click()")
    time.sleep(20)
    #driver.find_element_by_xpath('//*[@id="ext-gen71"]').click()
    driver.find_element_by_xpath('//*[@id="ext-gen66"]').click()
    time.sleep(1)
    if nivel == "Primaria":
        #driver.find_element_by_id('ext-gen102').click()
        driver.find_element_by_id('ext-gen98').click()
    if nivel == "Secundaria":
        driver.find_element_by_id('ext-gen110').click()
        #driver.find_element_by_id('ext-gen114').click()
    time.sleep(1)
    if nivel == "Primaria":
        driver.execute_script("document.querySelectorAll('td')[110].click()")
    if nivel == "Secundaria":
        #driver.find_element_by_id('ext-gen177').click()
        # driver.execute_script("document.querySelectorAll('td')[161].click()")
        driver.execute_script("document.querySelectorAll('td')[166].click()")
    time.sleep(3)
    if nivel == "Primaria":
        driver.switch_to.frame("ext-gen124")
    if nivel == "Secundaria":
        driver.switch_to.frame("ext-gen136")


    hoja = xlrd.open_workbook(fname).sheet_by_name(nom_hoja)

    nodos = ['id_' + mat + '_calificacion_' for mat in mats if mat != "faltas"]
    if "faltas" in mats:
        nodos.append('id_esp_inasistencias_')

    dicc_mats = {}
    if nivel == "Primaria":
        dicc_mats = {"esp":4,"mat":5,"exns_cn":6,"ledv_geo":7,"his":8,"fce":9,"eart":10,"ef":11,"lex":13,"faltas":12}
    if nivel == "Secundaria":
        dicc_mats = {"esp": 4,"mat": 5,"lex": 6,"cie": 7,"his": 8,"geo": 9,"fce": 10,"art": 11,"edf": 12,"tec": 14,"faltas": 13}


    dicc_califs = {} #Tuple de (alumno, materia) a calificación.
    for aux_fila in range(1,hoja.nrows):
        for mat in mats:
            valor_tmp = hoja.cell(aux_fila,dicc_mats[mat]-1).value
            if valor_tmp != '':
                dicc_califs[(hoja.cell(aux_fila,0).value,mat)] = int(valor_tmp)
        aux_fila += 1

    grados = [1,2,3,4,5,6]
    grupos = [1,2,3,4]
    nom_gpos = ["A","B","C","D"]

    no_encontrados = 0

    aux_alum = 1
    for i_grd in grados:
        for i_gpo in grupos:
            nombre_grupo = str(i_grd) + nom_gpos[i_gpo-1]
            if nombre_grupo in sologrupos:
                time.sleep(1)
                espera.until(EC.presence_of_element_located((By.XPATH,'/html/body/table/tbody/tr/td[3]/select/option[2]')))
                Select(driver.find_element_by_xpath('/html/body/table/tbody/tr/td[3]/select')).select_by_index(i_grd) #Grado
                try:
                    driver.switch_to.alert.accept()
                    driver.switch_to.default_content()
                    driver.switch_to.frame("ext-gen124")
                except:
                    noalerta = 1
                time.sleep(1)
                espera.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td[5]/select/option[2]')))
                Select(driver.find_element_by_xpath('/html/body/table/tbody/tr/td[5]/select')).select_by_index(1) #Turno
                try:
                    driver.switch_to.alert.accept()
                    driver.switch_to.default_content()
                    driver.switch_to.frame("ext-gen124")
                except:
                    noalerta = 1
                time.sleep(1)
                espera.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td[7]/select/option[2]')))
                Select(driver.find_element_by_xpath('/html/body/table/tbody/tr/td[7]/select')).select_by_index(i_gpo) #Grupo
                try:
                    driver.switch_to.alert.accept()
                    driver.switch_to.default_content()
                    driver.switch_to.frame("ext-gen124")
                except:
                    noalerta = 1
                time.sleep(1)
                espera.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr/td[9]/select/option[2]')))
                Select(driver.find_element_by_xpath('/html/body/table/tbody/tr/td[9]/select')).select_by_index(i_bim) #Periodo
                x_yo = '1'
                if con_interrupciones:
                    x_yo = input('Seguir?(1/0)')
                if x_yo == '1':
                    for i_alum in range(0,40):
                        try:
                            alumno = driver.find_element_by_id("id_cell_nombre_" + str(i_alum)).text
                            for n_mat in range(len(mats)):
                                if (alumno,mats[n_mat]) in dicc_califs:
                                    calif = dicc_califs[(alumno,mats[n_mat])]
                                    driver.find_element_by_id(nodos[n_mat] + str(i_alum)).clear()
                                    driver.find_element_by_id(nodos[n_mat] + str(i_alum)).send_keys(str(calif))
                                else:
                                    no_encontrados = no_encontrados + 1
                                    print ("No encontrado: " + alumno + ", " + mats[n_mat])
                        except:
                            var_waste = "Nothing to do here...(ya es cuando se acaban los alumnos del grupo)"
                    driver.find_element_by_id('id_btn_guardar').click()
                    time.sleep(1)
                    espera.until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                    if nivel == "Secundaria":
                        espera.until(EC.alert_is_present())
                        driver.switch_to.alert.accept()
                    driver.switch_to.default_content()

                    if nivel == "Primaria":
                        driver.switch_to.frame("ext-gen124")
                    if nivel == "Secundaria":
                        driver.switch_to.frame("ext-gen136")


def llenar_woodland():
    nivel = "Primaria"
    usuario = "document.querySelector('#username').value = 'code_here'"
    password = "document.querySelector('#j_password').value = 'password_here'"
    i_bim = 3
    fname = "/Users/chrisgzj/Desktop/Para_Captura_3P_3a6.xlsx"
    nom_hoja = "Nva"
    sologrupos = ["3B"]
    mats = ["mat","ledv_geo","fce"]
    # 1y2 ["esp","mat","exns_cn","eart","ef","lex","faltas"]
    # 3 ["esp","mat","exns_cn","ledv_geo","fce","eart","ef","lex","faltas"]
    # 456 ["esp","mat","exns_cn","ledv_geo","his","fce","eart","ef","lex","faltas"]
    # Grupos ["1A","1B","1C","1D","2A","2B","2C","2D","3A","3B","3C","4A","4B","4C","5A","5B","5C","6A","6B","6C"]
    con_interrupciones = True
    llenar_sep(nivel, usuario, password, i_bim, fname, nom_hoja, sologrupos, mats, con_interrupciones)

def llenar_tomasmoro():
    nivel = "Primaria"
    usuario = "document.querySelector('#username').value = 'code_here'"
    password = "document.querySelector('#j_password').value = 'password_here'"
    i_bim = 3
    fname = "/Users/chrisgzj/Desktop/para_captura_TM_3P_corr.xlsx"
    nom_hoja = "SEP_3P"
    sologrupos = ["1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    mats = ["eart","ef"]
    # Grupos: ["1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B"]
    # 1y2 ["esp","mat","exns_cn","eart","ef","lex","faltas"]
    # 3 ["esp","mat","exns_cn","ledv_geo","fce","eart","ef","lex","faltas"]
    # 456 ["esp","mat","exns_cn","ledv_geo","his","fce","eart","ef","lex","faltas"]
    con_interrupciones = True
    llenar_sep(nivel, usuario, password, i_bim, fname, nom_hoja, sologrupos, mats, con_interrupciones)

def llenar_tomasmoro_sec():
    nivel = "Secundaria"
    usuario = "document.querySelector('#username').value = 'code_here'"
    password = "document.querySelector('#j_password').value = 'password_here'"
    i_bim = 3
    fname = "/Users/chrisgzj/Desktop/Para_Captura_Sec3P.xlsx"
    nom_hoja = "SEP_3P"
    sologrupos = ["2A","2B","3A","3B"]
    mats = ["esp","mat","lex","cie","his","fce","art","edf","tec","faltas"]
    # Grupos: ["1A","1B","2A","2B","3A","3B"]
    # Primero: ["esp","mat","lex","cie","his","geo","fce","art","edf","tec","faltas"]
    # SegYTerc: ["esp","mat","lex","cie","his","fce","art","edf","tec","faltas"]
    con_interrupciones = True
    llenar_sep(nivel, usuario, password, i_bim, fname, nom_hoja, sologrupos, mats, con_interrupciones)

llenar_tomasmoro()
