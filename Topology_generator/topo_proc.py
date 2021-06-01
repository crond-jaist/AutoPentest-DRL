import os
import sys
import json
import random
from random import choice
from jinja2 import Environment, select_autoescape, FileSystemLoader

TOPOLOGY_PATH = "MulVAL_P/"
GENERATION_TOPOLOGY_TEMPLATE = "topology_template.P"
GENERATION_TOPO_GEN_TEMPLATE = "topo_gen_template.P"
env = Environment(loader=FileSystemLoader('../' + TOPOLOGY_PATH), autoescape=select_autoescape('P'))
template = env.get_template(GENERATION_TOPO_GEN_TEMPLATE)

def deJsonTop():
    des_list = []
    source_list = []
    server_list = []
    client_list = []
    new_des_list = []
    new_source_list = []

    all_list = []
    new_all_list = []

    with open('./topology-generator/top_info_1.json', 'r') as top_file:
        all_top_data = json.load(top_file)
        if all_top_data['connections']:
            for data in all_top_data['connections']:
                des_id = data['destination_id']
                source_id = data['source_id']
                all_list.append([source_id, des_id])

        if all_top_data['nodes']:
            for data in all_top_data['nodes']:
                node_type = data['node_type']
                node_id = data ['node_id']
                if node_type == 'server':
                    server_list.append(node_id)
                if node_type == 'client':
                    client_list.append(node_id)

    for a in all_list:
        for b in server_list:
            if b == a[0]:
                new_source_list.append([a[0],a[1]])

    for i in new_source_list:
        for j in all_list:
            if i[1] == j[1] and i[0] != j[0]:
                new_all_list.append([i[0],j[0]])


    server_list = random.sample(server_list, len(server_list))
    client_list = random.sample(client_list, len(client_list))

    end = choice(client_list)

    print("Use topology generation template in '{}'...".format(TOPOLOGY_PATH + GENERATION_TOPO_GEN_TEMPLATE))
    output_name = TOPOLOGY_PATH + GENERATION_TOPOLOGY_TEMPLATE
    baiscFile = open('../' + output_name, 'w')
    basic_top = template.render(end=end, source_list0=new_all_list[0][0], source_list1=new_all_list[1][0],source_list2=new_all_list[2][0],source_list3=new_all_list[3][0],
                             des_list0=new_all_list[0][1], des_list1=new_all_list[1][1], des_list2=new_all_list[2][1],des_list3=new_all_list[3][1],
                            server_list0=server_list[0],
                            server_list1=server_list[1], client_list0=client_list[0],
                            CVE_Id_Web='{{CVE_Id_Web}}', Web_Module='{{Web_Module}}', Web_Transport='{{Web_Transport}}',
                            Web_Port='{{Web_Port}}', Web_Product='{{Web_Product}}',
                            CVE_Id_File='{{CVE_Id_File}}', File_Module='{{File_Module}}', File_Transport='{{File_Transport}}',
                            File_Port='{{File_Port}}')

    baiscFile.write(basic_top)
    baiscFile.close()

    print("Saved MulVAL topology template in '{}'.".format(output_name))


if __name__ == "__main__":
    deJsonTop()
