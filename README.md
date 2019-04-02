# extrato_tesouro_direto
This is a script that runs under Selenium that pulls data from you Tesouro Direto account.
----
1. Install PIP
> apt install python-pip

2 Install Selenium
> pip install --upgrade robotframework-seleniumlibrary

3. Install PyVirtualDisplay
> pip install PyVirtualDisplay

4. Install xvbf
> apt-get install -y xvfb --fix-missing

5. Install Firefox
> apt-get install firefox-esr

6. Install killall
> apt-get install psmisc

7. Download geckodriver and extract to /usr/bin
> wget -qO- https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz | tar xvz -C /usr/bin

8. Test Selenium
> python
* from pyvirtualdisplay import Display
* from selenium import webdriver
* display = Display(visible=0, size=(1024, 768))
* display.start()
* driver = webdriver.Firefox()
* driver.get("https://www.google.com")
* print driver.find_element_by_tag_name("body") != None
* display.stop()
* driver.quit()

9. Edit your "script_tesouro_direto_v0.py" with your credentials, title_type and email_option;

10. Run "python script_tesouro_direto_v0.py"

11. If necessary, add it in your crontab;
example>>> 0 17 * * FRI /usr/bin/python /<path_to_script>/script_tesouro_direto_v0.py >> /dev/null

12. Enjoy !!
