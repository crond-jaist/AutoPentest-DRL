import os
import sys
import time
import json
import csv
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import torch
from random import choice

# Files used in various operation modes
TOPOLOGY_PATH = "MulVAL_P/"
LOGICAL_ATTACK_TOPOLOGY = "logical_topology_1.P"
GENERATION_TOPOLOGY_TEMPLATE = "topology_template.P" # also defined in Topology_generator/topo_proc.py
GENERATION_TOPOLOGY_FINAL = "topology_generated.P"
REAL_ATTACK_TOPOLOGY = "real_topology_1.P" # also defined in Nmap_scan/create_top.py

# Lists of server data with vulnerabilties
filedataList = []
webdataList = []
firedataList = []


def createTemp_tem():
    
    env = Environment(loader=FileSystemLoader('./'+TOPOLOGY_PATH), autoescape=select_autoescape('P'))
    template_gen = env.get_template(GENERATION_TOPOLOGY_TEMPLATE)

    fileTemp = list(choice(filedataList))
    webTemp = list(choice(webdataList))
    fireTemp = list(choice(firedataList))

    baiscFile = open('./' + TOPOLOGY_PATH + GENERATION_TOPOLOGY_FINAL, 'w')

    basic_temp = template_gen.render(CVE_Id_Web=webTemp[3], Web_Module=webTemp[0], Web_Transport=webTemp[1],
                                            Web_Port=webTemp[2], Web_Product=webTemp[4], 
                                            CVE_Id_File=fileTemp[3], File_Module=fileTemp[0], 
                                            File_Transport=fileTemp[1], File_Port=fileTemp[2],
                CVE_Id_Fire=fireTemp[3], Fire_Module=fireTemp[0], Fire_Transport=fireTemp[1], 
                                            Fire_Port=fireTemp[2], Fire_Product=fireTemp[4], )


    baiscFile.write(basic_temp)
    baiscFile.close() 
    print("Saved logical topology in '{}'.".format(TOPOLOGY_PATH + GENERATION_TOPOLOGY_FINAL))


def saveVul():

    print('Open preprocessed server data...')
    fileProcessFile = open('./Database/ProcessData/fileData_process.csv', 'r')
    webProcessFile = open('./Database/ProcessData/webData_process.csv', 'r')
    msProcessFile = open('./Database/ProcessData/MSData_process.csv', 'r')
    fireProcessFile = open('./Database/ProcessData/fireData_process.csv', 'r')

    fileProcessData = csv.reader(fileProcessFile)
    webProcessData = csv.reader(webProcessFile)
    msProcessData = csv.reader(msProcessFile)
    fireProcessData = csv.reader(fireProcessFile)

    for filedata in fileProcessData:

        if filedata[1] == 'Permissions, Privileges, and Access Control ':
            file_module = filedata[2]
            file_transport = filedata[3]
            file_port = filedata[4]
            cve_id_file = filedata[0]
            file_product = filedata[5]

            filedataTuple = (file_module, file_transport, file_port, cve_id_file, file_product)
            filedataList.append(filedataTuple)

    webProcessFile.seek(0)
    for webdata in webProcessData:

        if webdata[1] == 'Permissions, Privileges, and Access Control ':
            web_module = webdata[2]
            web_transport = webdata[3]
            web_port = webdata[4]
            cve_id_web = webdata[0]
            web_product = webdata[5]

            webdataTuple = (web_module, web_transport, web_port, cve_id_web, web_product)
            webdataList.append(webdataTuple)

    fireProcessFile.seek(0)
    for firedata in fireProcessData:

        if firedata[1] == 'Permissions, Privileges, and Access Control ':
            fire_module = firedata[2]
            fire_transport = firedata[3]
            fire_port = firedata[4]
            cve_id_fire = firedata[0]
            fire_product = firedata[5]

            firedataTuple = (fire_module, fire_transport, fire_port, cve_id_fire, fire_product)
            firedataList.append(firedataTuple)

    fileProcessFile.close()
    webProcessFile.close()
    msProcessFile.close()
    fireProcessFile.close()

    print('Vulnerability information loaded.')


def startTrain(model):
    
    if not os.path.exists('./DQN/saved_model'):
        os.system('mkdir ./DQN/saved_model')

    if os.path.exists('./DQN/saved_model/dqn_model.pt'):
        os.system('rm ./DQN/saved_model/dqn_model.pt')
        print("Removed previous DQN model in 'DQN/saved_model/dqn_model.pt'.")

    if model == 'logical_attack':
        print("Generate attack graph using MulVAL...")
        os.system('rm -f ./mulval_result/*.*')
        os.chdir('./mulval_result')
        os.system('../repos/mulval/utils/graph_gen.sh ../' + TOPOLOGY_PATH + LOGICAL_ATTACK_TOPOLOGY + ' -v > /dev/null')
        os.chdir('../')
        os.chdir('./DQN')
        print("Process attack graph into attack matrix...")
        os.system('python3 ./confirm_path.py')
        os.chdir('./learn')
        status = os.system('python3 ./dqn_learn.py train')
        os.chdir('../../')
        if os.WIFSIGNALED(status):
            print("Interrupted while conducting DQN training => exit")
    elif model == 'logical_attack_gen':
        print("Generate attack graph using MulVAL...")
        os.system('rm -f ./mulval_result/*.*')
        os.chdir('./mulval_result')
        os.system('../repos/mulval/utils/graph_gen.sh ../' + TOPOLOGY_PATH + GENERATION_TOPOLOGY_FINAL + ' -v > /dev/null')
        os.chdir('../')
        os.chdir('./DQN')
        print("Process attack graph into attack matrix...")
        os.system('python3 ./confirm_path.py')
        os.chdir('./learn')
        status = os.system('python3 ./dqn_learn.py train')
        os.chdir('../../')
        if os.WIFSIGNALED(status):
            print("Interrupted while conducting DQN training => exit")
    elif model == 'nmap':
        print("Process attack graph into attack matrix...")
        os.chdir('./DQN')
        os.system('python3 ./confirm_path.py')
        os.chdir('./learn')
        status = os.system('python3 ./dqn_learn.py nmap')
        os.chdir('../../')
        if os.WIFSIGNALED(status):
            print("Interrupted while conducting DQN training => exit")


