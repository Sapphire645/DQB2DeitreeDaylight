import zlib
import struct
from datetime import datetime
from os import makedirs
#import time

#Loading Screen Variables
RunningTask = False

ChunkReading = 0
ItemReading = 0
ItemLocating = 0

BlockReading = 0
ItemReplacing = 0

Saving = 0

#Dictionaries

treeSwap = {577:28,583:29,579:30,578:31,575:1,576:122,15:2,585:820,342:7,159:390,160:442,652:398,466:390,42:249,22:249,23:31}
blockSwap = {156:2,158:126,256:126,232:3,234:7,500:4,147:2,596:155}

restorationItems = {47:52,334:53,50:59}
restorationBlocks = {519:244,28:26,138:139}

deitreeAreaOnlyItem = {26:3,124:6,168:7}
deitreeAreaOnlyBlocks = {530:243,497:161,520:139}

liquidSwap = {191:223,192:224,193:225,194:226,195:227,196:228,197:229,198:230,199:231,347:344,387:384,200:145,201:121,202:122,203:123,204:142,205:143,206:144,207:120,208:128,348:343,388:383}

chunkGridDic = {}
chunkGridDicForPrinting = {}

restorationMixed = {348:134,1360:45,1131:0,1130:0,340:0}
restorationBlockListOffset = {348:{},1360:{},1131:{},1130:{},340:{}}
restorationBlockListBlocks = {348:[],1360:[],1131:[],1130:[],340:[]}

liquidRanges = [1213,1302,1391,1480,1569,1658,1747,1836,1925,2014]
liquidBottomRanges = [1202,1291,1380,1469,1558,1647,1736,1825,1914,2003]

