
# User Guide

AutoPentest-DRL has two operation modes, which will be explained
below:
* Logical attack mode
* Real attack mode

We also provide some details about the way in which the DQN (Deep
Q-Network) model training needed by the DRL engine is conducted, and
an overview of the files included in the distribution.


## Logical Attack Mode

The logical attack mode is the main operation mode of AutoPentest-DRL.
In this operation mode no actual attack is conducted, and only the
attack path with highest score is computed for a given logical network
topology. In order to determine the optimal attack path,
AutoPentest-DRL trains the DQN model on the target topology; for
details about this process, see the section **DQN Training** below.

The following command starts AutoPentest-DRL in the logical attack
mode:
```
$ python3 ./AutoPentest-DRL.py logical_attack
```

When computation ends, the optimal attack path will be printed to the
terminal window as shown below:
```
AutoPentest-DRL: Optimal attack path was computed successfully
                 (labels match 'mulval_result/AttackGraph.pdf')
26->24->17->16->15->13->10->9->8->6->5->4->3->2->1
```

In order to understand the meaning of the attack path, please refer to
the node labels prefix that are shown in the file
`mulval_result/AttackGraph.pdf`, which is also generated in the
process. This attack graph visualization can be used to study the
logical attack steps. An example of such an attack graph is pictured
below.

![Example attack graph](/Figures/attack_graph.png?raw=true "Example attack graph")

