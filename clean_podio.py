from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import pandas as pd
import argparse

# Load credentials
with open('secret.json') as f:
    data = json.load(f)
    email = data['email']
    psswd = data['password']

# Load driver
driver = webdriver.Chrome()
actions = ActionChains(driver)

# Necessary XPATHS
xpaths = {
  'members_table': '//*[@id="wrapper"]/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/table',
  'name_user': '//*[@id="wrapper"]/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[1]/td[1]/div/div[2]/div',
  'hamburguer_icon': '//*[@id="header-global"]/nav/div[1]/div/div[1]/div[1]/div',
  'h3_num_members': '//*[@id="wrapper"]/div/div/div/div/div[1]/div/div/div[2]/div[1]/h3',
}

members_full = {}


def do_login(email, psswd):
    email_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
    email_input.clear()
    email_input.send_keys(email)
    psswd_input = driver.find_element(By.NAME, "password")
    psswd_input.clear()
    psswd_input.send_keys(psswd)
    psswd_input.send_keys(Keys.RETURN)

def wait_to_element_XPATH(name, timeout = 2):
    xpath = xpaths[name]
    try:
      elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
      return elem
    except TimeoutException as e:
      print(f"--- Can't find {name} element in {timeout} seconds timeout. \n")
      raise

def wait_to_element_CLASS(parent, class_name, timeout = 10):
    try:
      elem = WebDriverWait(parent, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
      return elem
    except TimeoutException as e:
      print(f"--- Can't find {class_name} element in {timeout} seconds timeout. \n")
      raise


def get_podio_members(table):
    print("Adicionando todos os membros ao dicionário de membros do Pódio...")
    members = {}
    rows = table.find_elements(By.XPATH, ".//tr")
    rows.pop(0)
    #print(rows[0:2])
    for row in rows:
        user_id = row.get_attribute("data-user-id")
        email = row.find_element(By.CLASS_NAME, "email").text
        members[user_id] = email
    
    return members

def scroll_down(table):
    print("Carregando a tabela completa...")
    total_members = int(driver.find_element(By.XPATH, xpaths['h3_num_members']).text.split('(')[1].split(')')[0])
    rows = table.find_elements(By.XPATH, ".//tr")
    while len(rows) < total_members:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        rows = table.find_elements(By.XPATH, ".//tr")
        time.sleep(1) 
      
    return total_members

def remove_old_members(remove_dict):
    # test_dict = {k: v for k, v in remove_dict.items()[:2]}
    # k = remove_dict.keys()
    # test_dict = {k: remove_dict[k] for k in list(k)[:3]}
    #print(test_dict)
    for k, v in remove_dict.items():
        print(f"Removing user {v} with id {k}")
        tr = driver.find_element(By.XPATH, f'//*[@data-user-id="{k}"]')
        action_dropdown = tr.find_element(By.CLASS_NAME, "action-dropdown")
        actions.move_to_element(action_dropdown).perform()
        action_dropdown.click()
        action_dropdown_wrapper = wait_to_element_CLASS(tr, "action-dropdown-wrapper")
        remove_member = wait_to_element_CLASS(action_dropdown_wrapper, "remove-member")
        remove_member.click()
        ok_button = wait_to_element_CLASS(driver, "button-new.okay-button.primary")
        ok_button.click()
        confirmation_input = wait_to_element_CLASS(driver, "equalToData.required")
        confirmation_input.send_keys("remover")
        time.sleep(1)
        remove_button = wait_to_element_CLASS(driver, "button-new.primary.confirm-button")
        remove_button.click() 
        ok_button = wait_to_element_CLASS(driver, "button-new.close-button.primary")
        ok_button.click() 
        time.sleep(0.5)
        

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # Get file name
  parser.add_argument("--file", help="Nome da planilha com extensão", required=True)
  args = parser.parse_args()

  # Open xlsx
  df = pd.read_excel(args.file)
  # Create Dataframe with column MEMBROS e EMAIL
  df = df[['MEMBROS', 'EMAIL']]
  # Get all members from dataframe and convert to list
  members_list = df["EMAIL"].tolist()

  # Initialize Selenium Chrome Webdriver
  driver.get("https://podio.com/fluxo-consultoria-2c2quifl81")
  assert "Podio" in driver.title  
  do_login(email, psswd)
  # Wait hamburguer_icon to load
  wait_to_element_XPATH('hamburguer_icon')
  # Go to org-members page
  driver.get("https://podio.com/fluxo-consultoria-2c2quifl81/organization/org-members?query=&filter=employee#")
  # Get table of members
  table = wait_to_element_XPATH('members_table')
  total_members = scroll_down(table)
  podio_dict = get_podio_members(table)
  remove_members = [member for member in podio_dict.values() if member not in members_list]
  print(f"{total_members} - {len(members_list)} = {total_members - len(members_list)}")
  print(f"Lenght of remove_members: {len(remove_members)}")
  # print(f"Members to be removed: {remove_members}")
  check_list = [member for member in members_list if member not in podio_dict.values()]
  if len(check_list) > 0:
    print(f"""{len(check_list)} emails aparecem na planilha mas não no Podio. Verificar: \n 
          \t-ortografia/escrita do email
          \t-verificar se o email associado ao pódio do membro é o mesmo da planilha.
          \t-se são novos membros: adicioná-los ao Pódio ou removê-los da Planilha.
          Emails a seguir:
          """)
    print(check_list)
    raise Exception("Emails não encontrados no Podio")

  remove_dict = {k: v for k, v in podio_dict.items() if v in remove_members}
  assert len(remove_dict) == total_members - len(members_list), "Quantidade de membros a serem removidos não corresponde ao esperado"  
  remove_old_members(remove_dict) 
  

  driver.close()