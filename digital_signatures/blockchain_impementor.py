import hashlib
import  json
from urllib.request import urlopen


def make_hash(file_path): 
    
    BLOCK_SIZE = 65536 
    file_hash = hashlib.sha256() 
    with open(file_path, 'rb') as f: 
        fb = f.read(BLOCK_SIZE) 
        while len(fb) > 0: # While there is still data being read from the file
            file_hash.update(fb) # Update the hash
            fb = f.read(BLOCK_SIZE) # Read the next block from the file
    return file_hash.hexdigest()

def add_to_chain(file_path):
    hash=make_hash(file_path)
    url = "http://127.0.0.1:4000/mine_block?file_hash="+hash
    with urlopen(url) as url1:
     data = json.loads(url1.read()) 
    return hash, data["index"]

def verify_hash(hash, index):
    url = "http://127.0.0.1:4000/get_chain"
    with urlopen(url) as url1:
     data = json.loads(url1.read()) 
    c=0
    for i in data["chain"]:
        c=c+1
        j=i["transactions"]
        if len(j)!=0:
            if((str(j[0]["file_hash"]))==str(hash) and c==index):
                return True
    return False

    

if __name__ == '__main__':
   
    hash,index=add_to_chain("input.pdf")
    print(index)
    print(verify_hash(hash,index))