By default, AutoPentest-DRL uses the sample logical topology in the
file `MulVAL_P/logical_topology_1.P` as target, which includes details
about some servers, their connections, and their vulnerabilities. This
file can modified following the syntax described in the [MulVAL
documentation](https://github.com/risksense/mulval). The file
`MulVAL_P/logical_topology_2.P` contains a second example we
provide. Should you wish to change the attack target, please edit as
needed the constant `LOGICAL_ATTACK_TOPOLOGY` in the file
`AutoPentest-DRL.py`. The two sample network topologies are pictured
below.

![Sample network topologies](/Figures/network_topologies.png?raw=true "Sample network topologies")

### Logical attack on generated topology

To allow studying attacks on various topologies, AutoPentest-DRL
includes a logical attack mode that uses a generated target logical
network topology. To enable this functionality, you need to first
install the tool named `topology-generator` into the directory
`Topology_generator/` by following the corresponding
[documentation](https://github.com/cesarghali/topology-generator). Depending
on your system, you may also need to install tools such as pip install
`matplotlib` (via `pip`) and `python-tk` (via `apt install`).

To start AutoPentest-DRL in the logical attack mode with generated
topology, run the command below:
```
$ python3 ./AutoPentest-DRL.py logical_attack_gen
```

This will first generate a random network topology according to the
configuration in `Topology_generator/topo-gen-config`. Then the
topology generation template `MulVAL_P/topo_gen_template.P` will be
used to create a MulVAL topology template, which will then be
populated with random vulnerabilities before proceeding to the regular
logical attack. Should you wish to make any changes to this operation
mode, please modify as necessary the two files mentioned above. The
generated logical topology with vulnerabilities is saved in
`MulVAL_P/topology_generated.P`, and should be used as reference
regarding the logical attack results for this operation mode.


## Real Attack Mode

The real attack mode refers to using AutoPentest-DRL to conduct an
actual penetration testing attack on a real network. This operation
mode is experimental, and is only provided for demonstration
purposes. Since attacks on real networks are dangerous, please make
sure you exercise caution, as mis-configurations can easily lead to
troubles.

This operation mode is semi-automatic, as it requires some advance
preparation and configuration before use, as follows:
1. Prepare the real target network, for instance by using virtual
   machines on which the desired services and vulnerabilities are
   configured.
2. Describe the target network as a template similar to the file
   `MulVAL_P/real_topology_1.P`, including details about the servers
   and their connections. Vulnerability information is filled in
   automatically by AutoPentest-DRL using Nmap to scan the real target
   network.
3. Specify the IP addresses of the servers to be scanned via Nmap in
   the file `Nmap_scan/scan_config.csv`, which contains the host names
   and their corresponding IP addresses separated by commas.

Once the target network is set up and configurations are done, the
following command can be used to start AutoPentest-DRL in the real
attack mode:
```
$ python3 ./AutoPentest-DRL.py real_attack
```

The command above will first initiate the Nmap scan, then compute the
optimal attack path, and finally Metasploit will be used to perform
the penetration testing attack on the target network. Should you wish
to change the name of the attack target template file, please edit as
needed the constant `REAL_ATTACK_TOPOLOGY` in the file
`AutoPentest-DRL.py`.

### Example attack

As an example, in the figure below AutoPentest-DRL is used to exploit
several vulnerabilities in order to execute an attack sequence via
three servers, so that in the end a tunnel is opened between the
**Internet** and the **workstation**, where a text file serving as a
placeholder for a Trojan virus will be uploaded.

![Example attack process](/Figures/attack_process.png?raw=true "Example attack process")

In the real attack mode, once an attack path is computed, Metasploit
is used to conduct an attack on the target network, and additional
settings may be necessary, depending on the actions that Metasploit is
to perform on the real target network. For instance, our example
requires that the file `/tmp/123.txt` is prepared in advance in order
to successfully complete the last step of copying a Trojan file to the
target machine.

Note that the current implementation of AutoPentest-DRL only includes
support for a few Metasploit actions, as needed for demonstration
purposes. Therefore, in order to use AutoPentest-DRL with other
vulnerabilities, source code modifications are necessary. This
limitation only applies to the real attack mode, and is not an issue
with the logical attack mode, which can make use of any vulnerability
in the database.


## DQN Training

AutoPentest-DRL needs a trained DQN model to operate, and since this
doesn't take very long for our system, we have decided to conduct a
training session each time the program is run. This ensures that the
computed attack path is optimal for the target topology.

Training is automatically conducted for the target topology both for
logical and real attacks before computing the optimal attack path for
that topology. The result may depend on the DQN settings; should you
wish to modify them, for example to change the architecture, you need
to edit the file `DQN/model/dqn_model.py`. Each time a training
session is conducted, the resulting DQN model will be stored in the
file `DQN/saved_model/dqn_model.pt`. An overview of the training
process is shown in the figure below.

![Training process](/Figures/training_process.png?raw=true "Training process")

An important component of the training is the host and vulnerability
database in the `Database/` directory. This directory contains CVE
information, as well as processed data for the Microsoft vulnerability
dataset and several host datasets with embedded CVE information. The
processed data is derived from raw data we retrieved from the
following sources: [Microsoft Security Response
Center](https://msrc.microsoft.com/update-guide/vulnerability) for the
MS dataset, [Shodan](https://www.shodan.io/) for the host dataset, and
[National Vulnerability Database](https://nvd.nist.gov/vuln) for the
CVE information. If you remove any processed data CSV file, then
AutoPentest-DRL will try to regenerate it from the corresponding raw
data files (this is considered to be advanced functionality, so please
see the source code for details).

## File Overview

The AutoPentest-DRL release contains a large number of files, and we
provide an overview below to facilitate development and further
extensions of AutoPentest-DRL.

```
├── DQN                            # Directory for DQN files
│   ├── learn                      # Directory for DQN learning
│   │   ├── env                    # Directory for DQN learning environment
│   │   │   └── environment.py     # DQN training environment
│   │   ├── dqn_learn.py           # DQN learning main file
│   │   └── generateMap.py         # Script to transform attack tree to matrix
│   ├── model                      # Directory for DQN model
│   │   └── dqn_model.py           # DQN model main file
│   ├── processdata                # Directory for DQN processed data
│   ├── saved_model                # Directory for DQN saved model
│   └── confirm_path.py            # Script to confirm the matrix path
├── Database                       # Directory for DQN training data
│   └── ProcessData                # Directory for processed DQN training data
├── Figures                        # Directory for figures
├── MulVAL_P                       # Directory for MulVAL files
│   ├── logical_topology_1.P       # Logical attack topology P file 1
│   ├── logical_topology_1.P       # Logical attack topology P file 2
│   ├── real_topology_1.P          # Real attack topology P file 1
│   ├── real_topology_2.P          # Real attack topology P file 2
│   └── topo_gen_node_temp.P       # Topology generation template P file
├── Nmap_scan                      # Directory for Nmap scan data
│   ├── create_top.py              # Script to create scanning topology
│   ├── decode_nmap.py             # Script to decode the Nmap scanning result
│   └── scan_config.csv            # Configure the IPs for scan targets
├── Penetration_tools              # Directory for penetration tools
│   └── start_attack.py            # Script to start penetration testing
├── Topology_generator             # Directory for topology generator
│   ├── topo-gen-config            # Topology generator config file
│   └── topo_proc.py               # Script to process generated topology
├── mulval_result                  # Directory for storing MulVAL results
├── repos                          # Directory for MulVAL repositories
├── tmp                            # Directory for penetration testing resources
├── AutoPentest-DRL.py             # Main file of AutoPentest-DRL
└── requirements.txt               # File containing required Python packages
```
