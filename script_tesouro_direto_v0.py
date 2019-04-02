# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time, datetime
import sys
import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib

##############################################
############# DADOS PARA ACESSO ##############

cliente = "SEU NOME"						# <<<< APENAS PARA APARECER NO EMAIL E NOS LOGS
cpf = "seu_cpf"								# <<<< CPF DA CONTA DO TESOURO
tesouro_passwd = "password"					# <<<< SENHA DA CONTA DO TESOURO
titulos=["Tesouro IPCA+ 2035", "Tesouro IPCA+ 2045"]	# <<<< LISTA DE TITULOS
script_folder = "script_folder"				# <<<< PASTA CONTENDO O SCRIPT
send_email = 1								# <<<< FLAG PARA ENVIO DE EMAIL
email_destino = ["to_email@gmail.com"]		# <<<< LISTA COM DESTINATARIOS
email_origem = "from_email@gmail.com"		# <<<< SOMENTE CONTA GMAIL COM OPCAO DE "Acesso a app menos seguro" ATIVO
email_origem_password = 'password'			# <<<< SENHA EXCLUSIVA DO "Acesso a app menos seguro" DA CONTA GOOGLE

##############################################
##############################################

os.chdir(script_folder)

try:
	#os.system('cls')
	print ""
	print "Aguarde..."
	print ""
	print "Verificando cotas do Tesouro Direto..."
	print ""
	
	status1=-1
	count=0
	while (status1 == -1):
		output = subprocess.Popen(["ping", "8.8.8.8", "-c", "1"], stdout=subprocess.PIPE).communicate()[0]
		#print output
		status1 = output.find("1 packets transmitted, 1 received, 0% packet loss")
		#print status1
		time.sleep(1)
		count += 1
		if count > 10:
			print "Teste de ping falhou."
			timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			file = open("./script_tesouro.log","a")
			file.write('['+cliente+'] '+str(timestamp)+': Teste de ping falhou.\n')
			file.close()
			quit()
		if status1 >= 0:
			print "Teste de ping OK."
			print ""

	def page1_is_loaded(driver):
		return driver.find_element_by_tag_name("body") != None
		
	def page2_is_loaded(driver):
		return driver.find_element_by_id("BodyContent_litTDPosiInv") != None

	def page3_is_loaded(driver):
		return driver.find_element_by_id("modalExtratoAnaliticoEntenda") != None

	def page4_is_loaded(driver):
		return driver.find_element_by_id("BodyContent_repSintetico_tblAgenteHeader_0") != None

	def page5_is_loaded(driver):
		return driver.find_element_by_id("modalExtratoAnaliticoEntenda") != None
		

	display = Display(visible=0, size=(1024, 768))
	display.start()

	driver = webdriver.Firefox()
	driver.get("https://tesourodireto.bmfbovespa.com.br/portalinvestidor/")
	
	wait = ui.WebDriverWait(driver, 60)
	wait.until(page1_is_loaded)

	#print ('Site Tesouro acessado.')
	#print ""
	
	#print driver.page_source
	
	#display.stop()
	#quit()
	
	email_field = driver.find_element_by_id("BodyContent_txtLogin")
	email_field.send_keys(cpf)

	password_field = driver.find_element_by_id("BodyContent_txtSenha")
	password_field.send_keys(tesouro_passwd)
	
	password_field.send_keys(Keys.RETURN)
	
	wait = ui.WebDriverWait(driver, 60)
	wait.until(page2_is_loaded)

	#print "Logon no Tesouro Direto efetuado."
	#print ""

	driver.get("https://tesourodireto.bmfbovespa.com.br/portalinvestidor/extrato.aspx")
	wait = ui.WebDriverWait(driver, 60)
	wait.until(page3_is_loaded)

	#print "Carregando extrato..."
	#print ""
	
	driver.find_element_by_id("BodyContent_btnConsultar").click()
	wait = ui.WebDriverWait(driver, 60)
	wait.until(page4_is_loaded)
	
	page1 = driver.page_source

	#cota_compra = subpage4.replace(".", "")
	#cota_compra = float(cota_compra.replace(",", "."))
	#print titulo + " (compra) = " + str(cota_compra)
	
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
	file = open("./script_tesouro.log","a")
	file.write('['+cliente+'] '+str(timestamp)+': Extrato carregado. Recuperando valores das cotas.\n')
	file.close()
	
	BODY = """\
	<html>
	  <head></head>
	  <body>
		<p>
		""" + cliente + """,<br><br>
		Saldo de cotas do Tesouro Direto:
		<br><br>
		<font face="Courier New, Courier, monospace">
	"""
	
	for titulo in titulos:
		subpage1 = page1[page1.find(titulo+"</a>")+22:]
		subpage2 = subpage1[subpage1.find("ExibirAnalitico('QS=")+20:]
		subpage3 = subpage2[:subpage2.find("')")]
		
		print "Carregando pagina de extrato detalhado..."
		print ""
		#print subpage3
		#print ""

		driver.get("https://tesourodireto.bmfbovespa.com.br/portalinvestidor/extrato-analitico.aspx?QS="+subpage3)
		wait = ui.WebDriverWait(driver, 60)
		wait.until(page5_is_loaded)
	
		page2 = driver.page_source
		
		#print page2
		
		subpage1 = page2[page2.find("<tr class=\"nowrap\">"):]
		subpage2 = subpage1[:subpage1.find("</tr>")]
		
		#print subpage2
		
		dados = subpage2.replace("\n", "")
		dados = dados.split("</td>")
		
		valor=[]
		for linha in dados:
			linha = linha.replace(" ","")
			linha = linha.replace(".","")
			linha = linha.replace(",",".")
			valor.append(linha)
			#print valor
		
		valor[0] = datetime.datetime.strptime(valor[0][-10:], '%d/%m/%Y')
		valor[3] = float(valor[3][valor[3].find(">")+1:])
		valor[15] = float(valor[15][valor[15].find(">")+1:])
		n_dias = float((datetime.datetime.now() - valor[0]).days)
		
		print "Titulo: " + titulo
		print "Investido em: " + valor[0].strftime("%d/%m/%Y")
		print "Valor investido: R$ " + str("{:0.2f}".format(valor[3]))
		print "Data atual: " + datetime.datetime.now().strftime("%d/%m/%Y")
		print "Valor atual: R$ " + str("{:0.2f}".format(valor[15])) + " (" + str("{:+0.2f}".format((valor[15]/valor[3]-1)*100)) + "%)"
		print "Media anual: " + str("{:+0.2f}".format((((valor[15]/valor[3])**(1/n_dias))**365-1)*100)) + "%"
		print ""
		
		BODY = BODY + """Título: """ + titulo +"""<br>"""
		BODY = BODY + """Investido em: """ + valor[0].strftime("%d/%m/%Y") +"""<br>"""
		BODY = BODY + """Valor investido: R$ """ + str("{:0.2f}".format(valor[3])) +"""<br>"""
		BODY = BODY + """Data atual: """ + datetime.datetime.now().strftime("%d/%m/%Y") +"""<br>"""
		BODY = BODY + """Valor atual: R$ """ + str("{:0.2f}".format(valor[15])) + " (" + str("{:+0.2f}".format((valor[15]/valor[3]-1)*100)) + "%)" +"""<br>"""
		BODY = BODY + """Média anual: """ + str("{:+0.2f}".format((((valor[15]/valor[3])**(1/n_dias))**365-1)*100)) + "%" +"""<br>"""
		BODY = BODY + """-------------------------------------<br>"""
	
	BODY = BODY + """</font></p></body></html>"""
	display.stop()
	driver.quit()
	
	###################### EMAIL ######################
	
	if send_email == 1:
	
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Saldo Tesouro Direto - " + cliente
		msg['From'] = email_origem
		msg['To'] = ", ".join(email_destino)

		BODY_MIME = MIMEText(BODY, 'html')

		msg.attach(BODY_MIME)
		
		try:  
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.ehlo()
			server.login(email_origem, email_origem_password)
			server.sendmail(email_origem, email_destino, msg.as_string())
			server.close()
			print ""
			print 'Email enviado!'
			print ""
			timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			file = open("./script_tesouro.log","a")
			file.write('['+cliente+'] '+str(timestamp)+': Email enviado.\n')
			file.close()
		except:
			timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			file = open("./script_tesouro.log","a")
			file.write('['+cliente+'] '+str(timestamp)+': Erro de envio de email.\n')
			file.close()
		###################################################
	
except SystemExit:
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	file = open("./script_tesouro.log","a")
	file.write('['+cliente+'] '+str(timestamp)+': Script finalizado.\n')
	file.close() 
except:
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	file = open("./script_tesouro.log","a")
	file.write('['+cliente+'] '+str(timestamp)+': Erro inesperado.\n')
	file.close() 
	subprocess.Popen(["killall", "firefox-esr", "geckodriver", "Xvfb"])