def process(binary_file_path,blocks,liquid,restore,deitree):
    global RunningTask,ChunkReading,ItemReading,ItemLocating,BlockReading,ItemReplacing,Saving
    RunningTask = True
    # Load the binary data from the file
    with open(binary_file_path, 'rb') as f:
        binary_data_raw = f.read()
    # Backup
    makedirs("Backup",exist_ok=True)
    backup = str(datetime.now()).split(".")[0].replace(":","-")
    with open("Backup//"+backup+"-STGDAT02.BIN", 'wb') as backf:
        backf.write(binary_data_raw)
    
    binary_data= zlib.decompress(binary_data_raw[0X110:])
    
    #Get the 2 arrays
    blocksArray = bytearray(binary_data)[0x183FEF0:]
    itemArray = bytearray(binary_data)[0x24E7D1:0x150E7D1]

    itemOffsets = bytearray(binary_data)[0x150E7D1:0x182E7D1]

    chunkGrid = bytearray(binary_data)[0x24C7C1:0x24E7C1]
    
    #Get the Chunk Grid Correspondance
    for i in range(0,0x2000,2):
        if i % 1024 == 0:
            ChunkReading += 1
        gridN = chunkGrid[i] + (chunkGrid[i+1]*256)
        if gridN != 65535:
            chunkGridDic[i/2] = gridN
            chunkGridDicForPrinting[gridN] = [(i//2)%64,i//128]
    
    #Items.
    for i in range(8,0xC8000*24,24):
        if (i-8)//24 % 4096 == 0:
            ItemReading += 1
        itemID = itemArray[i] + (itemArray[i+1]&0x1F)*256
        if blocks and itemID in treeSwap:
            itemID = treeSwap[itemID]
            IDbytes = bytearray(struct.pack('<H', itemID))
            itemArray[i] = IDbytes[0]
            itemArray[i+1] = IDbytes[1] | (itemArray[i+1]&0xE0)
        elif restore and itemID in restorationItems:
                itemID = restorationItems[itemID]
                IDbytes = bytearray(struct.pack('<H', itemID))
                itemArray[i] = IDbytes[0]
                itemArray[i+1] = IDbytes[1] | (itemArray[i+1]&0xE0)
        elif deitree and itemID in deitreeAreaOnlyItem:
                itemID = deitreeAreaOnlyItem[itemID]
                IDbytes = bytearray(struct.pack('<H', itemID))
                itemArray[i] = IDbytes[0]
                itemArray[i+1] = IDbytes[1] | (itemArray[i+1]&0xE0)
        elif restore and itemID in restorationMixed:
            PosX = itemArray[i+1] >> 5
            tmp = itemArray[i+2] & 0x3
            PosX += tmp << 3
            PosY = itemArray[i+2] >> 2
            tmp = itemArray[i+3] & 0x1
            PosY += tmp << 6
            PosZ = itemArray[i+3] & 0x3E
            PosZ >>= 1;
            restorationBlockListOffset[itemID][(i-8)//24]=PosY*0x800+(PosZ*64+PosX*2)
            for delet in range(-8,16): #Delete record
                itemArray[i+delet] = 0

    if restore: ##Add the chunk value to the dict so we know where the block should go.
        for i in range(0,0xC8000*4,4):
            if i % 16384 == 0:
                ItemLocating += 1
            offset = ((itemOffsets[i+1] & 0xF0) >> 4) + (itemOffsets[i+2]<<4) + (itemOffsets[i+3] << 12)
            for IDi in restorationMixed:
                if offset in restorationBlockListOffset[IDi]:
                    chunkG = itemOffsets[i] + ((itemOffsets[i+1] & 0x0F) << 8)
                    if chunkG != 0:
                        chunkVal = chunkGridDic[chunkG]
                        restorationBlockListBlocks[IDi].append(chunkVal*0x30000 + restorationBlockListOffset[IDi][offset])
                        itemOffsets[i] = 0 #Delete record
                        itemOffsets[i+1] = itemOffsets[i+1] & 0xF0

    #Blocks.
    start_time = time.time()
    for i in range(0,0x30000*590,2):
        if i % (0x30000) == 0:
            BlockReading += 1
        CHANGE = False
        blockID = blocksArray[i] + (blocksArray[i+1]&0x07)*256
        if blockID < 28 or blockID == 130 or blockID == 131 or blockID == 146 or blockID == 209 or blockID == 241 or blockID == 341:
            continue #Will need to be tinkered. It's for optimization.
        elif blockID > 600:
            if liquid and blockID > 1201:
                tempIDLiquid = blockID%89
                if tempIDLiquid >= 56 and tempIDLiquid <= 66:
                    blockID = blockID-55
                    blockID = bytearray(struct.pack('<H', blockID))
                    blocksArray[i] = blockID[0]
                    blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
                elif tempIDLiquid >= 45 and tempIDLiquid <= 55:
                    blockID = blockID-33
                    blockID = bytearray(struct.pack('<H', blockID))
                    blocksArray[i] = blockID[0]
                    blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
            else:
                continue
        elif blocks and blockID in blockSwap:
            blockID = blockSwap[blockID]
            blockID = bytearray(struct.pack('<H', blockID))
            blocksArray[i] = blockID[0]
            blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
        elif restore and blockID in restorationBlocks:
            blockID = restorationBlocks[blockID]
            blockID = bytearray(struct.pack('<H', blockID))
            blocksArray[i] = blockID[0]
            blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
        elif deitree and blockID in deitreeAreaOnlyBlocks:
            blockID = deitreeAreaOnlyBlocks[blockID]
            blockID = bytearray(struct.pack('<H', blockID))
            blocksArray[i] = blockID[0]
            blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
        else:
            if liquid:
                if blockID in liquidSwap:
                    blockID = liquidSwap[blockID]
                    blockID = bytearray(struct.pack('<H', blockID))
                    blocksArray[i] = blockID[0]
                    blocksArray[i+1] = blockID[1] | (blocksArray[i+1]&0xF8)
                    
    #print(time.time()-start_time)
    if restore:
        for IDi in restorationMixed:
            for i in restorationBlockListBlocks[IDi]:
                blocksArray[i] = restorationMixed[IDi]
                blocksArray[i+1] = blocksArray[i+1]&0xF8
            ItemReplacing += 1
    #Save.
    binary_data = bytearray(binary_data)
    binary_data[0x183FEF0:] = blocksArray
    binary_data[0x24E7D1:0x150E7D1] = itemArray
    binary_data_edit= zlib.compress(binary_data)
    with open(binary_file_path, 'wb') as fin:
        fin.write(binary_data_raw[:0x110])
        fin.write(binary_data_edit)
    RunningTask = False