def startTrainCode(model):

    if model == 'logical_attack':
        print("--------------------------------------------------------------------------------")
        print("AutoPentest-DRL: Compute attack path for logical network...")
        env = Environment(loader=FileSystemLoader('./'+TOPOLOGY_PATH), autoescape=select_autoescape('P'))
        template = env.get_template(LOGICAL_ATTACK_TOPOLOGY)
        startTrain('logical_attack')
    elif model == 'logical_attack_gen':
        print("--------------------------------------------------------------------------------")
        print("AutoPentest-DRL: Load vulnerability information...")
        saveVul()
        print("--------------------------------------------------------------------------------")
        print("AutoPentest-DRL: Populate topology with vulnerabilities...")
        createTemp_tem()
        print("--------------------------------------------------------------------------------")
        print("AutoPentest-DRL: Compute attack path for generated logical network...")
        startTrain('logical_attack_gen')


def startTemCode():
    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Create random topology using topology-generator...")
    os.chdir('./Topology_generator/topology-generator')
    os.system('python2 topo-gen.py -c ../topo-gen-config -o top_info')
    print("Saved topology in 'Topology_generator/topology-generator/top_info_1.json'.")

    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Convert random topology to MulVAL topology...")
    os.chdir('../')
    status = os.system('python3 topo_proc.py')
    os.chdir('../')
    if os.WEXITSTATUS(status) != 0:
        print("AutoPentest-DRL: Random topology generation failed => abort")
        return

    startTrainCode('logical_attack_gen')


def startRealAttackCode():
    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Get vulnerabilities in target network using Nmap...")
    os.chdir('./Nmap_scan')
    status = os.system('python3 create_top.py')
    if os.WEXITSTATUS(status) != 0:
        print("AutoPentest-DRL: Nmap scanning failed => abort")
        return

    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Generate attack graph using MulVAL...")
    os.system('rm -f ../mulval_result/*.*')
    os.chdir('../mulval_result')
    os.system('../repos/mulval/utils/graph_gen.sh ../Nmap_scan/attack.P -v')

    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Compute attack path for real network...")
    os.chdir('../')
    startTrain('nmap')

    print("--------------------------------------------------------------------------------")
    print("AutoPentest-DRL: Perform penetration testing using Metasploit...")
    os.chdir('./Penetration_tools')
    os.system('python3 ./start_attack.py')
    os.chdir('../')


def start_function(model):

    if model == 'logical_attack':
        print("AutoPentest-DRL: Operation mode:  {}".format("Attack on logical network"))
        print("AutoPentest-DRL: Target topology: {}".format(TOPOLOGY_PATH + LOGICAL_ATTACK_TOPOLOGY))
        startTrainCode('logical_attack')
    elif model == 'logical_attack_gen':
        print("AutoPentest-DRL: Operation mode:  {}".format("Attack on generated logical network"))
        print("AutoPentest-DRL: Target topology: {}".format(TOPOLOGY_PATH + GENERATION_TOPOLOGY_FINAL))
        startTemCode()
    elif model == 'real_attack':
        print("AutoPentest-DRL: Operation mode:  {}".format("Attack on real network"))
        print("AutoPentest-DRL: Target topology: {}".format(TOPOLOGY_PATH + REAL_ATTACK_TOPOLOGY))
        startRealAttackCode()
    else:
        print("AutoPentest-DRL: ERROR: Unrecognized operation mode: {}".format(model))


if __name__ == '__main__':
    try:
        print("################################################################################")
        print("AutoPentest-DRL: Automated Penetration Testing Using Deep Reinforcement Learning")
        print("################################################################################")
        if len(sys.argv) != 2:
            print("ERROR: The operation mode must be specified:")
            print("       $ python3 ./AutoPentest-DRL.py <OPERATION_MODE>")
            print("OPERATION MODES:")
            print("       logical_attack:  Attack on logical network topology")
            print("       real_attack:     Attack on real network topology")
            sys.exit(2)
        model = str(sys.argv[1])
        start_function(model)
    except KeyboardInterrupt:
        print ("\nAutoPentest-DRL: Keyboard interrupt detected => end execution")
        sys.exit(1)
