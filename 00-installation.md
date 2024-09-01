# Installation 

1. Confirm that JasperGold can be found: `which jc` 

2. Install Python3 packages using following commands. 

```
cd fv
mkdir pyenv
python3 -m venv pyenv/
source pyenv/bin/activate
python3 -m pip install --upgrade pip 
python3 -m pip install matplotlib pandas networkx cvc5 numpy
python3 -c "import networkx; import numpy; import matplotlib; import cvc5; import pandas" 
```
Make sure no ModuleNotFoundError error returns for the last command.
    
3. Install Graphviz.  
    `$ yum install graphviz`   
     Make sure `$ which dot` returns. 
    
      
